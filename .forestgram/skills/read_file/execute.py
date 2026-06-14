#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Forest-gram Global Skill: read_file
セキュアにファイルを読み取るための物理実行スクリプト。
"""
import sys
import os
import json

def read_target_file(file_path):
    # パスが forest-gram-workspace (forest) 内に収まっているかを厳格にチェック
    abs_path = os.path.abspath(file_path)
    # 物理的なワークスペースパス（本スクリプトのあるディレクトリの3つ上）を基準にする
    allowed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    
    # 物理境界チェック
    try:
        common = os.path.commonpath([allowed_dir, abs_path])
        if common != allowed_dir:
            return {"status": "error", "message": "Security Violation: Path traversal outside workspace detected."}
    except ValueError:
        return {"status": "error", "message": "Security Violation: Invalid path resolution."}
    
    if not os.path.exists(abs_path):
        return {"status": "error", "message": f"File not found: {file_path}"}
        
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "status": "success",
            "content": content
        }
    except Exception as e:
        return {"status": "error", "message": f"Read failed: {str(e)}"}

if __name__ == "__main__":
    try:
        # LLMから引数がJSON文字列として渡されるのを想定
        input_args = json.loads(sys.argv[1])
        file_path = input_args.get("file_path")
        result = read_target_file(file_path)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Parser error: {str(e)}"}, ensure_ascii=False))
