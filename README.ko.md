# Model Room v1.1 · 사용 안내

[简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md) · [English](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

사람과 여러 AI가 하나의 방에서 대화하는 앱입니다. v1.1은 Linux/macOS 네이티브 패키지와 AI별 Markdown 성격 설정을 추가합니다. [MIT 라이선스](LICENSE).

## 다운로드

[Releases](https://github.com/MartZenTec-Co-Ltd/Model-Room/releases)에서 플랫폼에 맞는 완성본을 받으세요. Python, Tcl/Tk, Pillow를 포함하여 Python을 따로 설치할 필요가 없습니다. Code → Download ZIP은 개발자용 소스입니다.

| Platform | Download | Requirements |
| --- | --- | --- |
| Windows | `ModelRoom-v1.1-Windows-x64.exe` | Windows 10/11 x64 |
| Linux portable | `ModelRoom-v1.1-Linux-x86_64.AppImage` | x86_64, glibc 2.35+, X11/XWayland |
| Debian / Kali | `model-room_1.1_amd64.deb` | amd64, compatible Debian-family dependencies |
| macOS Apple Silicon | `ModelRoom-v1.1-macOS-arm64.dmg` or `.zip` | macOS 15+, Apple Silicon |
| macOS Intel | `ModelRoom-v1.1-macOS-x86_64.dmg` or `.zip` | macOS 15+, Intel |


AppImage는 `chmod +x ModelRoom-v1.1-Linux-x86_64.AppImage` 후 실행합니다. FUSE를 사용할 수 없으면 `./ModelRoom-v1.1-Linux-x86_64.AppImage --appimage-extract-and-run`을 사용할 수 있습니다. DEB는 `sudo apt install ./model-room_1.1_amd64.deb`로 설치합니다. ARM Linux는 포함하지 않습니다. 검증 환경은 릴리스 안내를 확인하세요.

macOS는 CPU에 맞는 DMG를 열어 ModelRoom.app을 Applications로 복사하세요. ZIP도 제공합니다. 이 버전은 ad-hoc 서명만 있으며 **Developer ID 서명이나 Apple 공증은 없습니다**. Gatekeeper가 첫 실행을 차단할 수 있습니다. 출처와 SHA256을 확인하고 [Apple 안내](https://support.apple.com/en-us/102445)를 참고하세요. 시스템 보안 기능을 끄지 않습니다.

## 첫 대화

1. 설정 → 연결 설정 → 모델 연결에서 프리셋을 추가하고 본인의 API 키를 입력합니다. 모델 목록에서 텍스트 채팅 모델을 선택하고 저장하세요.
2. 방을 만들고 AI 멤버 관리에서 사용할 수 있는 모델 2~3개를 추가하여 명단을 저장합니다. 연결 저장만으로 방에 참여하지 않습니다.
3. 보내기는 멤버별 1회 답변입니다. 라운드를 2 이상 입력하고 토론하면 다음 라운드에서 다른 멤버의 최근 발언을 참조합니다.
4. 내 발언 버튼은 이미 전송한 답변이 끝난 뒤 일시 정지합니다. 조건을 추가하고 전송 및 재개를 선택하세요. 고정 AI 사회자는 없습니다. 방당 최대 8석, 동시에 한 방에서 토론합니다.

## AI 성격

설정 → **AI 성격**에서 멤버를 선택하고 템플릿, 직접 편집 또는 UTF-8 Markdown 가져오기를 사용하세요. 최대 12,000자, 64KB입니다. 적용/확인으로 저장하며 취소하면 미저장 변경을 버립니다. 비워 두면 기본 스타일입니다.

방과 좌석별로 저장하며 API, Codex, Claude Code, Harness의 일반 답변과 모든 토론 라운드에 적용됩니다. Markdown은 텍스트로만 읽고 실행하거나 권한을 추가하지 않습니다. 해당 모델 서비스로 전달되므로 비밀 정보를 넣지 마세요. [성격 안내](PERSONALITIES.ko.md).

## 주요 연결

| Preset | Configuration |
| --- | --- |
| DeepSeek | Provider API Key → List models → choose a text chat model |
| OpenAI / GPT API | OpenAI Platform API Key; Chat Completions-compatible text model |
| Claude / Anthropic API | Claude Messages API Key; workspace ID when required |
| Codex · Local | Install and sign in to Codex CLI, auto-detect or select its executable |
| Claude Code · Local | Install and sign in to a supported CLI, save connection and add a seat |
| Other providers | Built-in presets or a custom compatible endpoint; see [preset catalog](examples/presets.json) |


프리셋은 계정, 키, 잔액, 모델 가중치를 포함하지 않습니다. 모델과 사고 모드는 서비스 및 계정에 따라 다릅니다. ChatGPT 구독과 API 잔액은 별개입니다. 로컬 Codex는 CLI를 호출하며 현재 데스크톱 대화를 제어하지 않습니다. 토론은 읽기 전용입니다. 비용은 서비스별로 부과되며 잔액 조회는 공식 DeepSeek만 지원합니다. token 표시는 요청별 사용량입니다.

## 기타 기능과 데이터

수신자 선택 및 앞부분 `@닉네임`, Codex/Brave/SearXNG 연결을 설정한 웹 검색, 신뢰하는 동일 LAN의 브라우저 참여, 저장된 전체 대화의 Markdown/텍스트/JSON 내보내기를 지원합니다. LAN은 HTTP이며 공개 호스팅이 아닙니다. 초대 시작 전 기록은 게스트에게 보이지 않으며 내보내기에 키 설정은 포함하지 않습니다.

5개 UI 언어, 닉네임, 아바타, 배경, 테마 및 입력 설정을 제공합니다. 이전 메시지는 자동 번역되지 않습니다.

데이터: Windows `%LOCALAPPDATA%\ModelRoom`, Linux `${XDG_DATA_HOME:-~/.local/share}/modelroom`, macOS `~/Library/Application Support/ModelRoom`. 테스트에는 `MODELROOM_DATA_DIR`을 사용할 수 있습니다.

Windows는 기존 DPAPI와 v1.0 데이터를 유지합니다. Linux/macOS는 Fernet 암호화, 권한 0600의 로컬 키와 0700 디렉터리를 사용합니다. **OS 키체인이나 암호 기반 금고가 아닙니다**. 동일 사용자로 전체 폴더에 접근할 수 있는 프로그램은 복호화할 수 있으므로 폴더 전체와 백업을 보호하세요. 필요한 텍스트 문맥은 모델로 보내지만 배경과 아바타는 보내지 않습니다. 오류 보고에서 비밀 정보를 가려 주세요.

## Source / build

Python 3.10+ with Tkinter runs the source. Build on the native target OS; CI uses Python 3.13.

```text
python -m pip install -r requirements.txt
python model_room.py
```

Windows: `powershell -File build-windows.ps1`.
Linux/macOS: install `requirements-build.txt`, then `python build_unix.py linux` or `python build_unix.py macos`.
Linux build tools: `xvfb`, `xauth`, Tcl/Tk, `squashfs-tools`, `desktop-file-utils`, `dpkg-deb`.
macOS build tools: Xcode Command Line Tools, `codesign`, `hdiutil`.

See [release notes](RELEASE_NOTES.md), [contributing](CONTRIBUTING.md) and [third-party notices](THIRD_PARTY_NOTICES.md).
