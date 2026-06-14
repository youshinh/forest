import os
import unittest
import shutil
import json
import uuid
import sqlite3
from db import init_db, get_db_connection
from git_ops import GitOperations
from physiology import Lignifier, Pruner, ResilientCaller
from genetics import CrossoverEngine, MetabolismManager, PiankaCalculator
from seed_skills import seed_skills_from_matrix

TEST_DB = "integration_test.db"
TEST_REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp_integration_git"))
TEST_WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp_integration_workspace"))

class TestE2EIntegration(unittest.TestCase):

    def setUp(self):
        # クリーンアップ
        for path in [TEST_DB, TEST_REPO_DIR, TEST_WORKSPACE_DIR]:
            if os.path.exists(path):
                if os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for f in files:
                            try:
                                os.chmod(os.path.join(root, f), 0o777)
                            except Exception:
                                pass
                        for d in dirs:
                            try:
                                os.chmod(os.path.join(root, d), 0o777)
                            except Exception:
                                pass
                    try:
                        shutil.rmtree(path)
                    except Exception:
                        import subprocess
                        subprocess.run(["rmdir", "/s", "/q", path], shell=True)
                else:
                    try:
                        os.chmod(path, 0o777)
                    except Exception:
                        pass
                    os.remove(path)

        os.makedirs(TEST_REPO_DIR, exist_ok=True)
        os.makedirs(TEST_WORKSPACE_DIR, exist_ok=True)

        # 1. データベース初期化 & スキルシード
        init_db(TEST_DB)
        seed_skills_from_matrix(db_path=TEST_DB)

        # 2. Gitモックリポジトリ設定
        try:
            import subprocess
            subprocess.run(["git", "init"], cwd=TEST_REPO_DIR, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Gardener"], cwd=TEST_REPO_DIR, check=True)
            subprocess.run(["git", "config", "user.email", "gardener@local"], cwd=TEST_REPO_DIR, check=True)
            # ダミーファイルコミットしてmainブランチ確立
            with open(os.path.join(TEST_REPO_DIR, ".gitkeep"), "w") as f:
                f.write("")
            subprocess.run(["git", "add", ".gitkeep"], cwd=TEST_REPO_DIR, check=True)
            subprocess.run(["git", "commit", "-m", "Initial"], cwd=TEST_REPO_DIR, check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=TEST_REPO_DIR, check=True)
            self.git_ops = GitOperations(TEST_REPO_DIR)
        except Exception as e:
            self.skipTest(f"Git execution is not available: {str(e)}")

        self.metabolism = MetabolismManager(db_path=TEST_DB, workspace_dir=TEST_WORKSPACE_DIR)

    def tearDown(self):
        for path in [TEST_DB, TEST_REPO_DIR, TEST_WORKSPACE_DIR]:
            if os.path.exists(path):
                if os.path.isdir(path):
                    # 読み取り専用になっている木化ファイルを解除してから削除
                    for root, dirs, files in os.walk(path):
                        for f in files:
                            try:
                                os.chmod(os.path.join(root, f), 0o777)
                            except Exception:
                                pass
                    shutil.rmtree(path)
                else:
                    os.remove(path)

    def test_e2e_metabolism_crossover_and_git(self):
        """データベース登録 -> チケットPull -> 実装コミット -> 木化 -> 5S -> 生存税 -> 交配の一連のライフサイクル統合テスト"""
        conn = get_db_connection(TEST_DB)
        cursor = conn.cursor()

        # 1. Tree Agent（親A, 親B）の登録
        agent_a_id = str(uuid.uuid4())
        agent_b_id = str(uuid.uuid4())
        palette_a = json.dumps(["#00ff00"] * 16)
        palette_b = json.dumps(["#ff0000"] * 16)

        cursor.execute("""
        INSERT INTO tree_agents (id, name, level, clade, smile_wallet, precision_val, velocity_val, efficiency_val, harmony_val, resilience_val, avatar_url, genetic_palette)
        VALUES (?, 'maple', 4, 'HARDWOOD', 600, 80, 80, 80, 80, 80, 'avatar_a', ?)
        """, (agent_a_id, palette_a))
        cursor.execute("""
        INSERT INTO tree_agents (id, name, level, clade, smile_wallet, precision_val, velocity_val, efficiency_val, harmony_val, resilience_val, avatar_url, genetic_palette)
        VALUES (?, 'walnut', 2, 'HARDWOOD', 500, 70, 70, 70, 70, 70, 'avatar_b', ?)
        """, (agent_b_id, palette_b))
        conn.commit()

        # 2. クエストチケット投下
        ticket_id = "FG-Q100"
        project_id = "PRJ-E2E"
        cursor.execute("""
        INSERT INTO quests (ticket_id, project_id, title, status, assigned_agent_id, smile_reward_base, test_commands, tags)
        VALUES (?, ?, '幾何公差計算関数の実装', 'OPEN', NULL, 300, '["python3 test.py"]', '["CAD", "Python"]')
        """, (ticket_id, project_id))
        conn.commit()

        # 3. エージェントがチケットをPull (CASロック)
        cursor.execute("""
        UPDATE quests 
        SET status = 'IN_PROGRESS', assigned_agent_id = ?
        WHERE ticket_id = 'FG-Q100' AND status = 'OPEN' AND assigned_agent_id IS NULL
        """, (agent_a_id,))
        conn.commit()

        # Gitブランチ切り替え
        self.git_ops.create_work_branch(project_id, ticket_id)

        # 4. 成果物実装と提出（REVIEW移行）
        deliverable_name = "geo_calc.py"
        deliverable_path = os.path.join(TEST_REPO_DIR, deliverable_name)
        with open(deliverable_path, "w") as f:
            f.write("print('optimized geometry calculation')")

        self.git_ops.commit_deliverable(deliverable_name, "maple", 85, "Optimized geometry math")
        self.git_ops.merge_work_branch(project_id, ticket_id, "maple")

        cursor.execute("UPDATE quests SET status = 'REVIEW', deliverable_path = ? WHERE ticket_id = ?", (deliverable_path, ticket_id))
        conn.commit()

        # 5. テスト合格 + ユーザー星5評価に伴う「木化（Lignification / chmod 444）」
        consecutive_passes = 3
        user_rating = 5
        self.assertTrue(Lignifier.check_lignification_eligibility(consecutive_passes, user_rating))
        Lignifier.lignify(deliverable_path)
        self.assertFalse(os.access(deliverable_path, os.W_OK)) # 読み取り専用化の検証

        # 6. 生存税徴収と枯死処理の監視 (Tax collection)
        # 10 smile 徴収
        withered = self.metabolism.collect_survival_tax(tax_amount=10)
        self.assertEqual(len(withered), 0) # どちらも残高が十分なので生き残る

        # 残高減少の検証
        cursor.execute("SELECT name, smile_wallet FROM tree_agents WHERE id = ?", (agent_a_id,))
        maple_wallet = cursor.fetchone()["smile_wallet"]
        self.assertEqual(maple_wallet, 590)

        # 7. 交配（Crossover）による次世代エージェントの作成
        # 親のレコードを取得
        cursor.execute("SELECT * FROM tree_agents WHERE id = ?", (agent_a_id,))
        parent_a = dict(cursor.fetchone())
        cursor.execute("SELECT * FROM tree_agents WHERE id = ?", (agent_b_id,))
        parent_b = dict(cursor.fetchone())

        child_params, mutation, mutated = CrossoverEngine.calculate_child_parameters(parent_a, parent_b)
        child_palette = CrossoverEngine.blend_palettes(
            json.loads(parent_a["genetic_palette"]),
            json.loads(parent_b["genetic_palette"])
        )
        
        child_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO tree_agents (id, name, level, clade, smile_wallet, precision_val, velocity_val, efficiency_val, harmony_val, resilience_val, avatar_url, genetic_palette)
        VALUES (?, 'ash', 1, 'HARDWOOD', 500, ?, ?, ?, ?, ?, 'avatar_child', ?)
        """, (
            child_id, 
            child_params["precision_val"], 
            child_params["velocity_val"], 
            child_params["efficiency_val"], 
            child_params["harmony_val"], 
            child_params["resilience_val"], 
            json.dumps(child_palette)
        ))
        
        # 家系図（genealogy）の記録
        genealogy_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO genealogy (id, child_id, parent_a_id, parent_b_id, generation, blend_ratio)
        VALUES (?, ?, ?, ?, 2, 0.5)
        """, (genealogy_id, child_id, agent_a_id, agent_b_id))
        conn.commit()

        # 家系図がDBに正しくマッピングされたか検証
        cursor.execute("SELECT * FROM genealogy WHERE child_id = ?", (child_id,))
        gen_record = cursor.fetchone()
        self.assertEqual(gen_record["parent_a_id"], agent_a_id)
        self.assertEqual(gen_record["parent_b_id"], agent_b_id)

        conn.close()

if __name__ == "__main__":
    unittest.main()
