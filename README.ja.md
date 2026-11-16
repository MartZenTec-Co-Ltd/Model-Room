# Model Room v1.1 · 使い方

[简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md) · [English](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

人間と複数の AI が同じグループで対話するアプリです。v1.1 では Linux/macOS のネイティブパッケージと、メンバー別 Markdown 性格設定を追加しました。[MIT ライセンス](LICENSE)。

## ダウンロード

[Releases](https://github.com/MartZenTec-Co-Ltd/Model-Room/releases) で OS に合った完成版を選んでください。Python、Tcl/Tk、Pillow を同梱しているため、Python の別途インストールは不要です。Code → Download ZIP は開発用ソースです。

| Platform | Download | Requirements |
| --- | --- | --- |
| Windows | `ModelRoom-v1.1-Windows-x64.exe` | Windows 10/11 x64 |
| Linux portable | `ModelRoom-v1.1-Linux-x86_64.AppImage` | x86_64, glibc 2.35+, X11/XWayland |
| Debian / Kali | `model-room_1.1_amd64.deb` | amd64, compatible Debian-family dependencies |
| macOS Apple Silicon | `ModelRoom-v1.1-macOS-arm64.dmg` or `.zip` | macOS 15+, Apple Silicon |
| macOS Intel | `ModelRoom-v1.1-macOS-x86_64.dmg` or `.zip` | macOS 15+, Intel |


AppImage は `chmod +x ModelRoom-v1.1-Linux-x86_64.AppImage` 後に起動します。FUSE が利用できない場合は `./ModelRoom-v1.1-Linux-x86_64.AppImage --appimage-extract-and-run` を使用できます。DEB は `sudo apt install ./model-room_1.1_amd64.deb`。ARM Linux は含みません。検証済み環境はリリースノートを参照してください。

macOS は CPU に合った DMG を開き、ModelRoom.app を Applications にコピーします。ZIP もあります。本版は ad-hoc 署名のみで、**Developer ID 署名・Apple 公証はありません**。Gatekeeper が初回起動を止める場合があります。出所と SHA256 を確認し、[Apple の説明](https://support.apple.com/en-us/102445)を参照してください。セキュリティ機能は無効化しません。

## 最初の会話

1. 設定 → 接続設定 → モデル接続でプリセットを追加。自分の API キーを入力し、モデル一覧から文字チャット対応モデルを選んで保存します。
2. グループを作成し、AI メンバー管理で利用可能なモデルを 2～3 席追加して保存。接続保存だけではグループに参加しません。
3. 送信は各メンバー 1 回の返信です。ラウンド数を 2 以上にして討論すると、次のラウンドで直近の同僚の発言を参照します。
4. 自分の発言ボタンで、送信済みの返信完了後に一時停止。補足を送って再開します。固定 AI 司会者はありません。最大 8 席、同時に討論できるのは 1 グループです。

## AI の性格

設定 → **AI の性格**でメンバーを選び、テンプレート・直接編集・UTF-8 Markdown 読み込みを利用します。最大 12,000 文字、64 KB。適用または OK で保存し、キャンセルは未保存変更を破棄。空欄は既定のスタイルです。

グループと席ごとに保存し、通常返信と全討論ラウンドに適用。API、Codex、Claude Code、Harness に対応します。Markdown は文字列として扱い実行しません。権限も追加しません。選択したメンバーのサービスに送るため、機密情報は書かないでください。[性格ガイド](PERSONALITIES.ja.md)。

## 主な接続

| Preset | Configuration |
| --- | --- |
| DeepSeek | Provider API Key → List models → choose a text chat model |
| OpenAI / GPT API | OpenAI Platform API Key; Chat Completions-compatible text model |
| Claude / Anthropic API | Claude Messages API Key; workspace ID when required |
| Codex · Local | Install and sign in to Codex CLI, auto-detect or select its executable |
| Claude Code · Local | Install and sign in to a supported CLI, save connection and add a seat |
| Other providers | Built-in presets or a custom compatible endpoint; see [preset catalog](examples/presets.json) |


プリセットはアカウント・キー・残高・モデル本体を含みません。利用モデルと思考モードはサービス次第です。ChatGPT 契約と API 残高は別です。本機 Codex は CLI を呼び出し、現在のデスクトップ会話は操作しません。討論時は読み取り専用。料金は各サービスに従い、残高照会は公式 DeepSeek のみです。token 表示は 1 回の使用量です。

## そのほか

宛先選択や先頭の `@名前`、Codex/Brave/SearXNG を設定した検索、信頼できる同一 LAN 内のブラウザー参加、全保存会話の Markdown・テキスト・JSON 出力を利用できます。LAN は HTTP で、公開ホスティングではありません。招待開始前の記録はゲストに見せません。出力にキー設定は含みません。

五言語 UI、名前・アバター・壁紙・テーマ・入力設定に対応し、過去の発言は自動翻訳しません。

データ: Windows `%LOCALAPPDATA%\ModelRoom`、Linux `${XDG_DATA_HOME:-~/.local/share}/modelroom`、macOS `~/Library/Application Support/ModelRoom`。テストには `MODELROOM_DATA_DIR` を指定できます。

Windows は従来の DPAPI と v1.0 データを維持。Linux/macOS は Fernet 暗号化と 0600 のローカル鍵、0700 ディレクトリを使用します。**OS キーチェーンやパスワード式保管庫ではありません**。同一ユーザーで全体にアクセスできるプログラムは復号可能です。フォルダー全体とバックアップを保護してください。モデルには必要な文字コンテキストが送られますが、壁紙とアバターは送りません。エラー報告では秘密情報を隠してください。

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
