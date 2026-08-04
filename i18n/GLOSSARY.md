# Translation Glossary

Shared terminology and conventions for translating this project's documentation. This file is for translators and is intentionally kept in English — it is not itself translated or mirrored into `i18n/<lang>/`.

## How to use this

- **Read this before you start translating.** Using the agreed term keeps a reader who moves between `README.md` and `docs/architecture.md` from meeting three names for the same component.
- **Introducing a new term? Add a row.** Same PR as the translation that needed it.
- **Disagree with an entry?** Change it here *and* in every file that uses it, in one PR. A glossary that drifts from the docs is worse than no glossary.
- **Filling in a new language?** The `ja` and `ko` columns are filled. Fill your column in the same PR as your first translation.

Coverage today: **zh-Hans**, **zh-Hant**, **ja**, and **ko** (`README.md`, `docs/architecture.md` translated).

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

**`AI Conversation Bridge`** is a product name and stays in Latin script. The generic phrase "the Bridge", however, *is* translated — zh-Hans 本桥接层, zh-Hant 本橋接層, ja 本ブリッジ, ko 브릿지 계층.

**Flowise UI labels stay in English.** The Flowise interface is English, so a translated menu name sends the reader hunting for something that isn't there. Keep **Agent Flows**, **Add New**, **Settings**, **Load Agentflow** as-is and translate the instruction around them.

## Product names: English first, local name in parentheses

On **first mention** give the English name followed by the local name in full-width parentheses; use the English name alone after that. This keeps the docs searchable both ways and matches the identifiers readers meet in config and code. Japanese has documented exceptions below (native kana forms such as ゴールデンウィーク and official names such as `Google Play ストア`) — follow the `ja first mention` column and the notes under the table rather than forcing the Chinese pattern.

| English | zh-Hans first mention | zh-Hant first mention | ja first mention | ko first mention |
|---|---|---|---|---|
| DingTalk | DingTalk（钉钉） | DingTalk（釘釘） | DingTalk（ディントーク） | DingTalk(딩톡) |
| WeChat | WeChat（微信） | WeChat（微信） | WeChat（ウィーチャット） | WeChat(위챗) |
| Feishu | Feishu（飞书） | Feishu（飛書） | Feishu（フィーシュー） | Feishu(페이슈) |
| KakaoTalk | KakaoTalk（韩国主流聊天应用） | KakaoTalk（韓國主流聊天應用） | KakaoTalk（カカオトーク） | KakaoTalk(카카오톡) |
| Alibaba Cloud Elastic Container Instance | Alibaba Cloud Elastic Container Instance（阿里云弹性容器实例） | Alibaba Cloud Elastic Container Instance（阿里雲彈性容器執行個體） | Alibaba Cloud Elastic Container Instance | Alibaba Cloud Elastic Container Instance *(no parenthetical)* |
| Tencent Kubernetes Engine | Tencent Kubernetes Engine（腾讯云容器服务） | Tencent Kubernetes Engine（騰訊雲容器服務） | Tencent Kubernetes Engine | Tencent Kubernetes Engine *(no parenthetical)* |
| Google Play Store | Google Play Store（谷歌应用商店） | Google Play Store（Google 應用程式商店） | Google Play ストア | Google Play 스토어 |
| Golden Week | Golden Week（黄金周） | Golden Week（黃金週） | ゴールデンウィーク | Golden Week(일본의 골든위크) |

`AWS App Runner` and `Azure Container Apps` stay in English with no parenthetical — there is no established local form worth introducing. Korean follows the same rule for Alibaba Cloud Elastic Container Instance and Tencent Kubernetes Engine.

**Korean exceptions to the English-first + gloss pattern:**

- **KakaoTalk** — the Chinese parenthetical is an explanatory gloss for a foreign reader ("Korea's mainstream chat app"). For a Korean reader that gloss is patronizing; use `KakaoTalk(카카오톡)` only.
- **Golden Week** — this is a Japanese holiday. A Korean reader may not know it, so a gloss helps: `Golden Week(일본의 골든위크)`.
- **Google Play 스토어** — official Korean product name. Write it as such (same pattern as Japanese `Google Play ストア`), not `Google Play Store(…)`.

**Japanese exceptions / notes:**

- **Golden Week** is a Japanese holiday. ゴールデンウィーク is the native term, not a gloss of an English one. Write it in kana as a Japanese reader would; do **not** produce `Golden Week（ゴールデンウィーク）`.
- **LINE** / **LINE WORKS** are native to the Japanese market and already Latin-script. No parenthetical.
- **KakaoTalk** has an established kana form (カカオトーク), so `KakaoTalk（カカオトーク）` is appropriate; an explanatory gloss is unnecessary.
- **DingTalk / WeChat / Feishu** use established kana forms rather than Chinese characters — friendlier to a Japanese technical reader.
- **Google Play ストア** is the official Japanese name; write it as such rather than `Google Play Store（…）`.
- **Alibaba Cloud Elastic Container Instance** and **Tencent Kubernetes Engine** stay in English with no parenthetical — same precedent as `AWS App Runner` / `Azure Container Apps`.

Korean uses ASCII `()` for parentheticals, not full-width `（）`. The "full-width parentheses" instruction above applies to the Chinese variants only.

## Terms

| English | zh-Hans | zh-Hant | ja | ko |
|---|---|---|---|---|
| APJ region | 亚太及日本（APJ）地区 | 亞太及日本（APJ）地區 | アジア太平洋および日本（APJ）地域 | APJ(아시아 태평양 및 일본) 지역 |
| architecture | 架构 | 架構 | アーキテクチャ | 아키텍처 |
| reference architecture | 参考架构 | 參考架構 | リファレンスアーキテクチャ | 참조 아키텍처 |
| orchestration | 编排 | 編排 | オーケストレーション | 오케스트레이션 |
| chat connector | 聊天连接器 | 聊天連接器 | チャットコネクター | 채팅 커넥터 |
| adapter | 适配器 | 適配器 | アダプター | 어댑터 |
| webhook adapter | Webhook 适配器 | Webhook 適配器 | Webhookアダプター | Webhook 어댑터 |
| system of action | 执行系统 | 執行系統 | 実行システム | 실행 시스템 |
| source of truth | 权威数据源 | 權威資料來源 | 信頼できる情報源 | 권위 있는 데이터 소스 |
| intent recognition | 意图识别 | 意圖識別 | 意図認識 | 의도 인식 |
| jargon | 专有术语 | 專有術語 | 専門用語 | 전문 용어 |
| jargon translation | 术语转换 | 術語轉換 | 専門用語の変換 | 전문 용어 변환 |
| session id | 会话 ID | 工作階段 ID | セッションID | 세션 ID |
| platform-scoped session id | 按平台隔离的会话 ID | 依平台隔離的工作階段 ID | プラットフォーム単位のセッションID | 플랫폼별 세션 ID |
| conversation memory | 对话记忆 | 對話記憶 | 会話メモリ | 대화 메모리 |
| tool calling | 工具调用 | 工具呼叫 | ツール呼び出し | 도구 호출 |
| tool execution | 工具执行 | 工具執行 | ツール実行 | 도구 실행 |
| prediction API | 预测 API | 預測 API | 予測API | 예측 API |
| endpoint | 端点 | 端點 | エンドポイント | 엔드포인트 |
| pipeline | 流水线 | 流程管線 | パイプライン | 파이프라인 |
| runtime | 运行时 | 執行階段 | ランタイム | 런타임 |
| deployment | 部署 | 部署 | デプロイ | 배포 |
| configuration / config *(noun — MCP configuration, Flowise configuration)* | 配置 | 組態 | 設定 | 설정 |
| channel *(chat channel / messaging channel)* | 渠道 | 渠道 | チャネル | 채널 |
| repository / repo | 仓库 | 儲存庫 | リポジトリ | 저장소 |
| credentials | 凭据 | 憑證 | 認証情報 | 자격 증명 |
| bot / robot | 机器人 | 機器人 | ボット / ロボット | 봇 / 로봇 |
| callback URL | 回调 URL | 回呼 URL | コールバックURL | 콜백 URL |
| fallback | 回退 | 後備 | フォールバック | 폴백 |
| profile | 档案信息 | 個人檔案 | プロフィール | 프로필 |
| stateless | 无状态 | 無狀態 | ステートレス | 무상태 |
| public-facing | 面向公网的 | 對外公開的 | パブリック向け | 공개 접근 가능한 |
| container platform | 容器平台 | 容器平台 | コンテナプラットフォーム | 컨테이너 플랫폼 |
| self-hosted | 自托管 | 自行託管 | セルフホスト | 자체 호스팅 |
| customer-managed | 客户自行管理 | 客戶自行管理 | 顧客管理 | 고객 관리 |
| data sovereignty | 数据主权 | 資料主權 | データ主権 | 데이터 주권 |
| regulatory hurdles | 监管障碍 | 法規障礙 | 規制上のハードル | 규제 장애 |
| regulatory restrictions | 监管限制 | 法規限制 | 規制上の制限 | 규제 제한 |
| local models | 本地模型 | 本地模型 | ローカルモデル | 로컬 모델 |
| separation of concerns | 关注点分离 | 關注點分離 | 関心の分離 | 관심사 분리 |
| platform agnostic | 平台无关 | 平台無關 | プラットフォーム非依存 | 플랫폼 독립성 |
| production hardening | 生产环境强化 | 生產環境強化 | 本番環境の堅牢化 | 프로덕션 보안 강화 |
| signature verification | 签名验证 | 簽章驗證 | 署名検証 | 서명 검증 |
| audit logging | 审计日志 | 稽核日誌 | 監査ログ | 감사 로그 |
| authentication | 身份验证 | 身分驗證 | 認証 | 인증 |
| rate limiting | 限流 | 速率限制 | レート制限 | 속도 제한 |
| retry logic | 重试逻辑 | 重試邏輯 | リトライロジック | 재시도 로직 |
| identity mapping | 身份映射 | 身分對應 | アイデンティティマッピング | 신원 매핑 |
| observability | 可观测性 | 可觀測性 | オブザーバビリティ | 관찰 가능성 |
| input limits | 输入长度限制 | 輸入長度限制 | 入力制限 | 입력 길이 제한 |
| response validation | 响应校验 | 回應驗證 | レスポンス検証 | 응답 검증 |
| network policies | 网络策略 | 網路原則 | ネットワークポリシー | 네트워크 정책 |
| mock data | 模拟数据 | 模擬資料 | モックデータ | 모의 데이터 |
| mock tools | 模拟工具 | 模擬工具 | モックツール | 모의 도구 |
| demo | 演示 | 演示 | デモ | 데모 |
| official / standard *(vendor-published — "the official MCP endpoint", "the standard Workday Android app")* | 官方 | 官方 | 公式 | 공식 / 표준 |
| server | 服务器 | 伺服器 | サーバー | 서버 |
| flow | 流程 | 流程 | フロー | 플로우 |
| flow template | 流程模板 | 流程範本 | フローテンプレート | 플로우 템플릿 |
| super-app dominance | 超级应用主导 | 超級應用的主導地位 | スーパーアプリの優位 | 슈퍼 앱 중심 환경 |
| worker *(Workday sense)* | 工作者 | 工作者 | ワーカー | 워커 |
| employee | 员工 | 員工 | 従業員 | 직원 |
| worker ID | 工作者 ID | 工作者 ID | ワーカーID | 워커 ID |
| time off | 休假 | 休假 | 休暇 | 휴가 |
| leave balance | 假期余额 | 假期餘額 | 休暇残日数 | 휴가 잔여일수 |
| leave request | 休假申请 | 休假申請 | 休暇申請 | 휴가 신청 |
| direct reports | 直接下属 | 直接下屬 | 直属の部下 | 직속 부하 직원 |
| emergency contact | 紧急联系人 | 緊急聯絡人 | 緊急連絡先 | 비상 연락처 |
| eligibility | 申请资格 | 申請資格 | 申請資格 | 신청 자격 |
| message routing | 消息路由 | 訊息路由 | メッセージルーティング | 메시지 라우팅 |
| response delivery | 响应投递 | 回應傳遞 | レスポンス配信 | 응답 전달 |
| AI provider | AI 提供方 | AI 供應商 | AIプロバイダー | AI 제공자 |
| AI backend | AI 后端 | AI 後端 | AIバックエンド | AI 백엔드 |
| environment variable | 环境变量 | 環境變數 | 環境変数 | 환경 변수 |
| default | 默认 | 預設 | デフォルト | 기본값 |
| network | 网络 | 網路 | ネットワーク | 네트워크 |
| project | 项目 | 專案 | プロジェクト | 프로젝트 |
| context *(business/cultural sense — not an LLM's context window)* | 语境 | 語境 | 文脈 | 맥락 |
| documentation | 文档 | 文件 | ドキュメント | 문서 |
| file | 文件 | 檔案 | ファイル | 파일 |
| license | 许可证 | 授權條款 | ライセンス | 라이선스 |
| quick start | 快速开始 | 快速開始 | クイックスタート | 빠른 시작 |
| prerequisites | 前置条件 | 前置條件 | 前提条件 | 필요한 것 |
| setup guide | 设置指南 | 設定指南 | セットアップガイド | 설정 가이드 |
| enterprise hardening guide | 企业强化指南 | 企業強化指南 | エンタープライズ堅牢化ガイド | 엔터프라이즈 보안 강화 가이드 |

Four entries above are not new decisions — they were already set by the placeholder titles in `i18n/zh-Hans/` and `i18n/zh-Hant/`: `演示` (demo), `服务器`/`伺服器` (server), `流程模板`/`流程範本` (flow template), and `设置指南`/`設定指南` (setup guide).

`configuration / config` is the noun: zh-Hant `組態`, ko `설정` (e.g. `MCP 설정`, `채널 설정`). Do not use ko `구성` here — that collides with `구성 요소` (components). The verb "configure / set" stays zh-Hant `設定` / ko `설정하다` (e.g. `환경 변수를 설정`).

### ⚠️ Ambiguous term: context

The English source uses "context" in the everyday sense — company jargon, local cultural nuances (`README.md`: "Language and context", `docs/architecture.md`: "Language/context gaps"). A literal `上下文`/`上下文` reads to a technical audience as an LLM's *context window*, which is not what's meant. Use `语境`/`語境` (linguistic/cultural context) instead. If a future passage really does mean the AI context window, `上下文` is correct there — check which sense applies before translating.

For Korean, the same trap exists: `컨텍스트` reads as the model's context window. Use `맥락` (or `문화적 배경`) for the business/cultural sense.

**Japanese:** the same trap applies with `コンテキスト`, which a technical Japanese audience reads as the model's context window. Use `文脈` for the business/cultural sense (or `商習慣・文化的背景` when the passage is more about local practice than language). Reserve `コンテキスト` for an actual LLM context window.

### ⚠️ False friend: 文件

| | *document* | *file* |
|---|---|---|
| **zh-Hans** | 文档 | 文件 |
| **zh-Hant** | 文件 | 檔案 |

`文件` means **document** in Traditional Chinese but **file** in Simplified Chinese. Anyone converting between the two scripts will get this backwards eventually — check every occurrence rather than trusting a converter.

More generally, **zh-Hant is not a character conversion of zh-Hans.** The vocabulary genuinely differs: 資料/数据, 訊息/消息, 專案/项目, 範本/模板, 呼叫/调用, 變數/变量, 預設/默认, 網路/网络, 回呼/回调, 身分/身份. Run a converter and you get Traditional characters, not Traditional Chinese.

## Style

### Both Chinese variants

The full-width punctuation and Latin–Han spacing rules below are **Chinese-only**. Do not apply them to Korean (or Japanese).

- Formal register: **您**, never 你. Requests are `请` + verb (zh-Hant `請`).
- Full-width punctuation in prose — `。`，`，`，`（）`，`：` — never ASCII `.` or `,`. Use `、` to separate items inside a list.
- One half-width space between Latin and Han characters: `Flowise 流程`, `演示 MCP 服务器`, `AI 提供方`. No space before full-width punctuation.
- Preserve the source's `**bold**`, especially on load-bearing warnings (*no business logic*, *must be deployed*, *no authentication*).
- Match the source's register per passage. Where the English is deliberately informal — the brain/ears/hands metaphor, the "Fun fact" aside — keep that warmth rather than flattening it into formal prose.

### Korean

- **Register:** body sentences use 합니다체 (`입니다` / `합니다`). Imperatives and short callout questions use the conventional developer-doc forms `~하세요` and `~시나요?` / `~신가요?` — do **not** convert those to `~하십시오` / `~십니까?`, which mixes registers inside the same callout and reads stiffer than this document's voice. Never use 한다체. The Chinese `您` rule has no Korean equivalent; Korean handles deference through verb endings, so **avoid 당신** entirely (it reads as confrontational) — drop the second-person pronoun rather than translating it.
- **Punctuation:** ASCII half-width `.` `,` `()` `:` — never full-width `。` `，` `（）` `：`, and never Japanese/Chinese corner quotes `「」` / `『』`. Use ASCII `"…"` for quotations. Separate list items with `,` or `·`, not `、`. Do not "fix" Korean punctuation into full-width to match the Chinese columns.
- **Spacing (띄어쓰기):** standard Korean rules; a space between Hangul and adjacent Latin tokens is normal (`Flowise 플로우`, `MCP 서버`), not a special typographic rule. Before `(`: no space when the parenthesis glosses or renames the preceding word (`KakaoTalk(카카오톡)`, `개인 정보(주소)`); one space when it is a separate aside (`채팅 커넥터 (chat-connector/)`, `Cloud Run (또는 …)`).
- **Loanword vs native-Sino:** prefer established loan forms where natural — 서버 not 봉사기; 엔드포인트 not 종점; 오케스트레이션. Use Sino-Korean where it is the settled technical term — 배포, 인증, 감사 로그. Pin each choice in the `ko` column.
- **Particles after Latin words:** choose by the *Korean pronunciation* of the preceding word, not its spelling. Never write dual forms like `은(는)` in prose — pick one. See the particle table below.
- Preserve the source's `**bold**`, especially on load-bearing warnings.
- Code fences are verbatim, including comments inside them — except sample conversation text, which is prose and should be translated.
- Match the source's register per passage. Where the English is deliberately informal — the brain/ears/hands metaphor, the "Fun fact" aside — keep that warmth (재미있는 사실) rather than flattening it into stiff formal prose.

### ⚠️ Korean particles after Latin words and acronyms

Korean particles are chosen by the **final sound of the preceding word**, and after a Latin word or acronym that means its *Korean pronunciation*, not its spelling. This is the single most common error in machine-assisted Korean technical translation:

| Word | Korean reading | Ends in | Correct particles |
|---|---|---|---|
| `Flowise` | 플로우와이즈 | vowel | `Flowise는`, `Flowise가`, `Flowise를` |
| `Workday` | 워크데이 | vowel | `Workday는`, `Workday가`, `Workday를` |
| `MCP` | 엠시피 | vowel | `MCP는`, `MCP가`, `MCP를` |
| `LLM` | 엘엘엠 | consonant | `LLM은`, `LLM이`, `LLM을` |
| `API` | 에이피아이 | vowel | `API는`, `API를` |
| `AI` | 에이아이 | vowel | `AI는`, `AI를` |
| `Webhook` | 웹훅 | consonant | `Webhook은`, `Webhook이`, `Webhook을` |
| `Cloud Run` | 클라우드 런 | consonant | `Cloud Run은`, `Cloud Run이` |
| `JSON` | 제이슨 | consonant | `JSON은`, `JSON이` |
| `DingTalk` | 딩톡 | consonant | `DingTalk은`, `DingTalk이`, `DingTalk을` |

Never write the `은(는)` / `이(가)` dual form in prose — pick the right one.

### Japanese

- **Register:** です・ます調 throughout — never mix in である調. Warm asides (brain/ears/hands, "Fun fact") stay warm but stay polite; prefer a 実は… register over a stiff literal 面白い事実.
- **Punctuation:** full-width `。` and `、` in Japanese sentences; full-width `（）` in prose. Never ASCII `.` or `,` ending a Japanese sentence.
- **Latin/Japanese spacing:** **no space** between Latin letters and Japanese (kana/kanji): `Flowiseフロー`, `MCPサーバー`, `AIプロバイダー`, `セッションID`, `ワーカーID`. This matches standard Japanese technical writing and the existing placeholder text (`[英語版（原文）を読む →]`). Apply uniformly — mixed spacing is the most visible consistency failure in a Japanese translation. (`Google Play ストア` keeps its internal space — that is the official product name, not this rule.)
- **Long-vowel marks (ー):** prefer the long form for katakana loanwords, matching modern Microsoft/JTF convention: サーバー, コンピューター, ユーザー, アダプター, コネクター, プロバイダー. Do not mix サーバ / サーバー.
- **Katakana vs kanji vs English:** サーバー / エンドポイント / オーケストレーション / アダプター stay in katakana; アーキテクチャ for architecture; 意図認識, 権限, 監査ログ in kanji where natural. Pin specifics in the `ja` column above.
- Preserve the source's `**bold**`, especially on load-bearing warnings.
- Code fences are verbatim (commands, env vars, JSON, comments) — except sample *conversation* text, which is prose and should be translated.

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
- **Markdown table padding doesn't need to align.** GitHub renders tables as HTML, so single-space padding around the pipes looks identical to hand-aligned columns. Don't spend effort on it.

#### Never put CJK (including Hangul) inside a diagram

This rule covers Han characters *and* Hangul — Korean syllables are East Asian Width "Wide", exactly like Han. A translated label inside a box **cannot be made to align on GitHub**, at any padding. GitHub's code font stack (`ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, …` at 12px) has no CJK/Hangul coverage, so those characters fall through to a system font whose advance width is not a whole multiple of the ASCII one. Measured in Chromium on macOS:

| | advance @12px | vs ASCII |
|---|---|---|
| ASCII (SF Mono) | 7.225px | 1.0 |
| CJK (PingFang SC fallback) | 12.0px | **1.66** |
| Box-drawing `┌ ─ │ ┘` | 7.225px | 1.0 |
| Arrows `▶ ◀` | 7.225px | 1.0 |

Windows resolves the same stack to Consolas plus a different CJK fallback and lands near **1.8**. The Unicode "East Asian Wide = 2 columns" rule that *terminals* follow does not hold in a browser, and no single padding satisfies 1.66, 1.8 and 2.0 at once. An earlier revision of `i18n/zh-Hans/docs/architecture.md` padded its diagram to a flawless 80 columns under the 2.0 rule and still rendered visibly crooked on GitHub.

Note what the table also shows: **box-drawing glyphs and arrows are not the problem.** They measure exactly one ASCII advance. They *are* East Asian Width category **Ambiguous**, so a renderer is free to draw them wide — but that only bites when CJK on the same line has already pulled the font into a CJK face. Keep the line free of CJK/Hangul and they can't drift.

So for any diagram whose labels are worth translating:

1. **Reuse the English diagram verbatim** — copy the fenced block byte-for-byte from the English source. It already aligns; leave it alone.
2. **Put the translations in a markdown table underneath.** Tables are HTML, so font metrics can't touch them. `i18n/zh-Hans/docs/architecture.md` is the worked example: the diagram is byte-identical to `docs/architecture.md`, followed by a 图例 table mapping each English label to its Chinese reading.

Line-oriented blocks are fine with CJK — the numbered request-flow list, the project-structure tree — because nothing to the right of the Chinese has to line up. Translate those normally.

Verify before committing. The check that matters is not column math; it's whether any line inside a fenced block has a vertical border to the *right* of CJK text:

```bash
python3 -c "
import sys, unicodedata
FENCE = chr(96) * 3
def wide(c): return unicodedata.east_asian_width(c) in 'WF'
for path in sys.argv[1:]:
    bad, inside = [], False
    for n, line in enumerate(open(path), 1):
        line = line.rstrip('\n')
        if line.lstrip().startswith(FENCE):
            inside = not inside
        elif inside and any(wide(c) for c in line):
            last = max(i for i, c in enumerate(line) if wide(c))
            if any(c in '|│' for c in line[last:]):
                bad.append((n, line))
    print(path + ': ' + ('OK' if not bad else str(len(bad)) + ' line(s) with CJK inside box art'))
    for n, line in bad: print('  ' + str(n) + ': ' + line)
" i18n/zh-Hans/docs/architecture.md i18n/zh-Hans/README.md i18n/zh-Hant/docs/architecture.md i18n/zh-Hant/README.md i18n/ja/docs/architecture.md i18n/ja/README.md i18n/ko/docs/architecture.md i18n/ko/README.md
```

It deliberately ignores markdown tables, which sit outside code fences, and trailing CJK comments in tree diagrams like `+-- app/services/   # 消息适配器`, where nothing to the right needs to align.
