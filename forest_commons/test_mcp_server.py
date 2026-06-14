import unittest
import json
import os
import shutil
from mcp_server import ForestGramMcpServer

class TestMcpServer(unittest.TestCase):

    def setUp(self):
        self.server = ForestGramMcpServer()
        # テスト用ワークスペース構造の確保
        self.project_id = "TEST-PRJ-MCP"
        self.temp_dir = os.path.join(self.server.workspace_dir, "projects", self.project_id, "temporary")
        os.makedirs(self.temp_dir, exist_ok=True)

    def tearDown(self):
        proj_dir = os.path.join(self.server.workspace_dir, "projects", self.project_id)
        if os.path.exists(proj_dir):
            shutil.rmtree(proj_dir)

    def test_initialize(self):
        """initialize リクエストに対するレスポンス形式の検証"""
        req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }
        res_str = self.server.handle_request(json.dumps(req))
        res = json.loads(res_str)
        
        self.assertEqual(res["id"], 1)
        self.assertEqual(res["result"]["serverInfo"]["name"], "forest-gram-mcp-server")

    def test_list_tools(self):
        """tools/list リクエストに対するツール取得検証"""
        req = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 2
        }
        res_str = self.server.handle_request(json.dumps(req))
        res = json.loads(res_str)
        
        self.assertEqual(res["id"], 2)
        tools = res["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("read_file", tool_names)
        self.assertIn("write_file", tool_names)

    def test_call_tool_read_file(self):
        """tools/call リクエストによる実ファイルの読み出し検証"""
        # テスト用ファイルをtemporary内に作成
        test_file = os.path.join(self.temp_dir, "mcp_test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("MCP target text content")

        req = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "read_file",
                "arguments": {
                    "file_path": test_file
                }
            },
            "id": 3
        }
        res_str = self.server.handle_request(json.dumps(req))
        res = json.loads(res_str)
        
        self.assertEqual(res["id"], 3)
        self.assertFalse(res["result"]["isError"])
        
        content = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(content["status"], "success")
        self.assertEqual(content["content"], "MCP target text content")

    def test_call_tool_invalid_name(self):
        """存在しない、または不正なツール名の指定時のエラー処理検証"""
        req = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "../malicious_tool",
                "arguments": {}
            },
            "id": 4
        }
        res_str = self.server.handle_request(json.dumps(req))
        res = json.loads(res_str)
        
        self.assertTrue(res["result"]["isError"])
        self.assertIn("Invalid tool name", res["result"]["content"][0]["text"])

if __name__ == "__main__":
    unittest.main()
