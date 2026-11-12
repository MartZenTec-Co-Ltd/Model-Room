# Model Room v1.0 · Windows 使用说明

[简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md) · [English](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

**让你、队友和多个 AI 在同一个群里交流。** 保留三栏布局，支持命名群聊、模型互相讨论、人类中途插话、局域网浏览器参会及聊天记录导出。


## V1.0 公开版 — 当前仅 Windows x64

**普通使用者：到本仓库的 Releases 页面下载 `ModelRoom-v1.0-Windows-x64.exe`，下载后双击即可，不用安装 Python、pip、Tkinter 或 Pillow。** EXE 已内含运行环境，首次启动会在本机展开缓存，不会另行下载 Python，也不依赖 PATH 中的 Python。

Windows ZIP 是同一个 EXE 加五语说明及许可证。GitHub 的 **Code → Download ZIP** 和 `ModelRoom-v1.0-Source.zip` 是开发者源码，不是普通使用者的程序下载。只有运行或构建源码才需要 Python。成品支持 **Windows 10/11 x64**，本次没有发布 Linux/macOS 版本。

对话需要配置自己的 API 账户，或另行安装并登录支持的本机 Agent；程序没有附送模型权重或付费账户。已有本机群聊与设置会继续沿用。

**开源许可证：[MIT](LICENSE)**。另见 [发布说明](RELEASE_NOTES.md)、[贡献说明](CONTRIBUTING.md) 和 [第三方声明](THIRD_PARTY_NOTICES.md)。维护者可用 `release-windows.ps1` 构建发布文件；GitHub 工作流会构建 EXE，但不会自动公开发布 Release。


## 完整聊天背景、个人资料与常用设置

背景现在铺满消息气泡后方的整个聊天区，滚动与缩放时仍保持覆盖。侧栏、群详情、标题栏和输入区保留纯色面板，方便阅读与操作。外观中可选 **填充**（可能裁边）、**适应**（保留整张图及留白）或 **平铺**，图片强度为 0–100%。消息气泡和昵称底色保持可读；消息字号可选 10–18。背景仅保存在本机。

设置现有 **通用 / 连接设置 / 界面外观 / 聊天与输入 / 数据与存储 / 关于**。通用新增 **我的昵称**、**我在本群的昵称**，以及选择或移除头像。本群昵称留空时跟随通用昵称；两项都空时显示当前语言的“你”。昵称最多 32 字。头像居中裁为圆形、去除元数据并复制到本机目录。新消息保存昵称和头像快照，之后改资料不改写这些署名；没有资料快照的旧记录跟随当前资料。内部路由与成员标识保持稳定。

局域网参会者能看到已分享消息中的昵称和小头像，仅传小尺寸 PNG，不暴露本机图片路径。头像和背景不会交给 AI 模型；昵称会用于文字上下文及记录导出。导出不包含头像图片文件或连接密钥。

聊天与输入新增 **Enter 发送消息**、**显示消息时间**、**新消息自动滚动** 开关及默认讨论轮数。关闭 Enter 发送后使用 Ctrl+Enter，Shift+Enter 始终换行。默认轮数用于启动和切换群聊，仍可在输入区临时填写轮数。数据与存储可打开或复制数据目录、导出当前群聊。关于显示版本与支持语言。套用保存设置并留在当前页面，确定保存后关闭，取消放弃尚未套用的设置；连接表单仍独立点击保存。

设置组织参考 [Signal 个人资料](https://support.signal.org/hc/en-us/articles/360007059952-Edit-my-Profile)、[Signal 字号](https://support.signal.org/hc/en-us/articles/360049670791-Font-Size-Options) 与 [Telegram 聊天背景](https://telegram.org/blog/animated-backgrounds)。这些软件仅作设计参考，不是运行依赖。

## 设置界面修复

设置里的布尔选项改为手机样式滑动开关：左边说明，右边开关，包括启动时检测本机 Agent 和深色模式。点击切换；Tab 聚焦，空格或 Enter 切换，左右方向键指定关闭或开启。聊天主界面的控件保持原有排版。

设置底部统一为分隔线与右下角 **套用 / 确定 / 取消或关闭**，不随页面滚动。套用保存通用、外观与聊天设置，保留设置窗口、当前页面和未保存的连接表单；确定保存这些设置后关闭。取消、Esc 或窗口关闭按钮放弃尚未套用的通用、外观与聊天更改；已套用的设置、已明确保存的连接仍然保留。连接表单仍使用页面内的保存按钮。未保存的密钥只在内存保留，不写入日志或发布包。

通用和外观独立滚动，最小 840 × 560 窗口下底栏始终可见，长说明自动换行，左侧显示当前选中的页面。保留五种界面语言和明暗主题。

## 统一设置、五语界面与本机 Agent

左下角现在是 **设置**（快捷键 `Ctrl+,`），依次提供：

1. **通用**：选择简体中文、繁体中文、英语、日语、韩语；可开启启动时自动检测本机 Agent。语言会用于实际桌面控件和系统提示，群名、昵称、模型 ID 与聊天原文保持不变。
2. **连接设置**：包含模型连接、联网搜索、本机 Codex 和本机 Agent。旧文中的“连接设置”均位于这个总设置里。
3. **界面外观**：选择 Light/Dark Mode、自定义强调色、导入自己的 JPG/PNG/WebP/GIF/BMP 图片、调节强度或恢复默认。背景铺满整个消息区域，保留三栏结构。图片解码、去除元数据后复制到本机数据目录，不会发给模型。设置即时应用，保留输入草稿和聊天；套用时会保留未保存的连接表单。

**自动检测只查找安装路径，不会安装、登录、发起付费模型请求或自动加群。** 在连接设置的 **本机 Agent** 页点自动检测，选择程序，必要时检测版本，再 **保存本机连接**。找到程序不等于登录成功或有余额。

- **Codex**：检测 PATH 及本机 Codex 缓存中的原生 `codex.exe`。保存后可加入当前群，登录状态在本机 Codex 页单独检查。
- **Claude Code**：支持原生程序，以及可解析到已安装 Node.js 包的 npm 包装器。包装脚本本身不会通过命令解释器执行。保存连接后到群成员管理添加席位。
- **DeepSeek Harness**：检测 `dsh`，调用官方 headless 模式，从 stdin 传入讨论材料，指定 read-only 和拒绝交互审批。模型使用 Harness 自身配置；headless 的鉴权可能需要 `DEEPSEEK_API_KEY`，GUI 登录不一定适用。版本不支持这些参数时会报错，不自动降低权限。此电脑上未安装的 Agent 不能凭预设变成已连接。参阅 [Harness CLI](https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli) 与 [headless 说明](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/bundle/headless)。

局域网 H5 页面也有五语选择，按浏览器保存偏好；原始聊天不翻译。桌面背景和主题属于本机设置，不会自动分享给访客。新增配置位于原数据库的 preferences 设置项；旧群、连接和加密密钥不迁移、不覆盖。

**Harness 兼容性：** 支持识别桌面安装包及正在运行的便携版，但找到程序不代表鉴权已可用。`0.2.1-rc.2` 等旧版可能缺少必要的 headless 只读及审批策略参数，请检查已安装版本的帮助，必要时更新。适配器不会静默移除必要策略。

## 第一次使用：照这三步做

1. 双击 `ModelRoom-v1.0-Windows-x64.exe`。Windows x64 版内含 Python，不用先装 Python。旧版用户会沿用本机原有群聊与设置；预设不会自动覆盖旧连接。
2. 点左侧 **连接设置 → 模型连接**：选 **快速预设 → 新增此预设**，填自己的密钥，点 **读取模型**，选文字聊天模型，再点 **保存连接**。**保存连接之后，还要到右侧「管理 AI 成员」添加该模型并保存本群成员。** 如果只用本机 Codex，直接按下文 Codex 示例操作。
3. 左侧 **新建群聊**并命名，选好成员。在中央输入问题，点 **发送**让成员各答一次，或填写轮数后点 **自由讨论**。先用少量轮次确认连接，再增加轮数。

设置窗口内容较长时可以向下滚动。点 **官方说明**会打开当前预设的官方文档。

## 先分清：连接、成员和额度

| 名称 | 实际含义 | 需要准备什么 |
| --- | --- | --- |
| API 连接 | 服务地址、模型和鉴权设置 | 对应服务的 API Key 与可用额度 |
| 群成员 | 本群的一个模型席位 | 从已保存连接选模型；一个连接可加多个席位 |
| 本机 Codex | 调用已安装的 Codex CLI | CLI 与它自己的登录；不是直接操控当前 Codex 聊天窗口 |
| 本机 Claude Code | 调用已安装的原生 Claude Code CLI | `claude.exe` 与它自己的登录或 API 配置 |
| 快速预设 | 自动填好地址和请求格式的模板 | 不附赠密钥、账号、模型下载或余额 |

多个云模型会分别发起请求；这不表示在电脑上下载并载入它们的模型权重。

## 五个常用配置示例

### 1. DeepSeek

选 **DeepSeek 官方 → 新增此预设**，填 DeepSeek 平台的 Key，**读取模型 → 选聊天型号 → 保存连接**。然后去 **管理 AI 成员**把它加入本群。已有默认 DeepSeek 连接可直接继续使用，不必重复新增。

点 **测试聊天**会发送一条真实、可能计费的验证消息；新回复的 **详情**可查看接口、返回型号、耗时及服务商返回的用量。**查 DeepSeek 余额**读取官方余额接口，适用于官方地址。见 [DeepSeek 官方入门](https://api-docs.deepseek.com/)。

### 2. OpenAI / GPT API（你说的 ChatGPT API）

选 **OpenAI / GPT API** 预设，填 **OpenAI 平台 API Key**，读取模型后选择支持 Chat Completions 的文字聊天型号，再保存并添加群成员。地址会自动填为 `https://api.openai.com/v1`。

这里使用平台 API 的鉴权和用量规则；**不要把 ChatGPT 订阅额度当成 API Key 的余额**。API Key、项目权限及可用额度以平台为准。本版走 Chat Completions，不支持仅提供 Responses 的型号。见 [官方 API 文档](https://developers.openai.com/api/reference/chat-completions/overview)。

### 3. Codex · 本机

选 **Codex · 本机 → 新增此预设**会切到 **本机 Codex** 页。点 **自动查找 → 检测登录**；找不到时用 **选择 CLI** 指向 `codex.exe`。尚未登录则点 **复制登录命令**，在自己的 PowerShell 运行并完成登录。然后在 **管理 AI 成员**点 **加入 Codex → 保存本群成员**。

本预设不用填 API 地址；实际使用哪种额度由 CLI 当前登录方式决定，可用 ChatGPT 登录或 API Key。讨论中 Codex 只读。普通发送时若要改项目文件，先选项目目录，再开启 **允许 Codex 改文件**。见 [官方认证说明](https://learn.chatgpt.com/docs/auth)。

### 4. Claude / Anthropic API

选 **Claude / Anthropic API**，填 Claude Console API Key。请求格式为 **Claude 原生 · Messages**，地址为 `https://api.anthropic.com/v1`。未限定工作区的 Key 还需填写控制台提供的 **Claude 工作区 ID**（`wrkspc_…`）。读取模型，选择聊天型号并保存，然后加入本群。

先用 **供应商默认**思考模式。需要手动配置时，新型号可按支持情况选 `adaptive`，旧型号可选 `budget_tokens`；并非每个型号都接受全部选项。见 [官方接口与鉴权](https://platform.claude.com/docs/en/api/overview)。

### 5. Claude Code · 本机

先按 [Claude Code 官方说明](https://code.claude.com/docs/en/cli-reference)安装并登录原生 CLI。选 **Claude Code · 本机**预设；**服务地址 / CLI** 留空会自动查找 `claude.exe`，也可填完整路径。Windows 支持原生程序及可解析的 npm 包装器；不直接执行 `.cmd` 或 `.ps1`。默认模型别名是 `sonnet`，也可手填本机支持的 `opus`、`haiku` 或模型 ID。

保存连接后，在 **管理 AI 成员**里把它作为一个模型席位加入。本适配器关闭工具、MCP、自定义技能与普通配置钩子，在临时目录进行纯聊天，不执行项目修改；组织的托管策略仍可能适用。登录和计费沿用 CLI 的配置，**并不等同于填一个 Claude API Key**。思考可用默认、开启或高强度；不支持把低强度当作“关闭思考”。

## 全部快速预设

| 预设（与界面名称一致） | 请求格式 | 地址 / 方式 |
| --- | --- | --- |
| [DeepSeek 官方](https://api-docs.deepseek.com/) | OpenAI-compatible | `https://api.deepseek.com` |
| [OpenAI / GPT API](https://developers.openai.com/api/reference/chat-completions/overview) | OpenAI-compatible | `https://api.openai.com/v1` |
| [Codex · 本机](https://learn.chatgpt.com/docs/auth) | 本机 CLI | 自动查找或填写 EXE 路径 |
| [Claude / Anthropic API](https://platform.claude.com/docs/en/api/overview) | Claude Messages | `https://api.anthropic.com/v1` |
| [Claude Code · 本机](https://code.claude.com/docs/en/cli-reference) | 本机 CLI | 自动查找或填写 EXE 路径 |
| [Google Gemini](https://ai.google.dev/gemini-api/docs/openai) | OpenAI-compatible | `https://generativelanguage.googleapis.com/v1beta/openai` |
| [OpenRouter](https://openrouter.ai/docs/api-reference/overview) | OpenAI-compatible | `https://openrouter.ai/api/v1` |
| [Qwen / 百炼 · 北京](https://www.alibabacloud.com/help/en/model-studio/base-url) | OpenAI-compatible | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| [Qwen / 百炼 · 新加坡](https://www.alibabacloud.com/help/en/model-studio/base-url) | OpenAI-compatible | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| [Kimi / Moonshot · 中国](https://platform.moonshot.cn/docs/api/chat) | OpenAI-compatible | `https://api.moonshot.cn/v1` |
| [智谱 GLM · 中国](https://docs.bigmodel.cn/cn/guide/develop/openai/introduction) | OpenAI-compatible | `https://open.bigmodel.cn/api/paas/v4` |
| [Z.AI / GLM · 国际](https://docs.z.ai/guides/overview/quick-start) | OpenAI-compatible | `https://api.z.ai/api/paas/v4` |
| [豆包 / 火山方舟 · 北京](https://docs.volcengine.com/docs/ark/APICallGuide?lang=zh) | OpenAI-compatible | `https://ark.cn-beijing.volces.com/api/v3` |
| [MiniMax · 中国](https://platform.minimax.cn/docs/api-reference/text-openai-api) | OpenAI-compatible | `https://api.minimax.cn/v1` |
| [MiniMax · 国际](https://platform.minimax.io/docs/api-reference/text-openai-api) | OpenAI-compatible | `https://api.minimax.io/v1` |
| [硅基流动 / SiliconFlow](https://docs.siliconflow.cn/docs/userguide/quickstart) | OpenAI-compatible | `https://api.siliconflow.cn/v1` |
| [Groq](https://console.groq.com/docs/openai) | OpenAI-compatible | `https://api.groq.com/openai/v1` |
| [Mistral](https://docs.mistral.ai/api) | OpenAI-compatible | `https://api.mistral.ai/v1` |
| [xAI / Grok](https://docs.x.ai/developers/quickstart) | OpenAI-compatible | `https://api.x.ai/v1` |
| [Ollama · 本机](https://docs.ollama.com/api/openai-compatibility) | OpenAI-compatible | `http://127.0.0.1:11434/v1` |
| [LM Studio · 本机](https://lmstudio.ai/docs/developer/openai-compat) | OpenAI-compatible | `http://127.0.0.1:1234/v1` |
| 自定义 OpenAI 兼容 | OpenAI-compatible | 自行填写 |

云端预设默认留空模型 ID，便于按账号实时读取列表。列表可能包含嵌入、语音等型号，请选文字聊天模型；接口没有模型列表时可手填准确 ID。百炼北京和新加坡的 Key 不通用，按量计费 Key 也不能与 Coding Plan 地址混用。地址可按服务商控制台要求修改。

本版支持 OpenAI 兼容聊天接口、Claude Messages 和两种本机 CLI；没有内置 Azure、Bedrock、Vertex 的专有 IAM 鉴权。需要这些服务时，使用匹配的兼容网关。`examples/presets.json` 是公开模板参考，不含密钥；本版通过界面选择预设，不提供该 JSON 的导入按钮。

## 群聊、讨论与文件目录

- 左侧各群分别保存名称、记录、AI 名单和可选项目目录。右侧显示人类及 AI；每群最多 8 个 AI 席位。API 连接全局保存，群成员按群保存。
- **发送给**可选全体、单人或 **仅群内发言**；也可在消息开头写 `@昵称`。**发送**各答一次；**讨论轮数**填写不小于 2 的整数后点 **自由讨论**，模型可参考近期同伴发言互相回应，没有指定会议主持人。
- **我来发言**在本轮已发出的回复收尾后暂停。输入补充并点 **发言并继续**，下一轮会考虑你的发言。可直接继续或停止；桌面同一时间运行一个群的 AI 讨论。
- **联网搜索**把本轮问题交给所选搜索服务，再把来源提供给成员。先在连接设置选 Codex、Brave 或自建 SearXNG 后端；Brave 需单独的搜索 Key，SearXNG 需启用 JSON。
- API 普通发送默认附该席位的近期对话；**附近期群聊给模型**会扩大共享范围。历史上下文有长度限制，完整本地记录不等于每次都全部发给模型。
- 项目目录可选择、打开及复制路径。关联目录不等于上传全部文件；API 和本版 Claude Code 适配器不会自行读取该目录。Codex 的修改权限只在普通发送且明确开启时生效。

## 队友用浏览器加入

右侧 **局域网参会 → 选择主机 IPv4 和端口 → 开启本群邀请**，把链接发给同一可信局域网的队友。对方填昵称即可发言，无需安装。`127.0.0.1` 只能本机访问；其他设备需使用主机的局域网地址，并允许相应的 Windows 入站连接。

浏览器仅看得到开启邀请后的本群消息；发言会保存并进入本群后续讨论。可关闭本群邀请或停止整个服务。此功能使用本地 HTTP，适用于可信局域网，没有提供公网托管服务。

## 下载聊天记录、备份与费用

点击群聊右上角 **导出记录**，选保存位置和 Markdown（`.md`）、文本（`.txt`）或 JSON（`.json`）。导出当前群的**全部已保存记录**，包括发言者、时间、正文、收件人和已有轮次，不受界面最近 100 条的限制。文件为 UTF-8，不包含连接配置或密钥文件。讨论进行中导出的是当时的快照。

记录和设置位于 `%LOCALAPPDATA%\ModelRoom\room.sqlite3`。退出程序后可备份整个 `%LOCALAPPDATA%\ModelRoom` 文件夹。密钥由 Windows DPAPI 绑定当前用户加密，复制到另一台电脑或另一用户通常需要重新填写；不要把数据目录放进公开源码仓库。

每个 API 请求和每轮讨论分别使用对应服务的额度，联网搜索也可能计费。本版只内置官方 DeepSeek 余额查询；其他服务到其控制台查询。回复详情中的 token 是单次服务返回的用量，**不是统一的剩余 token 或余额**。

## 遇到问题先看这里

| 现象 | 检查办法 |
| --- | --- |
| 401 / 403 | Key、权限、区域是否匹配；Claude 是否需要工作区 ID |
| 402 / 余额不足 | 在该服务控制台检查可用额度 |
| 404 / 型号不存在 | 基础地址是否重复添加 `/v1`，型号是否准确，请求格式是否匹配 |
| 429 / 请求过多 | 减少成员或轮数，稍后再试，并检查服务商限额 |
| 思考参数报错 | 改回供应商默认，再按该型号文档选择协议 |
| 读得到模型却不能聊天 | 列表不保证聊天权限；选支持本版接口的文字模型 |
| Codex 找不到 | 选择完整 `codex.exe` 路径；桌面已安装不一定代表终端 PATH 可用 |
| Claude Code 失败 | 检查原生 EXE、登录及 CLI 版本；本版不自动安装或登录 |
| 队友连不上 | 检查同一局域网、主机网卡、入站权限及 Wi-Fi 客户端隔离 |

## 源码与构建

源码包保留全部 Python、H5、Windows 启动器和五份说明。用含 Tkinter 的 Windows x64 Python 3.10+：

```powershell
python -m pip install -r requirements.txt
python .\model_room.py
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File .\build-windows.ps1
```

构建产物是 `dist\ModelRoom.exe`；发布包命名为 `ModelRoom-v1.0-Windows-x64.exe`。`room_presets.py` 管预设，`room_providers.py` 管 API，`room_claude.py` 管本机 Claude Code，`room_style.py` 管桌面图标与样式。原有 v0.6 配置会按兼容模式读取。本版已用本地模拟接口验证适配和旧功能；每个服务的实际可用型号、账号权限及收费以对应平台为准。
