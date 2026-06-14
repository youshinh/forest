# **Forest-gram（フォレスト・グラム）ヌケモレ補完・極限技術定義仕様書**

## **〜 セキュリティサンドボックス、自律Git/CI-CD、エラーレジリエンス、およびAPI物理定義 〜**

## **第1章：セキュリティ＆サンドボックス境界定義（Security & Sandbox Boundaries）**

エージェントが任意コード実行（RCE: Remote Code Execution）の権限を持つシステムにおいて、プロンプトインジェクション（悪意ある外部要求の注入）によるホストPCの破壊、不正なシステムコマンドの実行、および重要データの漏洩を防ぐための物理的な実行・隔離境界を定義する。

### **1.1 ユーザー権限とアクセススコープの分離**

* **非特権実行ユーザー（fg-runner）の義務：**  
  * ホストOS（自宅PC）上でエージェントプロセス、およびMCPツールを実行するユーザーは、絶対的なシステム管理者権限（root / Administrator）を排除した非特権専用ユーザー fg-runner に固定する。  
  * fg-runner ユーザーは、sudo 権限を剥奪され、アクセスできるファイルパスは /home/fg-runner/forest-gram-workspace/ 領域のみに物理隔離（chown / chmod 制限）される。

### **1.2 Dockerサンドボックスによる実行分離（Runtime Isolation）**

エージェントが自律生成したコードをテストコンパイル、あるいはG-codeの物理バリデーションに流し込む（客観ゲート検証、第4章・第7章）際、ホストOS上で直接実行することは厳格に禁止する。

1. **テスト専用隔離コンテナ（Sandbox Container）：**  
   * 検証が走る瞬間、システムは以下のDockerコマンドを用いて、ネットワークアクセスが完全遮断（--network none）され、メモリとCPUコアが厳格に制限された超軽量な一時実行コンテナを起動する。  
   * **コンテナ起動コマンド（物理定義）：**  
     `docker run --rm \`  
       `--network none \`  
       `--memory="512m" \`  
       `--cpus="1.0" \`  
       `-v /home/fg-runner/forest-gram-workspace/projects/${project_id}/temporary:/workspace:ro \`  
       `-v /home/fg-runner/forest-gram-workspace/projects/${project_id}/deliverables:/output:rw \`  
       `forestgram-python-runner:latest \`  
       `python3 /workspace/test_script.py`

   * **マウント境界：** 作業中の temporary 領域は「読み取り専用（:ro）」でマウントし、成果物を保護する deliverables 領域のみを「書き込み許可（:rw）」に制限することで、テスト中に悪意ある自動生成スクリプトが元のコードを上書き・改ざんすることを構造的に防止する。

## **第2章：自律Git/CI-CD運用プロトコル（Autonomous Git & CI/CD Workflow）**

100を超える自律樹木エージェントが、同一のコードベース（ワークスペース）に対して、競合（コンフリクト）を発生させることなく、整然とGitでのコミット、プルリクエスト、テストを自律運用するためのブランチモデルおよび自動コマンドフローを定義する。

### **2.1 ブランチトポロジー（Branching Topology）**

* **main ブランチ：**  
  * ユーザーによって完全に承認（👍 / 木化 LIGNIFIED）された最終アセットのみが配置される読み取り専用ブランチ。エージェントが直接このブランチへコミット・プッシュすることはシステムレベルで完全に禁止される。  
* **project/{project\_id} ブランチ：**  
  * SUN Agent（PM）が新規要件（プロジェクト）をパースした瞬間に、main から自律的に分岐作成（チェックアウト）される、プロジェクト共有の開発・統括ブランチ。  
* **agent-work/{ticket\_id} ブランチ：**  
  * 専門 Tree Agent（例：maple）がクエストチケットをスなッチ（Pull）した瞬間に、project/{project\_id} から自律的に切られる極小の作業用プライベートブランチ。

### **2.2 自律 Git ライフサイクルコマンドフロー**

エージェントの処理フェーズ（第4章）の遷移と Git コマンドの物理動作を完全に自動マッピング・同期する。

#### **① チケットPull（status: IN\_PROGRESS 移行時）**

エージェントが排他ロック（CASロック）に成功した瞬間、環境デーモンがホストPC上で以下のシェルコマンドを自動でシームレスに順次実行する。  
`# 1. ターゲットプロジェクトのブランチに切り替え`  
`git checkout project/PRJ-2026-0614-01`  
`# 2. クエスト専用の一時作業ブランチを自律生成`  
`git checkout -b agent-work/FG-2026-Q1002`

#### **② 成果物提出（status: REVIEW 移行時）**

エージェントがコード記述を完了し、自動単体テスト（Dockerサンドボックス）をパスした瞬間、自律的にコミットログ（年輪の記憶）を生成して親ブランチへ自動マージを試みる。  
`# 1. 成果物の追加`  
`git add projects/PRJ-2026-0614-01/deliverables/stairs_dimension.dxf`  
`# 2. 年輪コミットメッセージの自動生成（エゴを排除した事実のみの記述規則）`  
`git commit -m "feat(maple): Lignified stairs_dimension.dxf - Precision: 82, resolved zero-division safety gap"`  
`# 3. 親ブランチへの自動チェックアウトと、コンフリクトを回避するマージ`  
`git checkout project/PRJ-2026-0614-01`  
`git merge --no-ff agent-work/FG-2026-Q1002 -m "merge(system): Integrated maple output for Q1002"`  
`# 4. 作業ブランチの自律落葉（削除による5S維持）`  
`git branch -d agent-work/FG-2026-Q1002`

## **第3章：エラー制御＆自己修復（Resilience）詳細アルゴリズム**

ローカルLLMへの接続タイムアウト、外部APIのレートリミット超過（酸性雨デバフ時）、コンパイルの度重なる失敗時において、システムが「美しくクラッシュ（早期撤退）」しつつ、無駄なリソース消費を避けるための\*\*「指数バックオフ（Exponential Backoff）付き自己修復アルゴリズム」\*\*を数理定義する。

### **3.1 指数バックオフ数理モデル**

エージェントがAPI接続または外部システム操作に失敗した際、直近の試行回数を n、基本待機時間を T\_{base} \= 1.0 秒、最大待機時間を T\_{max} \= 16.0 秒とするとき、次の試行までのリトライ待機時間 T\_{wait}(n) は、以下の\*\*「ジッター（揺らぎ）付き指数バックオフ数理モデル」\*\*に従って算出される。これにより、複数のエージェントが一斉に再起動をかけてホストサーバーを再圧迫する「アバランシェ（雪崩）現象」を物理的に回避する。

T\_{wait}(n) \= \\min\\left(T\_{max}, T\_{base} \\cdot 2^{n-1}\\right) \+ \\text{Jitter} \\text{Jitter} \\sim \\text{Uniform}(0, 0.5 \\cdot \\text{Base\\\_Delay})

### **3.2 自己修復レジリエンスコード（Pythonプロトコル定義）**

システムBackend、またはMCPサーバーにビルトインされ、エージェントの推論ループを安全に防衛する物理プログラムロジック。  
`import time`  
`import random`  
`import requests`

`def call_llm_with_resilience(api_url, payload, max_retries=5):`  
    `base_delay = 1.0`  
    `max_delay = 16.0`  
      
    `for n in range(1, max_retries + 1):`  
        `try:`  
            `# タイムアウトは極限思考に基づき厳格に制限（第1章・第2章の落葉・剪定と同期）`  
            `response = requests.post(api_url, json=payload, timeout=30.0)`  
              
            `if response.status_code == 200:`  
                `return response.json()`  
            `elif response.status_code == 429: # Rate Limit`  
                `print(f"[Warning] Rate limited. Initiating environmental stress (Acid Rain).")`  
              
        `except requests.exceptions.RequestException as e:`  
            `print(f"[Retry {n}/{max_retries}] Connection failed: {str(e)}")`  
              
        `if n == max_retries:`  
            `# 極限思考（早期撤退）：最大リトライ失敗時は、中途半端な回復を試みず、美しくクラッシュさせる`  
            `raise TimeoutError("Environmental Collapse: Host LLM Engine unreachable after 5 attempts.")`  
              
        `# 数理バックオフの算出`  
        `backoff_delay = min(max_delay, base_delay * (2 ** (n - 1)))`  
        `jitter = random.uniform(0, 0.5 * backoff_delay)`  
        `total_sleep = backoff_delay + jitter`  
          
        `time.sleep(total_sleep)`

## **第4章：物理APIインターフェース仕様（System API Schema）**

スマートフォン（Next.js Web App UI）、自宅PC（FastAPI GraphQL Backend）、ローカルLLMホスト（Ollama）を安全かつ高速に結ぶメッセージング形式を定義する。

### **4.1 GraphQL クエリ / ミューテーション（Next.js ↔ Backend）**

スマホのギルドキャンバスから、エージェントをタップして「水やり（smileの寄付）」を行った際の、物理ミューテーション仕様。

#### **① 水やり（smileエネルギー直接充填）ミューテーション**

`mutation InjectWaterToAgent($agentId: ID!, $smileAmount: Int!) {`  
  `injectWater(agentId: $agentId, smileAmount: $smileAmount) {`  
    `agent {`  
      `id`  
      `name`  
      `smileWallet`  
      `trustScore`  
      `# 現在のデバフ状況`  
      `activeTraits {`  
        `name`  
        `type`  
      `}`  
    `}`  
    `success`  
    `message`  
  `}`  
`}`

* **レスポンス JSON 例（スマホUI描画同期用）：**  
  `{`  
    `"data": {`  
      `"injectWater": {`  
        `"agent": {`  
          `"id": "maple_v3",`  
          `"name": "maple",`  
          `"smileWallet": 650,`  
          `"trustScore": 95,`  
          `"activeTraits": []`  
        `},`  
        `"success": true,`  
        `"message": "Water injected successfully. Dieback debuff cured for maple!"`  
      `}`  
    `}`  
  `}`

### **4.2 ローカル推論 API 仕様（Backend ↔ Ollama）**

自宅PCバックエンドから Ollama 推論サーバー（ポート11434）へ投げる、低遅延・高精度指定の物理JSONペイロード仕様。

#### **① POST リクエスト（http://100.x.y.z:11434/api/generate）**

`{`  
  `"model": "gemma2:9b-instruct-q8_0",`  
  `"prompt": "### System Info:\nRole: maple (Level 4, Precision: 82)\nRules: [G-code zero-division guard mandatory]\n\n### Task:\nGenerate an optimized coordinate set for maple-wood jointer DXF. Return clean DXF format only.",`  
  `"stream": false,`  
  `"options": {`  
    `"num_predict": 2048,`  
    `"temperature": 0.2,`  
    `"top_p": 0.9,`  
    ````"stop": ["###", "```"],````  
    `"num_ctx": 4096`  
  `}`  
`}`

* **極限パラメータ制限（オプション制御）：**  
  * temperature: 幾何公差計算などの狂いを防ぐため、0.2 以下の低温推論に固定し、確実性と再現性を最大化する。  
  * num\_ctx: メモリ効率（第2章の土壌と水分）を守るため、アトミックなタスクにおいてはコンテキストサイズを 4096 トークンに厳しくクランプ（上限設定）し、無駄なVRAM消費による落葉（フリーズ）を物理的に防ぐ。

本「極限技術定義仕様書」に明記されたセキュリティ境界、自律Gitフロー、バックオフ数理、およびAPIインターフェーススキーマにより、Forest-gramを稼働させるためのすべてのピースは完璧に結合し、いかなるヌケモレ・曖昧さも完全に一掃された。