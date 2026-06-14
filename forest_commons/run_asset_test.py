import os
import json
import sqlite3
from gemini_client import generate_text_with_gemini

def run_asset_growth_simulation():
    # .env から API キーをロード
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

    print("=== [SUN Agent] Analyzing User Requirement ===")
    user_requirement = "明日から10年の間に資産を1000万増やす方法"
    print(f"User Goal: {user_requirement}\n")

    # DB 接続とチケット生成
    db_path = "forest_guild.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    ticket_id = "FG-ASSET-001"
    cursor.execute("DELETE FROM quests WHERE ticket_id = ?", (ticket_id,))
    cursor.execute("""
    INSERT INTO quests (ticket_id, project_id, title, status, tags, assigned_agent_id, smile_reward_base, requirements, test_commands, deliverable_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        "PRJ-ASSET",
        "10年で1000万円資産を増やすロードマップ構築",
        "IN_PROGRESS",
        json.dumps(["Finance", "Strategy"]),
        "gemini_expert_agent",
        500,
        user_requirement,
        "[]",
        "projects/PRJ-ASSET/deliverables/asset_strategy.md"
    ))
    conn.commit()
    print(f"[+] Created and assigned ticket {ticket_id} to gemini_expert_agent.")

    # Specialized Expert Agent (Gemini) triggering output
    print("\n=== [Gemini Expert Agent] Formulating Asset Strategy ===")
    prompt = f"""
あなたは自律循環型エージェント生態系「Forest-gram」のファイナンシャル・ストラテジスト専門エージェントです。
以下のユーザー要件に基づき、数学的・現実的かつ実行可能な10年間の資産形成ロードマップを詳細に提案してください。

【要件】
{user_requirement}

【出力形式】
1. 必要な年間・月間の積立・運用計画（利回りシミュレーションを含む）
2. 具体的な推奨ポートフォリオ設計（インデックス投資、自己投資、副業など）
3. リスク管理と注意点
"""

    try:
        strategy_output = generate_text_with_gemini(prompt, api_key=api_key)
        print("\n--- Strategy Output Generated ---")
        print(strategy_output)
        print("---------------------------------\n")

        # 成果物の保存
        deliverable_dir = os.path.join(os.path.dirname(__file__), "../projects/PRJ-ASSET/deliverables")
        os.makedirs(deliverable_dir, exist_ok=True)
        deliverable_path = os.path.join(deliverable_dir, "asset_strategy.md")
        
        with open(deliverable_path, "w", encoding="utf-8") as f:
            f.write(strategy_output)
        print(f"[+] Deliverable saved to {deliverable_path}")

        # 木化 (Lignification)
        os.chmod(deliverable_path, 0o444)
        print("[+] Lignified deliverable asset (chmod 444 / read-only).")

        # チケットのステータスを LIGNIFIED に移行
        cursor.execute("UPDATE quests SET status = 'LIGNIFIED', deliverable_path = ? WHERE ticket_id = ?", 
                       ("projects/PRJ-ASSET/deliverables/asset_strategy.md", ticket_id))
        conn.commit()
        print(f"[+] Ticket {ticket_id} status updated to LIGNIFIED.")

    except Exception as e:
        print(f"[-] Expert Agent failed to generate strategy: {str(e)}")
        cursor.execute("UPDATE quests SET status = 'POST_MORTEM' WHERE ticket_id = ?", (ticket_id,))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    run_asset_growth_simulation()
