"""Settings with scrollable pages and a persistent bottom-right action bar."""
import tkinter as tk
import os
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, ttk

from room_core import data_dir
from room_controls import SettingsScroll, ToggleSwitch
from room_locale import LANGUAGES, EnumCombo, tr
from room_identity import room_nickname, clean_nickname, import_avatar, avatar_photo
from room_version import VERSION
from room_preferences import DEFAULTS, import_wallpaper
from room_settings import ConnectionWindow
from room_style import SURFACE, BACKGROUND, INK, MUTED, LINE, ACCENT


class SettingsWindow:
    def __init__(self, room, describe_call, page="general"):
        self.room, self.describe_call = room, describe_call
        self.window = tk.Toplevel(room.root)
        self.window.transient(room.root)
        self.window.geometry(f"940x{min(760, room.root.winfo_screenheight()-100)}")
        self.window.minsize(840, 560)
        self.window.protocol("WM_DELETE_WINDOW", self.dismiss)
        self.window.bind("<Escape>", lambda _: self.dismiss())
        self.window.bind("<Destroy>", self._destroyed, add="+")
        self.traces = []
        self._build(page)

    def _build(self, page, connection_draft=None):
        self.window.title(tr("设置 · Model Room"))
        self.window.configure(bg=SURFACE)
        self.options = dict(self.room.preferences)
        self.language = tk.StringVar(value=LANGUAGES[self.options["language"]])
        self.mode = tk.StringVar(value="深色" if self.options["mode"] == "dark" else "浅色")
        self.dark = tk.BooleanVar(value=self.options["mode"] == "dark")
        self.accent = tk.StringVar(value=self.options["accent"])
        self.opacity = tk.IntVar(value=self.options["wallpaper_opacity"])
        self.auto = tk.BooleanVar(value=self.options["auto_detect_agents"])
        self.nickname = tk.StringVar(value=self.options["nickname"])
        self.room_nickname = tk.StringVar(value=room_nickname(self.room.store,self.room.current_room.id))
        self.chat_font = tk.StringVar(value=str(self.options["message_font_size"]))
        self.default_rounds = tk.StringVar(value=str(self.options["default_rounds"]))
        self.send_enter = tk.BooleanVar(value=self.options["send_with_enter"])
        self.timestamps = tk.BooleanVar(value=self.options["show_timestamps"])
        self.auto_scroll = tk.BooleanVar(value=self.options["auto_scroll"])
        self.wallpaper_fit = tk.StringVar(value={"cover":"填充", "contain":"适应", "tile":"平铺"}[self.options["wallpaper_fit"]])
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        content = ttk.Frame(self.window)
        content.grid(row=0, column=0, sticky="nsew")
        sidebar = ttk.Frame(content, padding=(16, 20), width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text=tr("设置"), font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(4, 24))
        ttk.Separator(content, orient="vertical").pack(side="left", fill="y")
        body = ttk.Frame(content)
        body.pack(side="left", fill="both", expand=True)
        self.pages, self.navigation, self.scrollers = {}, {}, {}
        for key, title in (("general", "通用"), ("connections", "连接设置"), ("appearance", "界面外观"),
                           ("chat","聊天与输入"), ("storage","数据与存储"), ("about","关于")):
            button = ttk.Button(sidebar, text=tr(title), command=lambda k=key: self.select(k))
            button.pack(fill="x", pady=5)
            self.navigation[key] = button
            self.pages[key] = ttk.Frame(body)
        self.build_general(self.pages["general"])
        self.connection = ConnectionWindow(self.room, self.describe_call, parent=self.pages["connections"])
        if connection_draft:
            self.connection.restore_draft(connection_draft)
        self.build_appearance(self.pages["appearance"])
        self.build_chat(self.pages["chat"])
        self.build_storage(self.pages["storage"])
        self.build_about(self.pages["about"])
        self.separator = ttk.Separator(self.window, orient="horizontal")
        self.separator.grid(row=1, column=0, sticky="ew")
        self.footer = ttk.Frame(self.window, padding=(20, 14))
        self.footer.grid(row=2, column=0, sticky="ew")
        self.footer.columnconfigure(0, weight=1)
        self.footer_note = ttk.Label(self.footer, foreground=MUTED, justify="left", wraplength=400)
        self.footer_note.grid(row=0, column=0, sticky="w", padx=(0, 18))
        actions = ttk.Frame(self.footer)
        actions.grid(row=0, column=1, sticky="e")
        self.apply_button = ttk.Button(actions, text=tr("套用"), command=self.apply)
        self.ok_button = ttk.Button(actions, text=tr("确定"), command=self.accept)
        self.cancel_button = ttk.Button(actions, text=tr("关闭"), command=self.dismiss)
        for button in (self.apply_button, self.ok_button, self.cancel_button):
            button.pack(side="left", padx=(8, 0))
        self.footer.bind("<Configure>", lambda e: self.footer_note.configure(wraplength=max(120, e.width-actions.winfo_reqwidth()-64)))
        for var in (self.language, self.mode, self.accent, self.opacity, self.auto, self.nickname,self.room_nickname,
                    self.chat_font,self.default_rounds,self.send_enter,self.timestamps,self.auto_scroll,self.wallpaper_fit):
            self.traces.append((var, var.trace_add("write", self._changed)))
        self.traces.append((self.dark, self.dark.trace_add("write", lambda *_: self.mode.set("深色" if self.dark.get() else "浅色"))))
        self.select(page)
        self._changed()

    def _remove_traces(self):
        for var, token in self.traces:
            var.trace_remove("write", token)
        self.traces.clear()

    def _destroyed(self, event):
        if event.widget is self.window:
            self._remove_traces()
            if self.room.settings_window is self:
                self.room.settings_window = None

    def select(self, page):
        for frame in self.pages.values():
            frame.pack_forget()
        self.page = page
        self.pages[page].pack(fill="both", expand=True)
        for key, button in self.navigation.items():
            button.configure(style="SelectedNav.TButton" if key == page else "Nav.TButton")
        if hasattr(self, "footer_note"):
            self._changed()

    def _values(self):
        def number(var):
            try: return int(var.get())
            except ValueError: return var.get()
        return {**self.options, "language": next(k for k, v in LANGUAGES.items() if v == self.language.get()),
                "mode": "dark" if self.mode.get() == "深色" else "light", "accent": self.accent.get(),
                "wallpaper_opacity": self.opacity.get(), "auto_detect_agents": self.auto.get(),
                "nickname":self.nickname.get(), "message_font_size":number(self.chat_font),
                "default_rounds":number(self.default_rounds), "send_with_enter":self.send_enter.get(),
                "show_timestamps":self.timestamps.get(), "auto_scroll":self.auto_scroll.get(),
                "wallpaper_fit":{"填充":"cover", "适应":"contain", "平铺":"tile"}[self.wallpaper_fit.get()]}

    def _changed(self, *_):
        dirty = self._values() != self.room.preferences or self.room_nickname.get()!=room_nickname(self.room.store,self.room.current_room.id)
        self.apply_button.configure(state="normal" if dirty else "disabled")
        self.cancel_button.configure(text=tr("取消") if dirty else tr("关闭"))
        note = "连接请使用页面内的保存按钮。套用会保留未保存的连接表单。" if self.page == "connections" else ("有尚未套用的更改" if dirty else "设置已保存")
        self.footer_note.configure(text=tr(note))
        if self.dark.get() != (self.mode.get() == "深色"):
            self.dark.set(self.mode.get() == "深色")
        self.preview()
        self.refresh_avatar()

    def panel(self, outer, key):
        scroll = SettingsScroll(outer)
        scroll.pack(fill="both", expand=True)
        self.scrollers[key] = scroll
        return scroll.panel

    @staticmethod
    def note(parent, text, **pack):
        label = ttk.Label(parent, text=tr(text), foreground=MUTED, wraplength=540, justify="left")
        label.pack(anchor="w", fill="x", **pack)
        label.bind("<Configure>", lambda e: label.configure(wraplength=max(120, e.width)))
        return label

    def heading(self, parent, title, note):
        ttk.Label(parent, text=tr(title), font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(0, 9))
        self.note(parent, note, pady=(0, 22))

    def switch_row(self, parent, title, variable, note=""):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=(18, 18))
        row.columnconfigure(0, weight=1)
        title_label = ttk.Label(row, text=tr(title), wraplength=430, justify="left")
        title_label.grid(row=0, column=0, sticky="w")
        switch = ToggleSwitch(row, variable, label=tr(title))
        switch.grid(row=0, column=1, rowspan=2 if note else 1, sticky="e", padx=(24, 0))
        labels = [title_label]
        if note:
            description = ttk.Label(row, text=tr(note), foreground=MUTED, wraplength=430, justify="left")
            description.grid(row=1, column=0, sticky="w", pady=(7, 0))
            labels.append(description)
        def wrap(event):
            for label in labels:
                label.configure(wraplength=max(120, event.width-88))
        row.bind("<Configure>", wrap)
        return switch

    def build_general(self, outer):
        panel = self.panel(outer, "general")
        self.heading(panel, "通用", "语言会用于主界面、设置、成员管理和系统提示。聊天原文保持不变。")
        ttk.Label(panel, text=tr("界面语言 / Language")).pack(anchor="w", pady=(0, 8))
        ttk.Combobox(panel, values=tuple(LANGUAGES.values()), textvariable=self.language,
                     state="readonly", width=26).pack(anchor="w", pady=(0, 10))
        ttk.Separator(panel).pack(fill="x", pady=(16, 20))
        ttk.Label(panel,text=tr("个人资料"),font=("Segoe UI",12,"bold")).pack(anchor="w",pady=(0,12))
        row=ttk.Frame(panel); row.pack(fill="x",pady=(0,14))
        self.avatar_preview=tk.Canvas(row,width=64,height=64,bg=SURFACE,highlightthickness=0)
        self.avatar_preview.pack(side="left",padx=(0,16))
        ttk.Button(row,text=tr("选择头像"),command=self.pick_avatar).pack(side="left")
        ttk.Button(row,text=tr("移除头像"),command=self.remove_avatar).pack(side="left",padx=8)
        self.avatar_photo=None
        self.refresh_avatar()
        for title,var in (("我的昵称",self.nickname),("我在本群的昵称",self.room_nickname)):
            ttk.Label(panel,text=tr(title)).pack(anchor="w",pady=(8,6))
            ttk.Entry(panel,textvariable=var).pack(fill="x")
        self.note(panel,"本群昵称留空时使用我的昵称。昵称最多 32 字；修改后用于新消息，不改写已保存的署名。",pady=(9,8))
        self.note(panel,"昵称和头像会显示在消息中，局域网参会者也可看到。头像不会交给模型。")
        ttk.Separator(panel).pack(fill="x", pady=(16, 0))
        self.auto_switch = self.switch_row(panel, "启动时自动检测本机 Agent", self.auto,
            "检测只查找程序路径，不安装软件、不发起模型请求，也不会自动把 Agent 加入群聊。")

    def refresh_avatar(self):
        if not hasattr(self,"avatar_preview") or not self.avatar_preview.winfo_exists():
            return
        self.avatar_preview.delete("all")
        self.avatar_photo=avatar_photo(self.window,self.options["avatar"],64)
        if self.avatar_photo:
            self.avatar_preview.create_image(32,32,image=self.avatar_photo)
        else:
            self.avatar_preview.create_oval(0,0,63,63,fill=ACCENT,outline="")
            name=self.room_nickname.get() or self.nickname.get() or tr("你")
            self.avatar_preview.create_text(32,32,text=name[:1].upper(),fill="#ffffff",font=("Segoe UI",20,"bold"))

    def pick_avatar(self):
        path=filedialog.askopenfilename(parent=self.window,title=tr("选择头像"),
            filetypes=[(tr("图片"),"*.png *.jpg *.jpeg *.webp *.gif *.bmp")])
        if not path: return
        try:
            self.options["avatar"]=import_avatar(path,data_dir())
        except (OSError,ValueError) as error:
            messagebox.showerror(tr("无法载入图片"),tr(str(error)),parent=self.window)
            return
        self._changed()

    def remove_avatar(self):
        self.options["avatar"]=""
        self._changed()

    def build_chat(self,outer):
        panel=self.panel(outer,"chat")
        self.heading(panel,"聊天与输入","设置输入方式、消息显示和新会话的默认讨论轮数。")
        self.switch_row(panel,"Enter 发送消息",self.send_enter,"关闭后使用 Ctrl+Enter 发送；Shift+Enter 始终换行。")
        self.switch_row(panel,"显示消息时间",self.timestamps)
        self.switch_row(panel,"新消息自动滚动",self.auto_scroll,"关闭后收到回复时保留当前阅读位置。")
        ttk.Label(panel,text=tr("默认讨论轮数")).pack(anchor="w",pady=(16,7))
        ttk.Entry(panel,textvariable=self.default_rounds,width=10).pack(anchor="w")
        self.note(panel,"默认值用于启动和切换群聊；仍可在聊天输入区临时修改。",pady=(8,0))

    def build_storage(self,outer):
        panel=self.panel(outer,"storage")
        self.heading(panel,"数据与存储","查看本机保存位置并导出当前群聊。不会自动清理聊天记录或上传数据。")
        ttk.Label(panel,text=tr("数据目录")).pack(anchor="w",pady=(0,7))
        directory=tk.StringVar(value=str(data_dir()))
        ttk.Entry(panel,textvariable=directory,state="readonly").pack(fill="x")
        row=ttk.Frame(panel); row.pack(fill="x",pady=12)
        ttk.Button(row,text=tr("打开数据目录"),command=self.open_data_dir).pack(side="left")
        ttk.Button(row,text=tr("复制路径"),command=lambda:self.connection.copy(str(data_dir()))).pack(side="left",padx=8)
        self.note(panel,"数据库、头像和背景图片都保存在该目录。密钥仍由 Windows 当前用户加密保护。",pady=(6,20))
        ttk.Separator(panel).pack(fill="x",pady=(0,20))
        ttk.Button(panel,text=tr("导出当前群聊记录"),command=lambda:self.room.download_history(parent=self.window)).pack(anchor="w")
        self.note(panel,"导出 Markdown、文本或 JSON；不包含密钥和头像图片文件。",pady=(9,0))

    def open_data_dir(self):
        try:
            os.startfile(str(data_dir()))
        except OSError as error:
            messagebox.showerror(tr("数据目录"),str(error),parent=self.window)

    def build_about(self,outer):
        panel=self.panel(outer,"about")
        self.heading(panel,"关于","Model Room · Windows v"+VERSION)
        self.note(panel,"面向人类与多个 AI 成员的本地群聊。支持简体中文、繁体中文、英语、日语和韩语。",pady=(0,16))
        self.note(panel,"源码与五语使用说明随发布包保留。模型调用由各服务商独立处理与计费。")

    def build_appearance(self, outer):
        panel = self.panel(outer, "appearance")
        self.heading(panel, "界面外观", "保留三栏布局，自选明暗、强调色和本地背景图片。图片不会上传到模型。")
        self.dark_switch = self.switch_row(panel, "深色模式", self.dark)
        ttk.Separator(panel).pack(fill="x", pady=(0, 20))
        row = ttk.Frame(panel)
        row.pack(fill="x")
        ttk.Label(row, text=tr("强调色")).pack(side="left", padx=(0, 12))
        ttk.Entry(row, textvariable=self.accent, width=12).pack(side="left")
        ttk.Button(row, text=tr("选择颜色"), command=self.pick_color).pack(side="left", padx=10)
        ttk.Label(panel,text=tr("消息字号")).pack(anchor="w",pady=(20,7))
        ttk.Spinbox(panel,from_=10,to=18,textvariable=self.chat_font,width=8).pack(anchor="w")
        ttk.Label(panel, text=tr("背景图片 · JPG / PNG / WebP / GIF")).pack(anchor="w", pady=(24, 9))
        row = ttk.Frame(panel)
        row.pack(fill="x")
        ttk.Button(row, text=tr("选择图片"), command=self.pick_wallpaper).pack(side="left")
        ttk.Button(row, text=tr("移除图片"), command=self.remove_wallpaper).pack(side="left", padx=8)
        self.wallpaper_note = self.note(panel, "", pady=(8, 14))
        self.refresh_wallpaper()
        ttk.Label(panel,text=tr("背景铺放方式")).pack(anchor="w",pady=(0,7))
        EnumCombo(panel,textvariable=self.wallpaper_fit,values=("填充","适应","平铺"),state="readonly",width=24).pack(anchor="w",pady=(0,12))
        self.note(panel,"背景覆盖完整聊天区域。填充可能裁边；适应保留整张图片；平铺重复图片。",pady=(0,12))
        ttk.Label(panel, text=tr("图片强度（0–100%）")).pack(anchor="w")
        ttk.Scale(panel, from_=0, to=100, variable=self.opacity, length=350).pack(anchor="w", fill="x", pady=9)
        self.swatch = tk.Canvas(panel, width=420, height=98, bg=BACKGROUND, highlightthickness=1, highlightbackground=LINE)
        self.swatch.pack(fill="x", pady=(8, 16))
        self.swatch.bind("<Configure>", lambda _: self.preview())
        self.preview_photo = None
        self.preview()
        ttk.Button(panel, text=tr("恢复默认外观"), command=self.reset_appearance).pack(anchor="w", pady=(0, 12))

    def refresh_wallpaper(self):
        self.wallpaper_note.configure(text=tr("已选择本地图片") if self.options["wallpaper"] else tr("未设置背景图片"))

    def preview(self):
        if not hasattr(self, "swatch") or not self.swatch.winfo_exists():
            return
        from room_preferences import validate_preferences, wallpaper_photo
        from room_style import blend
        options = validate_preferences(self._values())
        bg, fg = ("#101725", "#edf1f8") if options["mode"] == "dark" else ("#f4f6fb", "#202c45")
        width = max(260, self.swatch.winfo_width()) if self.swatch.winfo_width() > 1 else 420
        self.swatch.configure(bg=bg)
        self.swatch.delete("all")
        self.preview_photo = wallpaper_photo(self.window, options, width, 98, bg)
        if self.preview_photo:
            self.swatch.create_image(0, 0, image=self.preview_photo, anchor="nw")
        self.swatch.create_rectangle(18, 20, width-18, 78, fill=blend(bg, options["accent"], .18), outline=options["accent"])
        self.swatch.create_text(32, 49, text=tr("外观预览"), fill=fg, anchor="w", font=("Segoe UI", 12))

    def pick_color(self):
        selected = colorchooser.askcolor(self.accent.get(), parent=self.window, title=tr("选择强调色"))[1]
        if selected:
            self.accent.set(selected)

    def pick_wallpaper(self):
        source = filedialog.askopenfilename(parent=self.window, title=tr("选择背景图片"),
            filetypes=[(tr("图片"), "*.jpg *.jpeg *.png *.webp *.gif *.bmp")])
        if not source:
            return
        try:
            self.options["wallpaper"] = import_wallpaper(source, data_dir())
        except (OSError, ValueError, ImportError) as error:
            messagebox.showerror(tr("无法载入图片"), tr(str(error)), parent=self.window)
            return
        self.refresh_wallpaper()
        self._changed()

    def remove_wallpaper(self):
        self.options["wallpaper"] = ""
        self.refresh_wallpaper()
        self._changed()

    def reset_appearance(self):
        self.dark.set(False)
        self.accent.set(DEFAULTS["accent"])
        self.opacity.set(18)
        self.chat_font.set(str(DEFAULTS["message_font_size"]))
        self.wallpaper_fit.set("填充")
        self.remove_wallpaper()

    def accept(self):
        return self.apply(close=True)

    def dismiss(self):
        self.window.destroy()

    def apply(self, *, close=False):
        import re
        if self.room.running or self.connection.busy:
            messagebox.showinfo(tr("请稍候"), tr("请等待当前请求结束后再应用界面设置。"), parent=self.window)
            return False
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", self.accent.get()):
            messagebox.showerror(tr("颜色无效"), tr("请填写 #RRGGBB 格式的颜色。"), parent=self.window)
            return False
        options = self._values()
        try:
            options["nickname"]=clean_nickname(self.nickname.get())
            nickname=clean_nickname(self.room_nickname.get())
            if not isinstance(options["message_font_size"],int) or not 10<=options["message_font_size"]<=18:
                raise ValueError("消息字号请填写 10–18 之间的整数。")
            if not isinstance(options["default_rounds"],int) or not 2<=options["default_rounds"]<=1000000:
                raise ValueError("默认讨论轮数请填写 2–1000000 之间的整数。")
        except ValueError as error:
            messagebox.showerror(tr("设置无效"),tr(str(error)),parent=self.window)
            return False
        self.nickname.set(options["nickname"])
        self.room_nickname.set(nickname)
        if options != self.room.preferences or nickname!=room_nickname(self.room.store,self.room.current_room.id):
            draft = self.connection.capture_draft()
            positions = {key: scroll.canvas.yview()[0] for key, scroll in self.scrollers.items()}
            page = self.page
            if not self.room.apply_preferences(options, preserve_settings=True, room_nickname_value=nickname):
                return False
            if not close:
                self._remove_traces()
                for widget in list(self.window.winfo_children()):
                    widget.destroy()
                self._build(page, draft)
                self.window.update_idletasks()
                self.connection.canvas.yview_moveto(draft["position"])
                for key, position in positions.items():
                    self.scrollers[key].canvas.yview_moveto(position)
        if close:
            self.dismiss()
        return True
