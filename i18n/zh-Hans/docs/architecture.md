# 架构

<p align="center"><sub>
  <a href="../../../docs/architecture.md">English</a> |
  简体中文 |
  <a href="../../zh-Hant/docs/architecture.md">繁體中文</a> |
  <a href="../../ja/docs/architecture.md">日本語</a> |
  <a href="../../ko/docs/architecture.md">한국어</a>
</sub></p>

---

## 概述
<p align="center">
   <img width="900" height="490" alt="高层架构" src="https://github.com/user-attachments/assets/cdd3bcc0-ece8-48ab-9631-0006513cb5a8" />
</p>

AI Conversation Bridge 是一套参考架构，通过由 AI 驱动的编排能力，将企业消息平台连接到 Workday。它针对亚太及日本（APJ）地区的四项关键挑战：

1. **监管限制** —— 中国法规限制使用境外托管的 LLM
2. **语言与语境差异** —— 企业 LLM 难以妥善处理客户专有术语
3. **超级应用主导** —— 中国的工作者使用 WeChat（微信），日本使用 LINE，韩国使用 KakaoTalk（韩国主流聊天应用）
4. **Android 应用无法获取** —— Google Play Store（谷歌应用商店）在中国无法访问

## 本仓库是什么 / 不是什么

### 本仓库是什么

- 桥接模式的参考实现：聊天适配器 -> Flowise 编排 -> MCP 工具 -> Workday 执行系统。
- 一个附带模拟 MCP 服务器的开发与演示环境，便于团队安全地验证流程原型。
- 供客户与合作伙伴在自有环境中构建生产部署的起点。

### 本仓库不是什么

- 不是生产就绪的 Workday MCP 端点，也不能替代 Workday Agent Gateway。
- 不是在单个版本中提供的完整多平台适配器套件。
- 不是 Flowise 的托管运行时，也不提供 LLM 托管服务。

## 系统架构

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

> **图例：** 上图中的框线标签保持英文原样，以确保在 GitHub 上的等宽渲染不会错位；对应中文含义如下。

| 图中标签 | 中文含义 |
| --- | --- |
| Chat Platform (External) | 聊天平台（外部） |
| Chat Connector | 聊天连接器 |
| Flowise (The Core) | Flowise（核心） |
| MCP Server (Workday) | MCP 服务器（Workday） |
| Webhook adapter / Message routing / Response delivery | Webhook 适配器 / 消息路由 / 响应投递 |
| LLM orchestration / Intent recognition / Jargon translation | LLM 编排 / 意图识别 / 术语转换 |
| Tool execution / Workday APIs / Mock data (dev) | 工具执行 / Workday API / 模拟数据（开发） |

## 组件详解

### 聊天连接器（`chat-connector/`）

一个轻量、无状态的 Flask 应用，负责：

- 接收来自消息平台的 Webhook
- 提取用户消息与身份信息
- 将消息转发给 Flowise
- 将 AI 响应回传给用户

连接器**不包含任何业务逻辑** —— 它纯粹是一个适配器。新增聊天平台只需添加一个新的服务文件和路由，无需改动 AI 流水线。同一部署中可以同时启用多个渠道连接器；例如，LINE WORKS 与 DingTalk（钉钉）可以同时接入共享的 Flowise/OpenRouter 后端。

由于需要接收来自外部消息平台的 Webhook，聊天连接器**必须部署到面向公网的环境**，并提供 HTTPS 端点。本文以 Google Cloud Run 作为参考示例，但任何能提供公网 URL 的容器平台均可，例如 AWS App Runner、Azure Container Apps、Alibaba Cloud Elastic Container Instance（阿里云弹性容器实例）、Tencent Kubernetes Engine（腾讯云容器服务）等。

**运行环境：** Python / Gunicorn / Cloud Run（或同等的面向公网的容器平台）

### Flowise（`flowise/`）

真正的“桥接层” —— 一个 Flowise 流程，负责：

- 接收来自聊天连接器的消息
- 通过客户自行选择的 LLM 进行处理
- 识别意图并转换专有术语
- 通过 MCP 调用 Workday 工具
- 返回格式化后的响应

Flowise 由客户在自有云环境中管理。本项目提供流程模板，而非 Flowise 运行时。如果自托管 Flowise，则必须将其部署在**面向公网的基础设施**上，以便聊天连接器能够访问其预测 API。

**运行环境：** 客户自行管理的 Flowise 实例（云端，或自托管在面向公网的基础设施上）

### MCP 服务器（`mcp-demo-server/`）

本项目提供一个演示 MCP 服务器，内置模拟 Workday 工具与示例数据，供开发与测试使用。与聊天连接器一样，演示服务器也应**部署到云环境**（例如 Google Cloud Run、Alibaba Cloud Elastic Container Instance、Tencent Kubernetes Engine），以便 Flowise 能够访问。任何提供公网 URL 的容器平台均可。

演示服务器**不包含任何身份验证**，不适用于生产环境。在生产环境中，请通过 Agent Gateway 将其替换为 **Workday 官方 MCP 端点**，以获得企业级安全能力（OAuth 2.1、mTLS、审计日志、网络策略）。同时请将 Flowise 流程中的 MCP URL 更新为 Agent Gateway 的地址。

**运行环境：** Python / FastMCP / Cloud Run（演示）或 Workday Agent Gateway（生产）

## 请求流程

```text
1. 用户在 LINE WORKS 或 DingTalk 中发送“我还有多少天年假？”
   │
2. 聊天平台将 Webhook POST 到聊天连接器
   - LINE WORKS：/lineworks/callback（或旧版 /callback）
   - DingTalk：/dingtalk/callback
   │
3. 聊天连接器提取消息 + 按平台隔离的会话 ID，调用 Flowise 预测 API
   │
4. Flowise LLM 识别意图：get_current_user_time_off_balance
   │
5. Flowise MCP 客户端调用 MCP 服务器 → get_current_user_time_off_balance()
   │
6. MCP 服务器返回：{ vacation: { available: 12, used: 3 } }
   │
7. Flowise LLM 格式化响应：“您还有 12 天年假（共 15 天，已使用 3 天）”
   │
8. 聊天连接器收到响应，通过原聊天平台回传给用户
```

## 核心设计原则

### 清晰的关注点分离

- **Workday** 通过 MCP 始终作为安全的“执行系统”
- **客户** 掌控 AI 层（自有 LLM）以及消息与界面
- **本桥接层**（Flowise）连接两者，且不存储敏感数据

### 数据主权

客户的 LLM 运行在自有环境中，消息也在自有基础设施内处理。本桥接层在设计上即满足监管要求。

### 平台无关

聊天连接器模式可复用于任何消息平台。Flowise 流程无需编写特定平台的 Webhook 或回复逻辑；连接器会传入按平台隔离的会话 ID，例如 `lineworks:<userId>` 或 `dingtalk:<conversationId>:<senderStaffId>`，从而确保同时运行的多个聊天渠道不会在对话记忆中相互冲突。

### 生产环境强化

本参考架构实现了基线安全措施（Webhook 签名验证、输入长度限制、响应校验）。对于生产部署，请参阅[企业强化指南](enterprise-guide.md)，其中提供了关于限流、PII 处理、重试逻辑、身份映射、可观测性以及基础设施选型（Workday 官方 MCP 服务器、Flowise Cloud Enterprise）的更多建议。
