# Model Room v1.0 · Windows 사용 안내

[简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md) · [English](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

**사용자, 동료, 여러 AI가 함께 참여하는 그룹 채팅입니다.** 이름 있는 채팅방, 모델 간 토론, 사람의 중간 발언, LAN 브라우저 참여, 기록 내보내기를 지원하며 기존 3열 구성을 유지합니다.



## 공개 버전 v1.0 — 현재 Windows x64만 제공

**일반 사용자는 이 저장소의 Releases에서 `ModelRoom-v1.0-Windows-x64.exe`를 내려받아 더블 클릭하세요. Python, pip, Tkinter, Pillow를 설치할 필요가 없습니다.** EXE에 실행 환경이 포함되어 있으며 최초 실행 시 로컬 캐시로 풉니다. Python을 추가 다운로드하거나 PATH의 Python에 의존하지 않습니다.

Windows ZIP에는 같은 EXE와 5개 언어 안내서, 라이선스가 있습니다. GitHub의 **Code → Download ZIP**과 `ModelRoom-v1.0-Source.zip`은 개발용 소스이며 일반 사용자의 실행 파일 다운로드가 아닙니다. 소스 실행·빌드에만 Python이 필요합니다. 바이너리는 **Windows 10/11 x64**를 지원하며 Linux/macOS 버전은 아직 제공하지 않습니다.

대화에는 본인의 API 인증 정보 또는 별도로 설치·로그인한 로컬 Agent가 필요합니다. 모델 가중치나 유료 계정은 포함하지 않습니다. 기존 로컬 대화와 설정은 이어서 사용합니다.

**라이선스: [MIT](LICENSE)**. [배포 안내](RELEASE_NOTES.md), [기여 안내](CONTRIBUTING.md), [타사 라이선스](THIRD_PARTY_NOTICES.md)도 확인하세요. `release-windows.ps1`로 배포 파일을 만들 수 있습니다. GitHub 워크플로는 EXE를 빌드하지만 Release를 자동 공개하지는 않습니다.


## 전체 채팅 배경, 프로필 및 일상 설정

배경은 말풍선 뒤의 전체 대화 영역을 덮으며 스크롤과 창 크기 변경에도 맞춰집니다. 사이드바, 그룹 상세, 헤더, 입력 영역은 읽기 쉬운 단색 패널을 유지합니다. 외관에서 **채우기**(가장자리가 잘릴 수 있음), **맞추기**(전체 이미지와 여백), **바둑판식**을 고르고 강도를 0~100%로 설정합니다. 말풍선과 이름 배경은 읽기 쉽게 유지하며 글꼴 크기는 10~18입니다. 배경은 호스트에만 적용됩니다.

설정은 **일반 / 연결 설정 / 화면 모양 / 채팅 및 입력 / 데이터 및 저장소 / 정보** 6개 항목입니다. 일반에서 기본 닉네임, 그룹별 닉네임, 프로필 사진을 설정합니다. 그룹 닉네임을 비우면 기본값, 둘 다 비우면 현재 언어의 나 표시를 사용합니다. 최대 32자입니다. 사진은 중앙을 원형으로 자르고 메타데이터를 제거해 로컬 저장합니다. 새 메시지는 당시 이름과 사진을 기록하므로 이후 변경으로 저장된 이름이 바뀌지 않습니다. 이전 형식의 기록은 현재 프로필을 사용합니다. 내부 라우팅 ID는 유지됩니다.

LAN 참여자는 공유된 메시지의 이름과 작은 PNG 사진을 볼 수 있습니다. 로컬 경로를 보내거나 사진을 AI 모델에 전달하지 않습니다. 이름은 텍스트 문맥과 기록 내보내기에 사용합니다. 내보내기에는 사진 파일이나 연결 키를 포함하지 않습니다.

채팅 및 입력에는 Enter로 보내기, 메시지 시간 표시, 자동 스크롤, 기본 토론 회차가 있습니다. Enter 전송을 끄면 Ctrl+Enter로 보내고 Shift+Enter는 항상 줄 바꿈입니다. 회차는 시작과 그룹 전환 시 적용하며 입력 영역에서 임시 변경할 수 있습니다. 데이터 및 저장소에서는 폴더 열기·경로 복사·기록 내보내기를 제공합니다. 적용은 같은 페이지를 유지하고 확인은 저장 후 닫으며 취소는 미적용 설정을 버립니다. 연결은 전용 저장 버튼으로 저장합니다.

구성은 [Signal 프로필](https://support.signal.org/hc/en-us/articles/360007059952-Edit-my-Profile), [글꼴 크기](https://support.signal.org/hc/en-us/articles/360049670791-Font-Size-Options), [Telegram 배경](https://telegram.org/blog/animated-backgrounds)을 참고했습니다. 실행에 필요한 종속 제품은 아닙니다.

## 설정 화면 수정

설정의 불리언 옵션을 왼쪽 설명과 오른쪽 스마트폰 형태 스위치로 바꿨습니다. 시작 시 로컬 Agent 감지와 다크 모드가 해당됩니다. 클릭으로 전환하며 Tab으로 이동, Space/Enter로 전환, 좌우 키로 끄기/켜기를 선택합니다. 채팅 화면의 기존 조작 배치는 유지됩니다.

구분선 아래 오른쪽 하단에 **적용 / 확인 / 취소 또는 닫기**를 고정했습니다. 적용은 일반·외관·채팅 설정을 저장하고 현재 설정 페이지와 미저장 연결 입력을 유지합니다. 확인은 저장 후 닫습니다. 취소, Esc, 창 닫기는 적용하지 않은 설정 변경을 버립니다. 이미 적용한 설정과 명시적으로 저장한 연결은 유지됩니다. 연결은 각 페이지 안의 저장 버튼으로 저장합니다. 미저장 키는 메모리에만 유지하며 로그나 배포 파일에 쓰지 않습니다.

일반·외관 페이지는 독립적으로 스크롤되며 최소 840 × 560에서도 하단 버튼이 보입니다. 긴 설명은 줄 바꿈하고 선택한 페이지를 강조합니다. 5개 언어와 밝은/어두운 테마를 유지합니다.

## 통합 설정, 다섯 UI 언어, 로컬 Agent

왼쪽 아래 **설정** 또는 `Ctrl+,`로 엽니다.

1. **일반**: 간체·번체 중국어, 영어, 일본어, 한국어를 실제 화면에 적용하고 시작 시 Agent 검색을 설정합니다. 채팅방 이름, 닉네임, 모델 ID와 대화 원문은 바뀌지 않습니다.
2. **연결 설정**: 모델, 검색, 로컬 Codex, 로컬 Agent입니다. 아래의 이전 연결 설정 설명은 이 메뉴 안에 해당합니다.
3. **화면 모양**: 라이트/다크, 강조 색, 로컬 JPG/PNG/WebP/GIF/BMP 이미지, 강도와 초기화를 제공합니다. 3열을 유지하며 전체 대화 영역에 배경을 표시합니다. 이미지는 메타데이터 제거 후 앱 데이터에 복사하며 모델로 업로드하지 않습니다. 적용 시 입력 중인 글과 기록을 보존합니다. 적용해도 미저장 연결 입력은 유지됩니다.

**자동 검색은 설치된 프로그램 경로만 찾습니다. 설치, 로그인, 유료 모델 호출, 자동 참여는 하지 않습니다.** 로컬 Agent에서 검색·선택하고 필요하면 버전을 확인한 뒤 연결을 저장하세요. 발견만으로 인증이나 잔액을 확인하지는 않습니다.

- **Codex**: PATH와 데스크톱 CLI 캐시의 `codex.exe`를 찾습니다. 저장 후 방에 추가할 수 있으며 로그인은 따로 확인합니다.
- **Claude Code**: 네이티브 실행 파일과 설치된 Node.js 패키지로 해석 가능한 npm 래퍼를 지원합니다. 래퍼 스크립트를 셸에서 실행하지 않습니다. 저장 후 AI 참여자로 추가하세요.
- **DeepSeek Harness**: `dsh`의 headless 모드에 stdin으로 발언을 보내고 read-only 및 대화형 승인 거부를 지정합니다. 모델은 Harness 설정을 따릅니다. headless에 `DEEPSEEK_API_KEY`가 필요할 수 있으며 GUI 로그인과 다를 수 있습니다. 필요한 인자를 지원하지 않으면 실패하며 권한을 자동 완화하지 않습니다. 미설치 Agent를 연결됨으로 표시하지 않습니다. [CLI](https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli) · [headless](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/bundle/headless).

LAN H5에서도 다섯 언어를 선택하며 브라우저마다 기억합니다. 대화 원문은 번역하지 않습니다. 데스크톱 배경과 외관은 방문자에게 공유하지 않습니다. 기존 DB에 설정을 저장하고 이전 기록·연결·암호화 키를 유지합니다.

**Harness 호환성:** 데스크톱 패키지와 실행 중인 포터블 버전을 감지하지만 인증 성공을 보장하지는 않습니다. `0.2.1-rc.2` 등 이전 버전에는 필요한 headless 읽기 전용·승인 정책 인수가 없을 수 있습니다. 설치된 CLI 도움말을 확인하고 필요하면 업데이트하세요. 필수 정책 인수를 자동으로 제거하지 않습니다.

## 처음 시작하는 세 단계

1. Windows x64에서 `ModelRoom-v1.0-Windows-x64.exe`를 실행하세요. Python이 포함되어 있습니다. 기존 채팅방과 설정은 이어서 사용하며 프리셋이 기존 연결을 자동으로 덮어쓰지 않습니다.
2. 왼쪽 **연결 설정 → 모델 연결**(연결 설정 → 모델 연결)에서 **빠른 프리셋 → 프리셋 추가**(빠른 프리셋 → 이 프리셋 추가)를 선택하세요. 자신의 키를 넣고 **모델 읽기**(모델 읽기)로 텍스트 채팅 모델을 골라 **연결 저장**(연결 저장)합니다. **다음으로 오른쪽「AI 멤버 관리」에서 모델을 이 방에 추가하고 명단을 저장해야 합니다.** 로컬 Codex만 사용한다면 아래 예시를 참고하세요.
3. **새 채팅방**로 방 이름을 정하고 질문을 입력하세요. **보내기**는 선택된 모델마다 한 번 답하고, **토론 시작**는 입력한 회차만큼 토론합니다. 적은 회차로 연결부터 확인하세요.

설정 창은 세로로 스크롤할 수 있습니다. **공식 문서**은 선택한 프리셋의 공식 문서를 엽니다.

## 연결, 참여자, 사용량의 차이

| 항목 | 의미 | 준비물 |
| --- | --- | --- |
| API 연결 | 주소, 모델, 인증 설정 | 해당 서비스의 키와 사용 가능량 |
| AI 참여자 | 특정 방의 모델 자리 하나 | 저장한 연결. 같은 연결에서 여러 모델 추가 가능 |
| 로컬 Codex | 설치된 Codex CLI 실행 | CLI와 로그인. 현재 Codex 채팅 창을 직접 제어하지 않음 |
| 로컬 Claude Code | 네이티브 Claude Code CLI 실행 | `claude.exe`와 로그인 또는 API 설정 |
| 프리셋 | 공개 주소와 요청 형식 자동 입력 | 키, 계정, 모델 다운로드, 잔액은 제공하지 않음 |

클라우드 모델마다 요청을 보내며 모델 가중치를 이 프로그램에 내려받는 방식이 아닙니다.

## 자주 쓰는 다섯 가지 설정

### 1. DeepSeek

**DeepSeek 공식 → 프리셋 추가**를 선택하고 DeepSeek 플랫폼 키를 입력하세요. **모델 읽기 → 채팅 모델 선택 → 연결 저장** 후 **AI 참여자 관리**에서 방에 추가합니다. 기존 기본 DeepSeek 연결도 그대로 쓸 수 있습니다.

**채팅 테스트**은 과금될 수 있는 실제 요청을 보냅니다. 답변의 **상세**에서 주소, 반환 모델, 시간, 서비스가 보고한 사용량을 확인합니다. **DeepSeek 잔액**는 공식 DeepSeek 주소의 잔액을 조회합니다. [공식 시작 안내](https://api-docs.deepseek.com/)를 참고하세요.

### 2. OpenAI / GPT API

**OpenAI / GPT API**를 선택하고 OpenAI Platform API 키를 넣으세요. 목록에서 Chat Completions를 지원하는 텍스트 모델을 골라 저장하고 방에 추가합니다. 기본 주소는 `https://api.openai.com/v1`입니다.

플랫폼 API 인증 및 사용량 규칙을 따릅니다. **ChatGPT 구독 한도를 API 키 잔액과 같다고 생각하지 마세요.** 프로젝트 권한과 사용 가능량은 플랫폼에서 확인합니다. Responses 전용 모델은 이 어댑터에서 지원하지 않습니다. [공식 API 문서](https://developers.openai.com/api/reference/chat-completions/overview).

### 3. 로컬 Codex

**Codex · 로컬**를 고르면 **로컬 Codex** 탭으로 이동합니다. **자동 검색 → 로그인 확인**(자동 찾기 → 로그인 확인)을 누르세요. 필요하면 **CLI 선택**로 `codex.exe`를 지정합니다. 로그인 전이라면 **로그인 명령 복사**을 눌러 자신의 PowerShell에서 실행하고 로그인하세요. **AI 참여자 관리 → Codex 추가 → 참여자 명단 저장**로 추가합니다.

API 주소는 필요 없습니다. 사용량은 CLI의 ChatGPT 또는 API 키 로그인 방식에 따릅니다. 토론에서는 읽기 전용이며 일반 메시지로 파일을 바꾸려면 프로젝트를 고른 뒤 **Codex 파일 수정 허용**를 명시적으로 켜야 합니다. [공식 인증 설명](https://learn.chatgpt.com/docs/auth).

### 4. Claude / Anthropic API

**Claude / Anthropic API**를 선택해 Claude Console API 키를 입력하세요. **Claude 기본 · Messages** 형식과 `https://api.anthropic.com/v1` 주소를 사용합니다. 워크스페이스가 지정되지 않은 키는 Console의 `wrkspc_…`를 **Claude 워크스페이스 ID**에 입력해야 합니다. 모델을 읽고 저장한 뒤 참여자로 추가하세요.

추론은 먼저 **공급자 기본값**(공급자 기본값)을 쓰세요. 지원되는 새 모델은 `adaptive`, 이전 모델은 `budget_tokens`를 선택할 수 있지만 모든 모델이 모든 옵션을 받지는 않습니다. [공식 API 및 인증](https://platform.claude.com/docs/en/api/overview).

### 5. 로컬 Claude Code

[공식 문서](https://code.claude.com/docs/en/cli-reference)에 따라 네이티브 CLI를 설치하고 로그인하세요. **Claude Code · 로컬**에서 **서비스 주소 / CLI**를 비우면 `claude.exe`를 자동으로 찾으며 전체 경로를 넣어도 됩니다. 네이티브 파일 및 해석 가능한 npm 래퍼를 지원하며 스크립트를 직접 실행하지 않습니다. 초기 별칭은 `sonnet`이며 CLI가 지원하는 `opus`, `haiku`, 모델 ID도 입력할 수 있습니다.

저장 후 **AI 참여자 관리**에서 추가하세요. 어댑터는 도구, MCP, 사용자 스킬과 일반 설정 후크를 끄고 임시 폴더에서 대화하며 프로젝트를 수정하지 않습니다. 조직 관리 정책은 적용될 수 있습니다. 인증과 요금은 CLI 설정을 따르므로 **여기에 Claude API 키를 넣는 방식과 다릅니다**. 추론은 기본값, 켜기, 높음을 지원하며 낮은 강도를 추론 끄기로 표시하지 않습니다.

## 전체 프리셋

| 프리셋 (실제 화면 이름) | 요청 형식 | 주소 / 방식 |
| --- | --- | --- |
| [DeepSeek 공식](https://api-docs.deepseek.com/) | OpenAI-compatible | `https://api.deepseek.com` |
| [OpenAI / GPT API](https://developers.openai.com/api/reference/chat-completions/overview) | OpenAI-compatible | `https://api.openai.com/v1` |
| [Codex · 로컬](https://learn.chatgpt.com/docs/auth) | 로컬 CLI | 자동 찾기 또는 EXE 경로 입력 |
| [Claude / Anthropic API](https://platform.claude.com/docs/en/api/overview) | Claude Messages | `https://api.anthropic.com/v1` |
| [Claude Code · 로컬](https://code.claude.com/docs/en/cli-reference) | 로컬 CLI | 자동 찾기 또는 EXE 경로 입력 |
| [Google Gemini](https://ai.google.dev/gemini-api/docs/openai) | OpenAI-compatible | `https://generativelanguage.googleapis.com/v1beta/openai` |
| [OpenRouter](https://openrouter.ai/docs/api-reference/overview) | OpenAI-compatible | `https://openrouter.ai/api/v1` |
| [Qwen · 베이징](https://www.alibabacloud.com/help/en/model-studio/base-url) | OpenAI-compatible | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| [Qwen · 싱가포르](https://www.alibabacloud.com/help/en/model-studio/base-url) | OpenAI-compatible | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| [Kimi / Moonshot · 중국](https://platform.moonshot.cn/docs/api/chat) | OpenAI-compatible | `https://api.moonshot.cn/v1` |
| [Zhipu GLM · 중국](https://docs.bigmodel.cn/cn/guide/develop/openai/introduction) | OpenAI-compatible | `https://open.bigmodel.cn/api/paas/v4` |
| [Z.AI / GLM · 글로벌](https://docs.z.ai/guides/overview/quick-start) | OpenAI-compatible | `https://api.z.ai/api/paas/v4` |
| [Doubao / Volcengine · 베이징](https://docs.volcengine.com/docs/ark/APICallGuide?lang=zh) | OpenAI-compatible | `https://ark.cn-beijing.volces.com/api/v3` |
| [MiniMax · 중국](https://platform.minimax.cn/docs/api-reference/text-openai-api) | OpenAI-compatible | `https://api.minimax.cn/v1` |
| [MiniMax · 글로벌](https://platform.minimax.io/docs/api-reference/text-openai-api) | OpenAI-compatible | `https://api.minimax.io/v1` |
| [SiliconFlow](https://docs.siliconflow.cn/docs/userguide/quickstart) | OpenAI-compatible | `https://api.siliconflow.cn/v1` |
| [Groq](https://console.groq.com/docs/openai) | OpenAI-compatible | `https://api.groq.com/openai/v1` |
| [Mistral](https://docs.mistral.ai/api) | OpenAI-compatible | `https://api.mistral.ai/v1` |
| [xAI / Grok](https://docs.x.ai/developers/quickstart) | OpenAI-compatible | `https://api.x.ai/v1` |
| [Ollama · 로컬](https://docs.ollama.com/api/openai-compatibility) | OpenAI-compatible | `http://127.0.0.1:11434/v1` |
| [LM Studio · 로컬](https://lmstudio.ai/docs/developer/openai-compat) | OpenAI-compatible | `http://127.0.0.1:1234/v1` |
| 사용자 지정 OpenAI 호환 | OpenAI-compatible | 직접 주소 입력 |

클라우드 모델 ID는 비운 상태로 시작하여 계정의 목록에서 고릅니다. 임베딩이나 음성 모델도 섞일 수 있으므로 텍스트 채팅 모델을 선택하세요. 목록 API가 없으면 정확한 ID를 직접 입력합니다. Qwen 베이징과 싱가포르 키는 지역별이며 종량제 키와 Coding Plan 주소도 혼용할 수 없습니다. 주소는 수정 가능합니다.

OpenAI 호환 채팅, Claude Messages, 두 로컬 CLI를 지원합니다. Azure, Bedrock, Vertex의 전용 IAM 인증은 구현하지 않았으므로 필요하면 적합한 호환 게이트웨이를 쓰세요. `examples/presets.json`은 키 없는 공개 참고 목록이며 JSON 가져오기 버튼은 없습니다.

## 채팅방, 토론, 폴더

- 방별로 이름, 기록, AI 명단, 선택한 폴더를 따로 저장합니다. AI는 방마다 최대 8자리입니다. 연결 설정은 전역이며 참여자 명단은 방별입니다.
- **받는 사람**에서 전체, 한 명, **메시지만 게시**(AI 답변 없이 게시)을 선택하거나 앞에 `@닉네임`을 붙일 수 있습니다. **토론 회차**에 2 이상의 정수를 입력하면 자유 토론이 가능합니다. 최근 동료 발언을 참고하며 별도의 의장은 지정하지 않습니다.
- **내가 발언**을 누르면 이미 요청한 이번 회차 답변이 끝난 뒤 멈춥니다. 보충 발언 후 **발언 후 재개**를 누르면 다음 회차에 반영합니다. 재개·중지도 가능하며 데스크톱은 한 번에 한 방의 AI 토론을 실행합니다.
- **웹 검색**는 이번 질문을 검색 백엔드에 보내고 출처를 모델에 전달합니다. 설정에서 Codex, Brave, 자체 SearXNG를 고르세요. Brave는 별도 검색 키, SearXNG는 JSON 활성화가 필요합니다.
- 일반 API 요청은 해당 자리의 최근 대화를 첨부합니다. **최근 기록 공유**는 공유 범위를 넓힙니다. 문맥 길이에 제한이 있으므로 전체 로컬 기록을 매번 보내지는 않습니다.
- 폴더 선택·열기·경로 복사가 가능합니다. 연결만으로 모든 파일을 업로드하지 않습니다. API와 이 Claude Code 어댑터는 폴더를 자동으로 읽지 않으며 Codex 수정은 일반 메시지와 명시적 수정 스위치가 필요합니다.

## 동료의 LAN 브라우저 참여

오른쪽 **LAN 참여**에서 호스트 IPv4와 포트를 정하고 **이 방 초대 활성화**를 누르세요. 같은 신뢰할 수 있는 LAN의 동료에게 링크를 공유하면 닉네임으로 참여합니다. `127.0.0.1`은 해당 PC만 접근합니다. 다른 기기는 LAN 주소와 적절한 Windows 인바운드 허용이 필요합니다.

초대 활성화 이후의 해당 방 메시지만 보입니다. 게시물은 저장되어 이후 토론에 전달됩니다. 초대 취소나 서버 전체 중지가 가능합니다. 로컬 HTTP 기능이며 공개 호스팅은 제공하지 않습니다.

## 기록 저장, 백업, 비용

방 오른쪽 위 **기록 내보내기**에서 저장 위치와 Markdown(`.md`), 텍스트(`.txt`), JSON(`.json`)을 고르세요. 방에 **저장된 전체 기록**, 발언자, 시간, 본문, 수신자, 회차를 UTF-8로 저장합니다. 화면의 최근 100개 제한은 적용되지 않으며 연결 설정과 키 파일은 제외합니다. 토론 중에는 그때까지의 스냅샷입니다.

기록과 설정은 `%LOCALAPPDATA%\ModelRoom\room.sqlite3`에 있습니다. 종료 후 `%LOCALAPPDATA%\ModelRoom` 폴더 전체를 백업할 수 있습니다. 키는 현재 Windows 사용자에 묶인 DPAPI로 암호화되어 다른 사용자나 PC에서는 보통 다시 입력해야 합니다. 데이터 폴더를 공개 소스 저장소에 넣지 마세요.

요청과 회차마다 해당 서비스 사용량이 발생하며 검색도 과금될 수 있습니다. 공식 DeepSeek 잔액 조회만 내장되어 있고 다른 서비스는 콘솔에서 확인합니다. 답변의 토큰 수는 개별 요청 사용량이며 **통합된 남은 토큰 잔액이 아닙니다**.

## 문제 해결

| 증상 | 확인할 사항 |
| --- | --- |
| 401 / 403 | 키, 권한, 지역, 필요한 Claude 워크스페이스 ID |
| 402 / 잔액 부족 | 해당 서비스 콘솔의 사용 가능량 |
| 404 / 알 수 없는 모델 | 중복 `/v1`, 정확한 모델 ID와 요청 형식 |
| 429 | 참여자·회차를 줄이고 잠시 후 재시도, 서비스 한도 확인 |
| 추론 매개변수 오류 | 공급자 기본값으로 되돌리고 모델 문서 확인 |
| 모델 목록은 보이나 대화 실패 | 이 어댑터의 API를 지원하는 텍스트 모델과 권한 확인 |
| Codex 없음 | `codex.exe` 전체 경로 선택. 데스크톱 설치만으로 PATH에 없을 수 있음 |
| Claude Code 실패 | 네이티브 EXE, 로그인, CLI 버전 확인. 자동 설치·로그인은 하지 않음 |
| 동료 연결 실패 | LAN 주소, 네트워크 어댑터, 인바운드 허용, Wi-Fi 클라이언트 격리 |

## 소스와 빌드

Python, H5, Windows 실행기와 다섯 언어 설명서를 보존합니다. Tkinter가 포함된 Windows x64 Python 3.10+를 사용하세요.

```powershell
python -m pip install -r requirements.txt
python .\model_room.py
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File .\build-windows.ps1
```

빌드 결과는 `dist\ModelRoom.exe`, 배포 이름은 `ModelRoom-v1.0-Windows-x64.exe`입니다. 프리셋, API, Claude Code, 스타일은 각각 `room_presets.py`, `room_providers.py`, `room_claude.py`, `room_style.py`에 있습니다. v0.6 설정을 호환해서 읽습니다. 로컬 모의 API와 기존 동작을 검증했으며 실제 모델, 계정 권한과 요금은 각 서비스에 따릅니다.
