"""Shared desktop palette and original, code-drawn icons. No external assets."""

import os
import sys
import tkinter as tk
from tkinter import font as tkfont, ttk
from room_locale import tr

SURFACE = "#ffffff"
BACKGROUND = "#f4f6fb"
SIDEBAR = "#f8f9fd"
INK = "#202c45"
MUTED = "#67758c"
LINE = "#e4e9f2"
ACCENT = "#5262d5"
ACCENT_PALE = "#edf0ff"
GREEN = "#16806b"
FONT = "Microsoft YaHei UI" if os.name == "nt" else "TkDefaultFont"
SOFT = "#f1f4fa"
HOVER = "#e5eafb"
DISABLED = "#f3f5f9"
DISABLED_INK = "#9aa5b7"


def blend(first, second, amount):
    a = tuple(int(first[i:i+2], 16) for i in (1, 3, 5))
    b = tuple(int(second[i:i+2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{round(x*(1-amount)+y*amount):02x}" for x, y in zip(a, b))


def configure_palette(options):
    colors = dict(SURFACE="#ffffff", BACKGROUND="#f4f6fb", SIDEBAR="#f8f9fd", INK="#202c45",
                  MUTED="#67758c", LINE="#e4e9f2", SOFT="#f1f4fa", DISABLED="#f3f5f9", DISABLED_INK="#9aa5b7")
    if options["mode"] == "dark":
        colors.update(SURFACE="#192233", BACKGROUND="#101725", SIDEBAR="#141c2b", INK="#edf1f8",
                      MUTED="#a9b6ca", LINE="#354158", SOFT="#243047", DISABLED="#202a3c", DISABLED_INK="#72809a")
    colors["ACCENT"] = options["accent"]
    colors["ACCENT_PALE"] = blend(colors["SURFACE"], colors["ACCENT"], .18)
    colors["HOVER"] = blend(colors["SURFACE"], colors["ACCENT"], .28)
    for name in ("room_style", "model_room", "__main__", "room_settings", "room_members", "room_lan_ui", "room_settings_hub"):
        if module := sys.modules.get(name):
            for key, value in colors.items():
                if hasattr(module, key):
                    setattr(module, key, value)
    return colors


def setup_theme(root):
    """Apply the same spacing and colors to the settings and member dialogs."""
    root.option_add("*Font", (FONT, 10))
    root.option_add("*Listbox.background", BACKGROUND)
    root.option_add("*Listbox.foreground", INK)
    root.option_add("*Listbox.selectBackground", ACCENT_PALE)
    root.option_add("*Listbox.selectForeground", ACCENT)
    root.option_add("*Listbox.relief", "flat")
    root.option_add("*Listbox.highlightThickness", 0)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", font=(FONT, 10), background=SURFACE, foreground=INK)
    style.configure("TButton", padding=(12, 8), relief="flat", background=ACCENT_PALE,
                    foreground=ACCENT, borderwidth=0, focusthickness=1, focuscolor=ACCENT)
    style.map("TButton", background=[("active", HOVER), ("disabled", BACKGROUND)],
              foreground=[("disabled", MUTED)])
    style.configure("Nav.TButton", background=SURFACE, foreground=MUTED, anchor="w", padding=(12, 12))
    style.configure("SelectedNav.TButton", background=ACCENT_PALE, foreground=INK, anchor="w", padding=(12, 12))
    style.map("Nav.TButton", background=[("active", HOVER)])
    style.map("SelectedNav.TButton", background=[("active", HOVER)])
    style.configure("TEntry", padding=7, fieldbackground=BACKGROUND, bordercolor=LINE,
                    lightcolor=LINE, darkcolor=LINE)
    style.map("TEntry", bordercolor=[("focus", ACCENT)])
    style.configure("TCombobox", padding=6, fieldbackground=BACKGROUND, background=BACKGROUND,
                    bordercolor=LINE, arrowcolor=MUTED, lightcolor=LINE, darkcolor=LINE)
    style.map("TCombobox", fieldbackground=[("readonly", BACKGROUND)],
              foreground=[("readonly", INK)], selectbackground=[("readonly", BACKGROUND)],
              selectforeground=[("readonly", INK)], bordercolor=[("focus", ACCENT)])
    style.configure("TNotebook", background=SURFACE, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(17, 10), background=BACKGROUND, foreground=MUTED)
    style.map("TNotebook.Tab", background=[("selected", ACCENT_PALE)],
              foreground=[("selected", INK)])
    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE, foreground=INK,
                    bordercolor=LINE, rowheight=30)
    style.map("Treeview", background=[("selected", ACCENT_PALE)], foreground=[("selected", INK)])
    style.configure("Treeview.Heading", background=BACKGROUND, foreground=INK, padding=7)
    style.configure("TCheckbutton", background=SURFACE, foreground=INK)
    style.map("TCheckbutton", background=[("active", SURFACE)], foreground=[("active", INK)])
    style.layout("Vertical.TScrollbar", [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
        ("Vertical.Scrollbar.thumb", {"expand": 1, "sticky": "nswe"})]})])
    thumb = blend(SURFACE, MUTED, .4)
    style.configure("Vertical.TScrollbar", background=thumb, troughcolor=BACKGROUND,
                    lightcolor=thumb, darkcolor=thumb, bordercolor=BACKGROUND,
                    borderwidth=0, arrowsize=8, width=8, gripcount=0)
    style.map("Vertical.TScrollbar", background=[("active", MUTED)],
              lightcolor=[("active", MUTED)], darkcolor=[("active", MUTED)])


def draw_icon(canvas, name, x, y, color, size=18):
    """Draw a consistent 24-unit stroke icon in native Tk canvas coordinates."""
    scale = size / 24

    def points(values):
        return [(x if i % 2 == 0 else y) + value * scale for i, value in enumerate(values)]

    def line(*values):
        canvas.create_line(*points(values), fill=color, width=1.7 * scale,
                           capstyle="round", joinstyle="round")

    def box(a, b, c, d):
        canvas.create_rectangle(*points((a, b, c, d)), outline=color, width=1.7 * scale)

    def oval(a, b, c, d):
        canvas.create_oval(*points((a, b, c, d)), outline=color, width=1.7 * scale)

    if name == "globe":
        oval(3, 3, 21, 21); oval(8, 3, 16, 21); line(3, 12, 21, 12)
    elif name == "shield":
        line(12, 2, 21, 6, 20, 15, 16, 20, 12, 23, 8, 20, 4, 15, 3, 6, 12, 2)
        line(8, 12, 11, 15, 16, 9)
    elif name == "download":
        line(12, 3, 12, 15); line(7, 10, 12, 15, 17, 10); line(4, 16, 4, 21, 20, 21, 20, 16)
    elif name == "plus":
        line(12, 4, 12, 20); line(4, 12, 20, 12)
    elif name == "folder":
        line(3, 20, 3, 5, 9, 5, 12, 8, 21, 8, 21, 20, 3, 20); line(3, 11, 21, 11)
    elif name == "open":
        line(13, 3, 21, 3, 21, 11); line(21, 3, 10, 14); line(9, 5, 3, 5, 3, 21, 19, 21, 19, 15)
    elif name == "copy":
        box(8, 8, 21, 21); line(16, 8, 16, 3, 3, 3, 3, 16, 8, 16)
    elif name == "edit":
        line(4, 16, 16, 4, 20, 8, 8, 20, 3, 21, 4, 16); line(13, 7, 17, 11)
    elif name == "settings":
        for a, b in ((6, 8), (12, 16), (18, 9)):
            line(a, 3, a, b - 3); line(a, b + 3, a, 21); oval(a - 2.5, b - 2.5, a + 2.5, b + 2.5)
    elif name == "people":
        oval(4, 3, 12, 11); oval(14, 6, 20, 12)
        line(2, 21, 2, 18, 4, 15, 12, 15, 14, 18, 14, 21); line(16, 15, 20, 15, 22, 18, 22, 21)
    elif name == "network":
        box(8, 2, 16, 8); box(2, 16, 10, 22); box(14, 16, 22, 22)
        line(12, 8, 12, 12, 6, 12, 6, 16); line(12, 12, 18, 12, 18, 16)
    elif name == "send":
        line(3, 3, 22, 12, 3, 21, 7, 12, 3, 3); line(7, 12, 22, 12)
    elif name in {"chat", "history"}:
        line(3, 4, 21, 4, 21, 17, 10, 17, 4, 22, 4, 17, 3, 17, 3, 4)
        line(7, 9, 17, 9); line(7, 13, 14, 13)
    elif name == "pause":
        line(8, 5, 8, 19); line(16, 5, 16, 19)
    elif name == "stop":
        box(5, 5, 19, 19)


class ActionButton(tk.Canvas):
    """Rounded keyboard-accessible button with vector icon and visible focus."""
    def __init__(self, parent, text, command, *, primary=False, icon=None, variable=None, compact=False):
        super().__init__(parent, background=parent.cget("bg"), highlightthickness=0,
                         borderwidth=0, takefocus=True, cursor="hand2", height=32 if compact else 36)
        self.text, self.command, self.primary, self.icon = text, command, primary, icon
        self.variable, self.compact = variable, compact
        self.enabled, self.hover, self.focused = True, False, False
        self.face = tkfont.Font(self, family=FONT, size=9, weight="bold" if primary else "normal")
        self.trace_id = variable.trace_add("write", lambda *_: self.draw()) if variable is not None else None
        self.bind("<Button-1>", self._click)
        self.bind("<Return>", self._key)
        self.bind("<space>", self._key)
        for event, flag, value in (("<Enter>", "hover", True), ("<Leave>", "hover", False),
                                   ("<FocusIn>", "focused", True), ("<FocusOut>", "focused", False)):
            self.bind(event, lambda _event, f=flag, v=value: self._flag(f, v))
        self.draw()

    def _flag(self, name, value):
        setattr(self, name, value)
        self.draw()

    def _key(self, _event):
        self.invoke()
        return "break"

    def _click(self, _event):
        if self.enabled:
            self.focus_set()
            self.invoke()

    def invoke(self):
        if not self.enabled:
            return
        if self.variable is not None:
            self.variable.set(not self.variable.get())
        if self.command:
            return self.command()

    def configure(self, cnf=None, **kwargs):
        if cnf:
            kwargs.update(cnf)
        redraw = False
        if "text" in kwargs:
            self.text = kwargs.pop("text"); redraw = True
        if "state" in kwargs:
            self.enabled = kwargs.pop("state") != "disabled"
            super().configure(state="normal" if self.enabled else "disabled", takefocus=self.enabled,
                              cursor="hand2" if self.enabled else "arrow")
            redraw = True
        result = super().configure(**kwargs) if kwargs else None
        if redraw:
            self.draw()
        return result

    config = configure

    def draw(self):
        self.delete("all")
        selected = self.variable is not None and self.variable.get()
        strong = self.primary and self.variable is None
        bg = ACCENT if strong else (ACCENT_PALE if selected else SOFT)
        light_accent = sum(int(ACCENT[i:i+2], 16) * weight for i, weight in ((1, .2126), (3, .7152), (5, .0722))) > 165
        fg = ("#172033" if light_accent else "#ffffff") if strong else (INK if selected else MUTED)
        if self.hover and self.enabled:
            bg = blend(ACCENT, INK, .12) if strong else HOVER
        if not self.enabled:
            bg, fg = DISABLED, DISABLED_INK
        h = 32 if self.compact else 36
        caption = tr(self.text)
        w = self.face.measure(caption) + 24 + (25 if self.icon else 0) + (13 if self.variable is not None else 0)
        super().configure(width=w, height=h)
        r = 8
        self.create_polygon(1+r, 1, w-1-r, 1, w-1, 1, w-1, 1+r, w-1, h-1-r,
                            w-1, h-1, w-1-r, h-1, 1+r, h-1, 1, h-1, 1, h-1-r,
                            1, 1+r, 1, 1, smooth=True, splinesteps=24, fill=bg,
                            outline=ACCENT if self.focused else bg, width=1)
        if self.icon:
            draw_icon(self, self.icon, 12, (h-18)/2, fg)
        self.create_text(37 if self.icon else 12, h/2, text=caption, anchor="w", fill=fg, font=self.face)
        if self.variable is not None:
            self.create_oval(w-13, h/2-3, w-7, h/2+3, outline=fg, fill=fg if selected else bg, width=1)

    def destroy(self):
        if self.trace_id is not None:
            self.variable.trace_remove("write", self.trace_id)
            self.trace_id = None
        super().destroy()
