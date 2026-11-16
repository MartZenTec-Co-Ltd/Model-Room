# Model Room v1.1 · 使用说明

[简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md) · [English](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

让你、队友和多个 AI 在同一个群里交流。v1.1 新增 Linux、macOS 原生打包及每个 AI 的 Markdown 性格设定。源码采用 [MIT](LICENSE) 许可证。

## 下载与安装

到 [Releases](https://github.com/MartZenTec-Co-Ltd/Model-Room/releases) 下载对应平台的成品。所有成品包含 Python、界面和图像运行库，使用者无需另装 Python。Code → Download ZIP 是开发者源码。

| Platform | Download | Requirements |
| --- | --- | --- |
| Windows | `ModelRoom-v1.1-Windows-x64.exe` | Windows 10/11 x64 |
| Linux portable | `ModelRoom-v1.1-Linux-x86_64.AppImage` | x86_64, glibc 2.35+, X11/XWayland |
| Debian / Kali | `model-room_1.1_amd64.deb` | amd64, compatible Debian-family dependencies |
| macOS Apple Silicon | `ModelRoom-v1.1-macOS-arm64.dmg` or `.zip` | macOS 15+, Apple Silicon |
| macOS Intel | `ModelRoom-v1.1-macOS-x86_64.dmg` or `.zip` | macOS 15+, Intel |


Linux AppImage：先执行 `chmod +x ModelRoom-v1.1-Linux-x86_64.AppImage`，再双击或在终端运行。需要适用的 FUSE 环境；没有时可使用 `./ModelRoom-v1.1-Linux-x86_64.AppImage --appimage-extract-and-run`。DEB 使用 `sudo apt install ./model-room_1.1_amd64.deb`。本包不支持 ARM Linux。最低基础库不等于所有发行版都已测试，以发布说明的测试记录为准。

macOS：按芯片选择 DMG，将 ModelRoom.app 拖到 Applications；也提供 ZIP。此版仅有 ad-hoc 签名，**没有 Apple Developer ID 签名或 Apple 公证**，Gatekeeper 可能阻止首次启动。请核对来源与 SHA256，并参阅 [Apple 官方说明](https://support.apple.com/en-us/102445)。程序不会关闭系统安全机制。

## 第一次使用

1. 设置 → 连接设置 → 模型连接，选择快速预设并新增，输入自己的 API Key，读取模型、选择文字聊天模型，再保存连接。
2. 新建并命名群聊，打开右侧管理 AI 成员，加入两到三个已经配置好的模型并保存本群成员。保存连接不代表自动加入群聊；一个连接也可以使用多个模型席位。
3. 点击发送让成员各答一次；在讨论轮数填入不小于 2 的整数，点击自由讨论，让后续轮次参考近期同伴发言。
4. 点击我来发言，等已发出的回复收尾后补充要求，再点击发言并继续。没有固定 AI 主持人；最多 8 个席位，同一时刻一个群运行讨论。模型意见仍需要人类判断。

## 每个 AI 的性格

设置 → **AI 性格**，选择当前群里的成员，可使用模板、直接编辑，或导入 UTF-8 `.md`。支持最多 12000 字、文件最多 64 KB。套用或确定保存，取消放弃未保存更改；留空恢复默认。

性格按“群聊 + AI 席位”分别保存，对普通回复和每轮讨论生效，支持 API、本机 Codex、Claude Code 与 Harness。Markdown 只按文字读取，不执行命令，也不会额外授予文件权限。只把该成员的性格传给其模型服务，请不要写入密钥或私密资料。详见 [性格指南](PERSONALITIES.zh-Hans.md)。

## 常用连接

| Preset | Configuration |
| --- | --- |
| DeepSeek | Provider API Key → List models → choose a text chat model |
| OpenAI / GPT API | OpenAI Platform API Key; Chat Completions-compatible text model |
| Claude / Anthropic API | Claude Messages API Key; workspace ID when required |
| Codex · Local | Install and sign in to Codex CLI, auto-detect or select its executable |
| Claude Code · Local | Install and sign in to a supported CLI, save connection and add a seat |
| Other providers | Built-in presets or a custom compatible endpoint; see [preset catalog](examples/presets.json) |


预设不包含账号、余额或模型权重，也不会自动安装本机 Agent。可用模型和思考模式由服务账户及接口支持情况决定。ChatGPT 订阅不等于 OpenAI API 余额。本机 Codex 调用 CLI，不会控制当前桌面 Codex 聊天；讨论时只读，普通发送需明确开启才可改文件。仅内置官方 DeepSeek 余额查询，回复详情的 token 是单次用量，并非统一剩余额度。搜索和多轮讨论也可能计费。

## 更多操作

- 发送给可选全体、单个成员或仅群内发言；支持开头 `@昵称`。
- 设置中的联网搜索需先配置 Codex、Brave 或 SearXNG 后端；搜索来源作为材料提供给模型，不能默认认为模型自带实时网络。
- 局域网参会：选择主机 IPv4、端口并开启本群邀请，同一可信局域网里的队友用浏览器填写昵称加入。使用 HTTP，不是公网托管服务。访客只能看见开启邀请后的消息。
- 导出记录：保存本群全部已保存消息为 Markdown、文本或 JSON，不含密钥配置与头像文件。正在讨论时导出的是当时快照。
- 设置支持简繁中文、英语、日语、韩语，以及昵称、头像、明暗主题、背景、输入方式和字号。切换语言不翻译旧消息。

## 数据与密钥

Windows：`%LOCALAPPDATA%\ModelRoom`；Linux：`${XDG_DATA_HOME:-~/.local/share}/modelroom`；macOS：`~/Library/Application Support/ModelRoom`。开发与测试可用 `MODELROOM_DATA_DIR` 指定独立目录。

Windows 继续使用当前用户 DPAPI，v1.0 原数据保留。Linux/macOS 使用 Fernet 加密与权限为 0600 的本机密钥文件，目录权限 0700；**不是系统钥匙串，也不是密码保护的保险库**。能访问整个数据目录的同一用户进程仍可能解密，请保护整个目录和备份。聊天记录保存在本机；调用模型时会发送相应上下文。背景与头像不发给模型，但局域网成员可看见消息里的昵称与小头像。

遇到 401/403 检查 Key、区域及权限；429 减少成员或轮数；模型列表可含非聊天模型，请选择兼容的文字聊天型号。错误截图请遮住敏感信息。

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
