"""Presentation translations; persisted identifiers, nicknames and chat stay untouched."""
import json
import locale
import re
import tkinter as tk
from pathlib import Path
from tkinter import ttk

LANGUAGES = {"zh-Hans": "简体中文", "zh-Hant": "繁體中文", "en": "English", "ja": "日本語", "ko": "한국어"}
_language = "zh-Hans"
_catalog = json.loads(Path(__file__).with_name("translations.json").read_text(encoding="utf-8"))
_patterns = []


def system_language():
    name = (locale.getlocale()[0] or "en").lower().replace("_", "-")
    if name.startswith("zh") or "chinese" in name:
        return "zh-Hant" if any(x in name for x in ("tw", "hk", "traditional")) else "zh-Hans"
    return next((code for code in ("ja", "ko") if name.startswith(code)), "en")


def set_language(code):
    global _language, _patterns
    _language = code if code in LANGUAGES else system_language()
    table = _catalog.get(_language, {})
    _patterns = []
    for source, target in table.items():
        if "{p" not in source:
            continue
        parts = re.split(r"(\{p\d+\})", source)
        pattern = "".join(f"(?P<{part[1:-1]}>.+?)" if re.fullmatch(r"\{p\d+\}", part)
                          else re.escape(part) for part in parts)
        _patterns.append((re.compile("^" + pattern + "$", re.S), target))
    _patterns.sort(key=lambda pair: len(pair[0].pattern), reverse=True)


def tr(text):
    if not isinstance(text, str) or not text or _language == "zh-Hans":
        return text
    table = _catalog.get(_language, {})
    if text in table:
        return table[text]
    if text != text.strip():
        left = text[:len(text)-len(text.lstrip())]
        right = text[len(text.rstrip()):]
        return left + tr(text.strip()) + right
    for pattern, target in _patterns:
        if match := pattern.fullmatch(text):
            return target.format(**match.groupdict())
    if "\n" in text:
        return "\n".join(tr(line) for line in text.split("\n"))
    if " · " in text:
        return " · ".join(tr(part) for part in text.split(" · "))
    return text


class DisplayVar(tk.StringVar):
    """A read-only display value whose Python get() retains the original status."""
    def __init__(self, *args, value="", **kwargs):
        self.source = value
        super().__init__(*args, value=tr(value), **kwargs)

    def set(self, value):
        self.source = value
        super().set(tr(value))

    def get(self):
        return self.source


class EnumCombo(ttk.Combobox):
    """Translate enum labels without changing the canonical variable or model IDs."""
    def __init__(self, parent, *, textvariable, values=(), translate_only=None, **kwargs):
        self.canonical = textvariable
        self.display = tk.StringVar(parent)
        self.sources = tuple(values)
        self.translate_only = translate_only
        super().__init__(parent, textvariable=self.display, **kwargs)
        self.token = self.canonical.trace_add("write", self.refresh)
        super().bind("<<ComboboxSelected>>", self.selected, add="+")
        self.configure(values=values)

    def caption(self, value):
        if self.translate_only is None and value == "关闭":
            return {"en": "Off", "zh-Hant": "關閉", "ja": "オフ", "ko": "끄기"}.get(_language, value)
        return tr(value) if self.translate_only is None or value in self.translate_only else value

    def refresh(self, *_):
        self.display.set(self.caption(self.canonical.get()))

    def selected(self, _event=None):
        index = self.current()
        if 0 <= index < len(self.sources):
            self.canonical.set(self.sources[index])

    def bind(self, sequence=None, func=None, add=None):
        if sequence == "<<ComboboxSelected>>" and func:
            return super().bind(sequence, func, add="+")
        return super().bind(sequence, func, add)

    def configure(self, cnf=None, **kwargs):
        if cnf:
            kwargs.update(cnf)
        if "values" in kwargs:
            self.sources = tuple(kwargs["values"])
            kwargs["values"] = tuple(self.caption(value) for value in self.sources)
        result = super().configure(**kwargs)
        self.refresh()
        return result

    config = configure

    def destroy(self):
        self.canonical.trace_remove("write", self.token)
        super().destroy()


set_language("zh-Hans")
