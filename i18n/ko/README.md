# AI Conversation Bridge

<p align="center"><sub>
  <a href="../../README.md">English</a> |
  <a href="../zh-Hans/README.md">简体中文</a> |
  <a href="../zh-Hant/README.md">繁體中文</a> |
  <a href="../ja/README.md">日本語</a> |
  한국어
</sub></p>

---

기업용 메시징 앱(LINE WORKS, WeChat(위챗), Feishu(페이슈) 등)을 AI 기반 오케스트레이션으로 Workday에 연결하는 참조 아키텍처입니다. 직원이 매일 사용하는 앱 안에서 AI를 이용할 수 있어야 하는 시장을 위해 설계되었습니다.


https://github.com/user-attachments/assets/9b1ea495-5f23-4ae6-b735-18874acdd327



## 왜 만들었는가

기업 AI는 대개 기술 때문에 실패하지 않습니다. 필요한 사람에게 도달하지 못해서 실패합니다.

APJ(아시아 태평양 및 일본) 지역, 특히 중국, 일본, 한국에서는 직원이 AI 도구를 실제로 쓰게 만드는 데 몇 가지 큰 장애가 있습니다.

- **규제 장애:** 중국의 직원에게 미국 호스팅 AI나 LLM을 그대로 쓰게 할 수 없습니다. 미·중 정책 환경이 장벽을 만들고, 현지 규제가 로컬 모델을 요구하는 경우도 있습니다.
- **언어와 맥락:** 글로벌 모델은 회사 고유의 전문 용어나 현지 문화적 뉘앙스를 잘 이해하지 못하는 경우가 많습니다. Golden Week(일본의 골든위크) 기간에 휴가를 요청하는 표현을 AI가 제대로 이해해야 합니다.
- **슈퍼 앱 중심 환경:** 중국의 직원은 WeChat과 Feishu를 일상적으로 사용하고, 일본에서는 LINE, 한국에서는 KakaoTalk(카카오톡)입니다. 수백만 명에게 별도의 업무용 앱을 다운로드하게 하는 방식은 통하지 않습니다.
- **Android 앱 가용성:** Google Play 스토어가 중국에서 차단되어, 상당수 직원이 표준 Workday Android 앱조차 받을 수 없습니다.

결과는? 기업은 Workday를 갖고 AI도 쓰고 싶지만, 가장 필요한 직원은 소외됩니다.

**AI Conversation Bridge는 이 구조를 뒤집습니다.** 직원에게 Workday에 로그인하라고 강요하는 대신, 즐겨 쓰는 채팅 앱에서 Workday를 이용할 수 있게 합니다. 로컬 LLM과 인프라를 쓰므로 지역 규정과 디지털 문화를 존중합니다. 직원이 WeChat에서 메시지를 보내면 AI가 나머지를 처리합니다. Workday는 여전히 안전하고 권위 있는 데이터 소스이지만, 입구는 직원이 이미 있는 곳입니다.

APJ를 염두에 두고 만들었지만, 자체 LLM이나 채팅 플랫폼을 쓰고 싶은 곳이라면 어디서든 이 패턴이 통합니다.



## 아키텍처

```text
채팅 앱  ←→  채팅 커넥터  ←→  Flowise (브릿지 계층)  ←→  MCP 서버  ←→  Workday
```

프로젝트는 세 가지 핵심으로 구성됩니다. **Flowise는 두뇌입니다** — LLM에 연결하고, 사용자가 원하는 것을 파악하며, MCP를 통해 Workday 도구를 호출합니다. 나머지 두 구성 요소는 귀와 손 역할을 합니다. 채팅 커넥터는 채팅 앱의 메시지를 듣고, MCP 서버는 Workday에서 작업을 실행합니다.

*(적용 범위와 용도에 대한 자세한 내용은 [docs/architecture.md](docs/architecture.md)를 참고하세요.)*


| 구성 요소 | 역할 | 위치 |
| --- | --- | --- |
| **Flowise 플로우** | LLM 오케스트레이션, 의도 인식, MCP 도구 호출을 담당합니다. | [flowise/](../../flowise/) |
| **채팅 커넥터** | 채팅 플랫폼에서 메시지를 받고 AI 응답을 다시 보내는 양방향 어댑터입니다. | [chat-connector/](../../chat-connector/) |
| **데모 MCP 서버** | 테스트·개발용 모의 Workday 도구입니다. (프로덕션에서는 Workday Agent Gateway로 교체하세요.) | [mcp-demo-server/](../../mcp-demo-server/) |


## 빠른 시작

### 필요한 것

- 공개 HTTPS 엔드포인트를 제공하는 컨테이너 호스팅 플랫폼([Google Cloud Run](https://cloud.google.com/run) 등)
- [Flowise](https://flowiseai.com/) 인스턴스(클라우드 또는 자체 호스팅, 공개 접근 가능해야 함)
- LINE WORKS 봇 자격 증명 및/또는 DingTalk(딩톡) 로봇 접근 권한(채팅 커넥터용)

*참고: 모든 구성 요소는 공개 접근 가능한 클라우드 환경에 배포해야 합니다. 이 예시에서는 Google Cloud Run을 사용하지만, AWS App Runner, Azure Container Apps, Alibaba Cloud Elastic Container Instance, Tencent Kubernetes Engine 등 어떤 컨테이너 플랫폼이든 가능합니다.*

### 1. 저장소 클론

```bash
git clone https://github.com/your-org/ai-conversation-bridge.git
cd ai-conversation-bridge
```

### 2. 데모 MCP 서버 배포

```bash
gcloud run deploy mcp-demo-server \
  --source mcp-demo-server
```

> **프로덕션 환경에 배포하시나요?** 실제 엔터프라이즈급 보안과 인증을 위해 Agent Gateway를 통해 이 데모 서버를 **Workday 공식 MCP 엔드포인트**로 교체하세요. Flowise 플로우의 MCP 설정도 잊지 말고 업데이트하세요!

### 3. Flowise 플로우 가져오기

1. Flowise 인스턴스를 엽니다.
2. **Agent Flows** → **Add New** → **Settings**(⚙️) → **Load Agentflow**로 이동합니다.
3. `flowise/flows/workday-mcp-agent.json`을 가져옵니다.
4. LLM 자격 증명을 설정합니다.
5. Agent 노드의 Custom MCP 도구에서 MCP 서버 URL을 배포한 데모 서버의 URL로 변경합니다(예: `https://mcp-demo-server-abc123.us-west1.run.app/mcp`).

*(도움이 더 필요하신가요? [flowise/README.md](flowise/README.md)를 참고하세요.)*

### 4. 채팅 커넥터 배포

```bash
gcloud run deploy chat-connector \
  --source chat-connector
```

> **중요:** 배포 후 Cloud Run 콘솔에서 환경 변수를 설정하는 것을 잊지 마세요! AI 제공자(`AI_PROVIDER`, `FLOWISE_API_URL` 등)와 채팅 채널을 설정해야 합니다. 전체 변수 목록은 `chat-connector/.env.example`을 참고하세요.

### 5. 채팅 채널 연결

채팅 플랫폼의 콜백 URL을 채널별 엔드포인트로 설정하세요.

- LINE WORKS: `https://chat-connector-abc123.us-west1.run.app/lineworks/callback`
- DingTalk HTTP 로봇: `https://chat-connector-abc123.us-west1.run.app/dingtalk/callback`

기존 배포와의 호환을 위해 레거시 `/callback` 경로는 LINE WORKS 별칭으로 계속 허용됩니다.

## AI 제공자

채팅 커넥터는 기본적으로 두 가지 AI 백엔드를 지원합니다. `CHAT_PROVIDER`는 폴백으로 여전히 허용되지만, 새 배포에서는 `AI_PROVIDER`를 사용하세요.


| 제공자 | 사용 시점 | 설정 |
| --- | --- | --- |
| **Flowise** (기본값) | 프로덕션 — 완전한 오케스트레이션과 MCP 도구 호출을 제공합니다. | `AI_PROVIDER=flowise` |
| **OpenRouter** | 데모/실험 — Flowise 없이 임의 LLM으로 빠르게 테스트하기에 적합합니다. | `AI_PROVIDER=openrouter` |


## 데모 MCP 도구

데모 MCP 서버에는 전체 파이프라인을 테스트할 수 있도록 모의 Workday 도구와 데이터가 포함되어 있습니다. 프로덕션 준비가 되면 Workday 공식 MCP 엔드포인트로 교체하면 됩니다.


| 도구 | 역할 |
| --- | --- |
| `find_employee_id_by_name` | 직원 이름으로 워커 ID를 조회합니다 |
| `get_current_user_info` | 현재 사용자의 프로필을 가져옵니다 |
| `get_current_user_time_off_balance` | 현재 사용자의 휴가 잔여일수를 가져옵니다 |
| `get_current_user_time_off_history` | 현재 사용자의 휴가 신청 이력을 가져옵니다 |
| `get_time_off_balance` | ID로 지정한 워커의 휴가 잔여일수를 가져옵니다 |
| `get_direct_reports` | 관리자의 직속 부하 직원을 나열합니다 |
| `get_more_employee_data` | 확장된 직원 데이터를 가져옵니다 |
| `get_my_time_off_eligibility` | 현재 사용자가 신청할 수 있는 휴가 유형을 확인합니다 |
| `get_personal_information` | 개인 정보(주소, 비상 연락처)를 가져옵니다 |
| `get_today_date_and_day_of_week` | 오늘 날짜와 요일을 가져옵니다 |
| `request_my_time_off` | 현재 사용자의 휴가 신청을 제출합니다 |


*참고로, 모의 데이터에는 중국, 일본, 한국의 워커가 포함되어 있으며, 이름과 통화가 현지화되어 있습니다!*

## 프로젝트 구조

```text
ai-conversation-bridge/
+-- chat-connector/          # Webhook 어댑터 (Flask, Python)
|   +-- app/services/        # 메시징 어댑터 (LINE WORKS, DingTalk) + AI 클라이언트
|   +-- Dockerfile
|   +-- .env.example
+-- flowise/                 # 플로우 템플릿 (핵심 브릿지 로직)
|   +-- flows/               # 내보낼 수 있는 Flowise 플로우 JSON 파일
|   +-- screenshots/
+-- mcp-demo-server/         # 데모 Workday MCP 서버
|   +-- mock_data/           # 워커, 휴가, 급여 샘플 데이터
|   +-- Dockerfile
|   +-- .env.example
+-- docs/                    # 아키텍처 및 설정 문서
+-- scripts/                 # 로컬 개발 설정 (setup.sh) 및 클라우드 배포 (deploy-cloud-run.sh)
+-- docker-compose.yml       # 컨테이너 빌드/테스트 유틸리티
+-- .github/                 # 이슈 템플릿, PR 템플릿
```

## 문서

- [아키텍처](docs/architecture.md) — 상세 시스템 설계와 요청 흐름
- [설정 가이드](docs/setup-guide.md) — 각 구성 요소의 단계별 설정
- [엔터프라이즈 보안 강화 가이드](docs/enterprise-guide.md) — 프로덕션을 위한 보안, 안정성, 운영 권장 사항
- [Flowise 구성](flowise/README.md) — 플로우 템플릿 가져오기 및 구성 방법
- [기여 가이드](CONTRIBUTING.md) — 이 프로젝트에 기여하는 방법

## 라이선스

이 프로젝트는 Apache License 2.0으로 라이선스됩니다 — 자세한 내용은 [LICENSE](../../LICENSE)를 참고하세요.
