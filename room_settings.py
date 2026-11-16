"""Cross-platform connection manager."""

import queue
import secrets
import sqlite3
import threading
import tkinter as tk
import os
import sys
import shlex
import webbrowser
from dataclasses import replace
from tkinter import filedialog, messagebox, ttk
from uuid import uuid4

from room_core import CODEX, DEEPSEEK, ReplyError, codex_login_status, codex_path, data_dir, deepseek_balance
from room_providers import PROTOCOLS, THINKING, Profile, api_base, ask_profile, discover_models, save_profiles
from room_search import SEARCH_NAMES, format_sources, search_web
from win_secrets import write_secret
from room_style import SURFACE, BACKGROUND, INK, MUTED, ACCENT, LINE
from room_presets import FORMATS, PRESETS
from room_locale import tr, DisplayVar, EnumCombo
from room_agents import LocalAgent, detect_agents, agent_version
from room_group import CODEX_MEMBER, save_members


class ConnectionWindow:
    def __init__(self, room, describe_call, *, parent=None):
        self.room = room
        self.embedded = parent is not None
        self.describe_call = describe_call
        self.window = tk.Toplevel(room.root) if parent is None else ttk.Frame(parent)
        if parent is None:
            self.window.title(tr("连接设置 · Model Room"))
            self.window.transient(room.root)
            self.window.resizable(True, True)
            self.window.minsize(650, 500)
        else:
            self.window.pack(fill="both", expand=True)
        self.on_close = self.window.winfo_toplevel().destroy
        self.results = queue.Queue()
        self.busy = False
        self.profile_name = tk.StringVar()
        self.name = tk.StringVar()
        self.address = tk.StringVar()
        self.model = tk.StringVar()
        self.protocol = tk.StringVar()
        self.thinking = tk.StringVar()
        self.key_source = DisplayVar()
        self.preset_name = tk.StringVar(value=PRESETS[0].name)
        self.preset_note = DisplayVar(value=PRESETS[0].note)
        self.transport = tk.StringVar()
        self.workspace = tk.StringVar()
        self.cli = tk.StringVar(value=room.store.setting("codex_executable"))
        self.cli_display = tk.StringVar()
        mode = room.store.setting("search_mode", "codex")
        self.search_mode = tk.StringVar(value=SEARCH_NAMES.get(mode, SEARCH_NAMES["codex"]))
        self.searx = tk.StringVar(value=room.store.setting("searx_url", "http://127.0.0.1:8080"))
        self._build()
        self.show_profile(room.active_profile())
        self.refresh_cli()
        if parent is not None:
            return
        self.window.update_idletasks()
        left = max(0, room.root.winfo_rootx() + (room.root.winfo_width() - self.window.winfo_reqwidth()) // 2)
        top = max(0, min(room.root.winfo_rooty() + 24, self.window.winfo_screenheight() - 560))
        height = min(self.window.winfo_reqheight(), self.window.winfo_screenheight() - top - 70)
        self.window.geometry(f"{self.window.winfo_reqwidth()}x{height}+{left}+{top}")

    @staticmethod
    def row(parent, text):
        line = ttk.Frame(parent)
        line.pack(fill="x", pady=3)
        ttk.Label(line, text=tr(text), width=15, wraplength=125, justify="left").pack(side="left", padx=(0, 8))
        return line

    @staticmethod
    def entry(parent, variable=None, **options):
        control = ttk.Entry(parent, textvariable=variable, width=53, **options)
        control.pack(side="left", fill="x", expand=True)
        return control

    @staticmethod
    def actions(parent, *buttons):
        line = ttk.Frame(parent)
        line.pack(fill="x", pady=(7, 1))
        for text, command in buttons:
            ttk.Button(line, text=tr(text), command=command).pack(side="left", padx=(0, 5))
        return line

    def _build(self):
        scroll = ttk.Scrollbar(self.window, orient="vertical")
        scroll.pack(side="right", fill="y")
        self.canvas = tk.Canvas(self.window, bg=SURFACE, highlightthickness=0, width=680, height=780,
                                 yscrollcommand=scroll.set)
        self.canvas.pack(fill="both", expand=True)
        scroll.configure(command=self.canvas.yview)
        container = ttk.Frame(self.canvas, padding=13)
        item = self.canvas.create_window(0, 0, window=container, anchor="nw")
        container.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(item, width=event.width))
        top = self.window.winfo_toplevel()
        def wheel(event):
            if str(event.widget).startswith(str(self.window)) and self.canvas.winfo_viewable():
                amount = -1 if getattr(event,'num',None) == 4 else (1 if getattr(event,'num',None) == 5 else
                         -int(event.delta) if sys.platform == 'darwin' else -int(event.delta/120))
                self.canvas.yview_scroll(amount, "units")
        bindings = [(event,top.bind(event,wheel,add='+')) for event in ('<MouseWheel>','<Button-4>','<Button-5>')]
        def cleanup(event):
            if event.widget is self.window:
                for sequence, token in bindings:
                    top.unbind(sequence,token)
        self.window.bind('<Destroy>',cleanup)
        tabs = self.tabs = ttk.Notebook(container)
        tabs.pack(fill="both", expand=True)
        providers = ttk.Frame(tabs, padding=12)
        search = ttk.Frame(tabs, padding=12)
        cli = ttk.Frame(tabs, padding=12)
        tabs.add(providers, text=tr("模型连接"))
        tabs.add(search, text=tr("联网搜索"))
        tabs.add(cli, text=tr("本机 Codex"))
        agents = ttk.Frame(tabs, padding=12)
        tabs.add(agents, text=tr("本机 Agent"))
        ttk.Label(agents, text=tr("自动检测 Codex、Claude Code 和 DeepSeek Harness。找到程序不代表已经登录或有可用额度。"),
                  wraplength=520, foreground=MUTED, justify="left").pack(anchor="w", pady=(0, 12))
        self.agent_tree = ttk.Treeview(agents, columns=("agent", "status"), show="headings", height=4, selectmode="browse")
        self.agent_tree.heading("agent", text=tr("本机 Agent")); self.agent_tree.heading("status", text=tr("检测状态"))
        self.agent_tree.column("agent", width=180); self.agent_tree.column("status", width=230)
        self.agent_tree.pack(fill="x")
        self.agent_path = DisplayVar()
        ttk.Label(agents, textvariable=self.agent_path, wraplength=520, foreground=MUTED).pack(anchor="w", pady=10)
        self.agent_tree.bind("<<TreeviewSelect>>", self.pick_agent)
        self.agent_results = list(getattr(self.room, "detected_agents", ()))
        self.draw_agents()
        self.actions(agents, ("自动检测本机 Agent", self.scan_agents), ("选择程序", self.choose_agent),
                     ("检测版本", self.check_agent_version))
        self.actions(agents, ("保存本机连接", self.connect_agent))
        ttk.Label(agents, text=tr("保存后到群成员管理中添加席位。Codex 可直接加入本群。Harness 使用 headless 只读模式，可能需要单独配置 API Key。"),
                  wraplength=520, foreground=MUTED, justify="left").pack(anchor="w", pady=12)

        line = self.row(providers, "快速预设")
        presets = EnumCombo(line, textvariable=self.preset_name, values=[row.name for row in PRESETS],
                               state="readonly", width=28)
        presets.pack(side="left", fill="x", expand=True)
        presets.bind("<<ComboboxSelected>>", lambda _: self.preset_note.set(self.selected_preset().note))
        ttk.Button(line, text=tr("新增此预设"), command=self.apply_preset).pack(side="left", padx=(5, 0))
        ttk.Button(line, text=tr("官方说明"), command=self.open_preset_docs).pack(side="left", padx=(5, 0))
        ttk.Label(providers, textvariable=self.preset_note, foreground=MUTED, wraplength=550,
                  justify="left").pack(fill="x", pady=(3, 8))
        line = self.row(providers, "已保存连接")
        self.picker = ttk.Combobox(line, textvariable=self.profile_name, state="readonly", width=28)
        self.picker.pack(side="left", fill="x", expand=True)
        self.picker.bind("<<ComboboxSelected>>", self.pick_profile)
        ttk.Button(line, text=tr("新增"), command=self.new_profile).pack(side="left", padx=(5, 0))
        ttk.Button(line, text=tr("删除"), command=self.delete_profile).pack(side="left", padx=(5, 0))
        self.entry(self.row(providers, "连接名称"), self.name)
        self.entry(self.row(providers, "服务地址 / CLI"), self.address)
        formats = EnumCombo(self.row(providers, "请求格式"), textvariable=self.transport, values=tuple(FORMATS),
                               state="readonly", width=41)
        formats.pack(side="left")
        formats.bind("<<ComboboxSelected>>", self.change_transport)
        self.key = self.entry(self.row(providers, "API 密钥"), show="*")
        self.workspace_entry = self.entry(self.row(providers, "Claude 工作区 ID"), self.workspace)
        ttk.Label(providers, textvariable=self.key_source, foreground=MUTED).pack(anchor="w")
        line = self.row(providers, "聊天模型 ID")
        self.models = ttk.Combobox(line, textvariable=self.model, width=39)
        self.models.pack(side="left", fill="x", expand=True)
        ttk.Button(line, text=tr("读取模型"), command=self.read_models).pack(side="left", padx=(5, 0))
        EnumCombo(self.row(providers, "思考协议"), textvariable=self.protocol, values=tuple(PROTOCOLS),
                     state="readonly", width=41).pack(side="left")
        EnumCombo(self.row(providers, "思考模式"), textvariable=self.thinking, values=tuple(THINKING),
                     state="readonly", width=19).pack(side="left")
        ttk.Label(providers, text=tr("API 模型需自己的 Key；本机 CLI 沿用自己的登录。已有连接密钥留空则沿用。"),
                  foreground=MUTED).pack(anchor="w")
        self.actions(providers, ("保存连接", self.save_profile), ("测试聊天", self.test_chat),
                     ("查 DeepSeek 余额", self.check_balance))

        EnumCombo(self.row(search, "搜索后端"), textvariable=self.search_mode,
                     values=tuple(SEARCH_NAMES.values()), state="readonly", width=29).pack(side="left")
        self.entry(self.row(search, "SearXNG 地址"), self.searx)
        self.search_key = self.entry(self.row(search, "Brave API Key"), show="*")
        ttk.Label(search, justify="left", wraplength=510, text=(
            tr("Codex 实时搜索复用本机登录。Brave 需要自己的 API Key。"
            "自建 SearXNG 要启用 JSON。保存后在群聊勾选「联网搜索」，本轮问题会发给选中的搜索服务。")
        )).pack(anchor="w", pady=7)
        self.actions(search, ("保存搜索设置", self.save_search), ("测试搜索", self.test_search))

        self.entry(self.row(cli, "可执行文件"), self.cli_display, state="readonly")
        self.actions(cli, ("选择 CLI", self.choose_cli), ("自动查找", self.auto_cli),
                     ("复制登录命令", self.copy_login))
        self.actions(cli, ("保存 CLI 路径", self.save_cli), ("检测登录", self.test_cli))
        ttk.Label(cli, text=tr("选择目录后，Model Room 会在项目目录中运行 Codex CLI。")).pack(anchor="w", pady=9)

        self.result = tk.Text(container, width=72, height=4, wrap="word", state="disabled", relief="flat",
                              bg=BACKGROUND, fg=INK, padx=12, pady=10, highlightthickness=1,
                              highlightbackground=LINE, selectbackground=ACCENT)
        self.result.pack(fill="x", pady=(8, 0))
        copy_action = ("复制结果", lambda: self.copy(self.result.get("1.0", "end-1c")))
        self.actions(container, copy_action, *(("关闭", self.on_close),) if not self.embedded else ())
        self.status("选快速预设 → 新增此预设 → 填密钥 → 读取模型 → 保存。再到「管理 AI 成员」把模型加入本群。")

    def capture_draft(self):
        """Keep unfinished fields only in memory while a theme/language is applied."""
        names = ("profile_name", "name", "address", "model", "protocol", "thinking", "transport", "workspace",
                 "preset_name", "preset_note", "cli", "cli_display", "search_mode", "searx")
        return {"current": self.current, "fields": {key: getattr(self, key).get() for key in names},
                "key": self.key.get(), "search_key": self.search_key.get(),
                "models": tuple(self.models.cget("values")), "tab": self.tabs.index(self.tabs.select()),
                "agents": self.agent_results, "selected_agent": self.agent_tree.selection(),
                "position": self.canvas.yview()[0]}

    def restore_draft(self, draft):
        self.show_profile(draft["current"])
        for key, value in draft["fields"].items():
            getattr(self, key).set(value)
        self.update_transport()
        if str(self.key.cget("state")) != "disabled":
            self.key.delete(0, "end")
            self.key.insert(0, draft["key"])
        self.search_key.delete(0, "end")
        self.search_key.insert(0, draft["search_key"])
        self.models.configure(values=draft["models"])
        self.agent_results = draft["agents"]
        self.draw_agents()
        if draft["selected_agent"]:
            self.agent_tree.selection_set(draft["selected_agent"])
            self.pick_agent()
        self.tabs.select(draft["tab"])
        self.window.update_idletasks()
        self.canvas.yview_moveto(draft["position"])

    def draw_agents(self):
        self.agent_tree.delete(*self.agent_tree.get_children())
        for agent in self.agent_results:
            self.agent_tree.insert("", "end", iid=agent.kind, values=(agent.name, tr(agent.status)))

    def pick_agent(self, _event=None):
        selected = self.agent_tree.selection()
        if selected:
            agent = next(row for row in self.agent_results if row.kind == selected[0])
            self.agent_path.set(agent.path or "未安装或未找到")

    def scan_agents(self):
        override = self.room.store.setting("codex_executable")
        def completed(rows):
            self.agent_results = rows
            self.room.detected_agents = rows
            self.draw_agents()
            self.status("检测完成。请选择找到的程序，再保存本机连接。")
        self.run(lambda: detect_agents(override), completed)

    def selected_agent(self):
        selected = self.agent_tree.selection()
        if not selected:
            self.status("请先选择一个本机 Agent。")
            return None
        return next(row for row in self.agent_results if row.kind == selected[0])

    def choose_agent(self):
        agent = self.selected_agent()
        if agent is None:
            return
        selected = filedialog.askopenfilename(parent=self.window, title=tr("选择本机 Agent 程序"),
            filetypes=[(tr("程序"), "*.exe *.cmd *.js *.mjs *.cjs"), (tr("全部文件"), "*.*")])
        if selected:
            updated = replace(agent, path=selected, status="已选择程序（尚未验证）")
            self.agent_results = [updated if row.kind == agent.kind else row for row in self.agent_results]
            self.draw_agents(); self.agent_tree.selection_set(agent.kind); self.pick_agent()

    def check_agent_version(self):
        if agent := self.selected_agent():
            self.run(lambda: agent_version(agent))

    def connect_agent(self):
        if self.busy or self.room.running:
            return
        agent = self.selected_agent()
        if not agent or not agent.path:
            self.status("请先检测或选择程序路径。")
            return
        if agent.kind == "codex":
            if __import__("os").name == "nt" and not agent.path.lower().endswith(".exe"):
                self.status("请选择原生 codex.exe，不使用命令包装脚本。")
                return
            if not codex_path(agent.path):
                self.status("指定的 Codex CLI 不存在。")
                return
            self.room.store.set_settings(codex_executable=agent.path)
            if not any(member.id == CODEX for member in self.room.members):
                if len(self.room.members) >= 8:
                    self.status("本群模型席位已满。")
                    return
                save_members(self.room.store, self.room.current_room.id, [*self.room.members, CODEX_MEMBER])
            self.room.refresh_connections()
            self.status("Codex 本机连接已保存并加入本群。登录状态请单独检测。")
            return
        from room_agents import launcher
        if not launcher(agent.kind, agent.path)[0]:
            self.status("无法解析此程序。npm 包装器需要对应的本机包和 Node.js。")
            return
        transport = "claude-cli" if agent.kind == "claude" else "dsh-cli"
        existing = next((row for row in self.room.profiles if row.transport == transport and row.base == agent.path), None)
        if existing:
            self.show_profile(existing)
        else:
            name = agent.name
            if any(row.name == name for row in self.room.profiles):
                name += " " + uuid4().hex[:4]
            profile = Profile(uuid4().hex, name, agent.path, "sonnet" if agent.kind == "claude" else "configured",
                              transport=transport)
            save_profiles(self.room.store, [*self.room.profiles, profile], self.room.active_id)
            self.room.refresh_connections(); self.show_profile(profile)
        self.status("本机连接已保存。请到「管理 AI 成员」把它加入本群。")

    def selected_preset(self):
        return next(row for row in PRESETS if row.name == self.preset_name.get())

    def open_preset_docs(self):
        if self.selected_preset().docs:
            webbrowser.open(self.selected_preset().docs)

    def apply_preset(self):
        if self.busy:
            return
        preset = self.selected_preset()
        if preset.transport == "codex-cli":
            self.tabs.select(2)
            self.refresh_cli()
            self.status(preset.note)
            return
        name, suffix = tr(preset.name)[:24], 2
        known = {profile.name.casefold() for profile in self.room.profiles}
        while name.casefold() in known:
            name = tr(preset.name)[:24] + f" {suffix}"
            suffix += 1
        self.show_profile(Profile(uuid4().hex, name, preset.base, preset.model,
                                  preset.protocol, transport=preset.transport))
        self.status(preset.note + "\n这是一个新连接；不会覆盖已有连接。")
        self.canvas.yview_moveto(0)

    def change_transport(self, _event=None):
        transport = FORMATS[self.transport.get()]
        if transport == "anthropic":
            self.protocol.set("Claude · adaptive")
        else:
            self.protocol.set("不发送思考参数")
        self.thinking.set("供应商默认")
        self.update_transport()

    def update_transport(self):
        transport = FORMATS[self.transport.get()]
        self.key.configure(state="normal")
        if transport == "claude-cli":
            self.key.delete(0, "end")
            self.key.configure(state="disabled")
        self.workspace_entry.configure(state="normal" if transport == "anthropic" else "disabled")

    def status(self, text):
        self.result.configure(state="normal")
        self.result.delete("1.0", "end")
        self.result.insert("1.0", tr(text))
        self.result.configure(state="disabled")

    def copy(self, text):
        self.window.clipboard_clear()
        self.window.clipboard_append(text)

    def show_profile(self, profile):
        self.current = profile
        self.picker.configure(values=[row.name for row in self.room.profiles])
        self.profile_name.set(profile.name if any(row.id == profile.id for row in self.room.profiles) else "")
        self.name.set(profile.name)
        self.address.set(profile.base)
        self.model.set(profile.model)
        self.models.configure(values=profile.models)
        self.protocol.set(next((key for key, value in PROTOCOLS.items() if value == profile.protocol), "自动"))
        self.thinking.set(next((key for key, value in THINKING.items() if value == profile.thinking), "供应商默认"))
        self.transport.set(next(key for key, value in FORMATS.items() if value == profile.transport))
        self.workspace.set(profile.workspace)
        self.key.configure(state="normal")
        self.key.delete(0, "end")
        self.update_transport()
        self.key_source.set("密钥来源  ·  " + profile.credential()[1])

    def pick_profile(self, _event=None):
        self.show_profile(next(row for row in self.room.profiles if row.name == self.profile_name.get()))

    def new_profile(self):
        if not self.busy:
            self.show_profile(Profile(uuid4().hex, "", "", ""))
            self.status("填名称和 API 基础地址，再读取模型或保存。")

    def delete_profile(self):
        if self.busy or self.current.id == DEEPSEEK:
            if not self.busy:
                self.status("DeepSeek 是随应用提供的连接，可编辑其设置。")
            return
        if not any(row.id == self.current.id for row in self.room.profiles):
            self.show_profile(self.room.active_profile())
            return
        if messagebox.askyesno(tr("删除连接"), tr(f"删除连接「{self.current.name}」？聊天记录会保留。"), parent=self.window):
            profiles = [row for row in self.room.profiles if row.id != self.current.id]
            active = self.room.active_id if self.room.active_id != self.current.id else profiles[0].id
            save_profiles(self.room.store, profiles, active)
            self.current.credential_file.unlink(missing_ok=True)
            self.room.refresh_connections()
            self.show_profile(self.room.active_profile())
            self.status("连接已删除。")

    def snapshot(self):
        name = self.name.get().strip()
        transport = FORMATS[self.transport.get()]
        base = self.address.get().strip() if transport in {"claude-cli", "dsh-cli"} else api_base(
            self.address.get(), ("/chat/completions", "/models", "/messages"))
        if not name or len(name) > 28 or "@" in name or name.casefold() in {
            "codex", "两位", "all", "你", "系统", "联网搜索",
        }:
            raise ReplyError("请使用 1–28 个字符的独立名称，避开 Codex、两位等保留名称。")
        if any(row.name.casefold() == name.casefold() and row.id != self.current.id for row in self.room.profiles):
            raise ReplyError("这个连接名称已被使用。")
        models = self.current.models if (base, transport) == (self.current.base, self.current.transport) else ()
        workspace = self.workspace.get().strip() if transport == "anthropic" else ""
        if workspace and (not workspace.startswith("wrkspc_") or not all(c.isalnum() or c == "_" for c in workspace)):
            raise ReplyError("Claude 工作区 ID 应为控制台提供的 wrkspc_ 开头的 ID。")
        return Profile(self.current.id, name, base, self.model.get().strip(), PROTOCOLS[self.protocol.get()],
                       THINKING[self.thinking.get()], models, transport, workspace), self.key.get().strip()

    def read_models(self, auto_save=False):
        try:
            profile, key = self.snapshot()
        except ReplyError as error:
            self.status(str(error))
            return
        original = (self.current.id, self.address.get(), self.key.get(), self.transport.get(), self.workspace.get())

        def completed(models):
            if (self.current.id, self.address.get(), self.key.get(), self.transport.get(), self.workspace.get()) != original:
                self.status("表单已变更。请用当前地址重新读取模型。")
                return
            self.current = replace(self.current, base=profile.base, models=models)
            self.models.configure(values=models)
            if self.model.get() not in models:
                self.model.set(models[0])
            self.status(f"已读取 {len(models)} 个模型。可从下拉列表切换。")
            if auto_save:
                self.save_profile()

        self.run(lambda: discover_models(profile, key or None), completed)

    def save_profile(self):
        if self.busy:
            return
        try:
            profile, key = self.snapshot()
            if not profile.model:
                self.read_models(auto_save=True)
                return
            if key:
                profile.save_key(key)
            known = any(row.id == profile.id for row in self.room.profiles)
            updated = [profile if row.id == profile.id else row for row in self.room.profiles]
            if not known:
                updated.append(profile)
            save_profiles(self.room.store, updated, self.room.active_id if known else profile.id)
            self.room.refresh_connections()
            self.show_profile(profile)
            self.status(f"已保存 {profile.name} · {profile.model}（已发现 {len(profile.models)} 个模型）。")
        except (ReplyError, OSError, sqlite3.Error) as error:
            self.status(str(error) if isinstance(error, ReplyError) else "无法保存连接，请检查本地存储权限。")

    def test_chat(self):
        try:
            profile, key = self.snapshot()
        except ReplyError as error:
            self.status(str(error))
            return
        nonce = "MR-" + secrets.token_hex(4).upper()

        def check():
            reply = ask_profile(profile, f"Reply with exactly this verification code: {nonce}", "[]", key or None,
                                claude_client=self.room.claude, harness_client=self.room.harness)
            verdict = "校验码匹配" if reply.body == nonce else "已返回，校验码不同"
            return f"{verdict} · 发出 {nonce} · 收到 {reply.body[:90]}\n{self.describe_call(reply.details)}"

        self.run(check)

    def check_balance(self):
        try:
            profile, key = self.snapshot()
        except ReplyError as error:
            self.status(str(error))
            return
        if not profile.official_deepseek:
            self.status("余额查询适用于 DeepSeek 官方地址。")
            return
        self.run(lambda: deepseek_balance(key or profile.credential()[0]))

    def refresh_cli(self):
        self.cli_display.set(codex_path(self.cli.get()) or self.cli.get() or "未找到 Codex CLI")

    def choose_cli(self):
        path = filedialog.askopenfilename(parent=self.window, title=tr("选择 Codex CLI"),
                                          filetypes=[("Codex CLI", "codex.exe" if os.name == 'nt' else 'codex'), (tr("全部文件"), "*")])
        if path:
            self.cli.set(path)
            self.refresh_cli()

    def auto_cli(self):
        self.cli.set("")
        self.refresh_cli()

    def copy_login(self):
        path = codex_path(self.cli.get())
        self.copy(("& '" + path.replace("'", "''") + "' login" if os.name == 'nt' else shlex.quote(path)+' login') if path else "codex login")
        self.status("登录命令已复制。请在终端执行。")

    def save_cli(self):
        value = self.cli.get()
        if value and not codex_path(value):
            self.status("指定的 Codex CLI 不存在。")
            return
        self.room.store.set_settings(codex_executable=value)
        self.room.refresh_connections()
        self.status("Codex CLI 路径已保存。")

    def test_cli(self):
        path = codex_path(self.cli.get())
        if path:
            self.run(lambda: codex_login_status(path))
        else:
            self.status("请安装或选择 Codex CLI。")

    def search_snapshot(self):
        mode = next(key for key, name in SEARCH_NAMES.items() if name == self.search_mode.get())
        url = self.searx.get().strip()
        return mode, api_base(url, ("/search",)) if mode == "searxng" else url, self.search_key.get().strip()

    def save_search(self):
        try:
            mode, url, key = self.search_snapshot()
            if key:
                write_secret(data_dir() / "keys" / "brave-search.key", key)
                self.search_key.delete(0, "end")
            self.room.store.set_settings(search_mode=mode, searx_url=url)
            self.room.refresh_connections()
            self.status(f"已保存搜索设置 · {SEARCH_NAMES[mode]}")
        except (ReplyError, OSError, sqlite3.Error) as error:
            self.status(str(error) if isinstance(error, ReplyError) else "无法保存搜索设置。")

    def test_search(self):
        try:
            mode, url, key = self.search_snapshot()
        except ReplyError as error:
            self.status(str(error))
            return
        executable = self.cli.get()
        self.run(lambda: format_sources(search_web("Python tkinter official documentation", mode, url,
                                                    self.room.search_client, executable, key or None)))

    def run(self, check, completed=None):
        if self.busy:
            return
        self.busy = True
        self.status("正在请求…")

        def worker():
            try:
                self.results.put((True, check()))
            except ReplyError as error:
                self.results.put((False, str(error)))
            except Exception:
                self.results.put((False, "请求失败，请检查配置后重试。"))

        def poll():
            if not self.window.winfo_exists():
                return
            try:
                success, result = self.results.get_nowait()
            except queue.Empty:
                self.room.root.after(100, poll)
                return
            self.busy = False
            if success and completed:
                completed(result)
            else:
                self.status(result)

        threading.Thread(target=worker, daemon=True).start()
        self.room.root.after(100, poll)
