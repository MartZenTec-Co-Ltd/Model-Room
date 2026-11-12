"""Edit the roster of the current room."""

import sqlite3
import tkinter as tk
from room_style import MUTED
from room_locale import tr, DisplayVar, EnumCombo
from tkinter import ttk
from uuid import uuid4

from room_core import CODEX, ReplyError
from room_group import CODEX_MEMBER, MAX_MEMBERS, RESERVED, Member, save_members


class MembersWindow:
    def __init__(self, room):
        self.room = room
        self.members = list(room.members)
        self.window = tk.Toplevel(room.root)
        self.window.title(tr("群成员 · Model Room"))
        self.window.transient(room.root)
        self.window.resizable(False, False)
        self.connection = tk.StringVar()
        self.model = tk.StringVar()
        self.nickname = tk.StringVar()
        self.status = DisplayVar(value="先在连接设置保存 API，再在这里添加模型席位。")
        self.profiles = {profile.name: profile for profile in room.profiles}
        self._build()
        self.refresh()
        self.connection.set(room.active_profile().name)
        self.pick_connection()
        self.window.update_idletasks()
        left = max(0, room.root.winfo_rootx() + (room.root.winfo_width() - self.window.winfo_reqwidth()) // 2)
        self.window.geometry(f"+{left}+{max(0, room.root.winfo_rooty() + 28)}")
        self.window.grab_set()

    def _build(self):
        frame = ttk.Frame(self.window, padding=16)
        frame.pack(fill="both", expand=True)
        self.heading = ttk.Label(frame)
        self.heading.pack(anchor="w", pady=(0, 5))
        box = ttk.Frame(frame)
        box.pack(fill="x")
        self.listbox = tk.Listbox(box, width=60, height=8, exportselection=False)
        scroll = ttk.Scrollbar(box, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="x", expand=True)
        scroll.pack(side="right", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.select_member)

        rows = ttk.Frame(frame)
        rows.pack(fill="x", pady=(10, 0))
        for index, title in enumerate(("API 连接", "模型", "群内昵称")):
            ttk.Label(rows, text=tr(title)).grid(row=index, column=0, sticky="w", padx=(0, 10), pady=3)
        combo = ttk.Combobox(rows, values=tuple(self.profiles), textvariable=self.connection,
                             state="readonly", width=43)
        combo.grid(row=0, column=1, sticky="ew")
        combo.bind("<<ComboboxSelected>>", self.pick_connection)
        self.models = ttk.Combobox(rows, textvariable=self.model, state="readonly", width=43)
        self.models.grid(row=1, column=1, sticky="ew")
        self.models.bind("<<ComboboxSelected>>", self.suggest_name)
        ttk.Entry(rows, textvariable=self.nickname, width=43).grid(row=2, column=1, sticky="ew")
        rows.columnconfigure(1, weight=1)

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(9, 0))
        for text, command in (
            ("添加模型成员", self.add_member), ("更新选中席位", self.update_member),
            ("加入 Codex", self.add_codex), ("移出选中", self.remove_member),
        ):
            ttk.Button(actions, text=tr(text), command=command).pack(side="left", padx=(0, 5))

        ttk.Label(frame, textvariable=self.status, foreground=MUTED, wraplength=500,
                  justify="left").pack(fill="x", pady=(9, 8))
        footer = ttk.Frame(frame)
        footer.pack(fill="x")
        ttk.Button(footer, text=tr("保存本群成员"), command=self.save).pack(side="right")
        ttk.Button(footer, text=tr("取消"), command=self.window.destroy).pack(side="right", padx=6)

    def refresh(self, selected=None):
        self.heading.configure(text=tr(f"本群成员 · {len(self.members)}/{MAX_MEMBERS} 个模型席位（另有你）"))
        self.listbox.delete(0, "end")
        known = {profile.id for profile in self.profiles.values()}
        for member in self.members:
            model = "本地 Codex" if member.id == CODEX else member.model
            suffix = "  ［连接已移除］" if member.id != CODEX and member.provider_id not in known else ""
            self.listbox.insert("end", f"{member.name}  ·  {model}{suffix}")
        if selected is not None:
            self.listbox.selection_set(selected)
            self.listbox.see(selected)

    def pick_connection(self, _event=None):
        profile = self.profiles[self.connection.get()]
        options = tuple(dict.fromkeys(model for model in (profile.model, *profile.models) if model))
        self.models.configure(values=options)
        self.model.set(profile.model or (options[0] if options else ""))
        self.suggest_name()

    def suggest_name(self, _event=None):
        name = self.connection.get()
        if any(member.name.casefold() == name.casefold() for member in self.members):
            name += " " + self.model.get()
        self.nickname.set(name[:28])

    def select_member(self, _event=None):
        selected = self.listbox.curselection()
        if not selected:
            return
        member = self.members[selected[0]]
        if member.id == CODEX:
            return
        profile = next((item for item in self.profiles.values() if item.id == member.provider_id), None)
        if profile:
            self.connection.set(profile.name)
            self.models.configure(values=tuple(dict.fromkeys((member.model, profile.model, *profile.models))))
        self.model.set(member.model)
        self.nickname.set(member.name)

    def member_from_form(self, member_id):
        name = self.nickname.get().strip()
        model = self.model.get().strip()
        if not name or len(name) > 28 or "@" in name or name.casefold() in RESERVED:
            raise ReplyError("昵称需为 1–28 个字符，避开 Codex、全体等保留名称。")
        if any(member.id != member_id and member.name.casefold() == name.casefold() for member in self.members):
            raise ReplyError("本群已有同名成员，请换一个昵称。")
        if not model:
            raise ReplyError("请先在连接设置读取或填写模型 ID。")
        return Member(member_id, name, self.profiles[self.connection.get()].id, model)

    def add_member(self):
        if len(self.members) >= MAX_MEMBERS:
            self.status.set(f"一个群最多 {MAX_MEMBERS} 个模型席位。")
            return
        try:
            self.members.append(self.member_from_form(uuid4().hex))
        except ReplyError as error:
            self.status.set(str(error))
            return
        self.refresh(len(self.members) - 1)
        self.status.set("席位已添加。保存后可在群聊里点名。")

    def update_member(self):
        selected = self.listbox.curselection()
        if not selected or self.members[selected[0]].id == CODEX:
            self.status.set("请先选中一位 API 模型成员。")
            return
        index = selected[0]
        current = self.members[index]
        try:
            updated = self.member_from_form(current.id)
        except ReplyError as error:
            self.status.set(str(error))
            return
        if (current.provider_id, current.model) != (updated.provider_id, updated.model):
            updated = Member(uuid4().hex, updated.name, updated.provider_id, updated.model)
        self.members[index] = updated
        self.refresh(index)
        self.status.set("选中的模型席位已更新。")

    def add_codex(self):
        if any(member.id == CODEX for member in self.members):
            self.status.set("Codex 已经在群里。")
        elif len(self.members) >= MAX_MEMBERS:
            self.status.set(f"一个群最多 {MAX_MEMBERS} 个模型席位。")
        else:
            self.members.append(CODEX_MEMBER)
            self.refresh(len(self.members) - 1)
            self.status.set("Codex 已加入，保存后生效。")

    def remove_member(self):
        if selected := self.listbox.curselection():
            self.members.pop(selected[0])
            self.refresh()
            self.status.set("已移出该席位，历史发言仍可在群聊中查看。")

    def save(self):
        try:
            save_members(self.room.store, self.room.current_room.id, self.members)
        except sqlite3.Error:
            self.status.set("无法保存群成员，请检查本地记录目录。")
            return
        self.room.refresh_connections()
        self.window.destroy()
