import os
import json
import requests
from physiology import ResilientCaller

class LocalLLMClient:
    """ローカルLLM API (LM Studio / Ollama 互換) に推論要求を送信します。
    
    12B規模のモデルは生成に時間がかかるため、タイムアウトは十分に長く設定しています。
    デフォルトモデル: gemma-4-12b-obliterated (LM Studio)
    """
    
    def __init__(self, api_url="http://localhost:1234/api/v1/chat", model="gemma-4-12b-obliterated"):
        self.api_url = api_url
        self.model = model

    def is_available(self, timeout=3.0) -> bool:
        """ローカルLLMが起動しているか素早く確認します（デフォルト3秒以内）。"""
        try:
            resp = requests.get("http://localhost:1234/v1/models", timeout=timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def _post_request(self, system_prompt, input_text):
        payload = {
            "model": self.model,
            "system_prompt": system_prompt or "You are a helpful assistant.",
            "input": input_text
        }
        # 12Bモデルの生成には時間がかかるため、タイムアウトは180秒に設定
        response = requests.post(self.api_url, json=payload, timeout=180.0)
        response.raise_for_status()
        
        # レスポンス形式をパースして結果のテキストを返す
        # LM Studio / Ollama / OpenAI互換API の各形式に対応
        try:
            data = response.json()
            if "response" in data:
                return data["response"]
            elif "content" in data:
                return data["content"]
            elif "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice:
                    return choice["message"].get("content", "")
                return choice.get("text", "")
            return json.dumps(data)
        except (ValueError, KeyError, TypeError):
            return response.text

    def generate(self, input_text, system_prompt=None, max_retries=2):
        """推論を実行します。
        
        - timeout: 180秒（12Bモデル向け）
        - max_retries: デフォルト2回（通信エラー時のみリトライ）
        - ローカルLLMが完全に落ちている場合は呼び出し元でGeminiにフォールバック
        """
        try:
            return ResilientCaller.call_with_backoff(
                self._post_request,
                system_prompt,
                input_text,
                max_retries=max_retries,
                base_delay=2.0,
                max_delay=10.0
            )
        except Exception as e:
            raise RuntimeError(f"Local LLM Generation failed: {str(e)}")

if __name__ == "__main__":
    client = LocalLLMClient()
    available = client.is_available()
    print(f"[*] Local LLM Client initialized. Available: {available}")
    print(f"[*] Model: {client.model}")
    print(f"[*] API URL: {client.api_url}")
