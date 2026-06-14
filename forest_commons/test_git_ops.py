import os
import unittest
import shutil
import subprocess
from git_ops import GitOperations

TEST_REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp_git_test"))

class TestGitOperations(unittest.TestCase):

    def setUp(self):
        # テスト開始前に既存のテスト用リポジトリディレクトリをクリーンアップして作成
        if os.path.exists(TEST_REPO_DIR):
            shutil.rmtree(TEST_REPO_DIR)
        os.makedirs(TEST_REPO_DIR, exist_ok=True)
        self.git_ops = GitOperations(TEST_REPO_DIR)

        # Gitのグローバル設定がない場合のエラーを防ぐため、テストローカル設定を施す
        try:
            subprocess.run(["git", "init"], cwd=TEST_REPO_DIR, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test Gardener"], cwd=TEST_REPO_DIR, check=True)
            subprocess.run(["git", "config", "user.email", "gardener@forestgram.local"], cwd=TEST_REPO_DIR, check=True)
            # mainブランチを作成
            with open(os.path.join(TEST_REPO_DIR, ".gitkeep"), "w") as f:
                f.write("")
            subprocess.run(["git", "add", ".gitkeep"], cwd=TEST_REPO_DIR, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=TEST_REPO_DIR, check=True)
            # デフォルトでmainブランチにしておく
            subprocess.run(["git", "branch", "-M", "main"], cwd=TEST_REPO_DIR, check=True)
        except subprocess.SubprocessError as e:
            self.skipTest(f"Git environment is not fully operational: {str(e)}")

    def tearDown(self):
        # 読み取り専用ファイルなどがあるとshutil.rmtreeで失敗することがあるので、パーミッションを戻しながら削除
        if os.path.exists(TEST_REPO_DIR):
            for root, dirs, files in os.walk(TEST_REPO_DIR):
                for file in files:
                    try:
                        os.chmod(os.path.join(root, file), 0o777)
                    except Exception:
                        pass
            shutil.rmtree(TEST_REPO_DIR)

    def test_checkout_project_branch(self):
        """プロジェクト用ブランチのチェックアウトおよび作成テスト"""
        self.git_ops.checkout_project_branch("PRJ-100")
        
        # 現在のブランチ名を取得して検証
        res = subprocess.run(["git", "branch", "--show-current"], cwd=TEST_REPO_DIR, capture_output=True, text=True)
        self.assertEqual(res.stdout.strip(), "project/PRJ-100")

    def test_git_lifecycle(self):
        """チケットPull -> 実装 -> コミット -> マージの一連のライフサイクルの検証"""
        project_id = "PRJ-999"
        ticket_id = "FG-Q777"
        agent_name = "maple"

        # 1. 作業ブランチの作成とチェックアウト
        self.git_ops.create_work_branch(project_id, ticket_id)
        res = subprocess.run(["git", "branch", "--show-current"], cwd=TEST_REPO_DIR, capture_output=True, text=True)
        self.assertEqual(res.stdout.strip(), f"agent-work/{ticket_id}")

        # 2. 成果物の擬似作成
        file_name = "test_deliverable.txt"
        file_path = os.path.join(TEST_REPO_DIR, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Test content")

        # 3. コミット実行
        self.git_ops.commit_deliverable(file_name, agent_name, 88, "Fix thickness clearance")
        
        # コミットログの検証
        log_res = subprocess.run(["git", "log", "-1", "--pretty=%B"], cwd=TEST_REPO_DIR, capture_output=True, text=True)
        self.assertIn("feat(maple): Lignified test_deliverable.txt", log_res.stdout)
        self.assertIn("Precision: 88", log_res.stdout)

        # 4. マージおよび作業ブランチの削除（落葉）
        self.git_ops.merge_work_branch(project_id, ticket_id, agent_name)

        # マージ後のブランチ検証
        current_branch = subprocess.run(["git", "branch", "--show-current"], cwd=TEST_REPO_DIR, capture_output=True, text=True)
        self.assertEqual(current_branch.stdout.strip(), f"project/{project_id}")

        # 作業ブランチが削除されたか検証
        all_branches = subprocess.run(["git", "branch"], cwd=TEST_REPO_DIR, capture_output=True, text=True)
        self.assertNotIn(f"agent-work/{ticket_id}", all_branches.stdout)

    def test_invalid_identifiers(self):
        """インジェクション攻撃用の無効な文字列を検出するか検証"""
        with self.assertRaises(ValueError):
            self.git_ops.checkout_project_branch("PRJ-100; rm -rf /")

        with self.assertRaises(ValueError):
            self.git_ops.create_work_branch("PRJ-100", "FG-1002 && echo 'hack'")

if __name__ == "__main__":
    unittest.main()
