#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Forest-gram Global Skill: write_file
セキュアにファイルを書き込むための物理実行スクリプト。
"""
import sys
import os
import json

def write_target_file(file_path, content):
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
    
    # 木化された不変アセット(deliverables配下のchmod 444等)に対する変更保護はOS/ファイルシステムで守られるが、
    # ツールレベルでもチェックを行う
    if "deliverables" in abs_path and os.path.exists(abs_path):
        # もし読み取り専用属性(chmod 444)ならエラーを吐く
        if not os.access(abs_path, os.W_OK):
            return {"status": "error", "message": "Lignification Constraint: Cannot modify a lignified immutable asset."}

    # 親ディレクトリの自動生成
    parent_dir = os.path.dirname(abs_path)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
        
    try:
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {
            "status": "success",
            "written_path": file_path
        }
    except Exception as e:
        return {"status": "error", "message": f"Write failed: {str(e)}"}

if __name__ == "__main__":
    try:
        input_args = json.loads(sys.argv[1])
        file_path = input_args.get("file_path")
        content = input_args.get("content")
        result = write_target_file(file_path, content)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Parser error: {str(e)}"}, ensure_ascii=False))
