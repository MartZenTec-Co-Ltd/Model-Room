"""Host controls for sharing a room with the local network."""

import tkinter as tk
import webbrowser
from room_style import MUTED
from room_locale import tr, DisplayVar, EnumCombo
from tkinter import ttk

from room_lan import local_addresses


class LanWindow:
    def __init__(self, window):
        self.host = window
        self.room_id = window.current_room.id
        self.window = tk.Toplevel(window.root)
        self.window.title(tr("局域网参会 · Model Room"))
        self.window.transient(window.root)
        self.window.resizable(False, False)
        addresses = local_addresses()
        listening = window.lan.address
        self.address = tk.StringVar(value=listening[0] if listening else addresses[0])
        self.port = tk.StringVar(value=str(listening[1]) if listening else "8765")
        self.link = tk.StringVar()
        self.status = DisplayVar()
        content = ttk.Frame(self.window, padding=16)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text=tr(f"邀请加入 · {window.current_room.name}")).pack(anchor="w")
        ttk.Label(content, text=tr("队友在同一网络用浏览器打开邀请链接，填写昵称即可发言。"),
                  wraplength=510).pack(anchor="w", pady=(4, 9))
        row = ttk.Frame(content)
        row.pack(fill="x")
        ttk.Label(row, text=tr("主机 IPv4")).pack(side="left")
        ttk.Combobox(row, values=addresses, textvariable=self.address, width=18).pack(side="left", padx=6)
        ttk.Label(row, text=tr("端口")).pack(side="left", padx=(5, 0))
        ttk.Entry(row, textvariable=self.port, width=7).pack(side="left", padx=6)
        ttk.Button(row, text=tr("开启本群邀请"), command=self.start).pack(side="right")
        ttk.Entry(content, textvariable=self.link, state="readonly", width=70).pack(fill="x", pady=(9, 6))
        actions = ttk.Frame(content)
        actions.pack(fill="x")
        for text, action in (
            ("复制邀请", self.copy), ("打开参会页", self.browse),
            ("关闭本群邀请", self.revoke), ("停止局域网服务", self.stop),
        ):
            ttk.Button(actions, text=tr(text), command=action).pack(side="left", padx=(0, 5))
        ttk.Label(content, textvariable=self.status, foreground=MUTED, wraplength=510,
                  justify="left").pack(fill="x", pady=(9, 0))
        self.refresh()

    def refresh(self):
        self.link.set(self.host.lan.link(self.room_id))
        self.status.set(
            "访客可见开启邀请后的本群消息。请在可信局域网内分享链接。"
            if self.link.get() else "邀请关闭。选择局域网地址后开启，127.0.0.1 仅供本机预览。"
        )

    def start(self):
        try:
            listening = self.host.lan.address
            if listening is None:
                self.host.lan.start(self.address.get().strip(), int(self.port.get()))
            elif (self.address.get(), self.port.get()) != (listening[0], str(listening[1])):
                self.status.set("服务已在其他地址或端口运行。更换前请先停止局域网服务。")
                return
            host, port = self.host.lan.address
            self.address.set(host)
            self.port.set(str(port))
            self.host.lan.invite(self.room_id, self.host.store.latest_message(self.room_id))
            self.host.publish_room(self.room_id)
        except ValueError:
            self.status.set("请选择有效的本机 IPv4 地址和端口。")
            return
        except OSError:
            self.status.set("无法监听该地址。请检查本机地址、端口占用或网络权限。")
            return
        self.refresh()

    def copy(self):
        if link := self.link.get():
            self.window.clipboard_clear()
            self.window.clipboard_append(link)
            self.status.set("邀请链接已复制。")

    def browse(self):
        if link := self.link.get():
            webbrowser.open(link)

    def revoke(self):
        self.host.lan.revoke(self.room_id)
        self.refresh()

    def stop(self):
        self.host.lan.close()
        self.refresh()
