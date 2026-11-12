"""Model Room desktop client."""

from __future__ import annotations

import os
import queue
import sqlite3
import subprocess
import threading
import tkinter as tk
from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from tkinter import filedialog, messagebox, simpledialog, ttk

from room_core import (
    CODEX, DEEPSEEK, CodexClient, Message, ReplyError, RoomStore, codex_path, data_dir,
)
from room_group import ALL_MEMBERS, HUMAN_ONLY, DiscussionControl, load_members, route_members, run_rounds, snapshot_targets
from room_lan import LanHub
from room_lan_ui import LanWindow
from room_members import MembersWindow
from room_providers import ask_profile, load_profiles
from room_search import SEARCH_NAMES, format_sources, search_web
from room_settings import ConnectionWindow
from room_export import export_chat, export_filename
from room_claude import ClaudeCodeClient
from room_agents import HarnessClient, detect_agents
from room_locale import tr, set_language, DisplayVar, EnumCombo
from room_preferences import load_preferences, save_preferences, wallpaper_photo
from room_identity import room_nickname, avatar_path, avatar_photo, display_author, avatar_data_url
from room_wallpaper import WallpaperTimeline
from room_version import VERSION
from room_style import (SURFACE, BACKGROUND, SIDEBAR, INK, MUTED, LINE, ACCENT, ACCENT_PALE,
                        GREEN, FONT, ActionButton, draw_icon, setup_theme, configure_palette)


PEER_COLORS = {"你": ACCENT, CODEX: "#263a57", DEEPSEEK: "#087e97", "系统": "#68758a",
               "联网搜索": GREEN, "讨论": "#7253a2"}
PEER_LETTERS = {"你": "你", CODEX: "C", DEEPSEEK: "D", "系统": "!", "联网搜索": "搜", "讨论": "议"}


def label(parent, text="", *, size=10, color=None, bg=None, bold=False, **kwargs):
    return tk.Label(
        parent, text=tr(text), fg=color or INK, bg=bg or SURFACE, font=(FONT, size, "bold" if bold else "normal"),
        borderwidth=0, anchor="w", **kwargs,
    )


def button(parent, text, command, *, primary=False, **kwargs):
    return ActionButton(parent, text, command, primary=primary, **kwargs)


def avatar(parent, name, *, bg, size=34, picture=None):
    icon = tk.Canvas(parent, width=size, height=size, bg=bg, borderwidth=0, highlightthickness=0)
    icon.photo = avatar_photo(icon, picture, size) if picture else None
    if icon.photo:
        icon.create_image(size/2,size/2,image=icon.photo)
        return icon
    icon.create_oval(0, 0, size - 1, size - 1, fill=PEER_COLORS.get(name, "#087e97"), outline="")
    icon.create_text(size / 2, size / 2, text=tr(PEER_LETTERS.get(name, name[:1].upper())), fill="#ffffff",
                     font=(FONT, max(10, size // 3), "bold"))
    return icon


def describe_call(details):
    thinking = details.get("thinking")
    if isinstance(thinking, bool):
        thinking = "开启" if thinking else "关闭"
    fields = (
        ("接口", details.get("endpoint")),
        ("HTTP 状态", details.get("status")),
        ("返回模型", details.get("model")),
        ("总耗时", f"{details['elapsed']:.2f} 秒"),
        ("完成 ID", details.get("completion_id")),
        ("请求 ID", details.get("request_id")),
        ("输入 token", details.get("prompt_tokens")),
        ("输出 token", details.get("completion_tokens")),
        ("深度思考", thinking),
    )
    return "\n".join(f"{name}  {value}" for name, value in fields if value is not None)


class Timeline(tk.Frame):
    def __init__(self, parent, suggest, *, options=None, own_name=None):
        super().__init__(parent, bg=BACKGROUND)
        from room_preferences import DEFAULTS
        self.options = options or DEFAULTS
        self.own_name = own_name or (lambda:tr("你"))
        self.view = tk.Text(
            self, bg=BACKGROUND, wrap="none", state="disabled", width=1, height=1,
            font=(FONT, 1), relief="flat", highlightthickness=0, borderwidth=0,
            padx=0, pady=0, takefocus=False, cursor="arrow",
        )
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.view.yview)
        self.view.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.view.pack(side="left", fill="both", expand=True)
        self.view.bind("<Configure>", self._resize)
        self.wheel_bindings = [(event, self.winfo_toplevel().bind(event, self._wheel, add="+"))
                               for event in ("<MouseWheel>", "<Button-4>", "<Button-5>")]

        self.rows = []
        self.resize_job = None
        self.scroll_job = None
        self.copy_menu = tk.Menu(self, tearoff=False)
        self.copy_menu.add_command(label=tr("复制消息"))
        self.copy_menu.add_command(label=tr("复制调用详情"))
        self.empty = tk.Frame(self, bg=BACKGROUND)
        logo = tk.Canvas(self.empty, width=68, height=68, bg=BACKGROUND, highlightthickness=0)
        logo.create_oval(1, 1, 67, 67, fill=ACCENT_PALE, outline="")
        draw_icon(logo, "chat", 18, 17, ACCENT, size=32)
        logo.pack(pady=(0, 15))
        label(self.empty, "开始一次讨论", size=20, bold=True, bg=BACKGROUND).pack()
        label(self.empty, "点名成员发送消息，或让全体分轮讨论。", color=MUTED,
              bg=BACKGROUND).pack(pady=(7, 17))
        examples = tk.Frame(self.empty, bg=BACKGROUND)
        examples.pack()
        button(examples, "填入讨论示例",
               lambda: suggest("@全体 小团队应该先自动化测试，还是先做代码评审？"), icon="chat").pack(side="left", padx=4)
        self.show_empty()

    def _wheel(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget is self.view:
            return None
        while widget:
            if widget is self:
                if event.num in (4, 5):
                    steps = -1 if event.num == 4 else 1
                else:
                    steps = -max(1, abs(event.delta) // 120) if event.delta > 0 else max(1, abs(event.delta) // 120)
                self.view.yview_scroll(steps, "units")
                return "break"
            widget = widget.master
        return None

    def _resize(self, _event):
        if self.resize_job:
            self.after_cancel(self.resize_job)
        self.resize_job = self.after(45, self._fit_all)

    def _fit_all(self):
        self.resize_job = None
        follow = self.view.yview()[1] >= 0.98
        for row, bubble in self.rows:
            row.columnconfigure(0, minsize=self._row_width())
            bubble.configure(wraplength=self._wrap_width())
            if hasattr(row,"meta"):
                row.meta.configure(wraplength=self._wrap_width())
        if follow and self.options["auto_scroll"]:
            self.schedule_scroll()

    def _row_width(self):
        return max(200, self.view.winfo_width() - 50)

    def _wrap_width(self):
        return max(155, int((self._row_width() - 68) * 0.78))

    def scroll_to_end(self):
        self.scroll_job = None
        self.view.see("end")

    def schedule_scroll(self, delay=0):
        if self.scroll_job:
            self.after_cancel(self.scroll_job)
        self.scroll_job = self.after(delay, self.scroll_to_end)

    def destroy(self):
        for event, token in self.wheel_bindings:
            self.winfo_toplevel().unbind(event, token)
        for job in (self.resize_job, self.scroll_job):
            if job:
                self.after_cancel(job)
        super().destroy()

    def _message_menu(self, event, message):
        def copy(value):
            self.clipboard_clear()
            self.clipboard_append(value)

        self.copy_menu.entryconfigure(0, command=lambda: copy(message.body))
        self.copy_menu.entryconfigure(
            1, state="normal" if "endpoint" in message.details else "disabled",
            command=lambda: copy(describe_call(message.details)),
        )
        self.copy_menu.tk_popup(event.x_root, event.y_root)

    def show_empty(self):
        self.empty.place(relx=0.5, rely=0.45, anchor="center")
        self.empty.lift()

    def load(self, messages):
        self.view.configure(state="normal")
        self.view.delete("1.0", "end")
        self.view.configure(state="disabled")
        self.rows.clear()
        if not messages:
            self.show_empty()
        for message in messages:
            self.add(message, auto_fit=False)
        self._resize(None)
        self.schedule_scroll(80)

    def add(self, message: Message, *, auto_fit=True):
        follow = self.options["auto_scroll"] and (message.author == "你" or self.view.yview()[1] >= 0.98)
        self.empty.place_forget()
        own = message.author == "你"
        side = "right" if own else "left"
        row = tk.Frame(self.view, bg=BACKGROUND)
        row.columnconfigure(0, minsize=self._row_width())
        line = tk.Frame(row, bg=BACKGROUND)
        line.grid(row=0, column=0, sticky="e" if own else "w")
        picture = avatar_path(data_dir(),message.details.get("avatar_asset")) if own else None
        if own and "avatar_asset" not in message.details:
            picture = self.options["avatar"]
        avatar(line, message.author, bg=BACKGROUND, picture=picture).pack(side=side, anchor="n", padx=(9, 0) if own else (0, 9))
        group = tk.Frame(line, bg=BACKGROUND)
        group.pack(side=side, anchor="n")
        title = display_author(message,self.own_name()) if own else (tr(message.author) if message.author in {"系统", "讨论", "联网搜索"} else message.author)
        if own and message.recipients:
            title += "  →  " + "、".join(message.details.get("audience", message.recipients))
        if number := message.details.get("round"):
            title += "  ·  " + tr(f"第 {number} 轮")
        meta = tk.Label(group,text=title+("   "+message.time[11:16] if self.options["show_timestamps"] else ""),
                        font=(FONT,9),fg=MUTED,bg=BACKGROUND,borderwidth=0,anchor="w",
                        wraplength=self._wrap_width(),justify="right" if own else "left")
        row.meta = meta
        meta.pack(anchor="e" if own else "w", pady=(0, 4))
        bubble = tk.Label(
            group, text=tr(message.body) if message.author in {"系统", "讨论"} else message.body,
            wraplength=self._wrap_width(), font=(FONT, self.options["message_font_size"]),
            justify="left", anchor="w", fg=INK,
            bg=ACCENT_PALE if own else SURFACE, relief="flat", highlightthickness=1,
            highlightbackground=ACCENT_PALE if own else LINE, padx=16, pady=12,
        )
        bubble.pack(anchor="e" if own else "w")
        bubble.bind("<Button-3>", lambda event: self._message_menu(event, message))
        if "endpoint" in message.details:
            details = message.details
            summary = f"API · {details.get('model') or '模型未返回'} · {details['elapsed']:.2f} 秒 · 详情"
            tk.Button(
                group, text=tr(summary), font=(FONT, 8), fg=ACCENT, bg=BACKGROUND,
                activebackground=ACCENT_PALE, relief="flat", borderwidth=0, padx=1,
                cursor="hand2", command=lambda: messagebox.showinfo(
                    tr("模型调用详情"), tr(describe_call(details)), parent=self.winfo_toplevel(),
                ),
            ).pack(anchor="w", pady=(2, 0))
        elif message.author == DEEPSEEK:
            label(group, "旧记录 · 未保存调用详情", size=8, color=MUTED,
                  bg=BACKGROUND).pack(anchor="w", pady=(2, 0))
        self.rows.append((row, bubble))
        self.view.configure(state="normal")
        self.view.window_create("end-1c", window=row, padx=24, pady=8)
        self.view.insert("end-1c", "\n")
        self.view.configure(state="disabled")
        if auto_fit and follow:
            self.schedule_scroll()


class RoomWindow:
    def __init__(self, root: tk.Tk, store: RoomStore):
        self.root = root
        self.store = store
        self.preferences = load_preferences(store)
        set_language(self.preferences["language"])
        configure_palette(self.preferences)
        self.codex = CodexClient()
        self.search_client = CodexClient()
        self.claude = ClaudeCodeClient()
        self.harness = HarnessClient()
        self.detected_agents = []
        self.settings_window = None
        self.results = queue.Queue()
        self.running = False
        self.discussing = False
        self.control = DiscussionControl(1)
        self.discussion_targets = ()
        self.lan = LanHub()
        self.lan_window = None
        self.online_guests = ()
        self.profiles = load_profiles(store)
        self.active_id = self.profiles[0].id
        self.members = []
        self.rooms = store.rooms()
        selected = store.setting("active_room")
        self.current_room = next((room for room in self.rooms if room.id == selected), self.rooms[0])
        self.drafts = {}
        self.recipient = tk.StringVar(value=ALL_MEMBERS)
        self.rounds = tk.StringVar(value=str(self.preferences["default_rounds"]))
        self.allow_edit = tk.BooleanVar(value=False)
        self.share_history = tk.BooleanVar(value=False)
        self.web_search = tk.BooleanVar(value=False)
        self.activity = DisplayVar(value="就绪")
        self.project = DisplayVar()
        self.room_title = tk.StringVar()
        self.connections = None
        self.member_window = None

        setup_theme(root)
        root.title("Model Room · " + tr("模型会议室") + " v" + VERSION)
        root.geometry(f"{min(1230, root.winfo_screenwidth() - 32)}x{min(760, root.winfo_screenheight() - 65)}")
        root.minsize(970, 640)
        root.configure(bg=SURFACE)
        root.protocol("WM_DELETE_WINDOW", self.close)
        if os.name == "nt":
            try:
                root.iconbitmap(str(Path(__file__).with_name("ModelRoom.ico")))
            except tk.TclError:
                pass

        self._build()
        root.bind("<Control-comma>", lambda _event: self.open_settings())
        self.load_room()
        self.update_controls()
        self.composer.focus_set()
        self.poll_job = root.after(80, self.poll)
        if self.preferences["auto_detect_agents"]:
            self.start_agent_detection()

    def start_agent_detection(self):
        override = self.store.setting("codex_executable")
        def scan():
            self.results.put(("agent_inventory", "", detect_agents(override), {}))
        threading.Thread(target=scan, daemon=True).start()

    def apply_preferences(self, options, *, preserve_settings=False, room_nickname_value=None):
        draft = self.composer.get("1.0", "end-1c")
        previous_rounds = self.preferences["default_rounds"]
        if self.settings_window and self.settings_window.connection.busy:
            return False
        try:
            self.preferences = save_preferences(self.store, options, room_id=self.current_room.id,
                                                room_nickname=room_nickname_value)
        except (OSError, sqlite3.Error):
            messagebox.showerror(tr("无法保存设置"), tr("请检查本地存储权限。"), parent=self.root)
            return False
        if self.rounds.get() == str(previous_rounds):
            self.rounds.set(str(self.preferences["default_rounds"]))
        # All networking objects and data stay alive while the presentation is rebuilt.
        if self.wallpaper_job:
            self.root.after_cancel(self.wallpaper_job)
            self.wallpaper_job = None
        settings = self.settings_window if preserve_settings else None
        for widget in list(self.root.winfo_children()):
            if settings is None or widget is not settings.window:
                widget.destroy()
        self.settings_window = settings
        self.connections = self.member_window = self.lan_window = None
        set_language(self.preferences["language"])
        self.activity.set(self.activity.get())
        configure_palette(self.preferences)
        setup_theme(self.root)
        self.root.configure(bg=SURFACE)
        self.root.title("Model Room · " + tr("模型会议室") + " v" + VERSION)
        self._build()
        self.load_room()
        self.suggest(draft)
        if self.preferences["auto_detect_agents"]:
            self.start_agent_detection()
        return True

    def open_settings(self, page="general"):
        from room_settings_hub import SettingsWindow
        if self.running:
            return
        if self.settings_window and self.settings_window.window.winfo_exists():
            self.settings_window.select(page)
            self.settings_window.window.lift()
        else:
            self.settings_window = SettingsWindow(self, describe_call, page)

    def _build(self):
        rail = tk.Frame(self.root, width=190, bg=SIDEBAR)
        rail.pack(side="left", fill="y")
        rail.pack_propagate(False)
        brand = tk.Frame(rail, bg=SIDEBAR)
        brand.pack(fill="x", padx=16, pady=(22, 5))
        mark = tk.Canvas(brand, width=27, height=29, bg=SIDEBAR, highlightthickness=0)
        draw_icon(mark, "chat", 0, 3, ACCENT, size=25)
        mark.pack(side="left", padx=(0, 6))
        label(brand, "Model Room", size=13, bold=True, bg=SIDEBAR).pack(side="left")
        label(rail, "让想法在对话中相遇", color=MUTED, size=9, bg=SIDEBAR).pack(anchor="w", padx=18)
        self.new_button = button(rail, "新建群聊", self.new_room, primary=True, icon="plus")
        self.new_button.pack(fill="x", padx=15, pady=(15, 10))
        label(rail, "我的群聊", size=9, bold=True, color=MUTED, bg=SIDEBAR).pack(anchor="w", padx=18, pady=(8, 4))
        self.room_list = self.listbox(rail, height=9, expand=True)
        self.room_list.bind("<<ListboxSelect>>", self.pick_room)
        self.rename_button = button(rail, "重命名本群", self.rename_room, icon="edit")
        self.rename_button.pack(anchor="w", padx=15, pady=(14, 0))
        self.connections_button = button(rail, "设置", self.open_settings, icon="settings")
        self.connections_button.pack(anchor="w", padx=15, pady=(7, 0))
        label(rail, "● " + tr("本地保存") + "   /   v" + VERSION, size=8, color=MUTED, bg=SIDEBAR).pack(anchor="w", padx=18, pady=(15, 16))
        tk.Frame(self.root, width=1, bg=LINE).pack(side="left", fill="y")

        right = tk.Frame(self.root, width=206, bg=SURFACE)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        tk.Frame(self.root, width=1, bg=LINE).pack(side="right", fill="y")
        self.member_count = label(right, "群成员", size=13, bold=True)
        self.member_count.pack(anchor="w", padx=15, pady=(19, 9))
        label(right, "人类参会者", size=9, color=MUTED, bold=True).pack(anchor="w", padx=15)
        self.human_list = self.listbox(right, height=4)
        label(right, "AI 成员", size=9, color=MUTED, bold=True).pack(anchor="w", padx=15, pady=(10, 0))
        self.member_list = self.listbox(right, height=7)
        self.member_list.bind("<<ListboxSelect>>", self.pick_recipient)
        self.members_button = button(right, "管理 AI 成员", self.open_members, icon="people")
        self.members_button.pack(anchor="w", padx=15, pady=(7, 0))
        self.lan_button = button(right, "局域网参会", self.open_lan, primary=True, icon="network")
        self.lan_button.pack(anchor="w", padx=15, pady=(7, 0))
        self.search_label = label(right, "", size=8, color=MUTED, wraplength=169, justify="left")
        self.search_label.pack(anchor="w", padx=15, pady=(9, 0))

        main = tk.Frame(self.root, bg=SURFACE)
        main.pack(side="left", fill="both", expand=True)
        header = tk.Frame(main, bg=SURFACE)
        header.pack(fill="x", padx=22, pady=(17, 14))
        title_row = tk.Frame(header, bg=SURFACE)
        title_row.pack(fill="x")
        self.export_button = button(title_row, "导出记录", self.download_history, icon="download", compact=True)
        self.export_button.pack(side="right", padx=(12, 0))
        label(title_row, textvariable=self.room_title, size=17, bold=True).pack(side="left")
        project_bar = tk.Frame(header, bg=SURFACE)
        project_bar.pack(fill="x", pady=(6, 0))
        self.pick = button(project_bar, "选择目录", self.choose_folder, icon="folder", compact=True)
        self.pick.pack(side="right", padx=(7, 0))
        self.open_dir = button(project_bar, "打开", self.open_folder, icon="open", compact=True)
        self.open_dir.pack(side="right", padx=(7, 0))
        self.copy_dir = button(project_bar, "复制路径", self.copy_folder, icon="copy", compact=True)
        self.copy_dir.pack(side="right", padx=(7, 0))
        path = tk.Entry(project_bar, textvariable=self.project, state="readonly",
                        readonlybackground=SURFACE, fg=MUTED, selectbackground=ACCENT,
                        relief="flat", highlightthickness=0, borderwidth=0, font=(FONT, 9))
        path.pack(side="left", fill="x", expand=True)
        tk.Frame(main, height=1, bg=LINE).pack(fill="x")

        self.wallpaper_job = None
        self.wallpaper_image = None

        composer_panel = tk.Frame(main, bg=SURFACE)
        composer_panel.pack(side="bottom", fill="x")
        tk.Frame(composer_panel, height=1, bg=LINE).pack(fill="x")
        self._build_composer(composer_panel)
        if self.preferences["wallpaper"]:
            self.timeline = WallpaperTimeline(main,self.suggest,options=self.preferences,own_name=self.local_name,
                describe_call=describe_call,on_wallpaper=lambda photo:setattr(self,"wallpaper_image",photo))
        else:
            self.timeline = Timeline(main, self.suggest, options=self.preferences, own_name=self.local_name)
        self.timeline.pack(fill="both", expand=True)

    @staticmethod
    def listbox(parent, height, expand=False):
        row = tk.Frame(parent, bg=parent.cget("bg"))
        row.pack(fill="both" if expand else "x", expand=expand, padx=15, pady=(4, 3))
        listing = tk.Listbox(row, height=height, bg=parent.cget("bg"), fg=INK, font=(FONT, 10),
                             selectbackground=ACCENT_PALE, selectforeground=ACCENT,
                             activestyle="none", relief="flat", highlightthickness=0, borderwidth=0,
                             selectborderwidth=0, exportselection=False)
        scroll = ttk.Scrollbar(row, orient="vertical", command=listing.yview)
        listing.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        listing.pack(side="left", fill="both", expand=True)
        return listing

    def _build_composer(self, panel):
        routing = tk.Frame(panel, bg=SURFACE)
        routing.pack(fill="x", padx=22, pady=(12, 8))
        label(routing, "发送给", size=9, bold=True, color=MUTED).pack(side="left", padx=(0, 8))
        self.recipient_picker = EnumCombo(routing, textvariable=self.recipient, state="readonly", width=16,
                                          translate_only={ALL_MEMBERS, HUMAN_ONLY})
        self.recipient_picker.pack(side="left")
        self.recipient_picker.bind("<<ComboboxSelected>>", lambda _event: self.update_controls())
        label(routing, "讨论轮数", size=8, color=MUTED).pack(side="left", padx=(8, 3))
        self.round_input = ttk.Entry(routing, textvariable=self.rounds, width=6)
        self.round_input.pack(side="left")
        tools = tk.Frame(panel, bg=SURFACE)
        tools.pack(fill="x", padx=22, pady=(0, 9))
        self.web_toggle = button(tools, "联网搜索", self.update_controls, variable=self.web_search,
                                 icon="globe", compact=True)
        self.web_toggle.pack(side="left", padx=(0, 6))
        self.edit_toggle = button(tools, "允许 Codex 改文件", self.update_controls, variable=self.allow_edit,
                                  icon="shield", compact=True)
        self.edit_toggle.pack(side="left", padx=(0, 6))
        self.share_toggle = button(tools, "附近期群聊给模型", self.update_controls, variable=self.share_history,
                                   icon="history", compact=True)
        self.share_toggle.pack(side="left")
        input_box = tk.Frame(panel, bg=LINE, padx=1, pady=1)
        input_box.pack(fill="x", padx=22)
        self.composer = tk.Text(
            input_box, height=3, wrap="word", font=(FONT, self.preferences["message_font_size"]), fg=INK, bg=BACKGROUND,
            insertbackground=ACCENT, selectbackground=ACCENT_PALE, selectforeground=INK,
            relief="flat", highlightthickness=0, padx=12, pady=10, undo=True,
        )
        self.composer.pack(fill="x", expand=True)
        self.composer.bind("<FocusIn>", lambda _: input_box.configure(bg=ACCENT))
        self.composer.bind("<FocusOut>", lambda _: input_box.configure(bg=LINE))
        self.composer.bind("<Return>", self.send_on_enter)
        self.composer.bind("<Control-Return>", self.send_on_enter)
        self.composer.bind("<KeyRelease>", lambda _event: self.update_controls())
        self.composer.bind("<<Paste>>", lambda _event: self.root.after_idle(self.update_controls))
        bottom = tk.Frame(panel, bg=SURFACE)
        bottom.pack(fill="x", padx=22, pady=(6, 10))
        self.send_button = button(bottom, "发送", self.send, primary=True, icon="send")
        self.send_button.pack(side="right")
        self.discuss_button = button(bottom, "自由讨论", self.start_discussion, icon="chat")
        self.discuss_button.pack(side="right", padx=6)
        self.stop_button = button(bottom, "停止讨论", self.stop_discussion, icon="stop")
        self.stop_button.pack(side="right")
        self.pause_button = button(bottom, "我来发言", self.pause_discussion, icon="pause")
        self.pause_button.pack(side="right", padx=6)
        label(panel, size=8, color=MUTED, textvariable=self.activity).pack(fill="x", padx=22, pady=(0, 7))

    def download_history(self, parent=None):
        destination = filedialog.asksaveasfilename(
            parent=parent or self.root, title=tr("导出当前群聊的完整记录"), initialfile=export_filename(self.current_room.name),
            defaultextension=".md", filetypes=[("Markdown", "*.md"), ("文本 / Text", "*.txt"), ("JSON", "*.json")],
        )
        if not destination:
            return
        try:
            count = export_chat(self.store, self.current_room, destination)
        except (OSError, ValueError, sqlite3.Error) as error:
            messagebox.showerror(tr("导出未完成"), tr(str(error)), parent=self.root)
            return
        self.activity.set(f"已导出 {count} 条消息 → {destination}")

    @property
    def directory(self):
        return self.current_room.directory

    def load_room(self):
        self.room_title.set(self.current_room.name)
        self.project.set(self.directory or "未关联项目目录")
        self.timeline.load(self.store.recent(self.current_room.id))
        self.draw_rooms()
        self.refresh_connections()

    def draw_rooms(self):
        self.rooms = self.store.rooms()
        self.room_list.delete(0, "end")
        for index, room in enumerate(self.rooms):
            self.room_list.insert("end", "  " + room.name)
            if room.id == self.current_room.id:
                self.room_list.selection_set(index)
                self.room_list.see(index)

    def activate_room(self, room):
        if self.running or room.id == self.current_room.id:
            return
        self.drafts[self.current_room.id] = self.composer.get("1.0", "end-1c")
        self.current_room = room
        self.rounds.set(str(self.preferences["default_rounds"]))
        self.store.set_settings(active_room=room.id)
        self.recipient.set(ALL_MEMBERS)
        for option in (self.allow_edit, self.share_history, self.web_search):
            option.set(False)
        if self.lan_window and self.lan_window.window.winfo_exists():
            self.lan_window.window.destroy()
        self.activity.set("就绪")
        self.load_room()
        self.suggest(self.drafts.get(room.id, ""))

    def pick_room(self, _event=None):
        if selected := self.room_list.curselection():
            self.activate_room(self.rooms[selected[0]])

    def room_name(self, initial=""):
        name = simpledialog.askstring("群聊名称", "请输入群聊名称", initialvalue=initial, parent=self.root)
        if name is None:
            return ""
        name = " ".join(name.split())
        if not 1 <= len(name) <= 36:
            self.activity.set("群名需为 1–36 个字符。")
            return ""
        if any(room.name.casefold() == name.casefold() and room.name != initial for room in self.rooms):
            self.activity.set("已有同名群聊，请换个名字。")
            return ""
        return name

    def new_room(self):
        if not self.running and (name := self.room_name()):
            self.activate_room(self.store.add_room(name))

    def rename_room(self):
        if not self.running and (name := self.room_name(self.current_room.name)):
            self.current_room = replace(self.current_room, name=name)
            self.store.update_room(self.current_room)
            self.room_title.set(name)
            self.draw_rooms()
            self.publish_room(self.current_room.id)

    def refresh_connections(self):
        executable = codex_path(self.store.setting("codex_executable"))
        self.profiles = load_profiles(self.store)
        saved = self.store.setting("active_provider")
        self.active_id = saved if any(profile.id == saved for profile in self.profiles) else self.profiles[0].id
        self.members = load_members(self.store, self.current_room.id, self.active_profile())
        self.refresh_people()
        self.member_list.delete(0, "end")
        known = {profile.id for profile in self.profiles}
        for member in self.members:
            if member.id == CODEX:
                detail = "本机" if executable else "CLI 未找到"
            else:
                detail = member.model if member.provider_id in known else "连接已移除"
            self.member_list.insert("end", f"{member.name}  ·  {detail}")
        names = (ALL_MEMBERS, HUMAN_ONLY, *(member.name for member in self.members))
        self.recipient_picker.configure(values=names)
        if self.recipient.get() not in names:
            self.recipient.set(ALL_MEMBERS)
        mode = self.store.setting("search_mode", "codex")
        self.search_label.configure(text=tr("搜索后端  ·  " + SEARCH_NAMES.get(mode, SEARCH_NAMES["codex"])))
        self.update_controls()
        self.publish_room(self.current_room.id)

    def refresh_people(self):
        self.online_guests = self.lan.guests(self.current_room.id)
        self.member_count.configure(text=tr(f"群成员 · {len(self.members) + len(self.online_guests) + 1}"))
        self.human_list.delete(0, "end")
        self.human_list.insert("end", self.local_name()+" · "+tr("本机"))
        for name in self.online_guests:
            self.human_list.insert("end", name + " · " + tr("在线"))

    def open_lan(self):
        if self.lan_window and self.lan_window.window.winfo_exists():
            self.lan_window.window.lift()
        else:
            self.lan_window = LanWindow(self)

    def append_message(self, room_id, author, body, recipients=(), *, details=None):
        if author == "你":
            custom = room_nickname(self.store,room_id) or self.preferences["nickname"]
            asset = Path(self.preferences["avatar"]).name if self.preferences["avatar"] else ""
            details = {**(details or {}), "display_name":custom or tr("你"), "avatar_asset":asset}
        message = self.store.add(room_id, author, body, recipients, details=details)
        if room_id == self.current_room.id:
            self.timeline.add(message)
        self.publish_room(room_id)
        return message

    def local_name(self, room_id=None):
        return room_nickname(self.store,room_id or self.current_room.id) or self.preferences["nickname"] or tr("你")

    def publish_room(self, room_id):
        cutoff = self.lan.share_cutoff(room_id)
        if cutoff is None:
            return
        room = next((room for room in self.rooms if room.id == room_id), None)
        if room is None:
            return
        roster = self.members if room_id == self.current_room.id else load_members(self.store, room_id, self.active_profile())
        self.lan.publish(room_id, {
            "name": room.name,
            "host_name": self.local_name(room_id),
            "members": [f"{member.name} · {member.model or '本机代理'}" for member in roster],
            "status": self.activity.get() if room_id == self.current_room.id else "已连接",
            "messages": [
                {"id": row.row_id, "author": display_author(row,self.local_name(room_id)) if row.author == "你" else row.author,
                 "is_host": row.author == "你",
                 "avatar": avatar_data_url(data_dir(),row.details.get("avatar_asset")) if row.author == "你" else "",
                 "body": row.body, "time": row.time, "round": row.details.get("round")}
                for row in self.store.recent(room_id, after=cutoff)
            ],
        })

    def active_profile(self):
        return next(profile for profile in self.profiles if profile.id == self.active_id)

    def pick_recipient(self, _event=None):
        if selected := self.member_list.curselection():
            self.recipient.set(self.members[selected[0]].name)
            self.update_controls()

    def open_members(self):
        if self.running:
            return
        if self.member_window and self.member_window.window.winfo_exists():
            self.member_window.window.lift()
        else:
            self.member_window = MembersWindow(self)

    def open_connections(self):
        self.open_settings("connections")

    def choose_folder(self):
        if self.running:
            return False
        current = self.directory if self.directory and Path(self.directory).is_dir() else str(Path.home())
        choice = filedialog.askdirectory(title=tr("选择共享项目目录"), initialdir=current, mustexist=True, parent=self.root)
        if not choice:
            return False
        self.current_room = replace(self.current_room, directory=str(Path(choice).resolve()))
        self.store.update_room(self.current_room)
        self.project.set(self.directory)
        self.activity.set("已选择项目目录")
        self.update_controls()
        return True

    def open_folder(self):
        try:
            if os.name == "nt":
                os.startfile(self.directory)
            else:
                subprocess.Popen(["xdg-open", self.directory])
        except OSError:
            messagebox.showerror(tr("无法打开目录"), tr("目录可能已经移动，请重新选择。"), parent=self.root)

    def copy_folder(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.directory)
        self.activity.set("已复制路径")

    def suggest(self, text):
        self.composer.delete("1.0", "end")
        self.composer.insert("1.0", text)
        self.composer.focus_set()
        self.update_controls()

    def send_on_enter(self, event):
        if event.state & 0x0001:  # Shift
            return None
        if not self.preferences["send_with_enter"] and not event.state & 0x0004:
            return None
        self.send()
        return "break"

    def update_controls(self):
        try:
            _, recipients = self.route()
        except ReplyError:
            recipients = ()
        editable = not self.running and any(member.id == CODEX for member in recipients)
        shareable = not self.running and any(member.id != CODEX for member in recipients)
        paused = self.discussing and self.control.paused
        self.edit_toggle.configure(state="normal" if editable else "disabled")
        self.share_toggle.configure(state="normal" if shareable else "disabled")
        for control in (self.pick, self.members_button, self.connections_button, self.new_button,
                        self.rename_button, self.room_list, self.round_input):
            control.configure(state="disabled" if self.running else "normal")
        self.recipient_picker.configure(state="disabled" if self.running else "readonly")
        self.send_button.configure(
            text=tr("发言并继续" if paused else "发送"),
            state="normal" if paused or not self.running else "disabled",
        )
        self.discuss_button.configure(state="normal" if recipients and not self.running else "disabled")
        controllable = self.discussing and not self.control.stopped and not self.control.finished
        self.stop_button.configure(state="normal" if controllable else "disabled")
        self.pause_button.configure(
            text=tr("继续讨论" if paused else "我来发言"), state="normal" if controllable else "disabled",
        )
        for item in (self.open_dir, self.copy_dir):
            item.configure(state="normal" if self.directory else "disabled")

    def route(self):
        return route_members(self.composer.get("1.0", "end-1c"), self.recipient.get(), self.members)

    def send(self):
        if self.discussing and self.control.paused:
            self.send_human_note()
        else:
            self.begin_turn(1)

    def start_discussion(self):
        try:
            rounds = int(self.rounds.get().strip())
        except ValueError:
            rounds = 0
        if rounds < 2:
            self.activity.set("请在讨论轮数里填写 2 或更大的整数。")
            return
        self.begin_turn(rounds)

    def pause_discussion(self):
        if not self.discussing:
            return
        if self.control.paused:
            self.control.resume()
            self.activity.set("继续讨论…")
        elif self.control.request_pause():
            self.activity.set("本轮回复收尾后暂停，你可以先输入发言。")
            self.composer.focus_set()
        self.update_controls()
        self.publish_room(self.current_room.id)

    def send_human_note(self):
        text = self.composer.get("1.0", "end-1c").strip()
        if not text:
            return
        if len(text) > 4000:
            self.activity.set("插话请控制在 4,000 字以内。")
            return
        self.append_message(self.current_room.id, "你", text, tuple(target.scope for target in self.discussion_targets),
                            details={"human_note": True, "audience": [target.member.name for target in self.discussion_targets]})
        self.composer.delete("1.0", "end")
        self.control.add_human(self.local_name(), text, resume=True)
        self.activity.set("发言已加入讨论，等待下一轮…")
        self.update_controls()
        self.publish_room(self.current_room.id)

    def stop_discussion(self):
        self.control.stop()
        self.activity.set("停止后续轮次，等待已发出的请求…")
        self.update_controls()
        self.publish_room(self.current_room.id)

    def begin_turn(self, rounds):
        if self.running:
            return
        try:
            text, recipients = self.route()
        except ReplyError as error:
            self.activity.set(str(error))
            return
        if not text:
            return
        if len(text) > 16_000:
            messagebox.showinfo(tr("消息太长"), tr("请把这条消息拆成每段 16,000 字以内。"), parent=self.root)
            return
        if not recipients and self.recipient.get() == HUMAN_ONLY and rounds == 1:
            self.append_message(self.current_room.id, "你", text, details={"public_note": True})
            self.composer.delete("1.0", "end")
            return
        try:
            targets = snapshot_targets(recipients, self.profiles)
        except ReplyError as error:
            self.activity.set(str(error))
            return
        if not targets:
            self.activity.set("请先添加或选择群成员。")
            return
        directory = self.directory
        room_id = self.current_room.id
        edit = rounds == 1 and self.allow_edit.get() and any(member.id == CODEX for member in recipients)
        if edit and not (directory and Path(directory).is_dir()):
            self.activity.set("允许修改时，请先选择项目目录。")
            return
        history = self.store.recent(room_id, 30)
        share = self.share_history.get()
        search = self.web_search.get()
        self.append_message(
            room_id, "你", text, tuple(target.scope for target in targets),
            details={"audience": [target.member.name for target in targets]},
        )
        self.composer.delete("1.0", "end")
        self.allow_edit.set(False)
        self.share_history.set(False)
        self.web_search.set(False)
        self.control = DiscussionControl(rounds)
        self.running = True
        self.discussing = rounds > 1
        self.discussion_targets = targets if self.discussing else ()
        if self.discussing:
            for entry in history:
                if entry.details.get("public_note"):
                    self.control.add_human(display_author(entry,self.local_name()) if entry.author == "你" else entry.author, entry.body)
        self.activity.set("正在联网搜索…" if search else "等待成员回复…")
        self.update_controls()
        self.publish_room(room_id)
        executable = self.store.setting("codex_executable")
        mode = self.store.setting("search_mode", "codex")
        local_url = self.store.setting("searx_url")
        threading.Thread(
            target=self.dispatch, args=(text, targets, history, directory, edit, share, rounds,
                                       executable, (mode, local_url) if search else None, self.control),
            daemon=True,
        ).start()

    def dispatch(self, text, targets, history, directory, edit, share, rounds, executable, search_config, control):
        def emit(event, author, body, details):
            self.results.put((event, author, body, details))

        status = "请求未完成"
        try:
            evidence = ""
            if search_config:
                mode, local_url = search_config
                sources = search_web(text, mode, local_url, self.search_client, executable)
                evidence = format_sources(sources)
                emit("line", "联网搜索", SEARCH_NAMES[mode] + "\n\n" + evidence, {})
                if not control.stopped and not control.paused:
                    emit("phase", "", "等待成员回复…", {})

            temporary = any(target.member.id == CODEX for target in targets) and not (
                directory and Path(directory).is_dir()
            )
            folder = TemporaryDirectory(prefix="ModelRoom-turn-") if temporary else nullcontext(directory)
            with folder as work_directory:
                def call(target, prompt, context):
                    if target.member.id == CODEX:
                        if temporary:
                            prompt = "这是通用群聊，没有指定项目目录。请直接讨论，不必读取本地文件。\n" + prompt
                        return self.codex.ask(prompt, context, work_directory, edit, executable), {}
                    response = ask_profile(target.profile, prompt, context, target.key,
                                           claude_client=self.claude, harness_client=self.harness)
                    return response.body, response.details

                status = run_rounds(text, targets, history, share, evidence, rounds > 1, control, call, emit)
        except ReplyError as error:
            emit("line", "系统", str(error), {})
        except Exception:
            emit("line", "系统", "请求未完成，请检查连接或搜索设置后重试。", {})
        finally:
            control.finish()
            emit("done", "", status, {})

    def poll(self):
        room_id = self.current_room.id
        for _ in range(24):
            try:
                room, name, text = self.lan.inbox.get_nowait()
            except queue.Empty:
                break
            author = "访客 · " + name
            self.append_message(room, author, text, details={"public_note": True})
            if room == room_id and self.discussing:
                self.control.add_human(author, text)
        if self.lan.guests(room_id) != self.online_guests:
            self.refresh_people()
        try:
            while True:
                event, author, reply, details = self.results.get_nowait()
                if event == "line":
                    self.append_message(room_id, author, reply, details=details)
                elif event == "agent_inventory":
                    self.detected_agents = reply
                    if self.settings_window and self.settings_window.window.winfo_exists():
                        self.settings_window.connection.agent_results = reply
                        self.settings_window.connection.draw_agents()
                elif event == "phase":
                    if not self.control.stopped and (not self.control.paused or reply.startswith("已暂停")):
                        self.activity.set(reply)
                        self.publish_room(room_id)
                elif event == "done":
                    self.running = self.discussing = False
                    self.activity.set(reply)
                    self.update_controls()
                    self.publish_room(room_id)
        except queue.Empty:
            pass
        self.poll_job = self.root.after(80, self.poll)

    def close(self):
        if self.running and not messagebox.askyesno(
            tr("关闭房间"), tr("还有回复正在生成。关闭房间会结束本地等待，确定关闭？"), parent=self.root,
        ):
            return
        self.control.stop()
        self.root.after_cancel(self.poll_job)
        self.lan.close()
        self.codex.close()
        self.search_client.close()
        self.claude.close()
        self.harness.close()
        if self.wallpaper_job:
            self.root.after_cancel(self.wallpaper_job)
        self.store.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    try:
        store = RoomStore(data_dir())
    except (OSError, sqlite3.Error):
        root.withdraw()
        messagebox.showerror(tr("Model Room"), tr("无法打开本地聊天记录目录。请检查目录权限。"), parent=root)
        root.destroy()
        return
    RoomWindow(root, store)
    root.mainloop()


if __name__ == "__main__":
    main()
