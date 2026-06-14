import unittest
from unittest.mock import patch, MagicMock
import requests
from llm_client import LocalLLMClient

class TestLocalLLMClient(unittest.TestCase):

    def setUp(self):
        self.client = LocalLLMClient()

    @patch("requests.post")
    def test_generate_success(self, mock_post):
        """正常にレスポンスが返ってきた場合の挙動を検証"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_type = dict
        mock_response.json.return_value = {"response": "This is a mock answer in rhyme."}
        mock_post.return_value = mock_response

        result = self.client.generate("What is your favorite color?", system_prompt="Answer in rhyme.")
        
        # 正しい引数でPOSTが送信されているか
        mock_post.assert_called_once_with(
            "http://localhost:1234/api/v1/chat",
            json={
                "model": "gemma-4-12b-obliterated",
                "system_prompt": "Answer in rhyme.",
                "input": "What is your favorite color?"
            },
            timeout=30.0
        )
        self.assertEqual(result, "This is a mock answer in rhyme.")

    @patch("requests.post")
    def test_generate_retries_and_failure(self, mock_post):
        """APIエラー時にリトライを行い、上限でRuntimeErrorを投げるか検証"""
        mock_post.side_effect = requests.exceptions.RequestException("API Down")

        with self.assertRaises(RuntimeError):
            # リトライを2回に制限して検証
            self.client.generate("test input", max_retries=2)
            
        # 2回試行したか検証 (初期呼び出し + リトライ1回)
        self.assertEqual(mock_post.call_count, 2)

if __name__ == "__main__":
    unittest.main()
