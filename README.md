# Model Room v1.0 for Windows

[简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md) · [English](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

**A group chat for you, your teammates, and multiple AI participants.** Keep separate named rooms, let models respond to one another, pause to speak, invite LAN browser guests, and export transcripts. The three-column desktop layout is retained.


## Public release v1.0 — Windows x64 only

**For ordinary users: download `ModelRoom-v1.0-Windows-x64.exe` from this repository's Releases page and double-click it. You do not need to install Python, pip, Tkinter or Pillow.** The EXE contains its own runtime and extracts a local cache on first launch; it does not download Python or search PATH for Python.

The Windows ZIP contains the same EXE plus five guides and license notices. GitHub's **Code → Download ZIP** and `ModelRoom-v1.0-Source.zip` contain developer source; they are not the normal app download. Python is needed only to run or build the source. Supported binary platform: **Windows 10/11 x64**. No Linux/macOS build is released yet.

Configure your own API credentials or a separately installed/logged-in local agent. Model weights and paid accounts are not bundled. Existing local conversations and settings are reused.

**License:** [MIT](LICENSE). See [release notes](RELEASE_NOTES.md), [contributing](CONTRIBUTING.md), and [third-party notices](THIRD_PARTY_NOTICES.md). Maintainers can build with `release-windows.ps1`; the GitHub workflow builds a standalone EXE without publishing a Release automatically.


## full chat wallpaper, your profile and practical settings

The wallpaper now covers the entire message area behind the bubbles, including when you scroll or resize. Navigation, room details, the header and composer remain solid panels for readability. In Appearance choose **Fill** (may crop edges), **Fit** (whole image with margins) or **Tile**, with 0–100% image strength. Bubbles and name chips remain readable. Chat font size is 10–18 points. Wallpaper stays on the host computer.

Settings now contains **General / Connections / Appearance / Chat & input / Data & storage / About**. General includes **My nickname**, **My nickname in this group**, and avatar selection/removal. Empty group nicknames use the main nickname; both empty use the localized “You” label. Names are at most 32 characters. Avatars are center-cropped to a circle, copied into local app data and stripped of metadata. New messages snapshot the nickname and avatar asset; later changes do not rewrite those saved names. Legacy messages without profile metadata follow the current profile. Model routing IDs stay unchanged.

LAN guests can see the host nickname and the small avatar attached to shared messages. Only a small PNG is sent, never the local image path; avatars and wallpapers are not sent to AI models. Nicknames appear in text context and transcript exports. Exports omit avatar image files and connection keys.

Chat & input has switches for **Enter to send**, **Show message times**, and **Auto-scroll**, plus default discussion rounds. With Enter to send off, use Ctrl+Enter; Shift+Enter always inserts a new line. Defaults apply on startup and group switching; the composer still allows temporary round counts. Data & storage opens/copies the data folder and exports the current group. About shows the version and supported languages. Apply saves preferences while staying on the same page, OK saves and closes, and Cancel discards unapplied preferences. Explicit connection Save buttons still save separately.

The profile/font/background organization was informed by [Signal profiles](https://support.signal.org/hc/en-us/articles/360007059952-Edit-my-Profile), [Signal font sizes](https://support.signal.org/hc/en-us/articles/360049670791-Font-Size-Options) and [Telegram wallpapers](https://telegram.org/blog/animated-backgrounds). These products are design references, not dependencies.

## settings layout fixes

Boolean settings use phone-style switches with the label on the left and the switch on the right, including startup agent detection and Dark mode. Click to toggle; Tab focuses the switch, Space/Enter toggles it and Left/Right selects off/on. Chat controls retain their existing layout.

A divider and fixed bottom-right **Apply / OK / Cancel or Close** bar are shared by all settings pages. Apply saves General, Appearance and Chat preferences while keeping Settings open on the current page, with unfinished connection fields retained in memory. OK saves those preferences and closes. Cancel, Escape or the window close button discards unapplied preference changes; already applied preferences and explicitly saved connections remain saved. Connection forms still have their own Save buttons. Unfinished keys are not copied to logs or public release files.

General and Appearance scroll independently, the footer stays visible at the minimum 840 × 560 size, long labels wrap, and selected navigation is highlighted. Five UI languages and light/dark themes are retained.

## Settings, five UI languages and local agents

Open **Settings** at the lower left, or press `Ctrl+,`. Navigation is ordered as follows:

1. **General**: choose Simplified Chinese, Traditional Chinese, English, Japanese or Korean for the actual desktop UI, and toggle automatic local-agent detection. User group names, nicknames, model IDs and original messages are never translated.
2. **Connections**: model connections, search, Local Codex and Local agents. Older references to Connection settings below now live inside this section.
3. **Appearance**: Light/Dark mode, custom accent, local JPG/PNG/WebP/GIF/BMP images, image strength and reset. The wallpaper covers the full message area while retaining the three columns. They are decoded, stripped of metadata and copied into local app data; never uploaded to models. Applying preferences preserves the composer draft and history. Unfinished connection forms are retained when Apply is used.

**Automatic detection only locates installed programs. It does not install, log in, request paid model replies or join groups.** In Connections → Local agents, detect, select, optionally check the version, then Save local connection. Finding a program does not verify authentication or allowance.

- **Codex**: detects native `codex.exe` on PATH and in the desktop CLI cache. Save and add it to the current group; check login separately.
- **Claude Code**: supports native executables and npm wrappers that resolve to an installed Node.js package. Wrapper scripts are not executed through a command shell. Save, then add a member.
- **DeepSeek Harness**: detects `dsh`, passes the task over stdin to headless mode, and requests read-only policy with interactive approvals denied. Models follow Harness configuration. Headless may require `DEEPSEEK_API_KEY`; a GUI login is not necessarily used. Unsupported policy flags fail rather than being silently removed. An uninstalled agent remains unavailable. See the official [CLI](https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli) and [headless guide](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/bundle/headless).

LAN H5 guests can independently choose the same five languages. Their preference is stored in the browser; original messages stay unchanged. Desktop wallpaper and appearance are not shared with guests. Preferences are stored in the existing database; saved rooms, connections and encrypted keys are retained.

**Harness compatibility:** Desktop packages and portable running installations can be detected, but a detected executable is not proof of working authentication. Older versions such as `0.2.1-rc.2` may lack the required headless read-only/approval-policy options. Check the installed CLI help and update when necessary. The adapter does not silently remove required policy flags.

## Start in three steps

1. Run `ModelRoom-v1.0-Windows-x64.exe` on Windows x64. Python is included. Existing local rooms and settings are reused; presets do not automatically replace saved connections.
2. Open **Connections → Model connections** (Connection settings → Model connections). Select **Quick preset → Add preset** (Quick preset → Add this preset), enter your own key, click **List models** (List models), choose a text chat model, and **Save connection** (Save connection). **Then open AI members (Manage AI members), add that model to this room, and save the roster.** For local Codex, use its example below.
3. Use **New group** (New room), name it, select members, and send a question. **Send** (Send) requests one reply per selected member; **Discuss** (Free discussion) uses your entered round count. Start small to verify connectivity.

The settings window scrolls vertically. **Official docs** opens the selected preset's official documentation.

## What the terms mean

| Term | Purpose | Required |
| --- | --- | --- |
| API connection | Endpoint, model, and authentication settings | That provider's key and available allowance |
| AI member | One model seat in a particular room | A saved connection; several seats can use different models from it |
| Local Codex | Runs the installed Codex CLI | CLI and its login; does not control the current Codex chat window |
| Local Claude Code | Runs the native Claude Code CLI | `claude.exe` and its login or API configuration |
| Preset | Fills public endpoint and request-format fields | Does not supply keys, accounts, model downloads, or credits |

Cloud models receive separate requests; their weights are not downloaded into this application.

## Five common setup examples

### 1. DeepSeek

Choose **DeepSeek official**, add the preset, enter a DeepSeek platform key, list models, select a chat model, and save. Add it to the room using **AI members**. An existing default DeepSeek connection can continue to be used.

**Test chat** (Test chat) sends a real, potentially billable request. Reply **Details** (Details) shows endpoint, returned model, elapsed time, and provider-reported usage. **DeepSeek balance** checks the official balance endpoint for official DeepSeek addresses. See [DeepSeek's guide](https://api-docs.deepseek.com/).

### 2. OpenAI / GPT API

Choose **OpenAI / GPT API**, enter an OpenAI Platform API key, list models, and choose a text model supporting Chat Completions. Save it and add a room member. The preset fills `https://api.openai.com/v1`.

This connection follows platform API authentication and usage rules. **Do not treat a ChatGPT subscription allowance as an API key balance**; check your platform project, permissions, and allowance. Responses-only models are not supported by this adapter. See [official API documentation](https://developers.openai.com/api/reference/chat-completions/overview).

### 3. Local Codex

Choosing **Codex · Local** switches to **Local Codex** (Local Codex). Click **Auto-detect → Check login** (Auto-detect → Check login). If needed, **Select CLI** selects `codex.exe`. If signed out, **Copy login command** copies a command for you to run and complete in PowerShell. In **AI members**, select **Add Codex → Save group members** (Add Codex → Save roster).

No API URL is required. Usage follows the CLI's active ChatGPT or API-key authentication. Codex is read-only during discussion. For an ordinary message that requests file changes, choose a project directory and explicitly enable **Codex file edits**. See [official authentication guidance](https://learn.chatgpt.com/docs/auth).

### 4. Claude / Anthropic API

Choose **Claude / Anthropic API** and enter a Claude Console API key. The preset uses **Claude native · Messages** at `https://api.anthropic.com/v1`. If the key is not scoped to one workspace, enter the Console's `wrkspc_…` ID in **Claude workspace ID**. List models, save, and add a room member.

Start with **Provider default** (Provider default) reasoning. Supported newer models may use `adaptive`; legacy models may use `budget_tokens`. Not every model accepts every mode. See [official API and authentication documentation](https://platform.claude.com/docs/en/api/overview).

### 5. Local Claude Code

Install and sign in to the native CLI using [Claude Code's documentation](https://code.claude.com/docs/en/cli-reference). Choose **Claude Code · Local**. Leave **Service URL / CLI** (Service URL / CLI) blank to auto-detect `claude.exe`, or enter its full path. Native executables and resolvable npm wrappers are supported; wrapper scripts are not shell-executed. The initial model alias is `sonnet`; you can enter `opus`, `haiku`, or another ID supported by your CLI.

Save and add it as a room member. The adapter disables tools, MCP, custom skills, and ordinary configuration hooks, and chats from a temporary directory without modifying your project. Organization-managed policies may still apply. Authentication and billing follow the CLI configuration, **which is different from adding a Claude API key here**. Reasoning supports default, on, or high; low effort is not presented as disabled thinking.

## All quick presets

| Preset (exact UI label) | Request format | Address / method |
| --- | --- | --- |
| [DeepSeek official](https://api-docs.deepseek.com/) | OpenAI-compatible | `https://api.deepseek.com` |
| [OpenAI / GPT API](https://developers.openai.com/api/reference/chat-completions/overview) | OpenAI-compatible | `https://api.openai.com/v1` |
| [Codex · Local](https://learn.chatgpt.com/docs/auth) | Local CLI | Auto-detect or enter executable path |
| [Claude / Anthropic API](https://platform.claude.com/docs/en/api/overview) | Claude Messages | `https://api.anthropic.com/v1` |
| [Claude Code · Local](https://code.claude.com/docs/en/cli-reference) | Local CLI | Auto-detect or enter executable path |
| [Google Gemini](https://ai.google.dev/gemini-api/docs/openai) | OpenAI-compatible | `https://generativelanguage.googleapis.com/v1beta/openai` |
| [OpenRouter](https://openrouter.ai/docs/api-reference/overview) | OpenAI-compatible | `https://openrouter.ai/api/v1` |
| [Qwen · Beijing](https://www.alibabacloud.com/help/en/model-studio/base-url) | OpenAI-compatible | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| [Qwen · Singapore](https://www.alibabacloud.com/help/en/model-studio/base-url) | OpenAI-compatible | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| [Kimi / Moonshot · China](https://platform.moonshot.cn/docs/api/chat) | OpenAI-compatible | `https://api.moonshot.cn/v1` |
| [Zhipu GLM · China](https://docs.bigmodel.cn/cn/guide/develop/openai/introduction) | OpenAI-compatible | `https://open.bigmodel.cn/api/paas/v4` |
| [Z.AI / GLM · Global](https://docs.z.ai/guides/overview/quick-start) | OpenAI-compatible | `https://api.z.ai/api/paas/v4` |
| [Doubao / Volcengine · Beijing](https://docs.volcengine.com/docs/ark/APICallGuide?lang=zh) | OpenAI-compatible | `https://ark.cn-beijing.volces.com/api/v3` |
| [MiniMax · China](https://platform.minimax.cn/docs/api-reference/text-openai-api) | OpenAI-compatible | `https://api.minimax.cn/v1` |
| [MiniMax · Global](https://platform.minimax.io/docs/api-reference/text-openai-api) | OpenAI-compatible | `https://api.minimax.io/v1` |
| [SiliconFlow](https://docs.siliconflow.cn/docs/userguide/quickstart) | OpenAI-compatible | `https://api.siliconflow.cn/v1` |
| [Groq](https://console.groq.com/docs/openai) | OpenAI-compatible | `https://api.groq.com/openai/v1` |
| [Mistral](https://docs.mistral.ai/api) | OpenAI-compatible | `https://api.mistral.ai/v1` |
| [xAI / Grok](https://docs.x.ai/developers/quickstart) | OpenAI-compatible | `https://api.x.ai/v1` |
| [Ollama · Local](https://docs.ollama.com/api/openai-compatibility) | OpenAI-compatible | `http://127.0.0.1:11434/v1` |
| [LM Studio · Local](https://lmstudio.ai/docs/developer/openai-compat) | OpenAI-compatible | `http://127.0.0.1:1234/v1` |
| Custom OpenAI-compatible | OpenAI-compatible | Enter your endpoint |

Cloud presets leave the model ID blank so you can list account-specific models. A list may also include embedding or audio models: select a text chat model. If discovery is unavailable, enter the exact ID manually. Qwen Beijing and Singapore use region-specific keys; pay-as-you-go keys and Coding Plan endpoints are not interchangeable. Endpoints remain editable.

Supported transports are OpenAI-compatible Chat Completions, Claude Messages, and the two local CLIs. Dedicated Azure, Bedrock, and Vertex IAM authentication is not implemented; use a suitable compatible gateway if needed. `examples/presets.json` is a public, key-free reference catalog, not a file with a UI import button.

## Rooms, discussions, and files

- Rooms independently store names, transcripts, rosters, and optional directories. Each supports up to eight AI seats. API connections are global; memberships are per room.
- **Send to** (Send to) selects all, one member, or **Post only** (Post without requesting AI replies). Leading `@nickname` mentions also work. Send requests one response each. Enter an integer of at least two under **Rounds**, then start free discussion. Members receive recent peer replies; no chairperson is assigned.
- **My turn** (My turn) pauses after already-dispatched replies finish. Enter your note and choose **Send & resume** (Speak and resume); the next round considers it. You can resume or stop. The desktop runs AI discussion in one room at a time.
- **Web search** (Web search) sends the current question to the configured search backend and gives sources to the selected models. Configure Codex search, Brave, or your SearXNG server first. Brave needs a separate search key; SearXNG needs JSON enabled.
- Ordinary API requests normally include that seat's recent conversation. **Share history** shares more room history. Context is bounded; keeping a full local transcript does not mean sending it all every time.
- Choose, open, or copy a project directory. Selecting one does not upload its contents. API models and this Claude Code adapter do not automatically read it. Codex edits require an ordinary message and the explicit file-edit toggle.

## Invite LAN browser guests

Open **LAN invite** (LAN participation), select the host IPv4 and port, then **Enable invitation** (Enable invitation). Share the link with teammates on the same trusted LAN; they join with a nickname. `127.0.0.1` is local-only. Other devices need your LAN address and appropriate Windows inbound permission.

Guests see only this room's messages saved after sharing was enabled. Their posts are saved and considered in later discussion. Revoke one invitation or stop the whole server. This is local HTTP for a trusted LAN, not a public hosting service.

## Export, backup, and cost

Use **Export chat** (Export history) at the room's top right, choose a destination, and select Markdown (`.md`), text (`.txt`), or JSON (`.json`). UTF-8 exports include **all saved messages in this room**, authors, times, bodies, recipients, and recorded rounds, beyond the UI's latest 100 messages. Connection settings and key files are excluded. Exporting mid-discussion captures the messages saved so far.

Data and settings live in `%LOCALAPPDATA%\ModelRoom\room.sqlite3`. After exiting, back up the whole `%LOCALAPPDATA%\ModelRoom` folder. Windows DPAPI binds encrypted keys to the current user; moving data to another user or PC generally requires re-entering keys. Keep this data folder out of public source repositories.

Each request and discussion round uses its corresponding provider's allowance; search may also cost money. Only official DeepSeek balance lookup is built in. Check other balances in provider consoles. Reply token counts are per-request usage, **not a universal remaining-token balance**.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| 401 / 403 | Key, permissions, region, and any required Claude workspace ID |
| 402 / insufficient balance | The provider console's available allowance |
| 404 / unknown model | Repeated `/v1`, exact model ID, and matching request format |
| 429 | Reduce members or rounds, retry later, and check limits |
| Rejected reasoning parameter | Return to provider default, then check model documentation |
| Listed model cannot chat | Select a permitted text model supporting this adapter's endpoint |
| Codex not found | Select the full `codex.exe` path; a desktop install need not put it on PATH |
| Claude Code failure | Native executable, login, and compatible CLI version; no automatic installation or login |
| Guest cannot connect | LAN address, network adapter, inbound permission, and Wi-Fi client isolation |

## Source and build

The source package retains Python, H5, the Windows launcher, and all five guides. Use Windows x64 Python 3.10+ with Tkinter:

```powershell
python -m pip install -r requirements.txt
python .\model_room.py
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File .\build-windows.ps1
```

The build creates `dist\ModelRoom.exe`; the release is named `ModelRoom-v1.0-Windows-x64.exe`. Presets, APIs, local Claude Code, and desktop styling are in `room_presets.py`, `room_providers.py`, `room_claude.py`, and `room_style.py`. Existing v0.6 configurations remain compatible. Adapters and existing behavior were checked with local fixtures; real model availability, account permissions, and charges depend on each provider.
