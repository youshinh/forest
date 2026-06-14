import os
import re
import json
import sqlite3
from db import get_db_connection, init_db

def seed_skills_from_matrix(db_path="forest_guild.db", matrix_path=None):
    if matrix_path is None:
        matrix_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs/AIエージェント完全能力マトリクス.md"))
        
    if not os.path.exists(matrix_path):
        raise FileNotFoundError(f"Matrix document not found: {matrix_path}")

    # Ensure DB is initialized
    init_db(db_path)

    # 100項目のパース用の正規表現
    # 例: * **01. 要求解釈・意図抽出 (Intent Extraction):** ユーザーの雑多な言葉...
    pattern = re.compile(r"^\*\s*\*\*(\d+)\\?\.\s*([^(]+?)\s*\(([^)]+)\):\*\*\s*(.*)$")

    skills_seeded = []
    with open(matrix_path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                num = match.group(1)
                name_jp = match.group(2).strip()
                name_en = match.group(3).strip()
                desc = match.group(4).strip()
                
                skill_id = f"skill-{num}"
                skills_seeded.append({
                    "id": skill_id,
                    "name": f"{name_jp} ({name_en})",
                    "description": desc,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string", "description": desc}
                        },
                        "required": ["input"]
                    }
                })

    # DBへの書き込み
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # 既存のスキルデータを一度クレンジング
    cursor.execute("DELETE FROM skills")
    
    for s in skills_seeded:
        cursor.execute("""
        INSERT INTO skills (id, name, description, schema_json)
        VALUES (?, ?, ?, ?)
        """, (s["id"], s["name"], s["description"], json.dumps(s["schema"], ensure_ascii=False)))
        
    conn.commit()
    conn.close()
    
    print(f"[+] Successfully seeded {len(skills_seeded)} skills into database.")
    return len(skills_seeded)

if __name__ == "__main__":
    seed_skills_from_matrix()
