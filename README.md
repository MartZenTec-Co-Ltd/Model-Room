# Model Room v1.1 · User guide

[简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md) · [English](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

Bring people and multiple AI members into one shared room. Version 1.1 adds native Linux/macOS packaging and per-member Markdown personalities. [MIT license](LICENSE).

## Download and install

Download your platform's binary from [Releases](https://github.com/MartZenTec-Co-Ltd/Model-Room/releases). Binaries include Python, Tcl/Tk and Pillow; users do not need to install Python. Code → Download ZIP is developer source.

| Platform | Download | Requirements |
| --- | --- | --- |
| Windows | `ModelRoom-v1.1-Windows-x64.exe` | Windows 10/11 x64 |
| Linux portable | `ModelRoom-v1.1-Linux-x86_64.AppImage` | x86_64, glibc 2.35+, X11/XWayland |
| Debian / Kali | `model-room_1.1_amd64.deb` | amd64, compatible Debian-family dependencies |
| macOS Apple Silicon | `ModelRoom-v1.1-macOS-arm64.dmg` or `.zip` | macOS 15+, Apple Silicon |
| macOS Intel | `ModelRoom-v1.1-macOS-x86_64.dmg` or `.zip` | macOS 15+, Intel |


AppImage: run `chmod +x ModelRoom-v1.1-Linux-x86_64.AppImage`, then launch it. A suitable FUSE environment is normally required; otherwise use `./ModelRoom-v1.1-Linux-x86_64.AppImage --appimage-extract-and-run`. DEB: `sudo apt install ./model-room_1.1_amd64.deb`. ARM Linux is not included. A minimum library version is not a claim that every distribution has been tested; see release validation notes.

macOS: select your CPU architecture, open the DMG and drag ModelRoom.app into Applications, or unpack the ZIP. This build is ad-hoc signed, **not Developer ID signed or Apple notarized**. Gatekeeper may block initial launch. Verify the source and SHA256 and consult [Apple's guidance](https://support.apple.com/en-us/102445). The app does not disable system security.

## First conversation

1. Settings → Connections → Model connections: add a quick preset, enter your own API key, list models, select a compatible text model and save.
2. Create a named room. In AI members, add two or three configured model seats and save the roster. Saving a connection does not add a room member automatically; one connection can supply several seats.
3. Send requests one reply from each selected member. Enter at least two Rounds and click Discuss for later rounds to use recent peer replies.
4. My turn pauses after dispatched replies finish. Add your requirement and choose Send & resume. There is no fixed AI chairperson. Up to eight seats per room; one room runs a discussion at a time. Evaluate model suggestions yourself.

## AI personalities

Settings → **AI personalities**: select a member in this room, use a template, edit text or import UTF-8 `.md`. Limit: 12,000 characters, 64 KB per imported file. Apply/OK saves; Cancel discards unapplied edits. Blank means the default style.

Preferences are stored per room and per seat and apply to ordinary replies and every discussion round, including API models, Codex, Claude Code and Harness. Markdown is text, never executed, and grants no extra tools or file permissions. The selected member's preferences are sent to its provider; do not put secrets in them. See the [personality guide](PERSONALITIES.md).

## Common connections

| Preset | Configuration |
| --- | --- |
| DeepSeek | Provider API Key → List models → choose a text chat model |
| OpenAI / GPT API | OpenAI Platform API Key; Chat Completions-compatible text model |
| Claude / Anthropic API | Claude Messages API Key; workspace ID when required |
| Codex · Local | Install and sign in to Codex CLI, auto-detect or select its executable |
| Claude Code · Local | Install and sign in to a supported CLI, save connection and add a seat |
| Other providers | Built-in presets or a custom compatible endpoint; see [preset catalog](examples/presets.json) |


Presets contain no accounts, keys, balances or model weights. They do not install agents. Available models and thinking options depend on the provider and account. ChatGPT subscriptions are not API balances. Local Codex invokes the CLI, not the current desktop chat; discussion is read-only and file edits require an explicit ordinary-message opt-in. Only official DeepSeek balance lookup is built in. Reply token counts are per-request usage, not a universal remaining allowance. Discussions and search may incur charges.

## Other features

- Send to everyone, one member, or post without requesting a reply; leading `@nickname` mentions are supported.
- Configure Codex, Brave or SearXNG before enabling Web search. Sources are supplied as reference material; models are not assumed to have native live browsing.
- LAN invite: select host IPv4 and port, enable an invitation and let teammates on the same trusted LAN join in a browser. Uses HTTP, not public hosting. Guests see messages saved after sharing was enabled.
- Export all saved messages in the current room to Markdown, text or JSON. Key configuration and avatar files are excluded; exporting mid-discussion captures a snapshot.
- Five UI languages, nicknames, avatars, full chat wallpaper, themes and input settings. Existing chat text is not translated.

## Data and credentials

Windows: `%LOCALAPPDATA%\ModelRoom`; Linux: `${XDG_DATA_HOME:-~/.local/share}/modelroom`; macOS: `~/Library/Application Support/ModelRoom`. `MODELROOM_DATA_DIR` provides an isolated development/test location.

Windows keeps DPAPI and existing v1.0 data. Linux/macOS use Fernet encryption, a local mode-0600 key file and mode-0700 directory; **this is not an OS keychain or a password-protected vault**. Processes with access to the full directory as the same user may decrypt it. Protect the entire directory and backups. Model requests send relevant text context. Avatars/wallpapers are not sent to models; LAN guests may see message names and small avatars.

401/403: check key, region and permissions. 429: reduce members/rounds. Discovery may list non-chat models; select a compatible text model. Redact secrets from error reports.

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
