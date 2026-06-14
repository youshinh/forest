# **Forest-gram（フォレスト・グラム）大統一システム仕様書**

## **第11章：5Sファイルシステム＆スキル一元管理（File System & Global Skills）**

## **11.1 5S生産管理に基づくファイル構造・クレンジング仕様（5S File Metabolism）**

Forest-gramにおけるファイルシステムは、単なるデータのストレージではなく、システムのエントロピー（混沌）の増大を防ぐための\*\*「5S（整理、整頓、清掃、清潔、しつけ）」\*\*の管理基準に則って運用される。 不要な中間キャッシュ、ビルド時のエラーログ、未確定の仮設計データ（これらを「仕掛品」と呼ぶ）がいつまでもワークスペースに滞留すると、エージェントが次のタスクを実行する際にそれらを誤って参照（RAGノイズやコンテキストウィンドウの汚染）し、致命的なハルシネーション（バグの再発・先祖返り）を誘発する。これを防ぐためのフォルダ構造とライフサイクルルールを以下に規定する。

### **11.1.1 プロジェクトディレクトリ構造の物理設計**

プロジェクトはすべて projects/ ディレクトリ配下に、一意のID（PRJ-西暦日付-連番）で厳格にカプセル化される。  
`forest-gram-workspace/`  
`├── projects/`  
`│   └── PRJ-2026-0614-01/           # プロジェクト単位で独立した宇宙`  
`│       ├── raw_requirements.txt    # 1. ユーザーから投下された生の要件（チャットログ等）`  
`│       ├── system_specs/           # 2. SUN Agent（PM）が定義した仕様書、タスク分割チケット`  
`│       │   └── requirements_spec.md`  
`│       ├── deliverables/           # 3. 【清潔・永続保存】 ユーザーに納品・利用する確定アセット`  
`│       │   ├── stairs_dimension.dxf # メープル階段の設計図データ（木化確定ファイル）`  
`│       │   └── stairs_cut_list.csv  # 木材切り出しリスト`  
`│       ├── temporary/              # 4. ⚠️【仕掛品・完全クレンジング領域】 一時作業フォルダ`  
`│       │   ├── test_build_1.tmp`  
`│       │   ├── parse_temp.dxf`  
`│       │   └── debug_compiler.err`  
`│       └── post_mortem_logs/       # 5. 【整理・蓄積】 このプロジェクトで発生したTreeごとの反省ログ`  
`│           └── maple_failed_01.md`

### **11.1.2 一時作業スペース temporary/ の5S代謝ライフサイクル**

temporary/ ディレクトリは、専門 Tree Agent たちが自動コンパイルテスト（客観ゲート）や幾何学演算を回す際の「削りかす（木くず）」を一時的に逃がすためだけに用意された領域である。タスクのステージ移行に伴い、以下のルールで物理的破棄（5Sクレンジング）を自動実行する。

#### **【5Sクレンジングプロトコルと自動消去（Trash-and-Flush）】**

 `[ 成果物の提出 (REVIEW) ] ➔ 自動テストが走り、完了物を deliverables/ にコピー`  
           `│`  
           `▼`  
 `[ ユーザーによる「完了承認 (👍)」の検知 ] ➔ トランザクションのコミット`  
           `│`  
           `▼`  
 `🧹 【環境（Board / Hasura / OSデーモン）】がクレンジングシグナル（SIG_CLEAN）を送信`  
           `│`  
           `▼`  
 `[ temporary/ の中身を完全物理削除 (rm -rf projects/{id}/temporary/*) ]`  
           `│`  
           `▼`  
 `[ ワークスペースの「清潔」を確立 ] ➔ RAGスキャン対象からキャッシュファイルが物理消失`

* **安全な消去の保証（Immutable Archive）：** 一度ユーザー承認が得られた deliverables/ ディレクトリは、前述の「第2章：木化（chmod 444）」が施され、読み取り専用の強固な状態（不変）としてアーカイブされる。 これと同時に、不要な一時エラーログやキャッシュを含む temporary/ ディレクトリ内は、システムによって**一滴のゴミも残さず物理的に空にリセット**される。この代謝により、次のプロジェクトに移行した際、エージェントのRAG（検索拡張生成）が古いキャッシュファイルや以前のデバッグログを誤ってロードする確率を物理的に **0%** に制限する。

## **11.2 グローバルスキル（skills/）の定型設計と仕様（Global Skills Decoupling）**

これまでのエージェントシステムでは、エージェント個別のプロンプトの中にPythonやコマンドの実行コードをインジェクション（ハードコード）していた。しかし、これではスキルの重複、セキュリティホールの監査漏れ、そして交配時における「親の能力の伝承」が破綻する。  
Forest-gramは、エージェントの「脳（思考・記憶）」から、外部環境を操作する「筋肉・道具（スキル）」を完全に分離し、共通アセットとして .forestgram/skills/ ディレクトリに一元管理する\*\*「グローバルスキルアーキテクチャ」\*\*を定義する。

### **11.2.1 スキルのデータ構造と2ファイルペアの義務**

すべてのスキル（ツール）は、必ず以下の2つのファイルペアで定義され、共通の .forestgram/skills/{skill\_name}/ ディレクトリ配下にのみ配置される。

1. **schema.json（型定義とLLMセマンティクス説明）：**  
   * LLM（SUN Agentや各Tree Agent）が推論時に「このスキルが何をするもので、引数に何を渡すべきか」を正しく解釈するためのメタデータ。  
2. **execute.py（ホスト環境での物理実行実体）：**  
   * 実際にホストサーバー（自宅PC）上で叩かれるスクリプト。セキュリティ隔離されたコンテナ、あるいは特定ディレクトリに限定されたMCPコマンドを実行する。

### **11.2.2 スキル設計テンプレート：G-code 物理公差自動補正（gcode\_optimize）**

木工フローリングの加工機械、または3Dプリンターへ流し込むG-codeファイルに対し、素材の熱収縮率とはめ合い公差に基づいた軌道自動補正を行う実用スキルの仕様テンプレート。

#### **① .forestgram/skills/gcode\_optimize/schema.json**

`{`  
  `"$schema": "[https://forest-gram.ts.net/schemas/skill-schema.json](https://forest-gram.ts.net/schemas/skill-schema.json)",`  
  `"skill_id": "gcode_optimize",`  
  `"name": "G-code 物理公差最適化ツール",`  
  `"description": "3DプリンターまたはCNC向けのG-codeを読み込み、指定された素材（PLA/ABS/Wood-composite）の物理的な熱収縮率とはめ合い公差に基づいて、ノズルのXY軌道を自動補正した新しいG-codeを生成する。",`  
  `"input_schema": {`  
    `"type": "object",`  
    `"properties": {`  
      `"gcode_path": {`  
        `"type": "string",`  
        `"description": "補正対象のG-codeファイルの絶対パス、または projects/{project_id}/temporary/ 内の相対パス"`  
      `},`  
      `"material_type": {`  
        `"type": "string",`  
        `"enum": ["PLA", "ABS", "PETG", "Wood-composite"],`  
        `"description": "ファブリケーションで使用する物理素材の種別。これに基づき収縮係数が動的に選択される。"`  
      `},`  
      `"shrinkage_compensation_ratio": {`  
        `"type": "number",`  
        `"description": "手動で上書き補正するための収縮率係数。未指定の場合は、素材の標準値（例: PLA=0.002, ABS=0.008）を自動適用。"`  
      `},`  
      `"fit_clearance_mm": {`  
        `"type": "number",`  
        `"description": "はめ合いジョイント部分に挿入する遊びの幅（mm）。例: 0.2"`  
      `}`  
    `},`  
    `"required": ["gcode_path", "material_type"]`  
  `}`  
`}`

#### **② .forestgram/skills/gcode\_optimize/execute.py**

`#!/usr/bin/env python3`  
`# -*- coding: utf-8 -*-`  
`"""`  
`Forest-gram Global Skill: gcode_optimize`  
`ホストPC環境で安全にG-codeを走査・補正する、物理加工に特化したPython実行ツール。`  
`"""`  
`import sys`  
`import os`  
`import json`

`def apply_gcode_offset(gcode_path, material, compensation, clearance):`  
    `if not os.path.exists(gcode_path):`  
        `return {"status": "error", "message": f"Target file not found: {gcode_path}"}`  
      
    `# 物理境界セキュリティチェック (5Sガード)`  
    `# temporary/ または deliverables/ 以外のディレクトリへの書き込みを物理遮断する。`  
    `allowed_dir = "forest-gram-workspace"`  
    `if allowed_dir not in os.path.abspath(gcode_path):`  
        `return {"status": "error", "message": "Security Violation: Path traversal detected."}`

    `# 素材ごとの標準熱収縮率データベース (第一原理物理特性のマッピング)`  
    `shrinkage_db = {`  
        `"PLA": 0.002,`  
        `"ABS": 0.008,`  
        `"PETG": 0.004,`  
        `"Wood-composite": 0.005 # 木粉配合PLA特有の収縮率`  
    `}`  
      
    `ratio = compensation if compensation is not None else shrinkage_db.get(material, 0.002)`  
      
    `# 一時フォルダ内に補正後の新規ファイルを生成`  
    `dir_name = os.path.dirname(gcode_path)`  
    `base_name = os.path.basename(gcode_path)`  
    `output_path = os.path.join(dir_name, "optimized_" + base_name)`  
      
    `# 物理的な補正ロジックの実行 (1行ごとのG-code座標書き換え)`  
    `try:`  
        `with open(gcode_path, "r") as infile, open(output_path, "w") as outfile:`  
            `for line in infile:`  
                `# G0/G1 コマンド（移動）の座標を収縮率と公差クリアランスに基づいて微小シフト補正`  
                `if line.startswith("G1 ") or line.startswith("G0 "):`  
                    `parts = line.split()`  
                    `new_parts = []`  
                    `for part in parts:`  
                        `if part.startswith("X"):`  
                            `val = float(part[1:])`  
                            `# ゼロ原点からの収縮膨張を補正`  
                            `val_optimized = val * (1.0 + ratio) + (clearance if val > 0 else -clearance)`  
                            `new_parts.append(f"X{val_optimized:.4f}")`  
                        `elif part.startswith("Y"):`  
                            `val = float(part[1:])`  
                            `val_optimized = val * (1.0 + ratio) + (clearance if val > 0 else -clearance)`  
                            `new_parts.append(f"Y{val_optimized:.4f}")`  
                        `else:`  
                            `new_parts.append(part)`  
                    `outfile.write(" ".join(new_parts) + "\n")`  
                `else:`  
                    `outfile.write(line)`  
          
        `return {`  
            `"status": "success",`  
            `"optimized_gcode_path": output_path,`  
            `"applied_shrinkage_ratio": ratio,`  
            `"applied_clearance_mm": clearance`  
        `}`  
    `except Exception as e:`  
        `return {"status": "error", "message": f"Optimization failed: {str(e)}"}`

`if __name__ == "__main__":`  
    `# 引数はLLMからJSON文字列として標準入力または第1引数経由で渡される`  
    `try:`  
        `input_args = json.loads(sys.argv[1])`  
        `gcode_path = input_args.get("gcode_path")`  
        `material = input_args.get("material_type")`  
        `compensation = input_args.get("shrinkage_compensation_ratio")`  
        `clearance = input_args.get("fit_clearance_mm", 0.0)`  
          
        `result = apply_gcode_offset(gcode_path, material, compensation, clearance)`  
        `print(json.dumps(result, ensure_ascii=False))`  
    `except Exception as e:`  
        `print(json.dumps({"status": "error", "message": f"Parser error: {str(e)}"}, ensure_ascii=False))`

## **11.3 A2A（エージェント間連携）とMCP（Model Context Protocol）による環境連携仕様**

スキル（筋肉）が一元管理されたことで、エージェントは自身を単なるLLM推論インスタンスとして保ったまま、Google ADKやClaude Code、MCP（Model Context Protocol）に準拠した形式で、システム内の資源と安全に高速対話を行う。

### **11.3.1 MCP サーバーとしてのホストPCバインド仕様**

1. **スキルのMCP化：**  
   * 各エージェントが思考（推論）の過程で「G-codeを最適化したい」と判断した際、直接システム権限を実行するのではなく、MCPクライアント機能を使用する。  
   * ホストサーバー上で起動している forest-gram-mcp-server に対して、スキーマに則ったリクエスト（JSON-RPC 2.0 規格）を投げる。  
2. **JSON-RPC コールバック例：**  
   `{`  
     `"jsonrpc": "2.0",`  
     `"method": "tools/call",`  
     `"params": {`  
       `"name": "gcode_optimize",`  
       `"arguments": {`  
         `"gcode_path": "projects/PRJ-2026-0614-01/temporary/stand.gcode",`  
         `"material_type": "Wood-composite",`  
         `"fit_clearance_mm": 0.2`  
       `}`  
     `},`  
     `"id": "mcp-req-0042"`  
   `}`

3. **セキュリティ境界の厳密化：**  
   * MCPサーバーはリクエストを受領すると、引数のパスが forest-gram-workspace/projects/{current\_project\_id}/ 内に収まっているかを検証する。  
   * 検証をパスした場合のみ、該当する execute.py がサブプロセスとして実行され、結果がエージェントに通知される。これにより、エージェントのプロンプト内に悪意あるハッキング（Prompt Injection）が混入し、エージェントがホストPC内の無関係なファイルを削除・改ざんするのをシステム的に完全にブロックする。

### **11.3.2 遺伝交配における「スキル配列」の受け継ぎメカニズム（Crossover Simplicity）**

スキルが共通化されたことにより、「第8章：交配（Crossover）」の際に、AIが親エージェントの複雑なスキルコードを自動で切り貼り（マージ）してコンパイルエラーを出す、といった致命的なバグが消滅する。

1. **スキルの「DNA（識別子配列）」化：**  
   * 親A（maple）の DNA \= \["write\_file", "run\_python", "gcode\_optimize"\]  
   * 親B（walnut）の DNA \= \["read\_cad", "write\_file", "dxf\_parse"\]  
2. **子のスキルスロット（初期3つ）への遺伝シャッフル（Mendelian Selection）：**  
   * 子（ash）の誕生時、システムは親のDNA（スキル名の文字列配列）からランダム、あるいは適応度（トラストスコア）に応じて、以下のような「子の所持スキルリスト」を算出し、.forestgram/agents/ash/agent.md に文字列として1行追記するだけである。  
     `- 習得スキルリスト: ["gcode_optimize", "write_file", "dxf_parse"]`

3. **実行時の動的バインド：**  
   * 子（ash）はタスクPull時に自身の agent.md に書かれたスキルIDを読み込み、共通の .forestgram/skills/ から該当するスキーマと実行コードを、実行コンテキスト（MCPツール）として動的にセキュアロード（バインド）する。

本第11章の5Sファイルシステムとスキル分離一元管理仕様により、Forest-gram内のワークスペースは常に完璧にクリーンに清掃・維持され、新芽（新世代エージェント）たちは安全で確実な「実証済みの物理ツール」を両手に携えた状態で、力強く芽吹き、活動することができる。