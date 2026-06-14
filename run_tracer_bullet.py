#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Forest-gram Step 1: 曳光弾（Tracer Bullet）循環シミュレータ
SQLiteデータベース（questsテーブル）およびローカルファイル連携の自律遷移サイクルを再現検証します。
"""
import os
import sys
import json
import sqlite3
import shutil
import time

DB_PATH = "forest_guild.db"
WORKSPACE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECTS_DIR = os.path.join(WORKSPACE_DIR, "projects")
COMMONS_DIR = os.path.join(WORKSPACE_DIR, "forest_commons")

# SQLiteの初期化
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quests (
        ticket_id TEXT PRIMARY KEY,
        project_id TEXT,
        title TEXT,
        status TEXT,
        tags TEXT,
        assigned_agent_id TEXT,
        smile_reward_base INTEGER,
        requirements TEXT,
        test_commands TEXT,
        deliverable_path TEXT
    )
    """)
    conn.commit()
    conn.close()

# ユーザー要件（raw_requirements.txt）の監視とSUN Agentによる分解シミュレーション
def sun_agent_simulate():
    req_file = os.path.join(WORKSPACE_DIR, "raw_requirements.txt")
    if not os.path.exists(req_file):
        # シミュレーション用のダミー要件ファイルを生成
        with open(req_file, "w", encoding="utf-8") as f:
            f.write("メープル材の100mm幅の板が、湿度11%から15%になったときの膨張寸法を計算するPython関数を書いて。クリアランス逃げは不要")
        print(f"[*] Created mock requirements at {req_file}")
        
    with open(req_file, "r", encoding="utf-8") as f:
        req_text = f.read().strip()
        
    print(f"[*] SUN Agent: Analyzing raw requirements: '{req_text}'")
    
    # チケットを生成してDBへ挿入
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    ticket_id = "FG-001"
    project_id = "PRJ-01"
    
    # 既存のチケットがあればクリア
    cursor.execute("DELETE FROM quests WHERE ticket_id = ?", (ticket_id,))
    
    cursor.execute("""
    INSERT INTO quests (ticket_id, project_id, title, status, tags, assigned_agent_id, smile_reward_base, requirements, test_commands, deliverable_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        project_id,
        "メープル板の湿度膨張計算関数の作成",
        "OPEN",
        json.dumps(["Python/Calculator"]),
        None,
        250,
        req_text,
        json.dumps([f"python3 projects/{project_id}/temporary/calc.py"]),
        f"projects/{project_id}/deliverables/calc.py"
    ))
    conn.commit()
    conn.close()
    print(f"[+] SUN Agent: Published ticket {ticket_id} to quest-board (status: OPEN)")

# willowエージェントによるタスク自律取得（CASロック）と実装シミュレーション
def willow_agent_simulate():
    print("[*] Tree Agent (willow): Scanning quest-board...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 対象チケットの取得
    cursor.execute("SELECT ticket_id, project_id, requirements FROM quests WHERE status = 'OPEN'")
    row = cursor.fetchone()
    if not row:
        print("[-] willow: No OPEN tickets found.")
        conn.close()
        return False
        
    ticket_id, project_id, requirements = row
    
    # 楽観的ロック（CAS）の実行
    cursor.execute("""
    UPDATE quests 
    SET status = 'IN_PROGRESS', assigned_agent_id = 'willow_v1'
    WHERE ticket_id = ? AND status = 'OPEN' AND assigned_agent_id IS NULL
    """, (ticket_id,))
    conn.commit()
    
    # 反映行数確認
    cursor.execute("SELECT changes()")
    changes = cursor.fetchone()[0]
    if changes == 0:
        print("[-] willow: CAS lock failed (already claimed).")
        conn.close()
        return False
        
    print(f"[+] willow: CAS lock succeeded for {ticket_id}. Status: IN_PROGRESS")
    
    # 成果物の実装（シミュレーション推論出力）
    # メープル接線膨張係数: 0.0035
    # 膨張計算式: width * factor * delta_moisture (15% - 11% = 4)
    # 100mm * 0.0035 * 4 = 1.4mm
    code_content = """def calculate_expansion(width_mm=100.0, initial_mc=11.0, final_mc=15.0):
    factor = 0.0035  # Maple tangential expansion coefficient
    delta_mc = max(final_mc - initial_mc, 0)
    expansion = width_mm * factor * delta_mc
    return expansion

if __name__ == "__main__":
    result = calculate_expansion()
    print(f"Calculated expansion: {result} mm")
    # 検証用アサーション
    assert abs(result - 1.4) < 1e-5, f"Expected 1.4 but got {result}"
"""
    
    # 共通スキル(write_file)を介した物理書き込みシミュレーション
    temp_dir = os.path.join(PROJECTS_DIR, project_id, "temporary")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, "calc.py")
    
    # write_fileスキルのインポートをシミュレートして実行
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(code_content)
    print(f"[+] willow: Wrote temporary source code to {temp_file_path}")
    
    # 成果物提出（REVIEWへ移行）
    cursor.execute("UPDATE quests SET status = 'REVIEW' WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    print(f"[+] willow: Submitted deliverables. Status: REVIEW")
    return True

# 環境自動テストと「木化（Lignification）」
def environment_test_simulate():
    print("[*] Environment: Running automated tests (Objective Gate)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT ticket_id, project_id, test_commands, deliverable_path FROM quests WHERE status = 'REVIEW'")
    row = cursor.fetchone()
    if not row:
        print("[-] Environment: No tickets in REVIEW state.")
        conn.close()
        return
        
    ticket_id, project_id, test_commands, deliverable_path = row
    
    # コマンド検証（サブプロセス実行の模擬）
    temp_code = os.path.join(PROJECTS_DIR, project_id, "temporary", "calc.py")
    
    # テストの実行
    import subprocess
    result = subprocess.run([sys.executable, temp_code], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"[+] Environment: Test passed. Output: {result.stdout.strip()}")
        
        # 成果物の永続移動 (deliverables配下へコピー)
        deliv_path = os.path.join(WORKSPACE_DIR, deliverable_path)
        os.makedirs(os.path.dirname(deliv_path), exist_ok=True)
        shutil.copy2(temp_code, deliv_path)
        print(f"[+] Environment: Moved verified asset to {deliv_path}")
        
        # 木化 (chmod 444) の適用
        os.chmod(deliv_path, 0o444)
        print(f"[+] Environment: Lignified asset (chmod 444 / read-only)")
        
        # ステータスを LIGNIFIED (木化完了) へ遷移
        cursor.execute("UPDATE quests SET status = 'LIGNIFIED' WHERE ticket_id = ?", (ticket_id,))
        conn.commit()
        print(f"[+] Environment: Ticket {ticket_id} status updated to LIGNIFIED")
    else:
        print(f"[-] Environment: Test failed. Error: {result.stderr}")
        cursor.execute("UPDATE quests SET status = 'POST_MORTEM' WHERE ticket_id = ?", (ticket_id,))
        conn.commit()
        
    conn.close()

# 5Sクレンジングと分解者（shiitake）の堆肥化（humus）
def decomposer_clean_simulate():
    print("[*] Fungi Agent (shiitake): Activating 5S clean & decomposition...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT ticket_id, project_id, deliverable_path FROM quests WHERE status = 'LIGNIFIED'")
    row = cursor.fetchone()
    if not row:
        print("[-] shiitake: No LIGNIFIED tickets to process.")
        conn.close()
        return
        
    ticket_id, project_id, deliverable_path = row
    
    # temporary/内のコードを構文解析したと見なして、humus化（堆肥化）
    temp_dir = os.path.join(PROJECTS_DIR, project_id, "temporary")
    temp_code_path = os.path.join(temp_dir, "calc.py")
    
    if os.path.exists(temp_code_path):
        with open(temp_code_path, "r", encoding="utf-8") as f:
            source_code = f.read()
            
        # humusディレクトリの作成
        humus_dir = os.path.join(COMMONS_DIR, "humus")
        os.makedirs(humus_dir, exist_ok=True)
        
        humus_file = os.path.join(humus_dir, f"vaccine_calculate_expansion.md")
        with open(humus_file, "w", encoding="utf-8") as f:
            f.write(f"# Humus snippet: calculate_expansion\n")
            f.write(f"- Source Agent: willow_v1\n")
            f.write(f"- Tags: [Python/Calculator]\n\n")
            f.write(f"```python\n{source_code}```\n")
        print(f"[+] shiitake: Consolidated reusable humus code at {humus_file}")
        
        # temporaryの物理削除 (5Sクレンジング)
        shutil.rmtree(temp_dir)
        print(f"[+] shiitake: Cleaned temporary workspace (rm -rf {temp_dir})")
        
    conn.close()

if __name__ == "__main__":
    print("=== Forest-gram Step 1: Tracer Bullet Loop Starting ===")
    init_db()
    sun_agent_simulate()
    if willow_agent_simulate():
        environment_test_simulate()
        decomposer_clean_simulate()
    print("=== Tracer Bullet Loop Completed ===")
