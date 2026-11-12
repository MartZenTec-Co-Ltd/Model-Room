# Model Room v1.0 · Windows ガイド

[简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md) · [English](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

**あなた、チームの仲間、複数の AI が参加するグループチャットです。** 名前付きルーム、モデル同士の討論、人間の途中参加、LAN ブラウザー参加、履歴のエクスポートを備え、3列の画面構成を維持しています。


## 公開版 v1.0 — 現在は Windows x64 のみ

**一般ユーザーは、このリポジトリの Releases から `ModelRoom-v1.0-Windows-x64.exe` をダウンロードしてダブルクリックしてください。Python、pip、Tkinter、Pillow のインストールは不要です。** EXE に実行環境を内蔵し、初回起動時にローカルへ展開します。Python の追加ダウンロードや PATH 上の Python は使用しません。

Windows ZIP は同じ EXE と5言語ガイド、ライセンスを含みます。GitHub の **Code → Download ZIP** と `ModelRoom-v1.0-Source.zip` は開発用ソースであり、一般向け実行ファイルではありません。Python が必要なのはソース実行・ビルド時だけです。対応バイナリは **Windows 10/11 x64**。Linux/macOS 版は未公開です。

会話には自分の API 認証情報、または別途導入・ログインしたローカル Agent を設定してください。モデルの重みや有料アカウントは含みません。既存のローカル履歴と設定は継続使用します。

**ライセンス：[MIT](LICENSE)**。[公開手順](RELEASE_NOTES.md)、[貢献ガイド](CONTRIBUTING.md)、[第三者ライセンス](THIRD_PARTY_NOTICES.md)も参照してください。`release-windows.ps1` で配布物を作成できます。GitHub ワークフローは EXE をビルドしますが、Release の一般公開は自動実行しません。


## 会話全体の背景、プロフィール、日常設定

背景は気泡の背後の会話エリア全体に表示し、スクロールやサイズ変更にも追従します。サイドバー・詳細・ヘッダー・入力欄は読みやすい単色パネルを維持します。外観で **画面を埋める**（端を切り取る場合あり）、**画像全体を表示**（余白あり）、**タイル**を選択し、濃さを0〜100%で調整できます。気泡と名前の背景は読みやすく保ち、文字サイズは10〜18です。背景はホスト内だけで使用します。

設定は **一般 / 接続設定 / 外観 / チャットと入力 / データと保存 / このアプリについて** の6項目です。一般で共通表示名、グループ別表示名、アバターを設定できます。グループ別を空欄にすると共通名を使い、両方空欄なら現在の言語の「あなた」を使います。32文字以内。画像は中央を円形に切り抜き、メタデータを除去してローカル保存します。新着メッセージは名前と画像を記録するため、その後の変更は保存済み署名を書き換えません。旧形式の履歴は現在のプロフィールを使用します。内部のルーティングIDは変えません。

LAN参加者には共有済みメッセージの名前と小さなPNGアバターを表示します。ローカルパスは送信せず、画像をAIモデルへ渡しません。名前は文字コンテキストと履歴書き出しに使用します。書き出しには画像ファイルや接続キーを含めません。

チャットと入力ではEnter送信、時刻表示、自動スクロール、既定の討論回数を設定します。Enter送信をオフにするとCtrl+Enterで送信し、Shift+Enterは常に改行します。回数は起動・グループ切替時に使い、入力欄で一時変更できます。データと保存では保存先を開く・コピーする・履歴を書き出す操作を提供します。適用は同じページを保持し、OKは保存して閉じ、キャンセルは未適用の設定を破棄します。接続は専用の保存ボタンで保存します。

構成は[Signalプロフィール](https://support.signal.org/hc/en-us/articles/360007059952-Edit-my-Profile)、[文字サイズ](https://support.signal.org/hc/en-us/articles/360049670791-Font-Size-Options)、[Telegram背景](https://telegram.org/blog/animated-backgrounds)を参考にしました。これらは実行時の依存製品ではありません。

## 設定画面の修正

設定の真偽値項目は、説明を左、スマートフォン風スイッチを右に配置します。起動時のローカル Agent 検出とダークモードが対象です。クリックで切替、Tab でフォーカス、Space/Enter で切替、左右キーでオフ／オンを選択できます。チャット側の操作配置は維持します。

区切り線の下、右下に **適用 / OK / キャンセルまたは閉じる** を固定します。適用は一般・外観・チャットの設定を保存し、現在の設定ページと未保存の接続入力を保持します。OK は保存して閉じます。キャンセル、Esc、ウィンドウを閉じる操作は未適用の設定変更を破棄します。適用済み設定や明示的に保存した接続は維持されます。接続は各ページの保存ボタンで保存します。未保存のキーはメモリ内でのみ保持し、ログや配布ファイルへ出力しません。

一般・外観は個別にスクロールでき、最小 840 × 560 でも下部操作を表示します。長い説明は折り返し、選択中のページを強調します。5 言語と明暗テーマを継続します。

## 統一設定、5言語の画面、ローカル Agent

左下の **設定**、または `Ctrl+,` から開きます。

1. **一般**：簡体字中国語、繁体字中国語、英語、日本語、韓国語を実際の画面に適用し、起動時の Agent 検出を設定します。グループ名、ニックネーム、モデル ID、会話原文は変更しません。
2. **接続設定**：モデル、検索、ローカル Codex、ローカル Agent。以下の旧接続設定はこの項目内です。
3. **外観**：ライト／ダーク、アクセント色、ローカル JPG/PNG/WebP/GIF/BMP 画像、画像の濃さ、初期化。3列を維持して会話エリア全体に背景を表示します。画像はメタデータを除去してアプリ内にコピーし、モデルには送信しません。適用時も入力中の文章と履歴を保持します。適用時も未保存の接続フォームを保持します。

**検出はプログラムの場所だけを調べます。インストール、ログイン、有料モデル呼び出し、自動参加は行いません。** ローカル Agent で検出・選択し、必要ならバージョンを確認して接続を保存します。検出だけで認証や残高は確認できません。

- **Codex**：PATH とデスクトップ CLI キャッシュの `codex.exe` を検出し、保存してグループに追加できます。ログインは別途確認します。
- **Claude Code**：ネイティブ版と、導入済み Node.js パッケージに解決できる npm ラッパーに対応します。ラッパーをシェル実行しません。保存後にメンバーとして追加します。
- **DeepSeek Harness**：`dsh` の headless に stdin で議題を渡し、read-only と対話承認の拒否を指定します。モデルは Harness 側の設定です。headless に `DEEPSEEK_API_KEY` が必要な場合があり、GUI ログインとは別です。未対応の引数で失敗しても権限を自動で緩めません。未導入の Agent は利用可能と表示しません。[CLI](https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli)・[headless](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/bundle/headless)。

LAN H5 も5言語を選択でき、ブラウザーごとに保存します。会話原文は翻訳しません。デスクトップ画像と外観はゲストへ共有しません。設定は既存データベースに保存し、以前の接続と履歴、暗号化キーを保持します。

**Harness の互換性：** デスクトップ版や実行中のポータブル版を検出できますが、認証の成功を意味しません。`0.2.1-rc.2` など古い版は必要な headless の読み取り専用・承認ポリシー引数に未対応の場合があります。導入済み CLI のヘルプを確認し、必要なら更新してください。必須ポリシーを自動解除しません。

## 最初の3ステップ

1. Windows x64 で `ModelRoom-v1.0-Windows-x64.exe` を起動します。Python は同梱されています。旧バージョンのルームと設定を引き継ぎ、プリセットで既存接続を自動上書きしません。
2. 左の **接続設定 → モデル接続**（接続設定 → モデル接続）を開き、**接続プリセット → プリセットを追加**（プリセット → この設定を追加）を選びます。自分のキーを入力し、**モデル取得**で文字チャットモデルを選択して **接続を保存**。**その後、右の「AI メンバー管理」でモデルをルームに追加し、メンバーを保存してください。** ローカル Codex だけなら下の例から始められます。
3. **新しいグループ**でルームを作り、質問を入力します。**送信**は各メンバーが1回ずつ回答し、**討論する**は入力した回数の討論を行います。まず少ない回数で接続を確認してください。

設定画面は縦にスクロールできます。**公式資料**は選択したプリセットの公式資料を開きます。

## 接続とメンバーの違い

| 項目 | 意味 | 必要なもの |
| --- | --- | --- |
| API 接続 | 接続先、モデル、認証設定 | 各サービスのキーと利用枠 |
| AI メンバー | 特定ルームのモデル席 | 保存した接続。同じ接続から複数モデルを追加可能 |
| ローカル Codex | インストール済み CLI を実行 | CLI とログイン。現在の Codex チャット画面は操作しません |
| ローカル Claude Code | ネイティブ CLI を実行 | `claude.exe` とログインまたは API 設定 |
| プリセット | 公開 URL と送信形式を自動入力 | キー、アカウント、モデルのダウンロード、残高は含みません |

クラウドのモデルには個別にリクエストします。モデルの重みをこのアプリにダウンロードするものではありません。

## よく使う5つの設定例

### 1. DeepSeek

**DeepSeek 公式 → プリセットを追加**を選び、DeepSeek のキーを入力します。**モデル取得 → チャットモデルを選択 → 接続を保存**の順に進み、**AI メンバー管理**で追加します。既存の DeepSeek 接続も継続使用できます。

**チャットをテスト**は課金される可能性のある実リクエストです。返信の **詳細**に接続先、返されたモデル、時間、使用量を表示します。**DeepSeek 残高**は公式接続の残高照会です。[公式入門](https://api-docs.deepseek.com/)を参照してください。

### 2. OpenAI / GPT API

**OpenAI / GPT API**を選択し、OpenAI Platform の API キーを入力します。モデルを読み取り、Chat Completions 対応の文字モデルを選んで保存し、ルームに追加します。URL は `https://api.openai.com/v1` です。

認証と使用量はプラットフォーム API の規則に従います。**ChatGPT の契約枠を API キーの残高と同一視しないでください。** 権限と枠はプラットフォームで確認します。Responses 専用モデルは未対応です。[公式 API 資料](https://developers.openai.com/api/reference/chat-completions/overview)。

### 3. ローカル Codex

**Codex · ローカル**を選ぶと **ローカル Codex**タブに移動します。**自動検出 → ログイン確認**で確認し、必要なら **CLI を選択**で `codex.exe` を指定します。未ログインなら **ログインコマンドをコピー**を使い、自分の PowerShell で実行してログインしてください。**AI メンバー管理 → Codex を追加 → メンバーを保存**で追加します。

API URL は不要です。利用枠は CLI の ChatGPT または API キーログインに従います。討論中は読み取り専用です。通常送信でファイルを変更する場合はプロジェクトを選び、**Codex の編集を許可**を明示的に有効にします。[公式認証資料](https://learn.chatgpt.com/docs/auth)。

### 4. Claude / Anthropic API

**Claude / Anthropic API**を選び、Claude Console の API キーを入力します。形式は **Claude ネイティブ · Messages**、URL は `https://api.anthropic.com/v1`。ワークスペースが限定されていないキーには、Console の `wrkspc_…` を **Claude ワークスペース ID**に入力します。モデルを取得して保存し、メンバーに追加します。

推論はまず **プロバイダー既定**（プロバイダー既定）を使います。対応する新モデルには `adaptive`、旧モデルには `budget_tokens` を選べますが、すべてのモードが全モデルに対応するわけではありません。[公式 API と認証](https://platform.claude.com/docs/en/api/overview)。

### 5. ローカル Claude Code

[公式資料](https://code.claude.com/docs/en/cli-reference)に従ってネイティブ CLI をインストールし、ログインします。**Claude Code · ローカル**を選び、**接続先 / CLI**は自動検出なら空欄、手動なら `claude.exe` の完全パスを入力します。ネイティブ版と解決可能な npm ラッパーに対応し、ラッパーを直接実行しません。初期モデル別名は `sonnet`。CLI が対応する `opus`、`haiku`、モデル ID も入力できます。

保存後に **AI メンバー管理**から追加します。この接続はツール、MCP、独自スキル、通常設定のフックを無効にして一時ディレクトリで会話し、プロジェクトを変更しません。組織の管理ポリシーは適用される場合があります。認証と料金は CLI 設定に従い、**この画面に Claude API キーを設定する方法とは別です**。推論は既定、オン、強に対応し、低強度をオフとは表示しません。

## 全プリセット

| プリセット（画面の表記） | 送信形式 | 接続先 / 方法 |
| --- | --- | --- |
| [DeepSeek 公式](https://api-docs.deepseek.com/) | OpenAI-compatible | `https://api.deepseek.com` |
| [OpenAI / GPT API](https://developers.openai.com/api/reference/chat-completions/overview) | OpenAI-compatible | `https://api.openai.com/v1` |
| [Codex · ローカル](https://learn.chatgpt.com/docs/auth) | ローカル CLI | 自動検出または EXE パス入力 |
| [Claude / Anthropic API](https://platform.claude.com/docs/en/api/overview) | Claude Messages | `https://api.anthropic.com/v1` |
| [Claude Code · ローカル](https://code.claude.com/docs/en/cli-reference) | ローカル CLI | 自動検出または EXE パス入力 |
| [Google Gemini](https://ai.google.dev/gemini-api/docs/openai) | OpenAI-compatible | `https://generativelanguage.googleapis.com/v1beta/openai` |
| [OpenRouter](https://openrouter.ai/docs/api-reference/overview) | OpenAI-compatible | `https://openrouter.ai/api/v1` |
| [Qwen · 北京](https://www.alibabacloud.com/help/en/model-studio/base-url) | OpenAI-compatible | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| [Qwen · シンガポール](https://www.alibabacloud.com/help/en/model-studio/base-url) | OpenAI-compatible | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| [Kimi / Moonshot · 中国](https://platform.moonshot.cn/docs/api/chat) | OpenAI-compatible | `https://api.moonshot.cn/v1` |
| [Zhipu GLM · 中国](https://docs.bigmodel.cn/cn/guide/develop/openai/introduction) | OpenAI-compatible | `https://open.bigmodel.cn/api/paas/v4` |
| [Z.AI / GLM · グローバル](https://docs.z.ai/guides/overview/quick-start) | OpenAI-compatible | `https://api.z.ai/api/paas/v4` |
| [Doubao / Volcengine · 北京](https://docs.volcengine.com/docs/ark/APICallGuide?lang=zh) | OpenAI-compatible | `https://ark.cn-beijing.volces.com/api/v3` |
| [MiniMax · 中国](https://platform.minimax.cn/docs/api-reference/text-openai-api) | OpenAI-compatible | `https://api.minimax.cn/v1` |
| [MiniMax · グローバル](https://platform.minimax.io/docs/api-reference/text-openai-api) | OpenAI-compatible | `https://api.minimax.io/v1` |
| [SiliconFlow](https://docs.siliconflow.cn/docs/userguide/quickstart) | OpenAI-compatible | `https://api.siliconflow.cn/v1` |
| [Groq](https://console.groq.com/docs/openai) | OpenAI-compatible | `https://api.groq.com/openai/v1` |
| [Mistral](https://docs.mistral.ai/api) | OpenAI-compatible | `https://api.mistral.ai/v1` |
| [xAI / Grok](https://docs.x.ai/developers/quickstart) | OpenAI-compatible | `https://api.x.ai/v1` |
| [Ollama · ローカル](https://docs.ollama.com/api/openai-compatibility) | OpenAI-compatible | `http://127.0.0.1:11434/v1` |
| [LM Studio · ローカル](https://lmstudio.ai/docs/developer/openai-compat) | OpenAI-compatible | `http://127.0.0.1:1234/v1` |
| カスタム OpenAI 互換 | OpenAI-compatible | 自分の URL を入力 |

クラウドのモデル ID は空欄で開始し、アカウントの一覧から選べます。埋め込み・音声モデルも表示されるため、文字チャットモデルを選んでください。一覧 API がなければ正確な ID を手入力できます。百煉の北京・シンガポールのキーは地域別で、従量課金と Coding Plan の接続先も混用できません。URL は変更できます。

OpenAI 互換チャット、Claude Messages、2つのローカル CLI に対応しています。Azure、Bedrock、Vertex 独自の IAM 認証は未実装です。必要なら適切な互換ゲートウェイを利用してください。`examples/presets.json` はキーを含まない参照用カタログで、JSON インポートボタンはありません。

## ルーム、討論、ディレクトリ

- 各ルームの名前、履歴、メンバー、任意のディレクトリを独立保存します。AI は最大8席。接続設定は共通、メンバー構成はルーム別です。
- **送信先**で全員、1人、**投稿のみ**（AI に回答を求めない投稿）を選べます。先頭の `@ニックネーム` も使用できます。**ラウンド数**は2以上の整数を入力します。後のラウンドでは最近の仲間の発言を参照し、特定の司会者は置きません。
- **発言する**は送信済みの回答が終わってから一時停止します。補足して **発言して再開**を押すと次のラウンドに反映します。再開・停止も可能です。デスクトップで同時に実行する AI 討論は1ルームです。
- **ウェブ検索**は今回の質問を検索バックエンドへ送り、出典をモデルに渡します。設定で Codex、Brave、自前 SearXNG を選びます。Brave は別の検索キー、SearXNG は JSON 有効化が必要です。
- 通常の API 送信はその席の最近の会話を付けます。**履歴を共有**で共有範囲を広げますが、コンテキストには長さ制限があり、全履歴を毎回送るわけではありません。
- 目録は選択・表示・パスのコピーができます。選択だけで全ファイルをアップロードしません。API と本版 Claude Code は自動で読まず、Codex の変更は通常送信時の明示的許可が必要です。

## LAN ブラウザー参加

右の **LAN で参加**でホスト IPv4 とポートを選び、**招待を有効化**。同じ信頼できる LAN の仲間にリンクを共有し、ニックネームで参加します。`127.0.0.1` は自分の PC 専用です。別端末には LAN アドレスと Windows の適切な受信許可が必要です。

招待を有効にした後の、そのルームのメッセージだけを表示します。投稿は保存され、後続の討論に渡ります。招待の取り消しや全サーバー停止も可能です。ローカル HTTP であり、公開ホスティングではありません。

## エクスポート、バックアップ、料金

右上の **履歴を書き出す**で保存先と Markdown（`.md`）、テキスト（`.txt`）、JSON（`.json`）を選びます。**ルームの保存済み全履歴**、発言者、時刻、本文、宛先、ラウンドを UTF-8 で保存し、画面の最近100件という制限はありません。接続設定とキーファイルは除外します。討論中はその時点までのスナップショットです。

データは `%LOCALAPPDATA%\ModelRoom\room.sqlite3`。終了後に `%LOCALAPPDATA%\ModelRoom` フォルダーをバックアップできます。キーは現在の Windows ユーザーに結びつく DPAPI で暗号化され、別ユーザーや別 PC では通常再入力が必要です。公開ソースにデータフォルダーを含めないでください。

各リクエストと各ラウンドは対応サービスの枠を使い、検索も課金される場合があります。残高確認は公式 DeepSeek のみ内蔵し、他社は各 Console を確認します。返信の token 数はそのリクエストの使用量で、**共通の残り token 数ではありません**。

## トラブル対処

| 症状 | 確認すること |
| --- | --- |
| 401 / 403 | キー、権限、地域、Claude ワークスペース ID |
| 402 / 残高不足 | 該当サービスの Console |
| 404 / 不明なモデル | `/v1` の重複、正確な ID、送信形式 |
| 429 | 席や回数を減らし、時間を置いて制限を確認 |
| 推論パラメーターのエラー | 既定に戻してモデルの資料を確認 |
| 一覧取得は成功、会話は失敗 | 本版 API 対応の文字モデルと権限を確認 |
| Codex がない | `codex.exe` の完全パス。デスクトップ導入だけでは PATH にない場合があります |
| Claude Code 失敗 | ネイティブ EXE、ログイン、CLI バージョン。自動インストールやログインはしません |
| LAN 接続不可 | NIC、受信許可、同一 LAN、Wi-Fi の端末分離 |

## ソースとビルド

Python、H5、Windows ランチャー、5言語の説明を含みます。Tkinter 付き Windows x64 Python 3.10+ を使用します。

```powershell
python -m pip install -r requirements.txt
python .\model_room.py
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File .\build-windows.ps1
```

出力は `dist\ModelRoom.exe`、配布名は `ModelRoom-v1.0-Windows-x64.exe` です。プリセット、API、Claude Code、スタイルは順に `room_presets.py`、`room_providers.py`、`room_claude.py`、`room_style.py`。v0.6 設定を互換読み込みします。ローカル模擬 API と既存動作を確認済みですが、実モデル、権限、料金は各サービスに依存します。
