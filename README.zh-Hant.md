# Model Room v1.1 · 使用說明

[简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md) · [English](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

讓你、隊友和多個 AI 在同一個群裡交流。v1.1 新增 Linux、macOS 原生封裝，以及每位 AI 的 Markdown 性格設定。原始碼採用 [MIT](LICENSE) 授權。

## 下載與安裝

請至 [Releases](https://github.com/MartZenTec-Co-Ltd/Model-Room/releases) 下載對應平台的成品。成品內含 Python、介面及影像執行環境，無須另裝 Python。Code → Download ZIP 是開發者原始碼。

| Platform | Download | Requirements |
| --- | --- | --- |
| Windows | `ModelRoom-v1.1-Windows-x64.exe` | Windows 10/11 x64 |
| Linux portable | `ModelRoom-v1.1-Linux-x86_64.AppImage` | x86_64, glibc 2.35+, X11/XWayland |
| Debian / Kali | `model-room_1.1_amd64.deb` | amd64, compatible Debian-family dependencies |
| macOS Apple Silicon | `ModelRoom-v1.1-macOS-arm64.dmg` or `.zip` | macOS 15+, Apple Silicon |
| macOS Intel | `ModelRoom-v1.1-macOS-x86_64.dmg` or `.zip` | macOS 15+, Intel |


Linux AppImage：執行 `chmod +x ModelRoom-v1.1-Linux-x86_64.AppImage` 後啟動。需要適用的 FUSE 環境；沒有時可用 `./ModelRoom-v1.1-Linux-x86_64.AppImage --appimage-extract-and-run`。DEB 使用 `sudo apt install ./model-room_1.1_amd64.deb`。不支援 ARM Linux；實際驗證平台以發行說明為準。

macOS：依晶片選擇 DMG，將 ModelRoom.app 拖入 Applications；亦提供 ZIP。此版只有 ad-hoc 簽章，**沒有 Apple Developer ID 簽章或 Apple 公證**，Gatekeeper 可能阻擋首次啟動。核對來源與 SHA256，參閱 [Apple 說明](https://support.apple.com/en-us/102445)。程式不會關閉系統安全機制。

## 第一次使用

1. 設定 → 連線設定 → 模型連線，新增快速預設，輸入自己的 API Key，讀取模型、選擇文字聊天型號，再儲存連線。
2. 新建並命名群聊，到右側管理 AI 成員加入兩到三個可用模型，再儲存本群成員。儲存連線不代表自動加入群聊。
3. 傳送讓每位成員回答一次；討論輪數填入至少 2 的整數後開始自由討論，後續輪次會參考近期同伴發言。
4. 按我來發言，等待已發出的回覆收尾，再輸入補充並發言繼續。沒有固定 AI 主持人；每群最多 8 個席位，同時只執行一群討論。

## AI 性格

設定 → **AI 性格**，選取本群成員，使用範本、直接編輯或匯入 UTF-8 `.md`；最多 12000 字、64 KB。套用或確定儲存，取消放棄未儲存變更，留空使用預設。

按群聊及 AI 席位獨立保存；一般回覆與每輪討論都會使用，支援 API、Codex、Claude Code 與 Harness。Markdown 只讀取文字，不執行指令、不增加檔案權限。設定會傳給該成員的模型服務，請勿填寫私密資料。見 [性格指南](PERSONALITIES.zh-Hant.md)。

## 常用連線

| Preset | Configuration |
| --- | --- |
| DeepSeek | Provider API Key → List models → choose a text chat model |
| OpenAI / GPT API | OpenAI Platform API Key; Chat Completions-compatible text model |
| Claude / Anthropic API | Claude Messages API Key; workspace ID when required |
| Codex · Local | Install and sign in to Codex CLI, auto-detect or select its executable |
| Claude Code · Local | Install and sign in to a supported CLI, save connection and add a seat |
| Other providers | Built-in presets or a custom compatible endpoint; see [preset catalog](examples/presets.json) |


預設不附帳號、金鑰、模型權重或餘額。模型及思考支援依服務商與帳號而定。ChatGPT 訂閱不等於 API 餘額。本機 Codex 呼叫 CLI，不控制目前桌面對話；討論時唯讀。僅內建官方 DeepSeek 餘額查詢，回覆的 token 是單次用量。多輪討論及搜尋可能計費。

## 更多操作與資料

可指定全體、單人或只在群內發言，支援開頭 `@暱稱`。搜尋先設定 Codex、Brave 或 SearXNG 後端。局域網邀請適用同一可信網路，以 HTTP 提供瀏覽器參會，不是公網託管；訪客僅看到邀請開啟後的訊息。匯出支援本群全部已保存紀錄的 Markdown、文字與 JSON，不含連線金鑰。

設定支援五種語言、暱稱、頭像、背景、明暗主題與輸入偏好；切換語言不翻譯舊訊息。

資料位置：Windows `%LOCALAPPDATA%\ModelRoom`；Linux `${XDG_DATA_HOME:-~/.local/share}/modelroom`；macOS `~/Library/Application Support/ModelRoom`。可用 `MODELROOM_DATA_DIR` 指定測試目錄。

Windows 沿用 DPAPI 及 v1.0 資料。Linux/macOS 以 Fernet 加密及 0600 本機金鑰檔案保護，目錄 0700；**不是系統鑰匙圈或密碼保險庫**。可存取整個目錄的同一使用者程式仍可解密，請保護目錄及備份。模型請求會傳送所需文字上下文；頭像與背景不交給模型。分享錯誤截圖前請遮住敏感資料。

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
