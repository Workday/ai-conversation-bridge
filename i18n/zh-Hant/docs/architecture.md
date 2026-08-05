# 架構

<p align="center"><sub>
  <a href="../../../docs/architecture.md">English</a> |
  <a href="../../zh-Hans/docs/architecture.md">简体中文</a> |
  繁體中文 |
  <a href="../../ja/docs/architecture.md">日本語</a> |
  <a href="../../ko/docs/architecture.md">한국어</a>
</sub></p>

---

## 概述
<p align="center">
   <img width="900" height="490" alt="高層架構" src="https://github.com/user-attachments/assets/cdd3bcc0-ece8-48ab-9631-0006513cb5a8" />
</p>

AI Conversation Bridge 是一套參考架構，透過由 AI 驅動的編排能力，將企業訊息平台連接到 Workday。它針對亞太及日本（APJ）地區的四項關鍵挑戰：

1. **法規限制** —— 中國法規限制使用境外託管的 LLM
2. **語言與語境差異** —— 企業 LLM 難以妥善處理客戶專有術語
3. **超級應用的主導地位** —— 中國的使用者使用 WeChat（微信），日本使用 LINE，韓國使用 KakaoTalk（韓國主流聊天應用）
4. **Android 應用可用性** —— Google Play Store（Google 應用程式商店）在中國無法存取

## 本儲存庫是什麼／不是什麼

### 本儲存庫是什麼

- 橋接模式的參考實作：聊天連接器 -> Flowise 編排 -> MCP 工具 -> Workday 執行系統。
- 一個附帶模擬 MCP 伺服器的開發與演示環境，便於團隊安全地驗證流程原型。
- 供客戶與合作夥伴在自有環境中建置生產部署的起點。

### 本儲存庫不是什麼

- 不是生產就緒的 Workday MCP 端點，也不能替代 Workday Agent Gateway。
- 不是在單一版本中提供的完整多平台適配器套件。
- 不是 Flowise 的託管執行階段，也不提供 LLM 託管服務。

## 系統架構

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                          AI CONVERSATION BRIDGE                              │
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌───────────┐   │
│  │ Chat Platform  │  │     Chat       │  │    Flowise     │  │    MCP    │   │
│  │  (External)    │─▶│   Connector    │─▶│  (The Core)    │─▶│  Server   │   │
│  │                │◀─│                │◀─│                │◀─│ (Workday) │   │
│  └────────────────┘  └────────────────┘  └────────────────┘  └───────────┘   │
│                                                                              │
│  LINE WORKS          Webhook adapter     LLM orchestration    Tool execution │
│  DingTalk            Message routing     Intent recognition   Workday APIs   │
│  WeChat/KakaoTalk    Response delivery   Jargon translation   Mock data(dev) │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **圖例：** 上圖中的框線標籤保持英文原樣，以確保在 GitHub 上的等寬渲染不會錯位；對應中文含義如下。

| 圖中標籤 | 中文含義 |
| --- | --- |
| Chat Platform (External) | 聊天平台（外部） |
| Chat Connector | 聊天連接器 |
| Flowise (The Core) | Flowise（核心） |
| MCP Server (Workday) | MCP 伺服器（Workday） |
| Webhook adapter / Message routing / Response delivery | Webhook 適配器／訊息路由／回應傳遞 |
| LLM orchestration / Intent recognition / Jargon translation | LLM 編排／意圖識別／術語轉換 |
| Tool execution / Workday APIs / Mock data (dev) | 工具執行／Workday API／模擬資料（開發） |

## 元件詳解

### 聊天連接器（`chat-connector/`）

一個輕量、無狀態的 Flask 應用，負責：

- 接收來自訊息平台的 Webhook
- 擷取使用者訊息與身分資訊
- 將訊息轉發給 Flowise
- 將 AI 回應回傳給使用者

連接器**不包含任何業務邏輯** —— 它純粹是一個適配器。新增聊天平台只需新增一個服務檔案和路由，無需改動 AI 流程管線。同一部署中可以同時啟用多個渠道連接器；例如，LINE WORKS 與 DingTalk（釘釘）可以同時接入共用的 Flowise/OpenRouter 後端。

由於需要接收來自外部訊息平台的 Webhook，聊天連接器**必須部署到對外公開的環境**，並提供 HTTPS 端點。本文以 Google Cloud Run 作為參考範例，但任何能提供公網 URL 的容器平台均可，例如 AWS App Runner、Azure Container Apps、Alibaba Cloud Elastic Container Instance（阿里雲彈性容器執行個體）、Tencent Kubernetes Engine（騰訊雲容器服務）等。

**執行階段：** Python / Gunicorn / Cloud Run（或同等的對外公開容器平台）

### Flowise（`flowise/`）

真正的「橋接層」 —— 一個 Flowise 流程，負責：

- 接收來自聊天連接器的訊息
- 透過客戶自行選擇的 LLM 進行處理
- 識別意圖並轉換專有術語
- 透過 MCP 呼叫 Workday 工具
- 回傳格式化後的回應

Flowise 由客戶在自有雲端環境中管理。本專案提供流程範本，而非 Flowise 執行階段。如果自行託管 Flowise，則必須將其部署在**對外公開的基礎設施**上，以便聊天連接器能夠存取其預測 API。

**執行階段：** 客戶自行管理的 Flowise 執行個體（雲端，或自行託管在對外公開的基礎設施上）

### MCP 伺服器（`mcp-demo-server/`）

本專案提供一個演示 MCP 伺服器，內建模擬 Workday 工具與範例資料，供開發與測試使用。與聊天連接器一樣，演示伺服器也應**部署到雲端環境**（例如 Google Cloud Run、Alibaba Cloud Elastic Container Instance、Tencent Kubernetes Engine），以便 Flowise 能夠存取。任何提供公網 URL 的容器平台均可。

演示伺服器**不包含任何身分驗證**，不適用於生產環境。在生產環境中，請透過 Agent Gateway 將其替換為 **Workday 官方 MCP 端點**，以獲得企業級安全能力（OAuth 2.1、mTLS、稽核日誌、網路原則）。同時請將 Flowise 流程中的 MCP URL 更新為 Agent Gateway 的位址。

**執行階段：** Python / FastMCP / Cloud Run（演示）或 Workday Agent Gateway（生產）

## 請求流程

```text
1. 使用者在 LINE WORKS 或 DingTalk 中傳送「我還有多少天年假？」
   │
2. 聊天平台將 Webhook POST 到聊天連接器
   - LINE WORKS：/lineworks/callback（或舊版 /callback）
   - DingTalk：/dingtalk/callback
   │
3. 聊天連接器擷取訊息 + 依平台隔離的工作階段 ID，呼叫 Flowise 預測 API
   │
4. Flowise LLM 識別意圖：get_current_user_time_off_balance
   │
5. Flowise MCP 用戶端呼叫 MCP 伺服器 → get_current_user_time_off_balance()
   │
6. MCP 伺服器回傳：{ vacation: { available: 12, used: 3 } }
   │
7. Flowise LLM 格式化回應：「您還有 12 天年假（共 15 天，已使用 3 天）」
   │
8. 聊天連接器收到回應，透過原聊天平台回傳給使用者
```

## 核心設計原則

### 清晰的關注點分離

- **Workday** 透過 MCP 始終作為安全的「執行系統」
- **客戶** 掌控 AI 層（自有 LLM）以及訊息與介面
- **本橋接層**（Flowise）連接兩者，且不儲存敏感資料

### 資料主權

客戶的 LLM 執行在自有環境中，訊息也在自有基礎設施內處理。本橋接層在設計上即滿足法規要求。

### 平台無關

聊天連接器模式可複用於任何訊息平台。Flowise 流程無需撰寫特定平台的 Webhook 或回覆邏輯；連接器會傳入依平台隔離的工作階段 ID，例如 `lineworks:<userId>` 或 `dingtalk:<conversationId>:<senderStaffId>`，從而確保同時執行的多個聊天渠道不會在對話記憶中相互衝突。

### 生產環境強化

本參考架構實作了基線安全措施（Webhook 簽章驗證、輸入長度限制、回應驗證）。對於生產部署，請參閱[企業強化指南](enterprise-guide.md)，其中提供了關於速率限制、PII 處理、重試邏輯、身分對應、可觀測性以及基礎設施選型（Workday 官方 MCP 伺服器、Flowise Cloud Enterprise）的更多建議。
