"""Offline release diagnostic, invoked explicitly with EXE --self-test report.json."""
import json
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path


def run():
    import tkinter as tk
    from PIL import Image
    from model_room import RoomWindow
    from room_core import RoomStore
    from room_identity import import_avatar
    from room_preferences import import_wallpaper, save_preferences
    from room_version import VERSION

    # No application data, user transcripts, API keys or network calls are needed.
    for name in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "BRAVE_SEARCH_API_KEY"):
        os.environ.pop(name, None)
    runtime = Path(getattr(sys,'_MEIPASS',Path(sys.executable).resolve().parent)).resolve()
    import model_room
    if (getattr(sys,'frozen',False) or os.environ.get('MODELROOM_REQUIRE_BUNDLED')) and not Path(model_room.__file__).resolve().is_relative_to(runtime):
        raise RuntimeError("Application module was not loaded from the bundled runtime.")
    with tempfile.TemporaryDirectory(prefix="ModelRoom-selftest-") as directory:
        directory = Path(directory)
        os.environ["MODELROOM_DATA_DIR"] = str(directory)
        source = directory/"fixture.png"
        Image.new("RGB", (800, 600), "#bed5f0").save(source)
        wallpaper = import_wallpaper(source, directory)
        avatar = import_avatar(source, directory)
        store = RoomStore(directory)
        save_preferences(store, {"language":"en", "auto_detect_agents":False,
                                 "wallpaper":wallpaper, "avatar":avatar, "nickname":"Release self-test"})
        root = tk.Tk()
        root.attributes("-alpha", 0)
        errors = []
        root.report_callback_exception = lambda *args: errors.append(''.join(traceback.format_exception(*args)))
        app = None
        try:
            app = RoomWindow(root, store)
            app.append_message(app.current_room.id, "你", "Offline release diagnostic")
            finish = time.monotonic()+2
            while time.monotonic()<finish:
                root.update()
                time.sleep(.02)
            if errors:
                raise RuntimeError('\n'.join(errors))
            assert app.wallpaper_image is not None, 'Wallpaper did not render in the bundled GUI.'
            assert app.wallpaper_image.height()==app.timeline.view.winfo_height()
            assert any(photo is not None for photo in app.timeline.avatars.values())
            app.open_settings()
            app.settings_window.window.attributes("-alpha", 0)
            root.update()
            assert len(app.settings_window.pages)==7
            assert app.settings_window.avatar_photo is not None
            personality=app.settings_window.personality
            personality.template.set('审阅伙伴')
            personality.use_template()
            assert app.settings_window.apply()
            assert 'Constructive reviewer' in app.members[0].personality
            from win_secrets import read_secret,write_secret
            key_file=directory/'keys/selftest.key'
            write_secret(key_file,'offline-selftest-fixture')
            assert read_secret(key_file)=='offline-selftest-fixture'
            assert VERSION in root.title()
            assert not errors, "Tk callback failed"
        finally:
            if app is not None:
                app.close()
            else:
                root.destroy()
                store.close()
    return {"ok":True, "version":VERSION, "executable":sys.executable,
            "checks":["bundled application modules", "Tcl/Tk GUI", "Pillow native image libraries",
                      "full chat wallpaper", "avatar rendering", "seven settings pages",
                      "personality template and persistence", "encrypted credential roundtrip", "no model requests"]}


def main():
    report = Path(os.environ["MODELROOM_SELFTEST_REPORT"])
    try:
        result, code = run(), 0
    except Exception:
        result, code = {"ok":False, "error":traceback.format_exc()}, 1
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if code and sys.stderr is not None:
        sys.stderr.write(result['error'])
    return code


if __name__ == "__main__":
    raise SystemExit(main())
