# AI 性格设置指南

设置 → AI 性格 → 选择本群成员 → 编辑或导入 Markdown → 套用 / 确定。每个群聊、每个 AI 席位独立保存；取消放弃未套用更改。普通回复和每轮讨论都会使用。

建议先用两到三个成员：创意伙伴、审阅伙伴、执行伙伴。它们是协作风格，没有固定会议主持人。自由讨论至少两轮，后续轮次才能收到上一轮同伴发言。

写明角色、表达风格、协作方式和边界。不要写 API Key 或私人资料，文字会传给选中的模型服务。Markdown 不会执行，链接文件不会自动读取。性格不会授予工具、改变文件权限，也不能保证回答正确。

UTF-8 · ≤12,000 characters · ≤64 KB

[Creative](examples/personalities/creative.md) · [Reviewer](examples/personalities/reviewer.md) · [Builder](examples/personalities/builder.md)

```markdown
# Practical reviewer

## Role
Review the proposed plan constructively.

## Style
Be concise and explain uncertainty.

## Collaboration
Respond to a specific peer suggestion; propose a practical improvement.

## Boundaries
Do not invent evidence or claim unperformed work. Follow the user's latest requirements.
```
