# AI Conversation Bridge

<p align="center"><sub>
  <a href="../../README.md">English</a> |
  <a href="../zh-Hans/README.md">简体中文</a> |
  繁體中文 |
  <a href="../ja/README.md">日本語</a> |
  <a href="../ko/README.md">한국어</a>
</sub></p>

---

一套參考架構，透過由 AI 驅動的編排能力，將 LINE WORKS、WeChat（微信）、Feishu（飛書）等企業訊息應用連接到 Workday。它專為這樣的市場而設計：讓使用者在他們日常使用的應用中就能用上 AI。


https://github.com/user-attachments/assets/9b1ea495-5f23-4ae6-b735-18874acdd327



## 我們為什麼要做這件事

企業 AI 的失敗通常不是因為技術，而是因為它沒有觸達真正需要它的人。

在亞太及日本（APJ）地區，尤其是中國、日本和韓國，要讓使用者真正用起 AI 工具，會遇到幾個主要障礙：

- **法規障礙：** 您無法直接讓中國的員工使用美國託管的 AI 或 LLM。中美政策環境為此設置了障礙，而且當地法規有時要求使用本地模型。
- **語言與語境：** 全球通用模型往往讀不懂企業專有術語，也把握不住當地的文化細節。當員工說要請 Golden Week（黃金週）的假時，AI 必須真正聽懂這句話。
- **超級應用的主導地位：** 中國的使用者離不開 WeChat 和 Feishu，日本是 LINE，韓國是 KakaoTalk（韓國主流聊天應用）。要求數百萬人再去下載一個獨立的企業應用，根本行不通。
- **Android 應用可用性：** Google Play Store（Google 應用程式商店）在中國無法存取，這意味著很大一部分員工甚至下載不到 Workday 官方的 Android 應用。

結果呢？企業已經擁有 Workday，也想用上 AI，但最需要它的那些員工卻被排除在外。

**AI Conversation Bridge 把這件事反過來做。** 它不再要求使用者登入 Workday，而是把 Workday 直接帶進他們最常用的聊天應用。它使用本地 LLM 與本地基礎設施，因此既符合區域法規，也貼合當地的數位文化。使用者只需在 WeChat 裡發一則訊息，剩下的交給 AI。Workday 依然是安全的權威資料來源，但入口就在使用者已經身處的地方。

雖然我們是針對 APJ 地區設計的，但只要您希望使用自有的 LLM 或聊天平台，這套模式在任何市場都同樣適用。



## 架構

```text
聊天應用  ←→  聊天連接器  ←→  Flowise（橋接層）  ←→  MCP 伺服器  ←→  Workday
```

專案包含三大部分。**Flowise 是大腦** —— 它連接 LLM，判斷使用者想要什麼，並透過 MCP 呼叫 Workday 工具。另外兩個元件則充當它的耳朵和雙手：聊天連接器負責監聽來自聊天應用的訊息，MCP 伺服器負責在 Workday 中執行操作。

*（關於邊界與預期用法的更多細節，請參閱 [docs/architecture.md](docs/architecture.md)。）*


| 元件 | 作用 | 位置 |
| --- | --- | --- |
| **Flowise 流程** | 負責 LLM 編排、意圖識別與 MCP 工具呼叫。 | [flowise/](../../flowise/) |
| **聊天連接器** | 雙向適配器，接收來自聊天平台的訊息，並將 AI 的回應回傳。 | [chat-connector/](../../chat-connector/) |
| **演示 MCP 伺服器** | 用於測試與開發的模擬 Workday 工具。（生產環境請替換為 Workday Agent Gateway。） | [mcp-demo-server/](../../mcp-demo-server/) |


## 快速開始

### 前置條件

- 一個提供公網 HTTPS 端點的容器託管平台（例如 [Google Cloud Run](https://cloud.google.com/run)）
- 一個 [Flowise](https://flowiseai.com/) 執行個體（雲端或自行託管均可，只要對外公開）
- LINE WORKS 機器人憑證和／或 DingTalk（釘釘）機器人存取權限（供聊天連接器使用）

*說明：所有元件都需要部署到對外公開的雲端環境。以下範例使用 Google Cloud Run，但任何容器平台均可，例如 AWS App Runner、Azure Container Apps、Alibaba Cloud Elastic Container Instance（阿里雲彈性容器執行個體）、Tencent Kubernetes Engine（騰訊雲容器服務）等。*

### 1. 複製儲存庫

```bash
git clone https://github.com/your-org/ai-conversation-bridge.git
cd ai-conversation-bridge
```

### 2. 部署演示 MCP 伺服器

```bash
gcloud run deploy mcp-demo-server \
  --source mcp-demo-server
```

> **準備上生產環境？** 請透過 Agent Gateway 把這個演示伺服器替換為 **Workday 官方 MCP 端點**，以獲得真正的企業級安全與身分驗證能力。別忘了同步更新 Flowise 流程中的 MCP 組態！

### 3. 匯入 Flowise 流程

1. 開啟您的 Flowise 執行個體。
2. 依序進入 **Agent Flows** → **Add New** → **Settings**（⚙️）→ **Load Agentflow**。
3. 匯入 `flowise/flows/workday-mcp-agent.json`。
4. 設定您的 LLM 憑證。
5. 在 Agent 節點的 Custom MCP 工具中，把 MCP 伺服器 URL 更新為您已部署的演示伺服器位址（例如 `https://mcp-demo-server-abc123.us-west1.run.app/mcp`）。

*（需要更多協助？請參閱 [flowise/README.md](flowise/README.md)。）*

### 4. 部署聊天連接器

```bash
gcloud run deploy chat-connector \
  --source chat-connector
```

> **重要：** 部署完成後，別忘了在 Cloud Run 主控台中設定環境變數！您需要設定 `AI_PROVIDER`（選擇 AI 供應商）和 `FLOWISE_API_URL`（Flowise 端點 URL），以及各聊天渠道的相關設定。完整的變數清單請參閱 `chat-connector/.env.example`。

### 5. 接入聊天渠道

將聊天平台的回呼 URL 設定為對應渠道的端點：

- LINE WORKS：`https://chat-connector-abc123.us-west1.run.app/lineworks/callback`
- DingTalk HTTP 機器人：`https://chat-connector-abc123.us-west1.run.app/dingtalk/callback`

為相容既有部署，舊版 `/callback` 路徑仍作為 LINE WORKS 的別名予以保留。

## AI 供應商

聊天連接器開箱即支援兩種 AI 後端。`CHAT_PROVIDER` 仍作為後備選項保留，但新部署應使用 `AI_PROVIDER`。


| 供應商 | 適用場景 | 組態 |
| --- | --- | --- |
| **Flowise**（預設） | 生產環境 —— 提供完整的編排能力與 MCP 工具呼叫。 | `AI_PROVIDER=flowise` |
| **OpenRouter** | 演示與實驗 —— 無需搭建 Flowise，即可用任意 LLM 快速測試。 | `AI_PROVIDER=openrouter` |


## 演示 MCP 工具

演示 MCP 伺服器內建了模擬 Workday 工具與資料，方便您測試整條流程管線。當您準備進入生產環境時，只需將其替換為 Workday 官方 MCP 端點。


| 工具 | 作用 |
| --- | --- |
| `find_employee_id_by_name` | 按姓名查詢員工的工作者 ID |
| `get_current_user_info` | 取得目前使用者的個人檔案 |
| `get_current_user_time_off_balance` | 取得目前使用者的假期餘額 |
| `get_current_user_time_off_history` | 取得目前使用者的休假申請歷史 |
| `get_time_off_balance` | 按 ID 取得任意工作者的假期餘額 |
| `get_direct_reports` | 列出某位管理者的直接下屬 |
| `get_more_employee_data` | 取得擴充的員工資料 |
| `get_my_time_off_eligibility` | 查詢目前使用者可申請的休假類型 |
| `get_personal_information` | 取得個人資訊（地址、緊急聯絡人） |
| `get_today_date_and_day_of_week` | 取得目前日期與時間 |
| `request_my_time_off` | 為目前使用者提交休假申請 |


*有趣的是：模擬資料涵蓋了中國、日本和韓國的員工，姓名與貨幣都做了在地化處理！*

## 專案結構

```text
ai-conversation-bridge/
+-- chat-connector/          # Webhook 適配器（Flask、Python）
|   +-- app/services/        # 訊息適配器（LINE WORKS、DingTalk）+ AI 用戶端
|   +-- Dockerfile
|   +-- .env.example
+-- flowise/                 # 流程範本（核心橋接邏輯）
|   +-- flows/               # 可匯出的 Flowise 流程 JSON 檔案
|   +-- screenshots/
+-- mcp-demo-server/         # 演示用 Workday MCP 伺服器
|   +-- mock_data/           # 員工、休假與薪酬範例資料
|   +-- Dockerfile
|   +-- .env.example
+-- docs/                    # 架構與設定文件
+-- scripts/                 # 本地開發設定（setup.sh）與雲端部署（deploy-cloud-run.sh）
+-- docker-compose.yml       # 容器建置／測試工具
+-- .github/                 # Issue 範本、PR 範本
```

## 文件

- [架構](docs/architecture.md) —— 詳細的系統設計與請求流程
- [設定指南](docs/setup-guide.md) —— 各元件的逐步設定說明
- [企業強化指南](docs/enterprise-guide.md) —— 面向生產環境的安全性、可靠性與營運建議
- [Flowise 組態](flowise/README.md) —— 如何匯入並設定流程範本
- [貢獻指南](CONTRIBUTING.md) —— 如何為本專案做貢獻

## 授權條款

本專案基於 Apache License 2.0 授權 —— 詳見 [LICENSE](../../LICENSE)。
