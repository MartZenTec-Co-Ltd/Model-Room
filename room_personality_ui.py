"""A draft-based per-seat Markdown editor inside Settings."""
from dataclasses import replace
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from room_group import save_members
from room_locale import tr, EnumCombo
from room_personality import clean_personality, read_personality
from room_style import MUTED


class PersonalityPanel:
    def __init__(self, parent, room, changed):
        self.room, self.changed = room, changed
        self.room_id = room.current_room.id
        self.members = list(room.members)
        self.original = {member.id: member.personality for member in self.members}
        self.drafts = dict(self.original)
        self.current = None
        panel = ttk.Frame(parent, padding=24)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text=tr('AI 性格'), font=('Segoe UI',17,'bold')).pack(anchor='w',pady=(0,10))
        ttk.Label(panel, text=tr('为本群每个 AI 设置表达方式和协作偏好；普通回复和每轮讨论都会使用。'),
                  wraplength=540, foreground=MUTED, justify='left').pack(fill='x',pady=(0,14))
        self.choice = ttk.Combobox(panel, state='readonly', values=[m.name for m in self.members])
        self.choice.pack(fill='x', pady=(0,12))
        self.choice.bind('<<ComboboxSelected>>', self.select)
        self.template = tk.StringVar(value='选择性格模板')
        templates = EnumCombo(panel,textvariable=self.template,state='readonly',
                             values=('选择性格模板','创意伙伴','审阅伙伴','执行伙伴'))
        templates.pack(fill='x',pady=(0,12))
        templates.bind('<<ComboboxSelected>>',self.use_template,add='+')
        box = ttk.Frame(panel)
        box.pack(fill='both',expand=True)
        self.editor = tk.Text(box, wrap='word', undo=True, height=12, width=40)
        scroll = ttk.Scrollbar(box, command=self.editor.yview)
        self.editor.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y')
        self.editor.pack(side='left',fill='both',expand=True)
        self.editor.bind('<<Modified>>', self.modified)
        actions = ttk.Frame(panel)
        actions.pack(fill='x',pady=12)
        for caption, command in (('导入 Markdown',self.import_markdown),('导出 Markdown',self.export_markdown),('清空性格',self.clear)):
            ttk.Button(actions,text=tr(caption),command=command).pack(side='left',padx=(0,8))
        ttk.Label(panel,text=tr('导入只复制文字，不执行文件。留空使用默认风格。套用或确定后保存；取消放弃未保存更改。'),
                  wraplength=540, foreground=MUTED,justify='left').pack(fill='x')
        if self.members:
            self.choice.current(0)
            self.select()
        else:
            self.editor.configure(state='disabled')
            ttk.Label(panel,text=tr('请先在管理 AI 成员中添加模型。')).pack(anchor='w',pady=10)

    def flush(self):
        if self.current is not None:
            self.drafts[self.current] = self.editor.get('1.0','end-1c')

    @property
    def dirty(self):
        self.flush()
        return self.drafts != self.original

    def select(self, _event=None):
        self.flush()
        index = self.choice.current()
        if index < 0:
            return
        self.current = self.members[index].id
        self.template.set('选择性格模板')
        self.editor.delete('1.0','end')
        self.editor.insert('1.0',self.drafts[self.current])
        self.editor.edit_modified(False)

    def modified(self, _event=None):
        if self.editor.edit_modified():
            self.flush()
            self.editor.edit_modified(False)
            self.changed()

    def clear(self):
        if self.current is not None:
            self.editor.delete('1.0','end')
            self.flush()
            self.changed()

    def use_template(self, _event=None):
        if self.current is None:
            return
        names={'创意伙伴':'creative.md','审阅伙伴':'reviewer.md','执行伙伴':'builder.md'}
        if name:=names.get(self.template.get()):
            content=read_personality(Path(__file__).parent/'examples/personalities'/name)
            self.editor.delete('1.0','end')
            self.editor.insert('1.0',content)
            self.flush()
            self.changed()

    def import_markdown(self):
        if self.current is None:
            return
        filename = filedialog.askopenfilename(parent=self.editor.winfo_toplevel(),title=tr('导入 Markdown'),
                                               filetypes=[('Markdown','*.md *.markdown')])
        if not filename:
            return
        try:
            content = read_personality(filename)
        except (OSError,ValueError) as error:
            messagebox.showerror(tr('AI 性格'),tr(str(error)),parent=self.editor.winfo_toplevel())
            return
        self.editor.delete('1.0','end')
        self.editor.insert('1.0',content)
        self.flush()
        self.changed()

    def export_markdown(self):
        if self.current is None:
            return
        self.flush()
        try:
            content = clean_personality(self.drafts[self.current])
            filename = filedialog.asksaveasfilename(parent=self.editor.winfo_toplevel(),title=tr('导出 Markdown'),
                defaultextension='.md',initialfile='AI-personality.md',filetypes=[('Markdown','*.md')])
            if filename:
                Path(filename).write_text(content+'\n',encoding='utf-8')
        except (OSError,ValueError) as error:
            messagebox.showerror(tr('AI 性格'),tr(str(error)),parent=self.editor.winfo_toplevel())

    def commit(self):
        self.flush()
        values = {key:clean_personality(text) for key,text in self.drafts.items()}
        if self.room.current_room.id != self.room_id:
            raise ValueError('群聊已切换，请重新打开设置。')
        if not self.dirty:
            return
        current = self.room.members
        if {member.id for member in current} != set(values):
            raise ValueError('群成员已变更，请重新打开设置。')
        updated = [replace(member,personality=values[member.id]) for member in current]
        save_members(self.room.store,self.room_id,updated)
        self.room.members = updated
        self.original = dict(values)
        self.drafts = dict(values)
        if self.current is not None:
            self.editor.delete('1.0','end')
            self.editor.insert('1.0',values[self.current])
            self.editor.edit_modified(False)
        self.room.refresh_connections()
