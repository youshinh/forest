import os
import json
import requests
from physiology import ResilientCaller

class LocalLLMClient:
    """ユーザー指定のカスタムローカルLLM API (http://localhost:1234/api/v1/chat) に推論要求を送信します。"""
    
    def __init__(self, api_url="http://localhost:1234/api/v1/chat", model="gemma-4-12b-obliterated"):
        self.api_url = api_url
        self.model = model

    def _post_request(self, system_prompt, input_text):
        payload = {
            "model": self.model,
            "system_prompt": system_prompt or "You are a helpful assistant.",
            "input": input_text
        }
        response = requests.post(self.api_url, json=payload, timeout=30.0)
        response.raise_for_status()
        
        # レスポンス形式をパースして結果のテキストを返します
        # 標準的なチャットAPIレスポンス、またはプレーンテキストをハンドリング
        try:
            data = response.json()
            # 一般的な戻り値キー (response, content, text, choices等) を探索
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

    def generate(self, input_text, system_prompt=None, max_retries=5):
        """ジッター付き指数バックオフを備えたレジリエンス呼び出しで推論を実行します。"""
        try:
            return ResilientCaller.call_with_backoff(
                self._post_request,
                system_prompt,
                input_text,
                max_retries=max_retries,
                base_delay=1.0,
                max_delay=16.0
            )
        except Exception as e:
            raise RuntimeError(f"Local LLM Generation failed: {str(e)}")

if __name__ == "__main__":
    # 簡易接続テスト
    client = LocalLLMClient()
    print("[*] Local LLM Client initialized.")
