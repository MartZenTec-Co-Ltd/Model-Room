# Model Room v1.0 · Windows 使用說明

[简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md) · [English](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

**讓你、隊友和多個 AI 在同一個群組交流。** 支援命名群聊、模型互相討論、真人插話、區域網路瀏覽器參會及聊天記錄匯出，保留原有三欄配置。


## V1.0 公開版 — 目前僅 Windows x64

**一般使用者：至本儲存庫的 Releases 頁面下載 `ModelRoom-v1.0-Windows-x64.exe`，下載後雙擊即可，不必安裝 Python、pip、Tkinter 或 Pillow。** EXE 已內含執行環境，首次啟動會在本機展開快取，不會另行下載 Python，也不依賴 PATH 中的 Python。

Windows ZIP 是同一個 EXE 加五語說明與授權文件。GitHub 的 **Code → Download ZIP** 和 `ModelRoom-v1.0-Source.zip` 是開發者原始碼，不是一般使用者的程式下載。只有執行或建置原始碼才需要 Python。成品支援 **Windows 10/11 x64**，本次未發布 Linux/macOS 版本。

對話需設定自己的 API 帳號，或另行安裝並登入支援的本機 Agent；程式未附送模型權重或付費帳號。既有本機群聊與設定會繼續沿用。

**開源授權：[MIT](LICENSE)**。另見 [發布說明](RELEASE_NOTES.md)、[貢獻說明](CONTRIBUTING.md) 與 [第三方聲明](THIRD_PARTY_NOTICES.md)。維護者可用 `release-windows.ps1` 建置發布檔案；GitHub 工作流程會建置 EXE，但不會自動公開發布 Release。


## 完整聊天背景、個人資料與常用設定

背景現在鋪滿訊息氣泡後方的整個聊天區，捲動與縮放時仍維持覆蓋。側欄、群組詳情、標題列及輸入區保留純色面板，方便閱讀與操作。外觀可選 **填滿**（可能裁邊）、**配合**（保留整張圖與留白）或 **平鋪**，圖片強度為 0–100%。氣泡與暱稱底色維持可讀；訊息字級可選 10–18。背景僅保存在本機。

設定現有 **通用 / 連線設定 / 介面外觀 / 聊天與輸入 / 資料與儲存 / 關於**。通用新增 **我的暱稱**、**我在本群的暱稱**，以及選擇或移除頭像。本群暱稱留空時跟隨通用暱稱；兩項皆空則顯示目前語言的「你」。暱稱最多 32 字。頭像置中裁為圓形、移除中繼資料並複製至本機目錄。新訊息儲存暱稱和頭像快照，之後變更資料不改寫這些署名；未含快照的舊記錄跟隨目前資料。內部路由與成員識別保持穩定。

區域網路參會者可看到已分享訊息中的暱稱與小頭像，僅傳送小尺寸 PNG，不暴露本機圖片路徑。頭像與背景不會交給 AI 模型；暱稱會用於文字上下文及記錄匯出。匯出不包含頭像圖片檔案或連線金鑰。

聊天與輸入新增 **Enter 傳送訊息**、**顯示訊息時間**、**新訊息自動捲動** 開關及預設討論輪數。關閉 Enter 傳送後使用 Ctrl+Enter，Shift+Enter 一律換行。預設輪數用於啟動與切換群聊，仍可在輸入區臨時填寫輪數。資料與儲存可開啟或複製資料目錄、匯出本群聊。關於顯示版本與支援語言。套用儲存設定並留在目前頁面，確定儲存後關閉，取消放棄尚未套用的設定；連線表單仍需獨立點擊儲存。

設定組織參考 [Signal 個人資料](https://support.signal.org/hc/en-us/articles/360007059952-Edit-my-Profile)、[Signal 字級](https://support.signal.org/hc/en-us/articles/360049670791-Font-Size-Options) 與 [Telegram 聊天背景](https://telegram.org/blog/animated-backgrounds)。這些軟體僅供設計參考，並非執行相依套件。

## 設定介面修復

設定中的布林選項改為手機樣式滑動開關：左邊說明，右邊開關，包括啟動時偵測本機 Agent 和深色模式。點擊切換；Tab 聚焦，空白鍵或 Enter 切換，左右方向鍵指定關閉或開啟。聊天主介面的控制項保留原有排版。

設定底部統一為分隔線與右下角 **套用 / 確定 / 取消或關閉**，不隨頁面捲動。套用儲存通用、外觀與聊天設定，保留設定視窗、目前頁面和未儲存的連線表單；確定儲存這些設定後關閉。取消、Esc 或視窗關閉按鈕放棄尚未套用的通用、外觀與聊天變更；已套用的設定、已明確儲存的連線仍然保留。連線表單仍使用頁面內的儲存按鈕。未儲存的金鑰僅在記憶體保留，不寫入日誌或發布包。

通用與外觀獨立捲動，最小 840 × 560 視窗下底欄仍可見，長說明自動換行，左側會標示目前選取的頁面。保留五種介面語言及明暗主題。

## 統一設定、五語介面與本機 Agent

左下角 **設定**（`Ctrl+,`）依序提供：

1. **一般**：簡體中文、繁體中文、英語、日語、韓語的實際介面切換，以及啟動時自動偵測。本群名稱、暱稱、模型 ID 和聊天原文保持不變。
2. **連線設定**：模型連線、搜尋、本機 Codex 與本機 Agent。下文舊的連線設定入口均位於這裡。
3. **介面外觀**：明暗模式、自訂強調色、本機 JPG/PNG/WebP/GIF/BMP 圖片與強度調整、還原預設。背景鋪滿整個訊息區域，維持三欄配置；解碼並移除中繼資料後複製至本機，絕不上傳模型。即時套用並保留草稿、記錄；套用時會保留未儲存的連線表單。

**自動偵測只找程式，不安裝、不登入、不發送付費模型請求，也不自動加群。** 在連線的 **本機 Agent** 頁偵測、選程式，必要時檢查版本，再儲存本機連線。找到程式不代表登入成功或有額度。

- **Codex**：偵測 PATH 與本機快取的原生 `codex.exe`，可儲存並加入本群；登入另行檢查。
- **Claude Code**：支援原生程式與能解析至既有 Node.js 套件的 npm 包裝器，不執行包裝腳本；儲存後到成員管理新增。
- **DeepSeek Harness**：偵測 `dsh`，以 stdin 傳送材料到 headless 模式，使用 read-only 並拒絕互動審批。模型由 Harness 設定，headless 可能需要 `DEEPSEEK_API_KEY`，GUI 登入未必適用。不支援必要參數時報錯，不自動放寬權限。未安裝的 Agent 不會因預設而顯示為可用。[CLI](https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli) · [headless](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/bundle/headless)。

LAN H5 也可選五語並保存瀏覽器偏好，不翻譯原始聊天。桌面圖片與主題不分享給訪客。偏好保存在原資料庫的 preferences，舊群組、連線及加密金鑰不覆寫。

**Harness 相容性：** 支援辨識桌面安裝包與正在執行的可攜版，但找到程式不代表驗證已可用。`0.2.1-rc.2` 等舊版可能缺少必要的 headless 唯讀與審批策略參數，請檢查已安裝版本的說明，必要時更新。介接器不會靜默移除必要策略。

## 第一次使用：三個步驟

1. 雙擊 `ModelRoom-v1.0-Windows-x64.exe`。Windows x64 版內含 Python，不用另外安裝。舊版群組和設定會沿用，快速預設不會自動覆寫舊連線。
2. 左側開啟 **連線設定 → 模型連線**，選 **快速預設 → 新增此預設**，輸入自己的金鑰，按 **讀取模型**並選擇文字聊天型號，再按 **儲存連線**。**還要到右側「管理 AI 成員」新增該模型，並儲存本群成員。** 只用本機 Codex 可直接參照下方範例。
3. 左側 **新增群聊**並命名。選好成員後輸入問題，按 **傳送**讓每位回答一次，或填輪數後按 **自由討論**。先少量測試，再增加輪數。

設定視窗可向下捲動；**官方說明**開啟所選預設的官方文件。

## 連線、成員與額度的差別

| 名稱 | 用途 | 需要準備 |
| --- | --- | --- |
| API 連線 | 服務網址、型號與驗證設定 | 對應服務的 API Key 和額度 |
| 群組成員 | 本群的一個模型席位 | 從已儲存連線選型號，可重複新增不同型號 |
| 本機 Codex | 呼叫已安裝的 Codex CLI | CLI 本身與登入；不操控目前的 Codex 聊天視窗 |
| 本機 Claude Code | 呼叫原生 Claude Code CLI | `claude.exe` 及其登入或 API 設定 |
| 快速預設 | 自動填好網址與請求格式 | 不提供金鑰、帳號、下載模型或贈送餘額 |

多個雲端模型各自發出請求，不表示把它們的模型權重下載到電腦。

## 五個常用設定範例

### 1. DeepSeek

選 **DeepSeek 官方 → 新增此預設**，輸入 DeepSeek 平台金鑰，**讀取模型 → 選聊天型號 → 儲存連線**，再去 **管理 AI 成員**加入本群。原有預設 DeepSeek 連線可以繼續使用。

**測試聊天**會發出可能計費的真實請求；回覆的 **詳情**顯示網址、實際型號、耗時及服務商回傳的用量。**查 DeepSeek 餘額**僅適用官方地址。參閱 [DeepSeek 官方入門](https://api-docs.deepseek.com/)。

### 2. OpenAI / GPT API

選 **OpenAI / GPT API**，輸入 OpenAI 平台 API Key，讀取並選擇支援 Chat Completions 的文字模型，再儲存及加入本群。預填網址為 `https://api.openai.com/v1`。

此處依平台 API 的驗證與用量規則運作；**不要把 ChatGPT 訂閱額度當成 API Key 餘額**，實際權限和額度以平台為準。不支援只提供 Responses 的型號。參閱 [官方 API 文件](https://developers.openai.com/api/reference/chat-completions/overview)。

### 3. Codex · 本機

選 **Codex · 本機 → 新增此預設**，會切換到 **本機 Codex**。按 **自動尋找 → 檢查登入**，找不到時以 **選擇 CLI**指定 `codex.exe`。尚未登入則 **複製登入指令**，到自己的 PowerShell 執行並完成登入。接著在 **管理 AI 成員**按 **加入 Codex → 儲存本群成員**。

不需 API 網址，額度依 CLI 的 ChatGPT 或 API Key 登入方式決定。討論中唯讀；一般發送要修改專案時，先選目錄，再開啟 **允許 Codex 改檔**。參閱 [官方認證說明](https://learn.chatgpt.com/docs/auth)。

### 4. Claude / Anthropic API

選 **Claude / Anthropic API**，輸入 Claude Console API Key；請求格式為 **Claude 原生 · Messages**，網址為 `https://api.anthropic.com/v1`。若 Key 未限定工作區，還需填控制台的 **Claude 工作區 ID**（`wrkspc_…`）。讀取型號、儲存連線，再加入本群。

思考先選 **供應商預設**。新型號可依支援情況選 `adaptive`，舊型號可選 `budget_tokens`；不是每個模型都接受全部選項。參閱 [官方介面與驗證](https://platform.claude.com/docs/en/api/overview)。

### 5. Claude Code · 本機

先依 [官方文件](https://code.claude.com/docs/en/cli-reference)安裝並登入原生 CLI。選 **Claude Code · 本機**；**服務網址 / CLI** 留白自動尋找 `claude.exe`，也可輸入完整路徑。Windows 支援原生程式及可解析的 npm 包裝器，不直接執行包裝腳本。預設別名為 `sonnet`，亦可手填本機支援的 `opus`、`haiku` 或型號 ID。

儲存後到 **管理 AI 成員**新增席位。此適配器關閉工具、MCP、自訂技能及一般設定掛鉤，在暫存目錄純聊天，不修改專案；組織託管政策仍可能適用。登入與計費依 CLI 設定，**與單純輸入 Claude API Key 不同**。思考支援預設、開啟及高強度，不把低強度冒充關閉。

## 全部快速預設

| 預設（與介面名稱一致） | 請求格式 | 網址 / 方式 |
| --- | --- | --- |
| [DeepSeek 官方](https://api-docs.deepseek.com/) | OpenAI-compatible | `https://api.deepseek.com` |
| [OpenAI / GPT API](https://developers.openai.com/api/reference/chat-completions/overview) | OpenAI-compatible | `https://api.openai.com/v1` |
| [Codex · 本機](https://learn.chatgpt.com/docs/auth) | 本機 CLI | 自動尋找或填 EXE 路徑 |
| [Claude / Anthropic API](https://platform.claude.com/docs/en/api/overview) | Claude Messages | `https://api.anthropic.com/v1` |
| [Claude Code · 本機](https://code.claude.com/docs/en/cli-reference) | 本機 CLI | 自動尋找或填 EXE 路徑 |
| [Google Gemini](https://ai.google.dev/gemini-api/docs/openai) | OpenAI-compatible | `https://generativelanguage.googleapis.com/v1beta/openai` |
| [OpenRouter](https://openrouter.ai/docs/api-reference/overview) | OpenAI-compatible | `https://openrouter.ai/api/v1` |
| [Qwen / 百煉 · 北京](https://www.alibabacloud.com/help/en/model-studio/base-url) | OpenAI-compatible | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| [Qwen / 百煉 · 新加坡](https://www.alibabacloud.com/help/en/model-studio/base-url) | OpenAI-compatible | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| [Kimi / Moonshot · 中國](https://platform.moonshot.cn/docs/api/chat) | OpenAI-compatible | `https://api.moonshot.cn/v1` |
| [智譜 GLM · 中國](https://docs.bigmodel.cn/cn/guide/develop/openai/introduction) | OpenAI-compatible | `https://open.bigmodel.cn/api/paas/v4` |
| [Z.AI / GLM · 國際](https://docs.z.ai/guides/overview/quick-start) | OpenAI-compatible | `https://api.z.ai/api/paas/v4` |
| [豆包 / 火山方舟 · 北京](https://docs.volcengine.com/docs/ark/APICallGuide?lang=zh) | OpenAI-compatible | `https://ark.cn-beijing.volces.com/api/v3` |
| [MiniMax · 中國](https://platform.minimax.cn/docs/api-reference/text-openai-api) | OpenAI-compatible | `https://api.minimax.cn/v1` |
| [MiniMax · 國際](https://platform.minimax.io/docs/api-reference/text-openai-api) | OpenAI-compatible | `https://api.minimax.io/v1` |
| [矽基流動 / SiliconFlow](https://docs.siliconflow.cn/docs/userguide/quickstart) | OpenAI-compatible | `https://api.siliconflow.cn/v1` |
| [Groq](https://console.groq.com/docs/openai) | OpenAI-compatible | `https://api.groq.com/openai/v1` |
| [Mistral](https://docs.mistral.ai/api) | OpenAI-compatible | `https://api.mistral.ai/v1` |
| [xAI / Grok](https://docs.x.ai/developers/quickstart) | OpenAI-compatible | `https://api.x.ai/v1` |
| [Ollama · 本機](https://docs.ollama.com/api/openai-compatibility) | OpenAI-compatible | `http://127.0.0.1:11434/v1` |
| [LM Studio · 本機](https://lmstudio.ai/docs/developer/openai-compat) | OpenAI-compatible | `http://127.0.0.1:1234/v1` |
| 自訂 OpenAI 相容 | OpenAI-compatible | 自行填寫 |

雲端模型 ID 預設留白，讓你依帳號讀取清單。清單可能包含嵌入或語音型號，請選文字聊天模型；無清單 API 可手填準確 ID。百煉北京與新加坡的金鑰不同，按量計費與 Coding Plan 也不能混用。網址可依控制台要求修改。

本版支援 OpenAI 相容聊天、Claude Messages 及兩種本機 CLI，未內建 Azure、Bedrock、Vertex 專用 IAM 驗證；可使用合適的相容閘道。`examples/presets.json` 是不含金鑰的公開模板參考，並無 JSON 匯入按鈕。

## 群聊、討論與目錄

- 各群獨立保存名稱、記錄、AI 名單及可選目錄。每群最多 8 個 AI；連線設定全域共用，席位按群保存。
- **傳送給**可選全體、單人或 **僅在群內發言**，也能在開頭 `@暱稱`。**傳送**各答一次；**討論輪數**填大於等於 2 的整數，再按 **自由討論**。成員參考近期同伴發言互相回應，沒有指定主持人。
- 按 **我要發言**，待本輪已送出的回覆結束後暫停。補充後按 **發言並繼續**，下輪會考慮你的發言。可繼續或停止；桌面同時執行一群的 AI 討論。
- **聯網搜尋**先將本輪問題送往選定搜尋服務，再把來源交給模型。設定頁可選 Codex、Brave 或自建 SearXNG；Brave 要另外的搜尋 Key，SearXNG 要開啟 JSON。
- 一般 API 發送預設附該席位的近期對話；**附上近期群聊**擴大共享範圍。上下文有長度限制，不會每次傳送全部本地歷史。
- 目錄可選擇、開啟和複製路徑；關聯不等於上傳全部檔案。API 與本版 Claude Code 不自行讀取目錄。Codex 改檔權限只在一般發送且明確開啟時生效。

## 隊友用瀏覽器參與

右側 **區域網路參會 → 選主機 IPv4 與連接埠 → 開啟本群邀請**，分享給同一可信區域網路的隊友，對方填暱稱即可發言。`127.0.0.1` 只供本機；其他裝置要用主機的區網位址，並允許 Windows 對應入站連線。

訪客只看得到開啟邀請後的本群訊息，發言會保存並進入後續討論。可關閉本群邀請或停止整個服務。此功能使用本地 HTTP，未提供公網託管。

## 匯出、備份與費用

右上角 **匯出記錄**可選 Markdown（`.md`）、文字（`.txt`）、JSON（`.json`）及儲存位置。匯出本群**全部已存歷史**、發言者、時間、正文、收件人與已有輪次，不受畫面最近 100 筆限制。採 UTF-8，不含連線設定或金鑰檔案。討論中匯出的是當時快照。

記錄和設定在 `%LOCALAPPDATA%\ModelRoom\room.sqlite3`。退出程式後可備份整個 `%LOCALAPPDATA%\ModelRoom`。金鑰由 Windows DPAPI 綁定目前使用者加密，換電腦或使用者通常要重填；請勿將資料目錄放入公開原始碼倉庫。

API 每次請求與每輪討論分別使用對應服務額度，搜尋也可能計費。本版僅內建官方 DeepSeek 餘額查詢，其他服務請看控制台。詳情的 token 為單次回傳用量，**不是統一剩餘額度**。

## 常見問題

| 現象 | 檢查方式 |
| --- | --- |
| 401 / 403 | 金鑰、權限、區域；Claude 是否缺工作區 ID |
| 402 / 餘額不足 | 對應平台的可用額度 |
| 404 / 型號不存在 | 網址是否重複 `/v1`，模型 ID 與格式是否正確 |
| 429 | 減少成員或輪數，稍後再試，檢查服務限額 |
| 思考參數錯誤 | 改回供應商預設，再依模型文件選協定 |
| 讀到模型但不能聊天 | 選支援本版介面的文字聊天模型並檢查權限 |
| 找不到 Codex | 指定 `codex.exe`；桌面已安裝不代表 PATH 可用 |
| Claude Code 失敗 | 檢查原生 EXE、登入及版本；本版不自動安裝或登入 |
| 區網無法連線 | 網卡位址、入站權限、同網段與 Wi-Fi 用戶端隔離 |

## 原始碼與建置

保留 Python、H5、Windows 啟動器與五份文件。使用含 Tkinter 的 Windows x64 Python 3.10+：

```powershell
python -m pip install -r requirements.txt
python .\model_room.py
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File .\build-windows.ps1
```

產物為 `dist\ModelRoom.exe`，發行名稱為 `ModelRoom-v1.0-Windows-x64.exe`。預設、API、本機 Claude Code、樣式分別在 `room_presets.py`、`room_providers.py`、`room_claude.py`、`room_style.py`。v0.6 設定相容讀取。本版已經過本地模擬介面及舊功能檢查；實際型號、帳號權限和收費依平台為準。
