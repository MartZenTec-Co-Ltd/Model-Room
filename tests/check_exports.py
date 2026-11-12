"""V0.6 export correctness and native widget integration checks (no paid APIs)."""
import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

WORK = Path(__file__).resolve().parent
SOURCE = WORK.parent
sys.path.insert(0, str(SOURCE))
from room_core import RoomStore
from room_export import export_chat, export_filename
from model_room import RoomWindow


def check():
    with TemporaryDirectory(dir=WORK) as directory:
        directory = Path(directory)
        os.environ["MODELROOM_DATA_DIR"] = str(directory)
        store = RoomStore(directory)
        a, b = store.add_room("导出測試 日本語 한국어"), store.add_room("另一群")
        store.set_settings(active_room=a.id, private_key="SECRET-CONNECTION-SETTING")
        for i in range(135):
            store.add(a.id, "你" if i % 2 == 0 else "Test model", f"消息 {i}\n第二行 🐈",
                      ("seat-internal",), details={"round": i // 2 + 1, "audience": ["模型甲"],
                                                  "endpoint": "SECRET-CALL-METADATA", "elapsed": 0.2})
        store.add(b.id, "你", "OTHER-ROOM-PRIVATE")
        for suffix in ("md", "txt", "json"):
            path = directory / f"记录.{suffix}"
            assert export_chat(store, a, path) == 135
            text = path.read_text(encoding="utf-8")
            assert "消息 0" in text and "消息 134" in text
            assert all(secret not in text for secret in (
                "OTHER-ROOM-PRIVATE", "SECRET-CONNECTION-SETTING", "SECRET-CALL-METADATA", "seat-internal"))
            if suffix == "json":
                body = json.loads(text)
                assert len(body["messages"]) == 135
                assert body["messages"][0]["round"] == 1
                assert body["messages"][-1]["body"] == "消息 134\n第二行 🐈"
                assert body["messages"][0]["recipients"] == ["模型甲"]
        original = directory / "original.md"
        original.write_text("keep", encoding="utf-8")
        with patch("room_export.os.replace", side_effect=PermissionError("locked")):
            try:
                export_chat(store, a, original)
            except PermissionError:
                pass
            else:
                raise AssertionError("Expected file write failure")
        assert original.read_text() == "keep"
        assert not list(directory.glob(".modelroom-*.tmp"))
        assert export_filename("CON").startswith("_CON-")
        assert not any(c in export_filename('a/b:c?') for c in '/:?')
        root = tk.Tk()
        root.attributes("-alpha", 0)
        errors = []
        root.report_callback_exception = lambda *args: errors.append(args)
        app = RoomWindow(root, store)
        root.update()
        assert not app.web_search.get()
        app.web_toggle.invoke()
        assert app.web_search.get()
        app.web_toggle.event_generate("<space>")
        root.update()
        # Enabling an option does not itself dispatch a network call.
        assert not app.running
        app.edit_toggle.configure(state="disabled")
        app.edit_toggle.invoke()
        assert not app.allow_edit.get()
        app.update_controls()
        for geometry in ("970x640", "1230x760"):
            root.geometry(geometry)
            root.update()
            for widget in (app.web_toggle, app.edit_toggle, app.share_toggle,
                           app.send_button, app.discuss_button, app.pause_button, app.stop_button):
                assert widget.winfo_ismapped()
                assert widget.winfo_width() >= widget.winfo_reqwidth(), (geometry, widget.text, "clipped width")
                assert widget.winfo_x() + widget.winfo_width() <= widget.master.winfo_width(), (geometry, widget.text)
        exported = directory / "from-ui.json"
        with patch("model_room.filedialog.asksaveasfilename", return_value=str(exported)):
            app.export_button.invoke()
        assert len(json.loads(exported.read_text(encoding="utf-8"))["messages"]) == 135
        with patch("model_room.filedialog.asksaveasfilename", return_value=""):
            app.export_button.invoke()
        assert not errors, errors
        app.close()
    print("PASS: 135-message full-room exports in MD/TXT/JSON, Unicode, isolation, metadata exclusion, atomic-write failure, filename rules, UI export/cancel, toggles, and layouts at 970/1230px.")


if __name__ == "__main__":
    check()
