# Translation Glossary

Shared terminology and conventions for translating this project's documentation. This file is for translators and is intentionally kept in English — it is not itself translated or mirrored into `i18n/<lang>/`.

## How to use this

- **Read this before you start translating.** Using the agreed term keeps a reader who moves between `README.md` and `docs/architecture.md` from meeting three names for the same component.
- **Introducing a new term? Add a row.** Same PR as the translation that needed it.
- **Disagree with an entry?** Change it here *and* in every file that uses it, in one PR. A glossary that drifts from the docs is worse than no glossary.
- **Filling in a new language?** The `ja` and `ko` columns are `—` because nobody has translated those yet. Fill your column in the same PR as your first translation.

Coverage today: **zh-Hans** (`README.md`, `docs/architecture.md` translated) and **zh-Hant** (terminology agreed, translation pending).

## Never translate

Product names, acronyms, and anything a reader will type or click:

`Flowise` · `MCP` · `AI` · `LLM` · `API` · `JSON` · `HTTPS` · `OAuth 2.1` · `mTLS` · `Webhook` · `Workday` · `Workday Agent Gateway` · `LINE WORKS` · `OpenRouter` · `Python` · `Flask` · `Gunicorn` · `FastMCP` · `Docker` · `Dockerfile` · `Cloud Run` · `PII`

Also verbatim:

| Category | Examples |
|---|---|
| Tool names | `get_current_user_time_off_balance`, `find_employee_id_by_name` |
| Environment variables | `AI_PROVIDER`, `FLOWISE_API_URL`, `CHAT_PROVIDER` |
| Paths and filenames | `chat-connector/`, `flowise/flows/`, `.env.example` |
| Routes | `/lineworks/callback`, `/dingtalk/callback` |
| Session id formats | `lineworks:<userId>`, `dingtalk:<conversationId>:<senderStaffId>` |
| Shell commands, URLs, JSON payloads | `gcloud run deploy …`, `{ vacation: { available: 12, used: 3 } }` |

**`AI Conversation Bridge`** is a product name and stays in Latin script. The generic phrase "the Bridge", however, *is* translated — zh-Hans 本桥接层, zh-Hant 本橋接層.

**Flowise UI labels stay in English.** The Flowise interface is English, so a translated menu name sends the reader hunting for something that isn't there. Keep **Agent Flows**, **Add New**, **Settings**, **Load Agentflow** as-is and translate the instruction around them.

## Product names: English first, local name in parentheses

On **first mention** give the English name followed by the local name in full-width parentheses; use the English name alone after that. This keeps the docs searchable both ways and matches the identifiers readers meet in config and code.

| English | zh-Hans first mention | zh-Hant first mention |
|---|---|---|
| DingTalk | DingTalk（钉钉） | DingTalk（釘釘） |
| WeChat | WeChat（微信） | WeChat（微信） |
| Feishu | Feishu（飞书） | Feishu（飛書） |
| KakaoTalk | KakaoTalk（韩国主流聊天应用） | KakaoTalk（韓國主流聊天應用） |
| Alibaba Cloud Elastic Container Instance | Alibaba Cloud Elastic Container Instance（阿里云弹性容器实例） | Alibaba Cloud Elastic Container Instance（阿里雲彈性容器執行個體） |
| Tencent Kubernetes Engine | Tencent Kubernetes Engine（腾讯云容器服务） | Tencent Kubernetes Engine（騰訊雲容器服務） |
| Google Play Store | Google Play Store（谷歌应用商店） | Google Play Store（Google 應用程式商店） |
| Golden Week | Golden Week（黄金周） | Golden Week（黃金週） |

`AWS App Runner` and `Azure Container Apps` stay in English with no parenthetical — there is no established local form worth introducing.

## Terms

| English | zh-Hans | zh-Hant | ja | ko |
|---|---|---|---|---|
| APJ region | 亚太及日本（APJ）地区 | 亞太及日本（APJ）地區 | — | — |
| architecture | 架构 | 架構 | — | — |
| reference architecture | 参考架构 | 參考架構 | — | — |
| orchestration | 编排 | 編排 | — | — |
| chat connector | 聊天连接器 | 聊天連接器 | — | — |
| adapter | 适配器 | 適配器 | — | — |
| webhook adapter | Webhook 适配器 | Webhook 適配器 | — | — |
| system of action | 执行系统 | 執行系統 | — | — |
| source of truth | 权威数据源 | 權威資料來源 | — | — |
| intent recognition | 意图识别 | 意圖識別 | — | — |
| jargon | 专有术语 | 專有術語 | — | — |
| jargon translation | 术语转换 | 術語轉換 | — | — |
| session id | 会话 ID | 工作階段 ID | — | — |
| platform-scoped session id | 按平台隔离的会话 ID | 依平台隔離的工作階段 ID | — | — |
| conversation memory | 对话记忆 | 對話記憶 | — | — |
| tool calling | 工具调用 | 工具呼叫 | — | — |
| tool execution | 工具执行 | 工具執行 | — | — |
| prediction API | 预测 API | 預測 API | — | — |
| endpoint | 端点 | 端點 | — | — |
| pipeline | 流水线 | 流程管線 | — | — |
| runtime | 运行时 | 執行階段 | — | — |
| deployment | 部署 | 部署 | — | — |
| repository / repo | 仓库 | 儲存庫 | — | — |
| credentials | 凭据 | 憑證 | — | — |
| bot / robot | 机器人 | 機器人 | — | — |
| callback URL | 回调 URL | 回呼 URL | — | — |
| fallback | 回退 | 後備 | — | — |
| profile | 档案信息 | 個人檔案 | — | — |
| stateless | 无状态 | 無狀態 | — | — |
| public-facing | 面向公网的 | 對外公開的 | — | — |
| container platform | 容器平台 | 容器平台 | — | — |
| self-hosted | 自托管 | 自行託管 | — | — |
| customer-managed | 客户自行管理 | 客戶自行管理 | — | — |
| data sovereignty | 数据主权 | 資料主權 | — | — |
| regulatory hurdles | 监管障碍 | 法規障礙 | — | — |
| regulatory restrictions | 监管限制 | 法規限制 | — | — |
| local models | 本地模型 | 本地模型 | — | — |
| separation of concerns | 关注点分离 | 關注點分離 | — | — |
| platform agnostic | 平台无关 | 平台無關 | — | — |
| production hardening | 生产环境强化 | 生產環境強化 | — | — |
| signature verification | 签名验证 | 簽章驗證 | — | — |
| audit logging | 审计日志 | 稽核日誌 | — | — |
| authentication | 身份验证 | 身分驗證 | — | — |
| rate limiting | 限流 | 速率限制 | — | — |
| retry logic | 重试逻辑 | 重試邏輯 | — | — |
| identity mapping | 身份映射 | 身分對應 | — | — |
| observability | 可观测性 | 可觀測性 | — | — |
| input limits | 输入长度限制 | 輸入長度限制 | — | — |
| response validation | 响应校验 | 回應驗證 | — | — |
| network policies | 网络策略 | 網路原則 | — | — |
| mock data | 模拟数据 | 模擬資料 | — | — |
| mock tools | 模拟工具 | 模擬工具 | — | — |
| demo | 演示 | 演示 | — | — |
| server | 服务器 | 伺服器 | — | — |
| flow | 流程 | 流程 | — | — |
| flow template | 流程模板 | 流程範本 | — | — |
| super-app dominance | 超级应用主导 | 超級應用主導 | — | — |
| worker *(Workday sense)* | 工作者 | 工作者 | — | — |
| employee | 员工 | 員工 | — | — |
| worker ID | 工作者 ID | 工作者 ID | — | — |
| time off | 休假 | 休假 | — | — |
| leave balance | 假期余额 | 假期餘額 | — | — |
| leave request | 休假申请 | 休假申請 | — | — |
| direct reports | 直接下属 | 直接下屬 | — | — |
| emergency contact | 紧急联系人 | 緊急聯絡人 | — | — |
| eligibility | 申请资格 | 申請資格 | — | — |
| message routing | 消息路由 | 訊息路由 | — | — |
| response delivery | 响应投递 | 回應傳遞 | — | — |
| AI provider | AI 提供方 | AI 供應商 | — | — |
| AI backend | AI 后端 | AI 後端 | — | — |
| environment variable | 环境变量 | 環境變數 | — | — |
| default | 默认 | 預設 | — | — |
| network | 网络 | 網路 | — | — |
| project | 项目 | 專案 | — | — |
| documentation | 文档 | 文件 | — | — |
| file | 文件 | 檔案 | — | — |
| license | 许可证 | 授權條款 | — | — |
| quick start | 快速开始 | 快速開始 | — | — |
| prerequisites | 前置条件 | 前置條件 | — | — |
| setup guide | 设置指南 | 設定指南 | — | — |
| enterprise hardening guide | 企业强化指南 | 企業強化指南 | — | — |

Four entries above are not new decisions — they were already set by the placeholder titles in `i18n/zh-Hans/` and `i18n/zh-Hant/`: `演示` (demo), `服务器`/`伺服器` (server), `流程模板`/`流程範本` (flow template), and `设置指南`/`設定指南` (setup guide).

### ⚠️ False friend: 文件

| | *document* | *file* |
|---|---|---|
| **zh-Hans** | 文档 | 文件 |
| **zh-Hant** | 文件 | 檔案 |

`文件` means **document** in Traditional Chinese but **file** in Simplified Chinese. Anyone converting between the two scripts will get this backwards eventually — check every occurrence rather than trusting a converter.

More generally, **zh-Hant is not a character conversion of zh-Hans.** The vocabulary genuinely differs: 資料/数据, 訊息/消息, 專案/项目, 範本/模板, 呼叫/调用, 變數/变量, 預設/默认, 網路/网络, 回呼/回调, 身分/身份. Run a converter and you get Traditional characters, not Traditional Chinese.

## Style

**Both Chinese variants:**

- Formal register: **您**, never 你. Requests are `请` + verb (zh-Hant `請`).
- Full-width punctuation in prose — `。`，`，`，`（）`，`：` — never ASCII `.` or `,`. Use `、` to separate items inside a list.
- One half-width space between Latin and Han characters: `Flowise 流程`, `演示 MCP 服务器`, `AI 提供方`. No space before full-width punctuation.
- Preserve the source's `**bold**`, especially on load-bearing warnings (*no business logic*, *must be deployed*, *no authentication*).
- Match the source's register per passage. Where the English is deliberately informal — the brain/ears/hands metaphor, the "Fun fact" aside — keep that warmth rather than flattening it into formal prose.

## Structure

### Language switcher

Every translated doc keeps the switcher block between its H1 and the `---` rule. The current language is **plain text, not a link**; the others are links. Order is fixed: English → 简体中文 → 繁體中文 → 日本語 → 한국어.

Relative depth differs by nesting. From a translated file:

| Translated file | → English | → sibling language |
|---|---|---|
| `i18n/<lang>/README.md` | `../../README.md` | `../zh-Hant/README.md` |
| `i18n/<lang>/CONTRIBUTING.md` | `../../CONTRIBUTING.md` | `../zh-Hant/CONTRIBUTING.md` |
| `i18n/<lang>/docs/*.md` | `../../../docs/*.md` | `../../zh-Hant/docs/*.md` |
| `i18n/<lang>/flowise/README.md` | `../../../flowise/README.md` | `../../zh-Hant/flowise/README.md` |
| `i18n/<lang>/mcp-demo-server/README.md` | `../../../mcp-demo-server/README.md` | `../../zh-Hant/mcp-demo-server/README.md` |

When you replace a placeholder with a real translation, **leave the H1 and switcher untouched** — they are already correct.

### Body links

Two rules, which look inconsistent but are not:

- **Links to docs that have translations stay relative** so they resolve inside `i18n/<lang>/`. From `i18n/zh-Hans/README.md`, `docs/architecture.md` correctly lands on the Chinese architecture doc. If the target is still a placeholder that's fine — it links onward to English, and no edit is needed once it *is* translated.
- **Links to code, assets, or untranslated files need `../../`** to escape the language directory: `[flowise/](../../flowise/)`, `[LICENSE](../../LICENSE)`.

So `flowise/` (the code directory) becomes `../../flowise/` while `flowise/README.md` (the translated doc) stays bare. Same prefix, different targets.

**Nothing in CI checks links.** Verify by hand from the translated file's own directory before opening a PR.

### Code, diagrams, and tables

- **Code fences are verbatim** — commands, env vars, JSON, and any comments inside them. Sample *conversation* text is prose and should be translated so the example reads naturally in the target language.
- **Markdown table padding doesn't need to align.** CJK characters are double-width, so aligning the pipes in your editor is wasted effort; GitHub renders single-space padding identically.
- **ASCII diagrams must keep their alignment in display columns**, where CJK characters and full-width punctuation count as **2**. Translating a label inside a box will break the border unless you re-pad it. Check before committing:

  ```bash
  python3 -c "
  import unicodedata, sys
  def w(s): return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)
  box = [l for l in open(sys.argv[1]).read().split('\n') if l and l[0] in '┌│└']
  print(sorted({w(l) for l in box}) or 'no box lines found')
  " i18n/zh-Hans/docs/architecture.md
  ```

  A single width in the output means the box is intact. If a label won't fit, prefer leaving that label in English over widening the box.
