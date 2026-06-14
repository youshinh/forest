import os
import sqlite3
import json

DB_FILE = "forest_guild.db"

def get_db_connection(db_path=DB_FILE):
    """SQLite接続を取得し、外部キー制約を有効にします。"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path=DB_FILE):
    """データベーステーブルとFIFOトリガーを初期化します。"""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # ① users（庭師マスターテーブル）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        tailscale_device_id TEXT,
        smile_wallet INTEGER NOT NULL DEFAULT 500
    );
    """)

    # ② tree_agents（樹木エージェントマスタテーブル）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tree_agents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        level INTEGER NOT NULL DEFAULT 1,
        experience INTEGER NOT NULL DEFAULT 0,
        clade TEXT NOT NULL CHECK (clade IN ('HARDWOOD', 'SOFTWOOD')),
        smile_wallet INTEGER NOT NULL DEFAULT 500,
        trust_score INTEGER NOT NULL DEFAULT 95 CHECK (trust_score BETWEEN 0 AND 100),
        precision_val INTEGER NOT NULL CHECK (precision_val BETWEEN 1 AND 100),
        velocity_val INTEGER NOT NULL CHECK (velocity_val BETWEEN 1 AND 100),
        efficiency_val INTEGER NOT NULL CHECK (efficiency_val BETWEEN 1 AND 100),
        harmony_val INTEGER NOT NULL CHECK (harmony_val BETWEEN 1 AND 100),
        resilience_val INTEGER NOT NULL CHECK (resilience_val BETWEEN 1 AND 100),
        avatar_url TEXT NOT NULL,
        genetic_palette TEXT NOT NULL -- JSON list of 16 color codes
    );
    """)

    # ③ quests（クエストチケットテーブル）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quests (
        ticket_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('RAW', 'OPEN', 'IN_PROGRESS', 'REVIEW', 'LIGNIFIED', 'POST_MORTEM')),
        assigned_agent_id TEXT REFERENCES tree_agents(id) ON DELETE SET NULL,
        smile_reward_base INTEGER NOT NULL CHECK (smile_reward_base BETWEEN 10 AND 1000),
        deliverable_path TEXT,
        test_commands TEXT NOT NULL, -- JSON string array
        requirements TEXT,
        tags TEXT -- JSON string array of skill tags
    );
    """)

    # ④ skills（グローバルスキルマスターテーブル）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        schema_json TEXT NOT NULL
    );
    """)

    # ⑤ agent_skills（エージェント保有スキル中間テーブル）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_skills (
        agent_id TEXT REFERENCES tree_agents(id) ON DELETE CASCADE,
        skill_id TEXT REFERENCES skills(id) ON DELETE CASCADE,
        PRIMARY KEY (agent_id, skill_id)
    );
    """)

    # ⑥ genealogy（多次元血統マッピングテーブル）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS genealogy (
        id TEXT PRIMARY KEY,
        child_id TEXT UNIQUE NOT NULL REFERENCES tree_agents(id) ON DELETE CASCADE,
        parent_a_id TEXT REFERENCES tree_agents(id) ON DELETE SET NULL,
        parent_b_id TEXT REFERENCES tree_agents(id) ON DELETE SET NULL,
        generation INTEGER NOT NULL DEFAULT 1,
        blend_ratio REAL NOT NULL CHECK (blend_ratio BETWEEN 0.200 AND 0.800),
        mutation_occurred INTEGER NOT NULL DEFAULT 0 CHECK (mutation_occurred IN (0, 1))
    );
    """)

    # ⑦ traits（動的状態異常・バフテーブル）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS traits (
        id TEXT PRIMARY KEY,
        agent_id TEXT NOT NULL REFERENCES tree_agents(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        type TEXT NOT NULL CHECK (type IN ('BUFF', 'DEBUFF', 'PASSIVE')),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ⑧ episodic_logs（短期エピソード記憶テーブル / FIFO 10件制限）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS episodic_logs (
        id TEXT PRIMARY KEY,
        agent_id TEXT NOT NULL REFERENCES tree_agents(id) ON DELETE CASCADE,
        log_content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # FIFO 10件制限トリガーの設定
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS limit_episodic_logs AFTER INSERT ON episodic_logs
    BEGIN
        DELETE FROM episodic_logs
        WHERE agent_id = NEW.agent_id
          AND id NOT IN (
              SELECT id FROM episodic_logs
              WHERE agent_id = NEW.agent_id
              ORDER BY rowid DESC
              LIMIT 10
          );
    END;
    """)

    conn.commit()
    conn.close()
    print("[+] Database initialized successfully.")

if __name__ == "__main__":
    init_db()
