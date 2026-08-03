# 아키텍처

<p align="center"><sub>
  <a href="../../../docs/architecture.md">English</a> |
  <a href="../../zh-Hans/docs/architecture.md">简体中文</a> |
  <a href="../../zh-Hant/docs/architecture.md">繁體中文</a> |
  <a href="../../ja/docs/architecture.md">日本語</a> |
  한국어
</sub></p>

---

## 개요
<p align="center">
   <img width="900" height="490" alt="전체 아키텍처" src="https://github.com/user-attachments/assets/cdd3bcc0-ece8-48ab-9631-0006513cb5a8" />
</p>

AI Conversation Bridge는 AI 기반 오케스트레이션으로 기업용 메시징 플랫폼을 Workday에 연결하는 참조 아키텍처입니다. APJ(아시아 태평양 및 일본) 지역의 네 가지 핵심 과제를 다룹니다.

1. **규제 제한** — 중국 규제가 해외 호스팅 LLM을 차단합니다
2. **언어/맥락 격차** — 엔터프라이즈 LLM이 고객 고유 전문 용어를 잘 다루지 못합니다
3. **슈퍼 앱 중심 환경** — 중국의 직원은 WeChat(위챗)을, 일본은 LINE을, 한국은 KakaoTalk(카카오톡)을 사용합니다
4. **Android 앱 이용 불가** — Google Play 스토어가 중국에서 차단됩니다

## 이 저장소가 제공하는 것 / 제공하지 않는 것

### 제공하는 것

- 브릿지 패턴의 참고 구현: 채팅 어댑터 -> Flowise 오케스트레이션 -> MCP 도구 -> Workday 실행 시스템.
- 팀이 안전하게 플로우를 프로토타입할 수 있도록 모의 MCP 서버를 포함한 개발·데모 환경.
- 고객과 파트너가 자체 환경에서 프로덕션 배포를 구축하기 위한 출발점.

### 제공하지 않는 것

- 프로덕션 준비된 Workday MCP 엔드포인트가 아니며, Workday Agent Gateway를 대체하지 않습니다.
- 단일 릴리스로 제공되는 완전한 멀티 플랫폼 어댑터 세트가 아닙니다.
- Flowise의 관리형 런타임이나 LLM 호스팅이 아닙니다.

## 시스템 아키텍처

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

> **범례:** 위 다이어그램의 상자 안 라벨은 GitHub에서 고정폭 렌더링이 깨지지 않도록 영문 그대로 두었습니다. 각 라벨의 한국어 의미는 아래와 같습니다.

| 다이어그램 라벨 | 한국어 의미 |
| --- | --- |
| Chat Platform (External) | 채팅 플랫폼 (외부) |
| Chat Connector | 채팅 커넥터 |
| Flowise (The Core) | Flowise (핵심) |
| MCP Server (Workday) | MCP 서버 (Workday) |
| Webhook adapter / Message routing / Response delivery | Webhook 어댑터 / 메시지 라우팅 / 응답 전달 |
| LLM orchestration / Intent recognition / Jargon translation | LLM 오케스트레이션 / 의도 인식 / 전문 용어 변환 |
| Tool execution / Workday APIs / Mock data (dev) | 도구 실행 / Workday API / 모의 데이터 (개발) |

## 구성 요소 상세

### 채팅 커넥터 (`chat-connector/`)

가볍고 무상태인 Flask 애플리케이션으로, 다음을 수행합니다.

- 메시징 플랫폼에서 Webhook을 수신합니다
- 사용자의 메시지와 신원 정보를 추출합니다
- 메시지를 Flowise로 전달합니다
- AI 응답을 사용자에게 다시 보냅니다

커넥터에는 **비즈니스 로직이 없습니다** — 순수 어댑터입니다. 새 채팅 플랫폼을 추가하려면 AI 파이프라인을 바꾸지 않고 서비스 파일과 라우트만 추가하면 됩니다. 동일 배포에서 여러 채널 커넥터를 동시에 활성화할 수 있습니다. 예를 들어 LINE WORKS와 DingTalk(딩톡)이 공유 Flowise/OpenRouter 백엔드로 동시에 연결될 수 있습니다.

외부 메시징 플랫폼에서 Webhook을 수신하므로, 채팅 커넥터는 HTTPS 엔드포인트가 있는 **공개 접근 가능한 환경에 반드시 배포되어야 합니다**. Google Cloud Run이 참고 예시이지만, 공개 URL을 제공하는 어떤 컨테이너 플랫폼이든 가능합니다(AWS App Runner, Azure Container Apps, Alibaba Cloud Elastic Container Instance, Tencent Kubernetes Engine 등).

**런타임:** Python / Gunicorn / Cloud Run (또는 동등한 공개 접근 가능한 컨테이너 플랫폼)

### Flowise (`flowise/`)

실제 "브릿지 계층" — 다음을 수행하는 Flowise 플로우입니다.

- 채팅 커넥터에서 메시지를 수신합니다
- 고객이 선택한 LLM으로 처리합니다
- 의도를 인식하고 전문 용어를 변환합니다
- MCP를 통해 Workday 도구를 호출합니다
- 포맷된 응답을 반환합니다

Flowise는 고객이 자체 클라우드 환경에서 관리합니다. 이 프로젝트는 Flowise 런타임이 아니라 플로우 템플릿을 제공합니다. Flowise를 자체 호스팅하는 경우, 채팅 커넥터가 예측 API에 도달할 수 있도록 **공개 접근 가능한 인프라**에 배포해야 합니다.

**런타임:** 고객이 관리하는 Flowise 인스턴스 (클라우드, 또는 공개 접근 가능한 인프라에 자체 호스팅)

### MCP 서버 (`mcp-demo-server/`)

이 프로젝트에는 개발·테스트용 모의 Workday 도구와 샘플 데이터가 포함된 데모 MCP 서버가 있습니다. 채팅 커넥터와 마찬가지로, Flowise가 접근할 수 있도록 데모 서버도 **클라우드 환경에 배포되어야 합니다**(예: Google Cloud Run, Alibaba Cloud Elastic Container Instance, Tencent Kubernetes Engine). 공개 URL을 제공하는 어떤 컨테이너 플랫폼이든 가능합니다.

데모 서버에는 **인증이 없으며** 프로덕션 사용에 적합하지 않습니다. 프로덕션에서는 Agent Gateway를 통해 엔터프라이즈급 보안(OAuth 2.1, mTLS, 감사 로그, 네트워크 정책)을 제공하는 **Workday 공식 MCP 엔드포인트**로 교체하세요. Flowise 플로우의 MCP URL도 Agent Gateway URL로 업데이트하세요.

**런타임:** Python / FastMCP / Cloud Run (데모) 또는 Workday Agent Gateway (프로덕션)

## 요청 흐름

```text
1. 사용자가 LINE WORKS 또는 DingTalk에서 "남은 연차가 며칠인가요?"를 보냅니다
   │
2. 채팅 플랫폼이 Webhook을 채팅 커넥터로 POST합니다
   - LINE WORKS: /lineworks/callback (또는 레거시 /callback)
   - DingTalk: /dingtalk/callback
   │
3. 채팅 커넥터가 메시지 + 플랫폼별 세션 ID를 추출하고 Flowise 예측 API를 호출합니다
   │
4. Flowise LLM이 의도를 인식합니다: get_current_user_time_off_balance
   │
5. Flowise MCP 클라이언트가 MCP 서버를 호출합니다 → get_current_user_time_off_balance()
   │
6. MCP 서버가 반환합니다: { vacation: { available: 12, used: 3 } }
   │
7. Flowise LLM이 응답을 포맷합니다: "남은 연차는 12일입니다(총 15일 중 3일 사용)."
   │
8. 채팅 커넥터가 응답을 받아 원래 채팅 플랫폼을 통해 사용자에게 다시 보냅니다
```

## 핵심 설계 원칙

### 명확한 관심사 분리

- **Workday**는 MCP를 통해 안전한 "실행 시스템"으로 유지됩니다
- **고객**이 AI 계층(자체 LLM)과 메시징/UI를 통제합니다
- **브릿지 계층**(Flowise)은 민감 데이터를 저장하지 않고 둘을 연결합니다

### 데이터 주권

고객의 LLM은 자체 환경에서 실행됩니다. 메시지는 자체 인프라를 통해 처리됩니다. 브릿지 계층은 규제 요구사항을 충족하도록 설계되었습니다.

### 플랫폼 독립성

채팅 커넥터 패턴은 어떤 메시징 플랫폼에도 반복 적용할 수 있습니다. Flowise 플로우는 플랫폼별 Webhook이나 응답 로직이 필요 없습니다. 커넥터가 `lineworks:<userId>` 또는 `dingtalk:<conversationId>:<senderStaffId>`와 같은 플랫폼별 세션 ID를 전달하므로, 동시에 동작하는 여러 채팅 채널이 대화 메모리에서 충돌하지 않습니다.

### 프로덕션 보안 강화

이 참조 아키텍처는 기본 보안(Webhook 서명 검증, 입력 길이 제한, 응답 검증)을 구현합니다. 프로덕션 환경에 배포할 때는 속도 제한, PII 처리, 재시도 로직, 신원 매핑, 관찰 가능성, 인프라 선택(공식 Workday MCP 서버, Flowise Cloud Enterprise)에 관한 추가 권장 사항을 [엔터프라이즈 보안 강화 가이드](enterprise-guide.md)에서 확인하세요.
