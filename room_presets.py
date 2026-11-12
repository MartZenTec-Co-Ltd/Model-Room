"""Public configuration templates, never credentials or pre-enabled members."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Preset:
    name: str
    base: str
    transport: str = "openai"
    protocol: str = "none"
    model: str = ""
    note: str = "填入该服务的 API Key → 读取模型 → 选择聊天模型 → 保存连接。"
    docs: str = ""


PRESETS = (
    Preset("DeepSeek 官方", "https://api.deepseek.com", protocol="deepseek",
           docs="https://api-docs.deepseek.com/"),
    Preset("OpenAI / GPT API", "https://api.openai.com/v1", protocol="effort",
           note="使用 OpenAI 平台 API Key。ChatGPT 订阅与 API 账单分开；读取后请选择支持 Chat Completions 的文字模型。",
           docs="https://developers.openai.com/api/reference/chat-completions/overview"),
    Preset("Codex · 本机", "", "codex-cli",
           note="切换到本机 Codex 页，自动查找并检测登录；无需填 API 地址。然后到管理 AI 成员里加入 Codex。",
           docs="https://learn.chatgpt.com/docs/auth"),
    Preset("Claude / Anthropic API", "https://api.anthropic.com/v1", "anthropic", "claude-adaptive",
           note="原生 Messages API。填 Claude Console API Key；若密钥未限定工作区，还需填写 Workspace ID。思考先用供应商默认。",
           docs="https://platform.claude.com/docs/en/api/overview"),
    Preset("Claude Code · 本机", "", "claude-cli", model="sonnet",
           note="使用已安装并登录的原生 claude.exe，路径留空自动查找。纯聊天模式关闭工具、MCP 和自定义技能；不是 Claude API Key 预设。",
           docs="https://code.claude.com/docs/en/cli-reference"),
    Preset("Google Gemini", "https://generativelanguage.googleapis.com/v1beta/openai", protocol="effort",
           docs="https://ai.google.dev/gemini-api/docs/openai"),
    Preset("OpenRouter", "https://openrouter.ai/api/v1", protocol="openrouter",
           docs="https://openrouter.ai/docs/api-reference/overview"),
    Preset("Qwen / 百炼 · 北京", "https://dashscope.aliyuncs.com/compatible-mode/v1", protocol="qwen",
           note="需要北京区域的按量计费 Key；Coding Plan Key 不能混用。可改成控制台提供的工作区专用地址。",
           docs="https://www.alibabacloud.com/help/en/model-studio/base-url"),
    Preset("Qwen / 百炼 · 新加坡", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1", protocol="qwen",
           note="需要新加坡区域的按量计费 Key。区域和计费计划必须与 API 地址匹配。",
           docs="https://www.alibabacloud.com/help/en/model-studio/base-url"),
    Preset("Kimi / Moonshot · 中国", "https://api.moonshot.cn/v1",
           docs="https://platform.moonshot.cn/docs/api/chat"),
    Preset("智谱 GLM · 中国", "https://open.bigmodel.cn/api/paas/v4",
           note="使用智谱中国站标准 API Key。Coding Plan 有专用地址，不能直接混用。无模型列表时按控制台手填模型 ID。",
           docs="https://docs.bigmodel.cn/cn/guide/develop/openai/introduction"),
    Preset("Z.AI / GLM · 国际", "https://api.z.ai/api/paas/v4",
           note="使用 Z.AI 国际站标准 API Key；与中国站及 Coding Plan 配置分开。无模型列表时手填模型 ID。",
           docs="https://docs.z.ai/guides/overview/quick-start"),
    Preset("豆包 / 火山方舟 · 北京", "https://ark.cn-beijing.volces.com/api/v3",
           note="使用北京区域方舟 API Key。选择获准调用的聊天型号；自定义部署可手填控制台给出的接入点 ID。Coding Plan 地址另行配置。",
           docs="https://docs.volcengine.com/docs/ark/APICallGuide?lang=zh"),
    Preset("MiniMax · 中国", "https://api.minimax.cn/v1",
           note="使用 MiniMax 中国站 Key，不能与国际站混用。若模型列表不可用，按控制台手填支持 OpenAI 兼容接口的模型 ID。",
           docs="https://platform.minimax.cn/docs/api-reference/text-openai-api"),
    Preset("MiniMax · 国际", "https://api.minimax.io/v1",
           note="使用 MiniMax 国际站 Key。若模型列表不可用，按控制台手填支持 OpenAI 兼容接口的模型 ID。",
           docs="https://platform.minimax.io/docs/api-reference/text-openai-api"),
    Preset("硅基流动 / SiliconFlow", "https://api.siliconflow.cn/v1",
           docs="https://docs.siliconflow.cn/docs/userguide/quickstart"),
    Preset("Groq", "https://api.groq.com/openai/v1",
           docs="https://console.groq.com/docs/openai"),
    Preset("Mistral", "https://api.mistral.ai/v1", docs="https://docs.mistral.ai/api"),
    Preset("xAI / Grok", "https://api.x.ai/v1", docs="https://docs.x.ai/developers/quickstart"),
    Preset("Ollama · 本机", "http://127.0.0.1:11434/v1",
           note="先启动本机 Ollama 并安装聊天模型。默认本机服务无需密钥；然后读取模型。",
           docs="https://docs.ollama.com/api/openai-compatibility"),
    Preset("LM Studio · 本机", "http://127.0.0.1:1234/v1",
           note="先在 LM Studio 加载聊天模型并开启本地服务器。未启用鉴权时密钥可空；端口以实际设置为准。",
           docs="https://lmstudio.ai/docs/developer/openai-compat"),
    Preset("自定义 OpenAI 兼容", "", note="填自己的兼容服务基础地址及密钥，再读取或手填聊天模型 ID。云端须用 HTTPS。"),
)

FORMATS = {"OpenAI 兼容 · Chat Completions": "openai", "Claude 原生 · Messages": "anthropic",
           "Claude Code · 本机 CLI": "claude-cli", "DeepSeek Harness · 本机 CLI": "dsh-cli"}
