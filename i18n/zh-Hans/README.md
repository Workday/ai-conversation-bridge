# AI Conversation Bridge

<p align="center"><sub>
  <a href="../../README.md">English</a> |
  简体中文 |
  <a href="../zh-Hant/README.md">繁體中文</a> |
  <a href="../ja/README.md">日本語</a> |
  <a href="../ko/README.md">한국어</a>
</sub></p>

---

一套参考架构，借助由 AI 驱动的编排能力，将 LINE WORKS、WeChat（微信）、Feishu（飞书）等企业消息应用连接到 Workday。它专为这样的市场而设计：让用户在他们日常使用的应用中就能用上 AI。


https://github.com/user-attachments/assets/9b1ea495-5f23-4ae6-b735-18874acdd327



## 我们为什么要做这件事

企业 AI 的失败通常不是因为技术，而是因为它没有触达真正需要它的人。

在亚太及日本（APJ）地区，尤其是中国、日本和韩国，要让用户真正用起 AI 工具，会遇到几个主要障碍：

- **监管障碍：** 您无法直接让中国的员工使用美国托管的 AI 或 LLM。中美政策环境为此设置了障碍，而且当地法规有时要求使用本地模型。
- **语言与语境：** 全球通用模型往往读不懂企业专有术语，也把握不住当地的文化细节。当员工说要请 Golden Week（黄金周）的假时，AI 必须真正听懂这句话。
- **超级应用的主导地位：** 中国的用户离不开 WeChat 和 Feishu，日本是 LINE，韩国是 KakaoTalk（韩国主流聊天应用）。要求数百万人再去下载一个独立的企业应用，根本行不通。
- **Android 应用可用性：** Google Play Store（谷歌应用商店）在中国无法访问，这意味着很大一部分员工甚至下载不到 Workday 官方的 Android 应用。

结果呢？企业已经拥有 Workday，也想用上 AI，但最需要它的那些员工却被排除在外。

**AI Conversation Bridge 把这件事反过来做。** 它不再要求用户登录 Workday，而是把 Workday 直接带进他们最常用的聊天应用。它使用本地 LLM 与本地基础设施，因此既符合区域法规，也贴合当地的数字文化。用户只需在 WeChat 里发一条消息，剩下的交给 AI。Workday 依然是安全的权威数据源，但入口就在用户已经身处的地方。

虽然我们是针对 APJ 地区设计的，但只要您希望使用自有的 LLM 或聊天平台，这套模式在任何市场都同样适用。



## 架构

```text
聊天应用  ←→  聊天连接器  ←→  Flowise（桥接层）  ←→  MCP 服务器  ←→  Workday
```

项目包含三大部分。**Flowise 是大脑** —— 它连接 LLM，判断用户想要什么，并通过 MCP 调用 Workday 工具。另外两个组件则充当它的耳朵和双手：聊天连接器负责监听来自聊天应用的消息，MCP 服务器负责在 Workday 中执行操作。

*（关于边界与预期用法的更多细节，请参阅 [docs/architecture.md](docs/architecture.md)。）*


| 组件 | 作用 | 位置 |
| --- | --- | --- |
| **Flowise 流程** | 负责 LLM 编排、意图识别与 MCP 工具调用。 | [flowise/](../../flowise/) |
| **聊天连接器** | 双向适配器，接收来自聊天平台的消息，并将 AI 的响应回传。 | [chat-connector/](../../chat-connector/) |
| **演示 MCP 服务器** | 用于测试与开发的模拟 Workday 工具。（生产环境请替换为 Workday Agent Gateway。） | [mcp-demo-server/](../../mcp-demo-server/) |


## 快速开始

### 前置条件

- 一个提供公网 HTTPS 端点的容器托管平台（例如 [Google Cloud Run](https://cloud.google.com/run)）
- 一个 [Flowise](https://flowiseai.com/) 实例（云端或自托管均可，只要面向公网）
- LINE WORKS 机器人凭据和/或 DingTalk（钉钉）机器人访问权限（供聊天连接器使用）

*说明：所有组件都需要部署到面向公网的云环境。以下示例使用 Google Cloud Run，但任何容器平台均可，例如 AWS App Runner、Azure Container Apps、Alibaba Cloud Elastic Container Instance（阿里云弹性容器实例）、Tencent Kubernetes Engine（腾讯云容器服务）等。*

### 1. 克隆仓库

```bash
git clone https://github.com/your-org/ai-conversation-bridge.git
cd ai-conversation-bridge
```

### 2. 部署演示 MCP 服务器

```bash
gcloud run deploy mcp-demo-server \
  --source mcp-demo-server
```

> **准备上生产环境？** 请通过 Agent Gateway 把这个演示服务器替换为 **Workday 官方 MCP 端点**，以获得真正的企业级安全与身份验证能力。别忘了同步更新 Flowise 流程中的 MCP 配置！

### 3. 导入 Flowise 流程

1. 打开您的 Flowise 实例。
2. 依次进入 **Agent Flows** → **Add New** → **Settings**（⚙️）→ **Load Agentflow**。
3. 导入 `flowise/flows/workday-mcp-agent.json`。
4. 配置您的 LLM 凭据。
5. 在 Agent 节点的 Custom MCP 工具中，把 MCP 服务器 URL 更新为您已部署的演示服务器地址（例如 `https://mcp-demo-server-abc123.us-west1.run.app/mcp`）。

*（需要更多帮助？请参阅 [flowise/README.md](flowise/README.md)。）*

### 4. 部署聊天连接器

```bash
gcloud run deploy chat-connector \
  --source chat-connector
```

> **重要：** 部署完成后，别忘了在 Cloud Run 控制台中设置环境变量！您需要配置 AI 提供方（例如 `AI_PROVIDER` 和 `FLOWISE_API_URL`），以及各聊天渠道的相关设置。完整的变量列表请参阅 `chat-connector/.env.example`。

### 5. 接入聊天渠道

将聊天平台的回调 URL 设置为对应渠道的端点：

- LINE WORKS：`https://chat-connector-abc123.us-west1.run.app/lineworks/callback`
- DingTalk HTTP 机器人：`https://chat-connector-abc123.us-west1.run.app/dingtalk/callback`

为兼容既有部署，旧版 `/callback` 路径仍作为 LINE WORKS 的别名予以保留。

## AI 提供方

聊天连接器开箱即支持两种 AI 后端。`CHAT_PROVIDER` 仍作为回退选项保留，但新部署应使用 `AI_PROVIDER`。


| 提供方 | 适用场景 | 配置 |
| --- | --- | --- |
| **Flowise**（默认） | 生产环境 —— 提供完整的编排能力与 MCP 工具调用。 | `AI_PROVIDER=flowise` |
| **OpenRouter** | 演示与实验 —— 无需搭建 Flowise，即可用任意 LLM 快速测试。 | `AI_PROVIDER=openrouter` |


## 演示 MCP 工具

演示 MCP 服务器内置了模拟 Workday 工具与数据，方便您测试整条流水线。当您准备进入生产环境时，只需将其替换为 Workday 官方 MCP 端点。


| 工具 | 作用 |
| --- | --- |
| `find_employee_id_by_name` | 按姓名查询员工的工作者 ID |
| `get_current_user_info` | 获取当前用户的档案信息 |
| `get_current_user_time_off_balance` | 获取当前用户的假期余额 |
| `get_current_user_time_off_history` | 获取当前用户的休假申请历史 |
| `get_time_off_balance` | 按 ID 获取任意工作者的假期余额 |
| `get_direct_reports` | 列出某位管理者的直接下属 |
| `get_more_employee_data` | 获取扩展的员工数据 |
| `get_my_time_off_eligibility` | 查询当前用户可申请的休假类型 |
| `get_personal_information` | 获取个人信息（地址、紧急联系人） |
| `get_today_date_and_day_of_week` | 获取当前日期与时间 |
| `request_my_time_off` | 为当前用户提交休假申请 |


*有趣的是：模拟数据涵盖了中国、日本和韩国的员工，姓名与货币都做了本地化处理！*

## 项目结构

```text
ai-conversation-bridge/
+-- chat-connector/          # Webhook 适配器（Flask、Python）
|   +-- app/services/        # 消息适配器（LINE WORKS、DingTalk）+ AI 客户端
|   +-- Dockerfile
|   +-- .env.example
+-- flowise/                 # 流程模板（核心桥接逻辑）
|   +-- flows/               # 可导出的 Flowise 流程 JSON 文件
|   +-- screenshots/
+-- mcp-demo-server/         # 演示用 Workday MCP 服务器
|   +-- mock_data/           # 员工、休假与薪酬示例数据
|   +-- Dockerfile
|   +-- .env.example
+-- docs/                    # 架构与设置文档
+-- scripts/                 # 本地开发设置（setup.sh）与云端部署（deploy-cloud-run.sh）
+-- docker-compose.yml       # 容器构建/测试工具
+-- .github/                 # Issue 模板、PR 模板
```

## 文档

- [架构](docs/architecture.md) —— 详细的系统设计与请求流程
- [设置指南](docs/setup-guide.md) —— 各组件的分步设置说明
- [企业强化指南](docs/enterprise-guide.md) —— 面向生产环境的安全性、可靠性与运维建议
- [Flowise 配置](flowise/README.md) —— 如何导入并配置流程模板
- [贡献指南](CONTRIBUTING.md) —— 如何为本项目做贡献

## 许可证

本项目基于 Apache License 2.0 授权 —— 详见 [LICENSE](../../LICENSE)。
