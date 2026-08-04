# AI Conversation Bridge

<p align="center"><sub>
  <a href="../../README.md">English</a> |
  <a href="../zh-Hans/README.md">简体中文</a> |
  <a href="../zh-Hant/README.md">繁體中文</a> |
  日本語 |
  <a href="../ko/README.md">한국어</a>
</sub></p>

---

AI駆動のオーケストレーションにより、企業向けメッセージングアプリ（LINE WORKS、WeChat（ウィーチャット）、Feishu（フィーシュー）など）をWorkdayに接続するリファレンスアーキテクチャです。ワーカーが日常的に使うアプリの中でAIを利用できることが求められる市場向けに設計されています。


https://github.com/user-attachments/assets/9b1ea495-5f23-4ae6-b735-18874acdd327



## なぜこれを作ったのか

企業AIが失敗する理由は、たいてい技術ではありません。届くべき人に届かないことです。

アジア太平洋および日本（APJ）地域（特に中国、日本、韓国）では、ワーカーにAIツールを実際に使ってもらううえで、次のような大きなハードルがあります。

- **規制上のハードル：** 中国のワーカーを米国ホストのAIやLLMにそのまま誘導することはできません。米中の政策環境が障壁となり、現地規制によってはローカルモデルが求められることもあります。
- **言語と文脈：** グローバルモデルは、企業固有の専門用語や現地の文化的なニュアンスを理解できないことがよくあります。「ゴールデンウィークに休みたい」という依頼を、AIが正しく理解できなければなりません。
- **スーパーアプリの優位：** 中国のワーカーはWeChatとFeishuを日常的に使っています。日本ではLINE、韓国ではKakaoTalk（カカオトーク）です。数百万人に別の企業アプリをダウンロードしてもらうよう求めるのは現実的ではありません。
- **Androidアプリの入手性：** Google Play ストアは中国でブロックされており、多くのワーカーが公式のWorkday Androidアプリすらダウンロードできません。

その結果どうなるか。企業はWorkdayを持ち、AIも使いたいのに、いちばん必要としているワーカーが取り残されてしまいます。

**AI Conversation Bridgeは、この構図をひっくり返します。** ワーカーにWorkdayへログインさせるのではなく、使い慣れたチャットアプリからWorkdayを利用できるようにします。ローカルLLMとローカルインフラを使うため、地域のルールとデジタル文化を尊重できます。ワーカーはWeChatでメッセージを送るだけで、あとはAIが処理します。Workdayは引き続き安全な信頼できる情報源であり続けますが、入り口はワーカーがすでにいる場所になります。

APJを念頭に設計しましたが、自前のLLMやチャットプラットフォームを使いたい場面であれば、どこでもこのパターンが通用します。



## アーキテクチャ

```text
チャットアプリ  ←→  チャットコネクター  ←→  Flowise（本ブリッジ）  ←→  MCPサーバー  ←→  Workday
```

プロジェクトは大きく3つの主要コンポーネントで構成されています。**Flowiseが脳です** —— LLMに接続し、ユーザーの意図を把握し、MCP経由でWorkdayツールを呼び出します。ほかの2つのコンポーネントは耳と手の役割です。チャットコネクターがチャットアプリからメッセージを受け取り、MCPサーバーがWorkdayで操作を実行します。

*（境界と想定用途の詳細は、[docs/architecture.md](docs/architecture.md)をご覧ください。）*


| コンポーネント | 役割 | 配置場所 |
| --- | --- | --- |
| **Flowiseフロー** | LLMオーケストレーション、意図認識、MCPツール呼び出しを担います。 | [flowise/](../../flowise/) |
| **チャットコネクター** | チャットプラットフォームからメッセージを受け取り、AIの応答を送り返す双方向アダプターです。 | [chat-connector/](../../chat-connector/) |
| **デモMCPサーバー** | テストと開発用のモックWorkdayツールです。（本番ではWorkday Agent Gatewayに差し替えてください。） | [mcp-demo-server/](../../mcp-demo-server/) |


## クイックスタート

### 必要なもの

- パブリックなHTTPSエンドポイントを提供するコンテナホスティングプラットフォーム（例：[Google Cloud Run](https://cloud.google.com/run)）
- [Flowise](https://flowiseai.com/)インスタンス（クラウドでもセルフホストでも可。パブリック向けであること）
- LINE WORKS Botの認証情報、および／またはDingTalk（ディントーク）ロボットへのアクセス（チャットコネクター用）

*注：すべてパブリック向けのクラウド環境にデプロイする必要があります。これらの例ではGoogle Cloud Runを使っていますが、任意のコンテナプラットフォームで動作します（AWS App Runner、Azure Container Apps、Alibaba Cloud Elastic Container Instance、Tencent Kubernetes Engineなど）。*

### 1. リポジトリをクローンする

```bash
git clone https://github.com/your-org/ai-conversation-bridge.git
cd ai-conversation-bridge
```

### 2. デモMCPサーバーをデプロイする

```bash
gcloud run deploy mcp-demo-server \
  --source mcp-demo-server
```

> **本番に進む場合は？** このデモサーバーを、Agent Gateway経由の**Workdayの公式MCPエンドポイント**に置き換え、本格的なエンタープライズグレードのセキュリティと認証を確保してください。Flowiseフロー内のMCP設定の更新も忘れずに！

### 3. Flowiseフローをインポートする

1. Flowiseインスタンスを開きます。
2. **Agent Flows** → **Add New** → **Settings**（⚙️）→ **Load Agentflow** の順に進みます。
3. `flowise/flows/workday-mcp-agent.json` をインポートします。
4. LLMの認証情報を設定します。
5. AgentノードのCustom MCPツールで、MCPサーバーURLをデプロイ済みのデモサーバー（例：`https://mcp-demo-server-abc123.us-west1.run.app/mcp`）に更新します。

*（さらにヘルプが必要ですか？[flowise/README.md](flowise/README.md)をご覧ください。）*

### 4. チャットコネクターをデプロイする

```bash
gcloud run deploy chat-connector \
  --source chat-connector
```

> **重要：** デプロイ後、Cloud Runコンソールで環境変数を設定することを忘れないでください！AIプロバイダー（`AI_PROVIDER`や`FLOWISE_API_URL`など）と、各チャットチャネルの設定が必要です。変数の一覧は`chat-connector/.env.example`を参照してください。

### 5. チャットチャネルを接続する

チャットプラットフォームのコールバックURLを、チャネル固有のエンドポイントに設定します。

- LINE WORKS：`https://chat-connector-abc123.us-west1.run.app/lineworks/callback`
- DingTalk HTTPロボット：`https://chat-connector-abc123.us-west1.run.app/dingtalk/callback`

レガシーの`/callback`パスは、既存デプロイ向けのLINE WORKSエイリアスとして引き続き受け付けられます。

## AIプロバイダー

チャットコネクターは、最初から二つのAIバックエンドをサポートしています。`CHAT_PROVIDER`はフォールバックとして引き続き受け付けられますが、新規デプロイでは`AI_PROVIDER`を使ってください。


| プロバイダー | 使う場面 | 設定 |
| --- | --- | --- |
| **Flowise**（デフォルト） | 本番 —— 完全なオーケストレーションとMCPツール呼び出しが得られます。 | `AI_PROVIDER=flowise` |
| **OpenRouter** | デモ／実験 —— Flowiseを用意せず、任意のLLMで素早く試せます。 | `AI_PROVIDER=openrouter` |


## デモMCPツール

デモMCPサーバーには、パイプライン全体をテストできるモックWorkdayツールとデータが付属しています。本番の準備ができたら、Workdayの公式MCPエンドポイントに差し替えるだけです。


| ツール | 役割 |
| --- | --- |
| `find_employee_id_by_name` | 氏名から従業員のワーカーIDを検索する |
| `get_current_user_info` | 現在のユーザーのプロフィールを取得する |
| `get_current_user_time_off_balance` | 現在のユーザーの休暇残日数を取得する |
| `get_current_user_time_off_history` | 現在のユーザーの休暇申請履歴を取得する |
| `get_time_off_balance` | ID指定で任意のワーカーの休暇残日数を取得する |
| `get_direct_reports` | マネージャーの直属の部下を一覧する |
| `get_more_employee_data` | 詳細な従業員データを取得する |
| `get_my_time_off_eligibility` | 現在のユーザーが申請できる休暇種別を確認する |
| `get_personal_information` | 個人情報（住所、緊急連絡先）を取得する |
| `get_today_date_and_day_of_week` | 現在の日付と曜日を取得する |
| `request_my_time_off` | 現在のユーザーの休暇申請を提出する |


*実は、モックデータには中国・日本・韓国のワーカーが含まれており、氏名も通貨もローカライズされています！*

## プロジェクト構造

```text
ai-conversation-bridge/
+-- chat-connector/          # Webhookアダプター（Flask、Python）
|   +-- app/services/        # メッセージングアダプター（LINE WORKS、DingTalk）+ AIクライアント
|   +-- Dockerfile
|   +-- .env.example
+-- flowise/                 # フローテンプレート（コアのブリッジロジック）
|   +-- flows/               # エクスポート可能なFlowiseフローJSONファイル
|   +-- screenshots/
+-- mcp-demo-server/         # デモ用Workday MCPサーバー
|   +-- mock_data/           # ワーカー、休暇、給与のサンプルデータ
|   +-- Dockerfile
|   +-- .env.example
+-- docs/                    # アーキテクチャとセットアップのドキュメント
+-- scripts/                 # ローカル開発セットアップ（setup.sh）とクラウドデプロイ（deploy-cloud-run.sh）
+-- docker-compose.yml       # コンテナのビルド／テスト用ユーティリティ
+-- .github/                 # Issueテンプレート、PRテンプレート
```

## ドキュメント

- [アーキテクチャ](docs/architecture.md) —— 詳細なシステム設計とリクエストフロー
- [セットアップガイド](docs/setup-guide.md) —— 各コンポーネントの手順付きセットアップ
- [エンタープライズ堅牢化ガイド](docs/enterprise-guide.md) —— 本番向けのセキュリティ、信頼性、運用に関する推奨事項
- [Flowise設定](flowise/README.md) —— フローテンプレートのインポートと設定方法
- [コントリビューション](CONTRIBUTING.md) —— 本プロジェクトへの貢献方法

## ライセンス

本プロジェクトはApache License 2.0の下でライセンスされています —— 詳細は[LICENSE](../../LICENSE)をご覧ください。
