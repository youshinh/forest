import os
import sys
import time
import random
import shutil
import subprocess
import requests

class Pruner:
    """エージェントプロセスの実行時間および一時ファイルサイズの監視と強制終了（剪定）を行います。"""
    
    @staticmethod
    def get_dir_size(path):
        """指定されたディレクトリの合計サイズ（バイト）を計算します。"""
        total_size = 0
        if not os.path.exists(path):
            return 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    try:
                        total_size += os.path.getsize(fp)
                    except OSError:
                        pass
        return total_size

    def monitor_and_prune(self, process, temp_dir, max_time_sec=60, max_size_bytes=1024*1024*1024):
        """プロセス実行時間とディスク使用量をリアルタイム監視し、制限を超えたら強制終了します。"""
        start_time = time.time()
        
        while process.poll() is None:
            # 1. タイムアウト監視（剪定）
            elapsed = time.time() - start_time
            if elapsed > max_time_sec:
                print(f"[!] Pruning Triggered: Process exceeded execution time limit ({max_time_sec}s). Killing process...")
                process.kill()
                return {"status": "pruned", "reason": "timeout", "elapsed_sec": elapsed}

            # 2. 一時ファイルサイズ監視（剪定）
            current_size = self.get_dir_size(temp_dir)
            if current_size > max_size_bytes:
                print(f"[!] Pruning Triggered: Temporary directory size exceeded limit ({max_size_bytes} bytes). Killing process...")
                process.kill()
                return {"status": "pruned", "reason": "size_overflow", "current_size_bytes": current_size}

            time.sleep(0.1)

        return {"status": "completed", "returncode": process.returncode}

class Defoliator:
    """ローカルLLM（Ollama）に対してモデルをVRAMから完全アンロード（落葉）するコマンドを送信します。"""
    
    def __init__(self, ollama_url="http://127.0.0.1:11434"):
        self.ollama_url = ollama_url

    def unload_model(self, model_name):
        """Ollama APIを叩き、keep_aliveを0に指定してモデルをアンロードします。"""
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": model_name,
            "prompt": "",
            "keep_alive": 0
        }
        try:
            # 短いタイムアウトを設定して非同期にアンロードを要求
            requests.post(url, json=payload, timeout=2.0)
            print(f"[+] Defoliation: Request sent to unload model '{model_name}' from VRAM.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[-] Defoliation failed (Ollama unreachable): {str(e)}")
            return False

class Lignifier:
    """成果物を読み取り専用（chmod 444 / 不変属性）に物理変更（木化）します。"""
    
    @staticmethod
    def lignify(file_path):
        """ファイルを読み取り専用に設定します。"""
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Lignification Target not found: {file_path}")
        
        # 読み取り専用属性 (chmod 444) に設定
        os.chmod(abs_path, 0o444)
        print(f"[+] Lignification: Locked asset as read-only (chmod 444): {abs_path}")
        return True

    @staticmethod
    def check_lignification_eligibility(consecutive_passes, user_rating):
        """木化の適性条件（テスト3回連続合格 かつ ユーザー評価星5）を満たすか判定します。"""
        return consecutive_passes >= 3 and user_rating == 5

class ResilientCaller:
    """指数バックオフ（ジッター付き）を用いたレジリエンス呼び出しユーティリティ。"""
    
    @staticmethod
    def call_with_backoff(api_func, *args, max_retries=5, base_delay=1.0, max_delay=16.0, **kwargs):
        """API呼び出しをジッター付き指数バックオフでリトライ実行します。"""
        for n in range(1, max_retries + 1):
            try:
                return api_func(*args, **kwargs)
            except Exception as e:
                print(f"[Retry {n}/{max_retries}] Exception occurred: {str(e)}")
                if n == max_retries:
                    raise TimeoutError(f"Environmental Collapse: API call failed after {max_retries} retries.")
                
                # 指数バックオフ + ジッターの計算
                backoff_delay = min(max_delay, base_delay * (2 ** (n - 1)))
                jitter = random.uniform(0, 0.5 * backoff_delay)
                total_sleep = backoff_delay + jitter
                
                print(f"[*] Sleeping for {total_sleep:.2f}s before retry...")
                time.sleep(total_sleep)
