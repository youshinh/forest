import unittest
import os
from unittest.mock import patch, MagicMock
from gemini_client import generate_text_with_gemini

class TestGeminiClient(unittest.TestCase):

    @patch("google.genai.Client")
    def test_generate_text_with_gemini_mock(self, mock_client_class):
        """Mockを用いたGeminiクライアントのテキスト生成テスト"""
        # クライアントおよびストリームレスポンスのモック設定
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_chunk_1 = MagicMock()
        mock_chunk_1.text = "Hello "
        mock_chunk_2 = MagicMock()
        mock_chunk_2.text = "World!"
        
        mock_client.models.generate_content_stream.return_value = [mock_chunk_1, mock_chunk_2]

        # 環境変数をモックするか、直接キーを渡してテスト
        result = generate_text_with_gemini("Say Hello World", api_key="test-api-key")
        
        self.assertEqual(result, "Hello World!")
        mock_client.models.generate_content_stream.assert_called_once()

    def test_missing_api_key_raises_error(self):
        """APIキーが指定されていない場合に例外を投げるか検証"""
        # 環境変数と引数を両方空にする
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                generate_text_with_gemini("Hello", api_key=None)

    def test_real_gemini_api_call_with_env(self):
        """保存された.envのキーをロードして実際のGemini API連携を実行するテスト"""
        # .envファイルをロード
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
        api_key = None
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        api_key = line.split("GEMINI_API_KEY=")[1].strip()
        
        if not api_key or "your_gemini" in api_key:
            self.skipTest("Real GEMINI_API_KEY is not set in .env")

        # 実際のキーを使って通信検証
        try:
            result = generate_text_with_gemini("Say 'TEST_SUCCESS'", api_key=api_key)
            print(f"\n[Real Gemini Output]: {result}")
            self.assertIn("TEST_SUCCESS", result)
        except Exception as e:
            self.fail(f"Real Gemini API call failed: {str(e)}")

if __name__ == "__main__":
    unittest.main()
