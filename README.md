# 🌳 Forest-gram — 自律循環型マルチエージェント生態系

Forest-gram は、自然界の森林生態系をメタファーとして設計された**自律型マルチエージェントシステム**です。  
AIエージェントたちが「樹木」「太陽」「菌類」として役割分担し、タスクを協調処理します。

---

## 🌿 システム概要

```
ユーザー要件 (光)
       ↓
  ☀️ SUN Agent (Gemini)        # 要件分解・クエスト発行
       ↓
  🌳 Tree Agent × N (Local LLM) # タスク並列実行・成果物生成
       ↓
  🍄 Fungi Agent               # 成果物分解・知識還元・クレンジング
       ↓
  📜 最終成果物 (木化 / chmod 444)
```

| エージェント | 役割 | 使用LLM |
|------------|------|--------|
| ☀️ **SUN Agent** | 要件分解・依存関係解決・クエスト発行 | Gemini Flash (クラウド) |
| 🌳 **Tree Agent** | 専門タスク実行・成果物生成 | ローカルLLM (LM Studio) |
| 🍄 **Fungi Agent** | 知識還元・5Sクレンジング | バックグラウンド |

---

## 🌲 植物学的メタファー

| 生物学的概念 | システム概念 |
|------------|------------|
| 根 (Roots) | MCP ツール / OS操作権限 |
| 幹 (Trunk) | `agent.md` + Gitコミット履歴（年輪） |
| 枝 (Branches) | 並列タスク処理トポロジー |
| 葉 (Leaves) | LLM推論コンテキスト + UIアバター |
| 菌糸 (Mycorrhiza) | エージェント間共有知識ネットワーク |
| 木化 (Lignification) | 成果物の不変化 (`chmod 444`) |

---

## 🚀 セットアップ

### 必要環境

- Python 3.10+
- Node.js 18+ (フロントエンド)
- [LM Studio](https://lmstudio.ai/) — ローカルLLM実行環境
- Gemini API Key

### インストール

```bash
git clone https://github.com/your-username/forest.git
cd forest

# Pythonパッケージ
pip install requests google-genai

# フロントエンド
cd frontend
npm install
npm run dev
```

### 環境変数設定

```bash
# .env ファイルを作成（リポジトリには含まれていません）
cp .env.example .env
# GEMINI_API_KEY=your_key_here を設定
```

### ローカルLLM設定

1. LM Studio を起動
2. `gemma-4-12b-obliterated` モデルをロード（または任意のモデル）
3. API サーバーを `http://localhost:1234` で起動

---

## 🧪 テスト実行

```bash
# マルチエージェント統合テスト
# タスク例: "明日から10年の間に資産を1000万増やす方法"
python forest_commons/run_multi_agent_test.py
```

### 実行フロー

```
Phase 1: SUN Agent (Gemini)
  → ユーザー要件を2つのサブタスク（クエスト）に分解
  → DBのギルドボード (quests テーブル) に登録

Phase 2: Tree Agent × 2 (Local LLM → Gemini Fallback)
  → FG-ASSET-01: maple_v3 — 数値シミュレーション & プラン構築
  → FG-ASSET-02: walnut_v1 — ポートフォリオ & 副業戦略策定
  ※ ローカルLLMが起動していれば優先使用（コスト削減）
  ※ 未起動の場合は Gemini API に自動フォールバック

Phase 3: Integration & Lignification
  → 2つの成果物を合成 → final_composite_roadmap.md
  → deliverables/ に木化 (chmod 444)
```

---

## 📁 ディレクトリ構造

```
forest/
├── agent.md                    # エージェント行動基準・システム定義書
├── forest_guild.db             # SQLite DB（ギルドボード / クエスト管理）※gitignore
├── forest_commons/             # 共有コードライブラリ（菌糸ネットワーク）
│   ├── run_multi_agent_test.py # 統合テストスクリプト
│   ├── llm_client.py           # ローカルLLMクライアント
│   ├── gemini_client.py        # Gemini APIクライアント
│   └── physiology.py           # ResilientCaller等の生理機能
├── frontend/                   # Vue.js フロントエンド（リアルタイム可視化）
│   ├── src/main.js
│   └── index.html
├── projects/                   # プロジェクト成果物
│   └── PRJ-ASSET/
│       ├── temporary/          # 仕掛品（gitignore）
│       └── deliverables/       # 木化済み成果物（gitignore）
├── docs/                       # ドキュメント
└── .forestgram/                # スキル定義 (schema.json + execute.py)
```

---

## 🎮 フロントエンド

```bash
cd frontend
npm run dev
# → http://localhost:3000 でリアルタイム可視化UI が起動
```

エージェントの群れ（Boids）が動き回る様子、クエストチケットの進行状況、最終成果物をブラウザで確認できます。

---

## ⚙️ 設定

### ローカルLLM タイムアウト設定 (`forest_commons/llm_client.py`)

```python
# 12Bモデルは生成に時間がかかるため 180秒 を推奨
timeout=180.0

# LM Studio で利用可能なモデルを確認
requests.get("http://localhost:1234/v1/models")
```

---

## 📜 ライセンス

MIT License

---

## 🌱 コントリビューション

Issues・PRs 歓迎です。Forest-gram の生態系を一緒に育てましょう！
