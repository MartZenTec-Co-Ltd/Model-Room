"""Reusable settings controls. Chat controls retain their existing behavior."""
import tkinter as tk
from tkinter import ttk

import room_style as palette


class ToggleSwitch(tk.Canvas):
    """A keyboard-operable Boolean switch, with a round track and sliding thumb."""
    def __init__(self, parent, variable, *, label="", command=None):
        super().__init__(parent, width=54, height=32, bg=palette.SURFACE,
                         highlightthickness=0, bd=0, takefocus=True, cursor="hand2")
        self.variable, self.command, self.label = variable, command, label
        self.enabled, self.focused = True, False
        self.trace = variable.trace_add("write", lambda *_: self.draw())
        self.bind("<Button-1>", self._click)
        self.bind("<space>", lambda _: self.invoke())
        self.bind("<Return>", lambda _: self.invoke())
        self.bind("<Left>", lambda _: self.set_value(False))
        self.bind("<Right>", lambda _: self.set_value(True))
        self.bind("<FocusIn>", lambda _: self._focus(True))
        self.bind("<FocusOut>", lambda _: self._focus(False))
        self.draw()

    def _click(self, _event):
        if self.enabled:
            self.focus_set()
            self.invoke()
        return "break"

    def _focus(self, focused):
        self.focused = focused
        self.draw()

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)
        self.configure(takefocus=self.enabled, cursor="hand2" if self.enabled else "arrow")
        self.draw()

    def set_value(self, value):
        if self.enabled and bool(self.variable.get()) != bool(value):
            self.variable.set(bool(value))
            if self.command:
                self.command()
        return "break"

    def invoke(self):
        return self.set_value(not self.variable.get())

    def draw(self):
        self.delete("all")
        self.configure(bg=palette.SURFACE)
        selected = self.variable.get()
        fill = palette.ACCENT if selected else palette.blend(palette.SURFACE, palette.MUTED, .42)
        if not self.enabled:
            fill = palette.DISABLED
        # Thick round-ended line makes a true capsule, without polygon seams.
        self.create_line(17, 16, 37, 16, fill=fill, width=28, capstyle="round", tags="track")
        x = 37 if selected else 17
        brightness = sum(int(fill[i:i+2],16)*weight for i,weight in ((1,.2126),(3,.7152),(5,.0722)))
        thumb = "#172033" if brightness > 190 else "#ffffff"
        self.create_oval(x-10, 6, x+10, 26, fill=thumb, outline=thumb, tags="thumb")
        if self.focused:
            self.create_rectangle(1, 1, 53, 31, outline=palette.ACCENT, width=1, tags="focus")

    def destroy(self):
        if self.trace:
            self.variable.trace_remove("write", self.trace)
            self.trace = None
        super().destroy()


class SettingsScroll(ttk.Frame):
    """Bound a form to the available width; keep dialog actions outside scrolling."""
    def __init__(self, parent, *, padding=24):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, bg=palette.SURFACE, highlightthickness=0, width=1, height=1)
        bar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.panel = ttk.Frame(self.canvas, padding=padding)
        slot = self.canvas.create_window(0, 0, window=self.panel, anchor="nw")
        self.panel.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(slot, width=e.width))
        self.top = self.winfo_toplevel()
        self.wheel_binding = self.top.bind("<MouseWheel>", self._wheel, add="+")
        self.bind("<Destroy>", self._destroyed)

    def _wheel(self, event):
        if self.winfo_viewable() and str(event.widget).startswith(str(self)):
            if self.canvas.bbox("all") and self.canvas.bbox("all")[3] > self.canvas.winfo_height():
                self.canvas.yview_scroll(-int(event.delta/120), "units")
                return "break"

    def _destroyed(self, event):
        if event.widget is self and self.wheel_binding:
            self.top.unbind("<MouseWheel>", self.wheel_binding)
            self.wheel_binding = None
