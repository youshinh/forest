#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Forest-gram Step 1: 共通スキルおよび物理境界セキュリティ検証用ユニットテスト
TDD（テスト駆動開発）の原則に従い、read_file / write_file スキルの動作を検証します。
"""
import unittest
import os
import json
import shutil
import stat
from unittest.mock import patch

# 監査対象スキルのインポート（ラッパー関数を定義）
# テストの実行のため、execute.pyのメインロジックをモジュールとして利用できるようにします。
sys_path_bak = os.sys.path.copy()
os.sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from read_file.execute import read_target_file
from write_file.execute import write_target_file

class TestForestSkills(unittest.TestCase):
    
    def setUp(self):
        self.workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.test_dir = os.path.join(self.workspace, "projects", "TEST-PRJ-01")
        self.temp_dir = os.path.join(self.test_dir, "temporary")
        self.deliv_dir = os.path.join(self.test_dir, "deliverables")
        
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.deliv_dir, exist_ok=True)
        
    def tearDown(self):
        # テスト終了後のクレンジング（5S）
        if os.path.exists(self.test_dir):
            # 読み取り専用ファイルを削除できるように権限を戻す
            for root, dirs, files in os.walk(self.test_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.chmod(file_path, stat.S_IWRITE)
            shutil.rmtree(self.test_dir)

    def test_read_file_within_boundary(self):
        # 境界内のファイル読み込みテスト
        test_file = os.path.join(self.temp_dir, "dummy.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("test content")
            
        result = read_target_file(test_file)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "test content")

    def test_read_file_outside_boundary(self):
        # 境界外（Path Traversal）のブロックテスト
        outside_file = os.path.abspath(os.path.join(self.workspace, "..", "attacker.txt"))
        result = read_target_file(outside_file)
        self.assertEqual(result["status"], "error")
        self.assertIn("Security Violation", result["message"])

    def test_write_file_within_boundary(self):
        # 境界内のファイル書き込みテスト
        target_file = os.path.join(self.temp_dir, "write_test.txt")
        result = write_target_file(target_file, "hello output")
        
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(target_file))
        with open(target_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "hello output")

    def test_write_file_outside_boundary(self):
        # 境界外（Path Traversal）の書き込みブロックテスト
        outside_file = os.path.abspath(os.path.join(self.workspace, "..", "hacked.txt"))
        result = write_target_file(outside_file, "hack")
        self.assertEqual(result["status"], "error")
        self.assertIn("Security Violation", result["message"])

    def test_write_file_lignified_protection(self):
        # 木化された不変アセットへの書き込みブロックテスト
        lignified_file = os.path.join(self.deliv_dir, "lignified.py")
        
        # 1. 最初に正常書き込み
        write_target_file(lignified_file, "print('stable')")
        
        # 2. 木化（読み取り専用化）
        os.chmod(lignified_file, stat.S_IREAD) # chmod 444 相当
        
        # 3. 再書き込みのテスト
        result = write_target_file(lignified_file, "print('hacked')")
        self.assertEqual(result["status"], "error")
        self.assertIn("Lignification Constraint", result["message"])

if __name__ == "__main__":
    unittest.main()
