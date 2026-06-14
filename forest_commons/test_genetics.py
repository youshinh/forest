import os
import unittest
import json
import shutil
import uuid
import zipfile
from db import init_db, get_db_connection
from genetics import CrossoverEngine, MetabolismManager, PiankaCalculator

TEST_DB = "test_genetics.db"
TEST_WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp_genetics_workspace"))

class TestGenetics(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_db(TEST_DB)

        if os.path.exists(TEST_WORKSPACE_DIR):
            shutil.rmtree(TEST_WORKSPACE_DIR)
        os.makedirs(TEST_WORKSPACE_DIR, exist_ok=True)
        
        self.metabolism = MetabolismManager(db_path=TEST_DB, workspace_dir=TEST_WORKSPACE_DIR)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        if os.path.exists(TEST_WORKSPACE_DIR):
            shutil.rmtree(TEST_WORKSPACE_DIR)

    def test_parameter_crossover(self):
        """交配時のパラメータ算出と突然変異発生ロジックの検証"""
        parent_a = {
            "level": 4,
            "precision_val": 80, "velocity_val": 70, "efficiency_val": 90, 
            "harmony_val": 60, "resilience_val": 80
        }
        parent_b = {
            "level": 2,
            "precision_val": 60, "velocity_val": 80, "efficiency_val": 70, 
            "harmony_val": 80, "resilience_val": 60
        }

        # 突然変異確率を1.0(必ず発生)にする
        child_params, mutation_occurred, mutated_params = CrossoverEngine.calculate_child_parameters(parent_a, parent_b, mutation_prob=1.0)
        self.assertTrue(mutation_occurred)
        self.assertEqual(len(mutated_params), 5)
        
        # パラメータが 1 ~ 100 の範囲に収まっているか検証
        for val in child_params.values():
            self.assertTrue(1 <= val <= 100)

    def test_blend_palettes(self):
        """パレットDNA融合（RGBブレンド）の検証"""
        palette_a = ["#ffffff"] * 16
        palette_b = ["#000000"] * 16

        child_palette = CrossoverEngine.blend_palettes(palette_a, palette_b)
        self.assertEqual(len(child_palette), 16)
        for color in child_palette:
            self.assertTrue(color.startswith("#"))
            self.assertEqual(len(color), 7)

    def test_pianka_calculator(self):
        """Pianka重複指数の計算検証"""
        # 完全重複 (1.0)
        tags_a = ["Python", "CAD"]
        tags_b = ["Python", "CAD"]
        index = PiankaCalculator.calculate_pianka_index(tags_a, tags_b)
        self.assertAlmostEqual(index, 1.0)

        # 完全不一致 (0.0)
        tags_c = ["C++"]
        index = PiankaCalculator.calculate_pianka_index(tags_a, tags_c)
        self.assertAlmostEqual(index, 0.0)

        # 部分重複
        tags_d = ["Python"]
        index = PiankaCalculator.calculate_pianka_index(tags_a, tags_d)
        # 共有タグ1つ、分母は sqrt((1/2 + 1/2) * 1) = sqrt(1 * 1) = 1, 分子 = (0.5 * 1.0) = 0.5
        # ただしタグ出現割合ベクトル: p_a = [0.5, 0.5], p_d = [1.0, 0]
        # dot = 0.5 * 1.0 = 0.5. sum_a_sq = 0.25+0.25=0.5. sum_d_sq = 1.0
        # denom = sqrt(0.5 * 1.0) = 0.7071
        # index = 0.5 / 0.7071 = 0.7071
        self.assertAlmostEqual(index, 0.7071, places=4)

    def test_survival_tax_and_withering(self):
        """生存税の徴収と枯死（ZIPアーカイブ退避）の検証"""
        conn = get_db_connection(TEST_DB)
        cursor = conn.cursor()

        # エージェントA: 生き残る (smile=100)
        # エージェントB: 枯死する (smile=5)
        palette = json.dumps(["#ffffff"] * 16)
        cursor.execute("""
        INSERT INTO tree_agents (id, name, clade, smile_wallet, precision_val, velocity_val, efficiency_val, harmony_val, resilience_val, avatar_url, genetic_palette)
        VALUES (?, ?, ?, ?, 80, 80, 80, 80, 80, 'url', ?)
        """, (str(uuid.uuid4()), "surviving_tree", "HARDWOOD", 100, palette))
        cursor.execute("""
        INSERT INTO tree_agents (id, name, clade, smile_wallet, precision_val, velocity_val, efficiency_val, harmony_val, resilience_val, avatar_url, genetic_palette)
        VALUES (?, ?, ?, ?, 80, 80, 80, 80, 80, 'url', ?)
        """, (str(uuid.uuid4()), "withered_tree", "SOFTWOOD", 5, palette))
        conn.commit()

        # 枯死するエージェント用のダミー物理フォルダを作成
        agent_dir = os.path.join(TEST_WORKSPACE_DIR, ".forestgram", "agents", "withered_tree")
        os.makedirs(agent_dir, exist_ok=True)
        with open(os.path.join(agent_dir, "agent.md"), "w") as f:
            f.write("agent rules here")

        # 税金を10徴収
        withered = self.metabolism.collect_survival_tax(tax_amount=10)
        
        # withered_treeが枯死リストに含まれていることを検証
        self.assertEqual(len(withered), 1)
        self.assertEqual(withered[0]["name"], "withered_tree")

        # 物理フォルダが消えて、withering_graveyardにZIPが作成されているか検証
        self.assertFalse(os.path.exists(agent_dir))
        
        graveyard_zip = os.path.join(TEST_WORKSPACE_DIR, "withering_graveyard", "withered_tree_withered.zip")
        self.assertTrue(os.path.exists(graveyard_zip))
        
        # ZIPの中身が正しいか検証
        with zipfile.ZipFile(graveyard_zip, "r") as zipf:
            self.assertIn("agent.md", zipf.namelist())

        # 残高確認
        cursor.execute("SELECT name, smile_wallet FROM tree_agents")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "surviving_tree")
        self.assertEqual(rows[0]["smile_wallet"], 90)
        
        conn.close()

if __name__ == "__main__":
    unittest.main()
