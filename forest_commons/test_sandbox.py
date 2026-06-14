import os
import unittest
import shutil
from sandbox import SandboxRunner

class TestSandboxRunner(unittest.TestCase):

    def setUp(self):
        self.runner = SandboxRunner()
        self.project_id = "TEST-PRJ-SANDBOX"
        self.temp_dir = os.path.join(self.runner.workspace_dir, "projects", self.project_id, "temporary")
        os.makedirs(self.temp_dir, exist_ok=True)

    def tearDown(self):
        proj_dir = os.path.join(self.runner.workspace_dir, "projects", self.project_id)
        if os.path.exists(proj_dir):
            shutil.rmtree(proj_dir)

    def test_path_traversal_detection(self):
        """不正なパス参照（パストラバーサル）が検知されブロックされるか検証"""
        with self.assertRaises(PermissionError):
            self.runner._validate_path(os.path.join(self.runner.workspace_dir, "..", "secret.txt"))

    def test_sandbox_run_success(self):
        """サンドボックス内で正常にPythonスクリプトが動作し、出力を回収できるか検証"""
        # Docker環境が使えるか確認
        try:
            self.runner.build_sandbox_image()
        except Exception as e:
            self.skipTest(f"Docker is not available or daemon is not running: {str(e)}")

        script_content = """
print("Hello from Docker Sandbox!")
"""
        script_name = "test_script.py"
        with open(os.path.join(self.temp_dir, script_name), "w", encoding="utf-8") as f:
            f.write(script_content)

        result = self.runner.run_in_sandbox(self.project_id, script_name)
        
        self.assertEqual(result['returncode'], 0)
        self.assertIn("Hello from Docker Sandbox!", result['stdout'])

    def test_sandbox_network_isolation(self):
        """サンドボックス内で外部ネットワークアクセス（urllibなど）がブロックされるか検証"""
        try:
            self.runner.build_sandbox_image()
        except Exception as e:
            self.skipTest(f"Docker is not available: {str(e)}")

        # 外部（google.com）への接続を試みるスクリプト
        script_content = """
import urllib.request
try:
    urllib.request.urlopen("https://www.google.com", timeout=2)
    print("CONNECTED")
except Exception as e:
    print(f"FAILED: {str(e)}")
"""
        script_name = "network_test.py"
        with open(os.path.join(self.temp_dir, script_name), "w", encoding="utf-8") as f:
            f.write(script_content)

        result = self.runner.run_in_sandbox(self.project_id, script_name)
        
        # ネットワーク接続が遮断され、例外が発生して "FAILED:" が出力されることを期待
        self.assertIn("FAILED", result['stdout'])
        self.assertNotIn("CONNECTED", result['stdout'])

if __name__ == "__main__":
    unittest.main()
