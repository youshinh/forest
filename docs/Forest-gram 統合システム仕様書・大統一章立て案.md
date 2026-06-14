# **Forest-gram（フォレスト・グラム）大統一システム仕様書：章立て構成案**

## **〜 自律循環型エージェント森林生態系の第一原理設計図 〜**

本ドキュメントは、「Forest-gram」システムの構築に必要なすべての仕様、データモデル、状態遷移、物理制限、およびユーザー体験を完全網羅するための大統一仕様書の構成案（章立て）である。

## **第1章：総論（Ecosystem Philosophy & Core Principles）**

### **1.1 プロローグとシステム哲学**

- 「Forest-gram」の基本概念（自律分散型知能の多層群れ）
- ツールから「Participant（共同創造者）」へのパラダイムシフト
- 応用圏論（Backprop as Functor）に基づく合成的知能

### **1.2 設計の第一原理（First Principles）**

- 有用性（Total Utility \= 利便性 × 影響範囲）の最大化
- エゴの徹底的排除と現実フィードバック（強化学習）の同期
- 極限思考（Limit Thinking）によるリソース境界設定

## **第2章：植物学的対称マッピングと生理学（Botanical-Software Symmetry）**

### **2.1 部位別対称マッピング**

- **【根 (Roots)】**：MCP（Model Context Protocol）による物理デバイス・OS低レイヤー操作
- **【幹 (Trunk)】**：エージェントの基底プロンプト、基本骨格（agent.md）、Git履歴（年輪）
- **【枝 (Branches)】**：並行・並列処理トポロジー（タスクの自動分岐）
- **【葉 (Leaves)】**：LLM推論インスタンス、およびアバターを宿すフロントエンド描画
- **【菌糸 (Mycorrhiza)】**：個体間を結ぶ共通知識ネットワーク（Forest-Commons）
- **【種・実 (Seeds/Fruits)】**：交配時に引き継がれるスキル遺伝子配列

### **2.2 システム生理機能の厳密定義**

- **【剪定 (Pruning)】**：SUN Agentによる暴走・不要プロセスの自動終了（Kill）
- **【落葉 (Defoliation)】**：アイドル時のコンテキストメモリ（VRAM）完全解放
- **【木化 (Lignification)】**：テスト＆ユーザー評価をクリアした「不変モジュール（共通部品）」の凍結
- **【土壌と水分 (Soil & Water)】**：CPU/VRAM/ストレージ/通信帯域等の物理計算資源の限界値管理

## **第3章：インフラストラクチャ＆ネットワーク構成（Infrastructure & Topology）**

### **3.1 ハイブリッドホスティング構成**

- 自宅PC（高火力GPUホスト）とローカルLLM（Ollama / vLLM）の設定
- スマホ/外部マルチデバイスからのTailscale VPNによる安全な接続規格
- Tailscale HTTPS証明書（Let's Encrypt）とMagicDNSによるクローズドWebアプリ展開

### **3.2 階層的LLMトポロジー（クラウドとローカルの適材適所）**

- **SUN Agent（PM）**：Gemini 2.5 Pro (クラウド) による長文要件解釈と依存関係チケット分割
- **Tree Agent（専門職）**：Ollama Gemma 2 / Llama 3 (ローカル) によるアトミックなタスク処理
- モデルの上書き（オーバーライド）優先順位設定ルール

## **第4章：プル型ギルドボード＆カンバン方式（Ecosystem Metabolism）**

### **4.1 メタボリズムチャネル（ Board UI ）の定義**

- チャネル構造（\#reception, \#quest-board, \#active-projects, \#review-gate, \#shame-log）
- クエストチケットの標準データスキーマ（JSON）

### **4.2 自律Pull（取得）メカニズムのトランザクション設計**

- PMエージェントによるタスク分割とチケット公開（Publish）
- 専門 Tree Agent による監視（Subscribe/Polling）
- 排他制御（Lock & Claim）と競合回避処理
- 成果物提出およびレビューゲートへの状態遷移

## **第5章：樹木エージェントの構造（Tree Agent Anatomy）**

### **5.1 樹木プロファイルと命名規則**

- 系統（広葉樹 / 針葉樹）と実在する樹木の名称（maple, walnut等）のマッピング
- レベルアップの数理モデルと累積経験値（EXP）の計算

### **5.2 100の能力マトリクスに基づく5大ステータス**

1. **【設計精度 (Precision)】** / 2\. **【実装速度 (Velocity)】** / 3\. **【資源効率 (Efficiency)】** / 4\. **【対話調和 (Harmony)】** / 5\. **【反省修復 (Resilience)】**

### **5.3 状態異常（バフ・デバフ）システム**

- **超バフ【光合成 (Photosynthesis)】**、**永続パッシブ【年輪の記憶 (Annular Ring)】**
- **危険デバフ【立ち枯れ (Dieback)】**、**環境デバフ【酸性雨 (Acid Rain)】**、**病気デバフ【虫食い (Infestation)】**

## **第6章：記憶の三層構造とガベージコレクション（Memory Consolidation）**

### **6.1 エピソード記憶（Private Memory）**

- episodic_log.json の仕様、過去の失敗と教訓
- 限界件数（最大10件）と、自動「忘却・要約（コンテキストGC）」ルール

### **6.2 個別ドメイン知識（Private Knowledge）**

- knowledge/ ディレクトリ設計
- 特化型仕様書（例: 木工伸縮計算、CNC加工限界値等）のRAG/プロンプトローディング仕様

### **6.3 共有地としての「Forest-Commons」**

- success_patterns/ と fail_patterns/ への抽出・還元プロセス
- 夜間・待機時の「地下根を伝う相互自己学習」の実行ステップ

## **第7章：smile（☺）経済・評価システム（Dual-Axis Economy）**

### **7.1 両軸評価ゲート（Dual-Axis Gate）**

- 自動CI/CDユニットテスト（客観ゲート）のスコア判定
- ユーザーによる絵文字/★評価（主観ゲート）の重み付け

### **7.2 smile 代謝トランザクション**

- クエストクリア時の smile 獲得計算式
- 維持（生存税）、自己訓練、モデルアンロック、交配時における smile の動的消費
- トラストスコア（生存信頼度）の変動ペナルティ

## **第8章：交配・突然変異・家系図グラフ（Genetics & GraphQL Genealogy）**

### **8.1 遺伝的アルゴリズム（Crossover & Mutation）**

- 交配トリガー（環境ストレス / コマンド）
- パラメーターのクロスオーバー数理モデル
- 突然変異（Mutation）確率とパラメータゆらぎ
- 遺伝子としてのMarkdownルールブック自動融合（Merge）プロセス

### **8.2 GraphQL 家系図スキーマ**

- GraphQLを用いた「多次元親子関係」のグラフマッピング
- 先祖（Ancestors）および末裔（Descendants）への追跡プロトコル
- 遺伝的カラーパレットの引き継ぎ

## **第9章：分解者（Decomposer）と生態遷移（Fungi & Succession Engine）**

### **9.1 菌類エージェント（Decomposer）**

- 菌類エージェントの命名（shiitake, matsutake等）と起動トリガー
- 廃棄コード・失敗ログからの「有用スニペット（腐植土：Humus）」抽出アルゴリズム

### **9.2 生態遷移（Ecological Succession）**

- パイオニア種（willow等）とクライマックス種（keyaki等）の動的バトンタッチ
- プロジェクトステージ（荒れ地 ➔ 植林 ➔ 極相林）の自動識別と割り当てシフト

## **第10章：ニッチ分化（Niche Partitioning）と自動棲み分け**

### **10.1 資源競争の動的解決**

- ロック競合および類似タグ衝突の検知方法
- 特性の置換（Character Displacement）プロンプト
- 各 Tree Agent による自律的「専門サブタグ」自動再定義仕様

## **第11章：5Sファイルシステム＆スキル一元管理（File System & Global Skills）**

### **11.1 プロジェクトフォルダの5Sライフサイクル**

- projects/{project_id}/ の内部構造
- 完了承認（👍）時の temporary/ フォルダ自動物理削除（rm \-rf）

### **11.2 グローバルスキル（skills/）の定型設計**

- スキル（ツール）の分離
- schema.json（LLM読み込み用スキーマ）と execute.py（物理スクリプト）の設計テンプレート

## **第12章：熱狂を呼ぶギルドビジュアル（UX & Canvas Specifications）**

### **12.1 ギルドキャンバスの動的レンダリング**

- 透過されたタスクにエージェントたちが「群がる」物理アニメーション（Boids）
- 各種バフ・デバフ時の動的パーティクル・スプライトアニメーション

### **12.2 アバター生成＆8bit自動ピクセル変換パイプライン**

- gemini-3.1-flash-image に対する世界観一貫メタプロンプト
- 白背景透過 ➔ ダウンサンプリング ➔ 輪郭線検出 ➔ パレット制限のクライアント処理
- レベルアップ・ファンファーレ、金文字、お祭りモード等の演出仕様

## **第13章：開発フェーズと曳光弾ロードマップ（Tracer Bullet Milestone）**

### **13.1 Step-by-Step 実装マイルストーン**

- 最小構成（SUN, Board, maple, walnut, shiitake）の動作確認
- テスト駆動開発（TDD）による各章機能の段階的検証計画
