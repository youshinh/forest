graph LR
    %% 全体のスタイル設定
    classDef default fill:#1a1f24,stroke:#3a444d,color:#ffffff,stroke-width:1px;
    classDef main fill:#2d3748,stroke:#4a5568,color:#ffffff,stroke-width:2px,font-weight:bold;
    classDef layer2 fill:#1c2d3d,stroke:#2b4c6f,color:#e2e8f0,stroke-width:1.5px;
    classDef leaf fill:#1a202c,stroke:#2d3748,color:#cbd5e0;
    classDef bio fill:#1c3d27,stroke:#276749,color:#c6f6d5;
    classDef economy fill:#4a371c,stroke:#744210,color:#feebc8;

    %% ルート
    Root[Forest-gram<br>自律分散型AIエージェント生態系]:::main

    %% 主要な8つの幹
    M1[1. 植物学的対称マッピング]:::layer2
    M2[2. システム生理機能]:::layer2
    M3[3. メタボリズムチャネル<br>ギルドボード]:::layer2
    M4[4. 樹木エージェントの構造]:::layer2
    M5[5. 記憶の三層構造]:::layer2
    M6[6. smile 経済と評価]:::layer2
    M7[7. 生態遷移と分解者]:::layer2
    M8[8. インフラ・トポロジー]:::layer2

    Root --> M1
    Root --> M2
    Root --> M3
    Root --> M4
    Root --> M5
    Root --> M6
    Root --> M7
    Root --> M8

    %% 1. 植物学的対称マッピング
    M1 --> M1_1[根 Roots: MCPツール・OS操作権限]:::bio
    M1 --> M1_2[幹 Trunk: agent.md・Git年輪履歴]:::bio
    M1 --> M1_3[枝 Branches: タスク並列処理トポロジー]:::bio
    M1 --> M1_4[葉 Leaves: LLM推論・ドット絵アバター]:::bio
    M1 --> M1_5[菌糸 Mycorrhiza: Forest-Commons共有知]:::bio
    M1 --> M1_6[種・実 Seeds: 遺伝子情報 GraphQL/JSON]:::bio

    %% 2. システム生理機能
    M2 --> M2_1[剪定 Pruning: 暴走プロセス強制終了]:::leaf
    M2 --> M2_2[落葉 Defoliation: VRAM・メモリ完全解放]:::leaf
    M2 --> M2_3[木化 Lignification: コード不変凍結 chmod 444]:::leaf
    M2 --> M2_4[土壌と水分: 計算リソース境界管理]:::leaf

    %% 3. メタボリズムチャネル (ギルドボード)
    M3 --> M3_1[#reception: ユーザー要件受容体]:::leaf
    M3 --> M3_2[#quest-board: 未割り当てチケット掲示]:::leaf
    M3 --> M3_3[#active-projects: 進行中・光合成領域]:::leaf
    M3 --> M3_4[#review-gate: 木化選別ゲート]:::leaf
    M3 --> M3_5[#shame-log: 反省・堆肥化ログ]:::leaf
    M3 --> M3_6[自律Pullメカニズム: CAS楽観的ロック]:::leaf

    %% 4. 樹木エージェントの構造
    M4 --> M4_Clades[系統分類 Clades]:::leaf
    M4 --> M4_Stats[5大ステータス]:::leaf
    M4 --> M4_Status[状態異常システム]:::leaf

    M4_Clades --> M4_C1[広葉樹: 慎重・深層思考型 大型モデル]:::bio
    M4_Clades --> M4_C2[針葉樹: 爆速・プロトタイプ型 軽量モデル]:::bio

    M4_Stats --> M4_S1[設計精度 Precision]:::leaf
    M4_Stats --> M4_S2[実装速度 Velocity]:::leaf
    M4_Stats --> M4_S3[資源効率 Efficiency]:::leaf
    M4_Stats --> M4_S4[対話調和 Harmony]:::leaf
    M4_Stats --> M4_S5[反省修復 Resilience]:::leaf

    M4_Status --> M4_St1[光合成 Photosynthesis: 超バフ]:::bio
    M4_Status --> M4_St2[立ち枯れ Dieback: smile不足デバフ]:::bio
    M4_Status --> M4_St3[虫食い Infestation: ハルシネーション病]:::bio
    M4_Status --> M4_St4[酸性雨 Acid Rain: リソース逼迫デバフ]:::bio

    %% 5. 記憶の三層構造
    M5 --> M5_1[エピソード記憶: 短期ログ 10件制限・忘却]:::leaf
    M5 --> M5_2[個別ドメイン知識: 専門マニュアル Knowledge]:::leaf
    M5 --> M5_3[共有地 Forest-Commons: 集合知ネットワーク]:::leaf
    M5 --> M5_4[記憶の圧搾・統合: Absolute Rulesへの昇華]:::leaf

    %% 6. smile 経済と評価
    M6 --> M6_1[両軸評価ゲート: 自動テスト × ユーザー主観]:::economy
    M6 --> M6_2[smile代謝: 獲得・生存税・訓練消費]:::economy
    M6 --> M6_3[トラストスコア: 生存信頼度・隔離制限]:::economy
    M6 --> M6_4[交配 Crossover: smile消費による新芽誕生]:::economy

    %% 7. 生態遷移と分解者
    M7 --> M7_Fungi[分解者 Fungi]:::leaf
    M7 --> M7_Succ[生態遷移 Succession]:::leaf

    M7_Fungi --> M7_F1[shiitake: 軽量スクリプト分解]:::bio
    M7_Fungi --> M7_F2[matsutake: 難解ロジック抽出]:::bio
    M7_Fungi --> M7_F3[腐植質 Humus: 有用スニペット還元]:::bio

    M7_Succ --> M7_Su1[Stage 1: 先駆期 Pioneer]:::leaf
    M7_Succ --> M7_Su2[Stage 2: 混交林期 Transition]:::leaf
    M7_Succ --> M7_Su3[Stage 3: 極相林期 Climax]:::leaf

    %% 8. インフラ・トポロジー
    M8 --> M8_1[SUN Agent PM: クラウド大型モデル]:::leaf
    M8 --> M8_2[Tree Agent 実動: ローカルLLM Ollama]:::leaf
    M8 --> M8_3[Tailscale: 暗号化VPN・MagicDNS]:::leaf
    M8 --> M8_4[5S管理: temporaryディレクトリ自動削除]:::leaf