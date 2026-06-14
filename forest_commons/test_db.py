import os
import unittest
import sqlite3
import json
import uuid
from db import init_db, get_db_connection

TEST_DB = "test_forest_guild.db"

class TestForestDatabase(unittest.TestCase):

    def setUp(self):
        # テスト開始前に既存のテスト用DBを削除して初期化
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_db(TEST_DB)
        self.conn = get_db_connection(TEST_DB)

    def tearDown(self):
        self.conn.close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_tables_creation(self):
        """必要なテーブルがすべて作成されているか検証します。"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row['name'] for row in cursor.fetchall()]
        
        expected_tables = [
            'users', 'tree_agents', 'quests', 'skills', 
            'agent_skills', 'genealogy', 'traits', 'episodic_logs'
        ]
        for table in expected_tables:
            self.assertIn(table, tables)

    def test_tree_agents_constraints(self):
        """tree_agentsの制約チェック (cladeの許容値、パラメータ範囲等)"""
        cursor = self.conn.cursor()
        
        # 正常なデータ挿入
        agent_id = str(uuid.uuid4())
        palette = json.dumps(["#ffffff"] * 16)
        cursor.execute("""
        INSERT INTO tree_agents (
            id, name, clade, precision_val, velocity_val, efficiency_val, 
            harmony_val, resilience_val, avatar_url, genetic_palette
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (agent_id, "test_maple", "HARDWOOD", 80, 80, 80, 80, 80, "http://ex.com/a.png", palette))
        self.conn.commit()

        # 不正なcladeの挿入を試みる (制約エラー期待)
        bad_id = str(uuid.uuid4())
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
            INSERT INTO tree_agents (
                id, name, clade, precision_val, velocity_val, efficiency_val, 
                harmony_val, resilience_val, avatar_url, genetic_palette
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (bad_id, "bad_agent", "INVALID_CLADE", 80, 80, 80, 80, 80, "http://ex.com/b.png", palette))
            self.conn.commit()

    def test_episodic_logs_fifo_trigger(self):
        """episodic_logsのFIFO 10件制限トリガーを検証します。"""
        cursor = self.conn.cursor()
        
        # 依存するエージェントを登録
        agent_id = str(uuid.uuid4())
        palette = json.dumps(["#ffffff"] * 16)
        cursor.execute("""
        INSERT INTO tree_agents (
            id, name, clade, precision_val, velocity_val, efficiency_val, 
            harmony_val, resilience_val, avatar_url, genetic_palette
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (agent_id, "willow", "SOFTWOOD", 90, 90, 90, 90, 90, "http://ex.com/willow.png", palette))
        self.conn.commit()

        # 12件のログを追加
        for i in range(12):
            log_id = f"LOG-{i:03d}"
            cursor.execute("""
            INSERT INTO episodic_logs (id, agent_id, log_content)
            VALUES (?, ?, ?)
            """, (log_id, agent_id, f"Log record number {i}"))
            self.conn.commit()

        # 件数が10件に制限されているか検証
        cursor.execute("SELECT id, log_content FROM episodic_logs WHERE agent_id = ? ORDER BY created_at ASC", (agent_id,))
        logs = cursor.fetchall()
        
        self.assertEqual(len(logs), 10)
        # 最も古い2件 (LOG-000, LOG-001) が削除され、LOG-002から始まっているか確認
        self.assertEqual(logs[0]['id'], 'LOG-002')
        self.assertEqual(logs[-1]['id'], 'LOG-011')

if __name__ == "__main__":
    unittest.main()
