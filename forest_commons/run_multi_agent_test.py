import os
import json
import sqlite3
from gemini_client import generate_text_with_gemini
from llm_client import LocalLLMClient

def run_multi_agent_system_simulation():
    # 1. ユーザー要件
    user_requirement = "明日から10年の間に資産を1000万増やす方法"
    
    # .env から API キーをロード (SUN Agent用)
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    api_key = None
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    api_key = line.split("GEMINI_API_KEY=")[1].strip()

    if not api_key:
        print("[-] Error: GEMINI_API_KEY not found in .env")
        return

    print("==================================================")
    print("【Phase 1: SUN Agent (Gemini)】要件パース・クエスト分解")
    print("==================================================")
    print(f"原始要件: '{user_requirement}'")
    
    sun_prompt = f"""
あなたはForest-gramの「SUN Agent (太陽エージェント)」です。ユーザーの曖昧な要求をパースし、
依存関係を持つ複数のサブタスク（クエストチケット）に分解してください。

【ユーザー要件】
{user_requirement}

【出力形式】
以下のJSONフォーマットのみを厳密に出力してください。他のテキストは一切含めないでください。

[
  {{
    "ticket_id": "FG-ASSET-01",
    "title": "資産形成の数値シミュレーションおよびプラン構築",
    "tags": ["Finance", "Calculator"],
    "assigned_agent_id": "maple_v3"
  }},
  {{
    "ticket_id": "FG-ASSET-02",
    "title": "ポートフォリオ設計および自己投資・副業戦略の策定",
    "tags": ["Finance", "Strategy"],
    "assigned_agent_id": "walnut_v1"
  }}
]
"""
    # SUN Agentが要件を分解してチケットを発行する
    tickets_json = generate_text_with_gemini(sun_prompt, api_key=api_key)
    
    # JSON以外の余計な文字を取り除くクレンジング
    if "```json" in tickets_json:
        tickets_json = tickets_json.split("```json")[1].split("```")[0].strip()
    elif "```" in tickets_json:
        tickets_json = tickets_json.split("```")[1].split("```")[0].strip()
    
    try:
        tickets = json.loads(tickets_json.strip())
    except Exception as e:
        print(f"[-] SUN Agent JSON parse error: {str(e)}")
        # フォールバック
        tickets = [
            {
                "ticket_id": "FG-ASSET-01",
                "title": "資産形成の数値シミュレーションおよびプラン構築",
                "tags": ["Finance", "Calculator"],
                "assigned_agent_id": "maple_v3"
            },
            {
                "ticket_id": "FG-ASSET-02",
                "title": "ポートフォリオ設計および自己投資・副業戦略の策定",
                "tags": ["Finance", "Strategy"],
                "assigned_agent_id": "walnut_v1"
            }
        ]
        
    print(f"[+] SUN Agent: Discovered {len(tickets)} subtasks and published to quest-board.")
    print(json.dumps(tickets, indent=2, ensure_ascii=False))

    # DBの初期化とシード（IMEDIATEトランザクションで競合防止）
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../forest_guild.db"))
    conn = sqlite3.connect(db_path)
    conn.isolation_level = None  # autocommit off -> manual BEGIN
    cursor = conn.cursor()
    
    # アトミックに既存チケットを削除してから再挿入
    cursor.execute("BEGIN IMMEDIATE")
    cursor.execute("DELETE FROM quests WHERE ticket_id LIKE 'FG-ASSET-%'")
    
    for t in tickets:
        cursor.execute("""
        INSERT INTO quests (ticket_id, project_id, title, status, tags, assigned_agent_id, smile_reward_base, requirements, test_commands, deliverable_path)
        VALUES (?, 'PRJ-ASSET', ?, 'OPEN', ?, NULL, 250, ?, '[]', '')
        """, (
            t["ticket_id"],
            t["title"],
            json.dumps(t["tags"]),
            user_requirement,
        ))
    cursor.execute("COMMIT")

    print("\n==================================================")
    print("【Phase 2: Tree Agent (Local LLM → Gemini Fallback)】チケット自律実行")
    print("==================================================")
    
    # ローカルLLMクライアントを初期化（接続確認用）
    local_client = LocalLLMClient()
    
    # ローカルLLMが使えるか事前チェック（3秒以内で判定）
    local_llm_available = local_client.is_available()
    if local_llm_available:
        print(f"[+] ローカルLLM 稼働中 → {local_client.model}")
    else:
        print("[!] ローカルLLM 応答なし → 全チケットを Gemini API で処理します（高速モード）")
    
    if not local_llm_available:
        print("[!] ローカルLLM は応答なし → 全チケットを Gemini API で処理します（高速モード）")
    
    for t in tickets:
        print(f"\n[*] Tree Agent: Processing ticket {t['ticket_id']} - {t['title']}")
        
        # ステータスを IN_PROGRESS に更新
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute("""
        UPDATE quests 
        SET status = 'IN_PROGRESS', assigned_agent_id = ?
        WHERE ticket_id = ? AND status = 'OPEN'
        """, (t["assigned_agent_id"], t["ticket_id"]))
        affected = conn.total_changes
        cursor.execute("COMMIT")
        
        print(f"[+] Agent '{t['assigned_agent_id']}' locked ticket {t['ticket_id']} (IN_PROGRESS)")
        
        # プロンプト構築
        prompt = f"""
あなたはForest-gramの専門樹木エージェントです。以下のタスク要件に沿って具体的かつ詳細な成果物を作成してください。

【全体ゴール】
{user_requirement}

【あなたのタスク】
{t['title']}

【あなたの専門スキルタグ】
{', '.join(t['tags'])}

具体的な数値、ステップ、実行可能なアクションプランを含めてください。
"""
        output_content = None
        
        # ローカルLLMで処理（利用可能な場合のみ、1回だけ試行）
        if local_llm_available:
            try:
                print(f"[*] ローカルLLM ({local_client.model}) で処理中...")
                output_content = local_client.generate(
                    prompt, 
                    system_prompt="You are a precise financial advisor specialized agent. Respond in Japanese."
                )
                print(f"[+] Agent '{t['assigned_agent_id']}' → ローカルLLMで成果物生成完了")
            except Exception as e:
                print(f"[!] ローカルLLM 失敗: {str(e)[:100]} → Gemini にフォールバック")
                output_content = None
        
        # Gemini API フォールバック（または直接使用）
        if output_content is None:
            try:
                print(f"[*] Gemini API で処理中... (Agent: {t['assigned_agent_id']})")
                fallback_prompt = prompt + "\n※あなたはローカル環境の専門Tree Agentとして振る舞い、具体的な数値やプランを算出してください。"
                output_content = generate_text_with_gemini(fallback_prompt, api_key=api_key)
                print(f"[+] Agent '{t['assigned_agent_id']}' → Gemini API で成果物生成完了")
            except Exception as fe:
                print(f"[-] Gemini フォールバックも失敗: {str(fe)}")
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("UPDATE quests SET status = 'POST_MORTEM' WHERE ticket_id = ?", (t["ticket_id"],))
                cursor.execute("COMMIT")
                continue
            
        # 成果物の一時保存
        try:
            temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../projects/PRJ-ASSET/temporary"))
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, f"{t['ticket_id']}_output.txt")
            
            # 既に木化（chmod 444）されていたら書き込み前に権限を緩める
            if os.path.exists(temp_path):
                try:
                    os.chmod(temp_path, 0o777)
                except Exception:
                    pass
                
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(output_content)
            print(f"[+] 一時成果物を保存: {temp_path}")
            
            # REVIEW ステータスに更新
            rel_path = f"projects/PRJ-ASSET/temporary/{t['ticket_id']}_output.txt"
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute(
                "UPDATE quests SET status = 'REVIEW', deliverable_path = ? WHERE ticket_id = ?",
                (rel_path, t["ticket_id"])
            )
            cursor.execute("COMMIT")
            print(f"[+] チケット {t['ticket_id']} → REVIEW に遷移完了")
            
        except Exception as e:
            print(f"[-] 成果物保存失敗: {str(e)}")
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("UPDATE quests SET status = 'POST_MORTEM' WHERE ticket_id = ?", (t["ticket_id"],))
            cursor.execute("COMMIT")

    print("\n==================================================")
    print("【Phase 3: Integration & Lignification (木化)】最終成果物合成")
    print("==================================================")
    
    # REVIEW ステータスのチケットを取得
    cursor.execute("SELECT ticket_id, title, assigned_agent_id, deliverable_path FROM quests WHERE status = 'REVIEW' AND ticket_id LIKE 'FG-ASSET-%'")
    review_tickets = cursor.fetchall()
    
    print(f"[*] REVIEW ステータスのチケット数: {len(review_tickets)}")
    
    if not review_tickets:
        print("[-] REVIEW 状態のチケットが0件です。Phase 2 の出力を確認してください。")
        conn.close()
        return
    
    # 最終ドキュメント構築
    final_output = "# 10年で1000万円増やす現実的資産形成ロードマップ (多エージェント合成版)\n\n"
    final_output += f"**生成日時**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    final_output += "---\n\n"
    
    for rt in review_tickets:
        tid, title, agent, deliv_rel_path = rt
        temp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../{deliv_rel_path}"))
        
        if os.path.exists(temp_path):
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            final_output += f"## {title}\n"
            final_output += f"**担当エージェント**: {agent} | **チケットID**: {tid}\n\n"
            final_output += f"{content}\n\n"
            final_output += "---\n\n"
            
            # deliverables フォルダにコピーして木化
            deliv_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), 
                f"../projects/PRJ-ASSET/deliverables/{tid}_output.txt"
            ))
            os.makedirs(os.path.dirname(deliv_path), exist_ok=True)
            
            if os.path.exists(deliv_path):
                try:
                    os.chmod(deliv_path, 0o777)
                except Exception:
                    pass
            
            with open(deliv_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # 木化 (読み取り専用)
            os.chmod(deliv_path, 0o444)
            print(f"[+] 木化完了: {deliv_path}")
            
            # ステータスを LIGNIFIED に更新
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("UPDATE quests SET status = 'LIGNIFIED' WHERE ticket_id = ?", (tid,))
            cursor.execute("COMMIT")
            print(f"[+] チケット {tid} → LIGNIFIED")
        else:
            print(f"[-] 成果物ファイルが見つかりません: {temp_path}")
    
    # 最終ドキュメントの保存
    final_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../projects/PRJ-ASSET/deliverables"))
    os.makedirs(final_dir, exist_ok=True)
    final_path = os.path.join(final_dir, "final_composite_roadmap.md")
    
    if os.path.exists(final_path):
        try:
            os.chmod(final_path, 0o777)
        except Exception:
            pass
    
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(final_output)
    
    os.chmod(final_path, 0o444)
    
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"[★ SUCCESS] 最終成果物が合成されました:")
    print(f"  {final_path}")
    print(f"{'='*50}")
    print(f"\n--- 最終成果物プレビュー (最初の500文字) ---")
    print(final_output[:500])
    print("...")

if __name__ == "__main__":
    run_multi_agent_system_simulation()
