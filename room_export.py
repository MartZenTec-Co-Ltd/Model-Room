"""Portable exports of a single room's full transcript; no connection settings."""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from room_identity import display_author


def export_filename(name):
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .")[:70] or "ModelRoom"
    if safe.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                                     *(f"LPT{i}" for i in range(1, 10))}:
        safe = "_" + safe
    return f"{safe}-{datetime.now():%Y%m%d-%H%M%S}.md"


def export_chat(store, room, destination):
    """Write a UTF-8 snapshot atomically. Return the number of exported messages."""
    destination = Path(destination)
    kind = destination.suffix.lower()
    if kind not in {".md", ".txt", ".json"}:
        raise ValueError("请选择 .md、.txt 或 .json 文件。")
    messages = store.recent(room.id, limit=-1)
    exported = datetime.now().astimezone().isoformat(timespec="seconds")
    if kind == ".json":
        body = json.dumps({"format": "model-room-transcript", "version": 1, "room": room.name,
                           "exported_at": exported, "messages": [
            {"author": display_author(m), "time": m.time, "body": m.body,
             "recipients": list(m.details.get("audience", m.recipients)),
             **({"round": m.details["round"]} if m.details.get("round") else {})}
            for m in messages]}, ensure_ascii=False, indent=2) + "\n"
    else:
        markdown = kind == ".md"
        title = room.name.replace("\r", " ").replace("\n", " ")
        lines = [f"{'# ' if markdown else ''}{title}", "", f"Model Room · {exported}",
                 f"消息数 / Messages: {len(messages)}", ""]
        for m in messages:
            heading = f"{display_author(m)} · {m.time.replace('T', ' ')}"
            if number := m.details.get("round"):
                heading += f" · 第 {number} 轮"
            if audience := m.details.get("audience", m.recipients):
                heading += " → " + "、".join(audience)
            lines.extend([f"{'## ' if markdown else ''}{heading}", "", m.body, "",
                          "---" if markdown else "─" * 32, ""])
        body = "\n".join(lines)
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", prefix=".modelroom-",
                                suffix=".tmp", dir=destination.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(body)
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return len(messages)
