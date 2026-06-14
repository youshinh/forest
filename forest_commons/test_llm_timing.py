"""ローカルLLM 応答時間テストスクリプト"""
import sys
import time
sys.path.insert(0, 'forest_commons')
from llm_client import LocalLLMClient

client = LocalLLMClient()

print("=== Local LLM Response Time Test ===")
print(f"Model  : {client.model}")
print(f"API URL: {client.api_url}")
print(f"Timeout: 180s")
print()

# Step 1: 起動確認（3秒以内）
t0 = time.time()
available = client.is_available()
t1 = time.time()
status = "UP" if available else "DOWN"
print(f"[Step 1] Health check ({t1-t0:.2f}s): {status}")

if not available:
    print("[-] Local LLM is not running. Please start LM Studio and load a model.")
    sys.exit(1)

# Step 2: 短いプロンプトで応答時間計測
print()
print("[Step 2] Inference test (short prompt)...")
prompt = "日本語で「こんにちは、私は元気です」と言ってください。一文だけ答えてください。"
system_prompt = "You are a helpful assistant. Respond only in Japanese. Be very brief."

start = time.time()
try:
    result = client.generate(prompt, system_prompt=system_prompt, max_retries=1)
    elapsed = time.time() - start
    print(f"[OK] Response received in {elapsed:.1f}s (timeout: 180s)")
    print()
    print("--- Response preview ---")
    print(result[:400])
    print("------------------------")
    
    if elapsed < 180:
        print(f"\n[PASS] 180秒以内に応答あり ({elapsed:.1f}s)")
    else:
        print(f"\n[FAIL] 180秒を超過 ({elapsed:.1f}s)")

except Exception as e:
    elapsed = time.time() - start
    print(f"[FAIL] Error after {elapsed:.1f}s: {e}")
    sys.exit(1)
