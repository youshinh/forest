import sys
import os
import json
import subprocess

class ForestGramMcpServer:
    def __init__(self, workspace_dir=None):
        if workspace_dir is None:
            workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.skills_dir = os.path.join(self.workspace_dir, ".forestgram", "skills")

    def list_tools(self):
        """skillsディレクトリを走査し、利用可能なツール一覧を返します。"""
        tools = []
        if not os.path.exists(self.skills_dir):
            return tools

        for item in os.listdir(self.skills_dir):
            item_path = os.path.join(self.skills_dir, item)
            if os.path.isdir(item_path):
                schema_path = os.path.join(item_path, "schema.json")
                execute_path = os.path.join(item_path, "execute.py")
                if os.path.exists(schema_path) and os.path.exists(execute_path):
                    try:
                        with open(schema_path, "r", encoding="utf-8") as f:
                            schema = json.load(f)
                        tools.append({
                            "name": schema.get("skill_id", item),
                            "description": schema.get("description", ""),
                            "inputSchema": schema.get("input_schema", {"type": "object", "properties": {}})
                        })
                    except Exception as e:
                        sys.stderr.write(f"Error loading skill schema {item}: {str(e)}\n")
        return tools

    def call_tool(self, name, arguments):
        """指定されたツール(execute.py)を実行します。"""
        # パスの安全性検証
        if not name or not isinstance(name, str) or ".." in name or "/" in name or "\\" in name:
            return {"isError": True, "content": [{"type": "text", "text": "Invalid tool name format."}]}

        execute_path = os.path.join(self.skills_dir, name, "execute.py")
        if not os.path.exists(execute_path):
            return {"isError": True, "content": [{"type": "text", "text": f"Tool '{name}' not found."}]}

        # 引数のバリデーション (JSONインジェクション防御)
        try:
            arg_str = json.dumps(arguments)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": f"Invalid arguments object: {str(e)}"}]}

        # execute.pyのサブプロセス起動
        try:
            result = subprocess.run(
                [sys.executable, execute_path, arg_str],
                capture_output=True,
                text=True,
                check=False
            )
            # execute.pyの標準出力はJSONであることを想定
            try:
                output_data = json.loads(result.stdout)
                is_error = output_data.get("status") == "error"
                text_content = json.dumps(output_data, ensure_ascii=False)
            except json.JSONDecodeError:
                is_error = result.returncode != 0
                text_content = result.stdout or result.stderr or "No output from tool execution."

            return {
                "isError": is_error,
                "content": [{"type": "text", "text": text_content}]
            }
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": f"Execution failed: {str(e)}"}]}

    def handle_request(self, req_json):
        """JSON-RPC 2.0 リクエストをパースして処理します。"""
        try:
            req = json.loads(req_json)
        except json.JSONDecodeError:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None
            })

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            # 初期化リクエストへの応答
            response = {
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "forest-gram-mcp-server", "version": "1.0.0"}
                },
                "id": req_id
            }
        elif method == "tools/list":
            # ツール一覧取得リクエスト
            tools = self.list_tools()
            response = {
                "jsonrpc": "2.0",
                "result": {"tools": tools},
                "id": req_id
            }
        elif method == "tools/call":
            # ツール実行リクエスト
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            result = self.call_tool(tool_name, tool_args)
            response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": req_id
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method not found: {method}"},
                "id": req_id
            }

        return json.dumps(response, ensure_ascii=False)

    def run_stdio_loop(self):
        """標準入出力を用いたメインループ処理。"""
        sys.stderr.write("[*] forest-gram-mcp-server started.\n")
        sys.stderr.flush()
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                response_str = self.handle_request(line)
                sys.stdout.write(response_str + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stderr.write(f"Error in main loop: {str(e)}\n")
                sys.stderr.flush()

if __name__ == "__main__":
    server = ForestGramMcpServer()
    server.run_stdio_loop()
