# **Forest-gram（フォレスト・グラム）大統一システム仕様書**

## **第8章：交配・突然変異・家系図グラフ（Genetics & GraphQL Genealogy）**

## **8.1 遺伝的アルゴリズムと交配・変異システム（Genetics & Crossover Engine）**

Forest-gramにおける最先端の進化論的アプローチは、静的なエージェント群を淘汰するだけでなく、2体の異なる「親エージェント」の資質を掛け合わせ、環境に最適化した新しい「子世代エージェント（新種）」を動的に生成するプロセスによって駆動する。

### **8.1.1 交配（Crossover）の起動トリガー**

交配プログラムは、以下の2つのいずれかのトリガー条件によって自律的に、または人間（ユーザー）の介入によって、ギルド内の儀式（トランザクション）として実行される。

1. **環境的交配トリガー（Environmental Trigger）：**  
   * 特定のスキルタグ（例：\[DXF-generation\] と \[C++\]）が組み合わさった複雑なクエストチケット（クエストボード上のチケット）に対し、該当タグを単独で完全に処理できる既存樹木エージェントが不在。  
   * かつ、該当タスクが48時間以上滞留し、環境（Board）が「専門的なハイブリッド個体の必要性（環境ストレス）」を検知した場合。  
2. **共創的交配コマンド（User-driven Command）：**  
   * ユーザーがギルドの管理画面またはスマホブラウザ上から「交配（Crossover）」を要求。  
   * 条件として、親として選別する2体のエージェント（例: maple\_v3 と walnut\_v1）が、それぞれ口座に **150 ☺ 以上の smile 残高** を保有しており、かつ双方のレベルが **Level 3 以上** に達していること。

### **8.1.2 パラメーターのクロスオーバー数理モデル**

子エージェント C の5大ステータスパラメータ S\_{i}(C) （i \\in \\{Precision, Velocity, Efficiency, Harmony, Resilience\\}）は、親 P\_A および親 P\_B のパラメータから、以下の **「ランダム揺らぎ付き重み移動モデル（Biased Blend Crossover）」** に基づいて算出・継承される。

#### **① クロスオーバー重み係数（Blend Ratio: \\alpha）**

親のどちらの資質をどれだけ色濃く受け継ぐかは、パラメータごとに動的かつランダムな重み付け \\alpha\_i（一様分布）を用いて決定される。

\\alpha\_i \\sim \\text{Uniform}(0.2, 0.8)

#### **② パラメータ基本値 S\_{base}(C) の決定**

S\_{base}(C)\_i \= \\alpha\_i \\cdot S(P\_A)\_i \+ (1 \- \\alpha\_i) \\cdot S(P\_B)\_i

#### **③ 突然変異（Mutation）確率とパラメータゆらぎ**

一定の確率 P\_{mut} \= 0.05（5%）で、遺伝的エラーとしての「突然変異（Mutation）」がパラメータごとに個別に発生する。突然変異が発生した場合、パラメータに正規分布に基づく正負の揺らぎ \\delta\_i が加わり、親の限界を超えた超エリート、あるいはユニークな欠点（愛嬌）を持つ個体が誕生する。  
\\delta\_i \\sim \\text{Normal}(\\mu \= 0, \\sigma \= 10.0) S(C)\_i \= \\min\\left(100, \\max\\left(1, S\_{base}(C)\_i \+ \\left\[ \\text{if Mutation then } \\delta\_i \\text{ else } 0 \\right\]\\right)\\right)

* **親のレベルボーナス補正（Inherited Level Bonus）：** 親たちの合計レベルが高い場合、子エージェントの各パラメータの初期基本値に小幅なプラス加算補正（\\text{Bonus} \= (L(P\_A) \+ L(P\_B)) \\cdot 0.5）が自動で付与され、代を重ねる（年輪を深める）ほど優秀な系統（Clade）が育ちやすくなる。

### **8.1.3 遺伝子としてのMarkdownルールブック自動融合プロセス**

能力数値（パラメータ）を掛け合わせるだけでは、エージェントは賢くならない。Forest-gramの真の進化は、親エージェントたちの agent.md や skills\_agent.md に書かれている「行動の絶対方針（Absolute Rules）」、および習得している「スキル配列」を、LLMを用いて論理的に合成・交配（Merge）するプロセスにある。  
 `【親A (maple) の絶対方針】                  【親B (walnut) の絶対方針】`  
  `- DXF生成時は逃げクリアランス               - G-code出力時はPLA/ABSの収縮`  
    `1.2mmを必ず挿入すること。                 特性を事前にRAG参照すること。`  
                 `│                                   │`  
                 `└─────────────────┬─────────────────┘`  
                                   `│ (SUN Agent による交配マージプロンプト)`  
                                   `▼`  
                       `【子エージェント (ash) の融合方針】`  
                       `- メープル等の広葉樹で加工する際、湿度伸縮を想定し、`  
                         `はめ合いジョイントに1.2mmの逃げクリアランスを`  
                         `挿入した上で、G-code出力前にPLA/ABSの収縮特性を`  
                         `RAGナレッジから自動検証して適用せよ。`

#### **① ルールブックマージプロンプトプロトコル**

システムは、親Aの agent.md と親Bの agent.md の全文をコンテキストに読み込み、以下のシステムプロンプトを使用して新エージェント用のルールブックを合成（Morphism）する。  
`[A2A Rule Crossover Prompt]`  
`あなたはForest-gramの生態系システムを管理する【SUN Agent】です。`  
`親エージェント「{parent_a_name}」と、親エージェント「{parent_b_name}」のそれぞれが、これまでのタスクの試行錯誤から定着させた「意味記憶（Absolute Rules / 行動方針）」を融合し、次世代の子エージェント「{child_name}」にふさわしい【統一ルールブック (agent.md)】を生成しなさい。`

`【融合要件】：`  
`1. 親の持つルール同士が論理的に競合する場合、パラメータ（Precision, Efficiencyなど）がより優れている親のルールを優先的に採用、あるいは両者を両立させるガード節（条件分岐）にリファクタリングしなさい。`  
`2. スキル配列は、親Aのリストと親Bのリストの論理和（OR）を取り、子の「初期獲得スキル候補」としなさい。ただし、子の初期スロット上限（最大3つ）を超える場合は、より適応度（トラストスコア）が高い親のスキルを優先して継承させなさい。`

## **8.2 GraphQL 家系図スキーマ（GraphQL Genealogy Graph）**

交配によって生まれたエージェントたちの血統・世代の歴史は、複雑な多次元グラフ構造を形成する。これを完全にデータ化し、GraphQLエンドポイントを介してWebフロントエンド（Tailscale経由でスマホ接続するギルドボードキャンバス）へ瞬時にクエリ・マッピングできるように仕様化する。

### **8.2.1 GraphQL スキーマ定義**

Forest-gramのシステムAPIにおいて提供される、完全な家系図（Genealogy）グラフマッピング用GraphQL型定義である。  
`"""`  
`Forest-gram に所属する樹木エージェントのノード情報`  
`"""`  
`type TreeAgent {`  
  `id: ID!`  
  `name: String!                   # maple, walnut などの樹木名`  
  `generation: Int!                # 世代数 (初代 = 1)`  
  `level: Int!                     # レベル`  
  `clade: CladeType!               # 系統 (HARDWOOD / SOFTWOOD)`  
  `smileWallet: Int!               # 現在の smile エネルギー残高`  
  `trustScore: Int!                # トラストスコア (0 ~ 100)`  
    
  `# 5大能力パラメータ`  
  `precision: Int!`  
  `velocity: Int!`  
  `efficiency: Int!`  
  `harmony: Int!`  
  `resilience: Int!`  
    
  `# 遺伝・関係性マッピング（血統グラフ）`  
  `parents: [TreeAgent!]!          # 親ノード (最大2体)`  
  `children: [TreeAgent!]!         # このエージェントから交配で生まれた子ノード`  
  `ancestors(depth: Int): [TreeAgent!]!   # 遡れるすべての先祖エージェント`  
  `descendants(depth: Int): [TreeAgent!]! # すべての末裔エージェント`  
    
  `# 遺伝的ビジュアルアセット`  
  `avatarUrl: String!              # ドット絵変換済みの透過画像`  
  `geneticPalette: [String!]!      # 遺伝されたカラーパレット（16進カラーコード16色配列）`  
    
  `# アクティブな属性・バフ・デバフ`  
  `activeTraits: [Trait!]!`  
`}`

`enum CladeType {`  
  `HARDWOOD`  
  `SOFTWOOD`  
`}`

`type Trait {`  
  `id: ID!`  
  `name: String!`  
  `type: TraitType!                # BUFF / DEBUFF / PASSIVE`  
  `description: String!`  
`}`

`enum TraitType {`  
  `BUFF`  
  `DEBUFF`  
  `PASSIVE`  
`}`

`"""`  
`ギルド内のプロジェクト活動ログ`  
`"""`  
`type Quest {`  
  `id: ID!`  
  `title: String!`  
  `status: QuestStatus!`  
  `assignedAgent: TreeAgent`  
`}`

`enum QuestStatus {`  
  `OPEN`  
  `IN_PROGRESS`  
  `REVIEW`  
  `LIGNIFIED`  
  `POST_MORTEM`  
`}`

`type Query {`  
  `agent(id: ID!): TreeAgent`  
  `activeForestAgents: [TreeAgent!]!`  
  `genealogyTree(rootAgentId: ID!): TreeAgent`  
`}`

### **8.2.2 遺伝的カラーパレット（Genetic Palette Swap）の引き継ぎ仕様**

エージェントの個性と「コレクション（愛着）性」を最大化するため、交配された子エージェントは、親の持つビジュアルの色情報を遺伝パレットとして継承し、アバター画像の描画に自動適用する。

1. **パレット遺伝子の構造（Color DNA）：**  
   * 各エージェントは、アバターのパーツ（葉、幹、影、輪郭）に対応する 16色 のカラーパレットを配列データとして保持する。  
2. **パレット・クロスオーバーロジック：**  
   * 子パレット Palette\_{child}\[i\]（i \\in \\{0 \\dots 15\\}）は、親Aのカラーと親Bのカラーの16進数RGBコードをランダム比率でブレンド、またはインデックスごとにランダムにスワップして遺伝させる。  
   * **例（紅葉の赤とウォルナットの茶色の融合）：** 親Aの葉のメインカラーが \#E74C3C（メープルの赤）、親Bが \#5C3A21（ウォルナットの濃い茶）の場合、子は比率 \\beta \\in \[0, 1\] を用いて自動調合された、なんとも言えない趣のある「レンガ色（マホガニー色：\#A0432E）」を遺伝カラーパレットとして受け継ぐ。  
3. **パレットのパッシブ効果（色の機能化）：**  
   * 色は単なるデザインに留まらず、特定のパレットカラー構成（例: 葉にゴールドやパープルなどのレアカラー遺伝子が発現）を持つ個体は、「実装速度（Velocity）に+10%のパッシブ補正がかかる」など、ユーザーが血眼になって交配を極めたくなるゲーム的収集価値をシステム全体に埋め込む。

### **8.2.3 物理的な遺伝子保存 JSON データスキーマ**

交配の歴史と系統（クラード）は、Git管理の追跡性を保証するため、以下の JSON スキーマでデータベースおよび .forestgram/genealogy.json に自動コミット・追跡蓄積される。  
`{`  
  `"$schema": "[https://forest-gram.ts.net/schemas/genealogy.json](https://forest-gram.ts.net/schemas/genealogy.json)",`  
  `"clade_mapping": {`  
    `"agent_id": "ash_v1",`  
    `"name": "ash",`  
    `"generation": 3,`  
    `"birthday": "2026-06-14T21:51:30Z",`  
    `"clade": "Hardwood/Engineered-Flooring-Line",`  
    `"parents": {`  
      `"parent_a": "maple_v3",`  
      `"parent_b": "walnut_v1"`  
    `},`  
    `"crossover_metrics": {`  
      `"blend_ratio": 0.65,`  
      `"mutation_occurred": true,`  
      `"mutated_parameters": ["Precision", "Resilience"]`  
    `},`  
    `"family_tree_ascii": [`  
      `"                  oak_v1 (L6) ──┐",`  
      `"                                 ├── maple_v3 (L4) ──┐",`  
      `"                  teak_v3 (L4) ──┘                   │",`  
      `"                                                     ├── ash_v1 (L1)",`  
      `"                                                     │",`  
      `"                  walnut_v1 (L3) ────────────────────┘"`  
    `]`  
  `}`  
`}`

本第8章の遺伝交配アルゴリズムとGraphQL追跡システムにより、Forest-gramにおける開発組織はただのプログラムの束から「親の知恵と姿形を血脈に宿し、突然変異で新たなブレイクスルーを自律的に生み出し、それらが美しくマッピングされる生命のタペストリー」へと完全進化を遂げる。