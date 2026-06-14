import os
import unittest
import shutil
import time
import subprocess
import sys
from physiology import Pruner, Lignifier, ResilientCaller

class TestPhysiology(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../projects/TEST-PRJ-PHY"))
        self.temp_dir = os.path.join(self.test_dir, "temporary")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.pruner = Pruner()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            for root, dirs, files in os.walk(self.test_dir):
                for f in files:
                    try:
                        os.chmod(os.path.join(root, f), 0o777)
                    except Exception:
                        pass
            shutil.rmtree(self.test_dir)

    def test_lignifier(self):
        """Lignification (木化) 処理および適性条件判定の検証"""
        # 条件チェックのテスト
        self.assertTrue(Lignifier.check_lignification_eligibility(3, 5))
        self.assertFalse(Lignifier.check_lignification_eligibility(2, 5))
        self.assertFalse(Lignifier.check_lignification_eligibility(3, 4))

        # ファイル不変属性 (chmod 444) 設定のテスト
        test_file = os.path.join(self.temp_dir, "to_lignify.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("immutable content")
        
        Lignifier.lignify(test_file)
        
        # 読み取り専用属性が付与されているかチェック (Windows/Linux共用)
        self.assertFalse(os.access(test_file, os.W_OK))

    def test_pruning_timeout(self):
        """プロセス実行タイムアウト時の自律剪定（Pruning / SIGKILL）の検証"""
        # 無限ループをシミュレートするpythonプロセスを起動
        process = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 1秒制限で監視実行
        result = self.pruner.monitor_and_prune(process, self.temp_dir, max_time_sec=1)
        
        self.assertEqual(result["status"], "pruned")
        self.assertEqual(result["reason"], "timeout")
        self.assertGreaterEqual(result["elapsed_sec"], 1.0)

    def test_pruning_size_overflow(self):
        """一時ディレクトリ容量オーバー時の自律剪定（Pruning / SIGKILL）の検証"""
        # ファイルを生成し続けるpythonプロセスを起動
        # projects/TEST-PRJ-PHY/temporary/ 配下にゴミファイルを書き出し続けます
        script_path = os.path.join(self.temp_dir, "spammer.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("""import time, os
for i in range(100):
    with open(f"workspace_junk_{i}.bin", "wb") as f_junk:
        f_junk.write(b"x" * (1024 * 1024)) # 1MBずつ書き込み
    time.sleep(0.1)
""")
            
        process = subprocess.Popen(
            [sys.executable, "spammer.py"],
            cwd=self.temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # ディレクトリ上限を 5MB に設定して監視 (通常1GBですがテスト用に小さく設定)
        result = self.pruner.monitor_and_prune(
            process, 
            self.temp_dir, 
            max_time_sec=10, 
            max_size_bytes=5 * 1024 * 1024
        )
        
        self.assertEqual(result["status"], "pruned")
        self.assertEqual(result["reason"], "size_overflow")
        self.assertTrue(os.path.exists(self.temp_dir))
        
        # 監視ディレクトリのサイズが 5MB 以上になっていることを検証
        dir_size = self.pruner.get_dir_size(self.temp_dir)
        self.assertGreater(dir_size, 5 * 1024 * 1024)

    def test_resilient_caller(self):
        """ジッター付き指数バックオフおよび早期撤退の動作検証"""
        call_count = 0
        
        def failing_api():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Mock Connection Timeout")
            
        # 3回のリトライ、最小ディレイ 0.1秒 で実行して例外スローを検証
        start_time = time.time()
        with self.assertRaises(TimeoutError):
            ResilientCaller.call_with_backoff(
                failing_api, 
                max_retries=3, 
                base_delay=0.1, 
                max_delay=0.5
            )
        elapsed = time.time() - start_time
        
        self.assertEqual(call_count, 3)
        # バックオフディレイが正しく発生しているか (0.1 + 0.2 + alpha秒 以上はかかるはず)
        self.assertGreater(elapsed, 0.3)

if __name__ == "__main__":
    unittest.main()
