"""UI preference persistence, five real UI languages, wallpaper and local agents."""
import json
import os
import sys
import time
import tkinter as tk
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK.parent))
from PIL import Image
import model_room
from model_room import RoomWindow
from room_core import RoomStore
from room_locale import LANGUAGES, tr, EnumCombo
from room_preferences import import_wallpaper, load_preferences
from room_agents import LocalAgent, HarnessClient, launcher, desktop_harness, agent_environment, agent_version
from room_providers import Profile, ask_profile


def widgets(parent):
    for child in parent.winfo_children():
        yield child
        yield from widgets(child)


with TemporaryDirectory(dir=WORK) as temporary:
    temporary = Path(temporary)
    os.environ["MODELROOM_DATA_DIR"] = str(temporary)
    store = RoomStore(temporary)
    group = store.add_room("设置")
    store.set_settings(active_room=group.id)
    store.add(group.id, "你", "设置")
    root = tk.Tk(); root.attributes("-alpha", 0)
    errors = []
    root.report_callback_exception = lambda *error: errors.append(error)
    app = RoomWindow(root, store)
    app.suggest("草稿 / draft / 下書き / 초안")
    original = temporary / "original.jpg"
    Image.new("RGB", (1400, 800), "#c982b3").save(original)
    wallpaper = import_wallpaper(original, temporary)
    original.unlink()
    for code in LANGUAGES:
        app.apply_preferences({**app.preferences, "language": code, "mode": "dark", "accent": "#b284e8",
                               "wallpaper": wallpaper, "auto_detect_agents": False})
        root.update()
        assert load_preferences(store)["language"] == code
        assert app.composer.get("1.0", "end-1c") == "草稿 / draft / 下書き / 초안"
        assert store.recent(group.id)[0].body == "设置", "Chat must never be translated"
        assert app.room_title.get() == "设置", "Custom group names must never be translated"
        assert model_room.SURFACE == "#192233"
        assert app.recipient.get() == "全体成员"
        assert app.recipient_picker.display.get() == tr("全体成员")
        assert app.activity.get() == "就绪"
        assert root.getvar(app.activity._name) == tr("就绪")
        app.open_settings()
        root.update()
        settings = app.settings_window
        assert list(settings.pages) == ["general", "connections", "appearance", "chat", "storage", "about"]
        labels = [str(w.cget("text")) for w in widgets(settings.window) if "text" in w.keys()]
        assert tr("套用") in labels and tr("自动检测本机 Agent") in labels
        settings.select("appearance")
        settings.window.geometry('900x560')
        root.update()
        canvas = settings.scrollers["appearance"].canvas
        canvas.yview_moveto(1)
        root.update()
        assert canvas.bbox('all')[3] > canvas.winfo_height(), 'Appearance controls must scroll in small windows'
        assert canvas.yview()[1] > .99, 'The bottom actions must remain reachable'
        settings.select("connections")
        c = settings.connection
        c.tabs.select(3)
        c.agent_results = [LocalAgent("claude", "Claude Code", sys.executable, "已找到程序")]
        c.draw_agents(); c.agent_tree.selection_set("claude")
        before = len(app.profiles)
        c.connect_agent(); c.connect_agent()
        assert len(app.profiles) <= before+1, "Saving the same local agent must not duplicate profiles"
        profile = next(p for p in app.profiles if p.transport == "claude-cli")
        assert profile.base == sys.executable
        settings.window.destroy()
        # Allow image resizing and stale callback bugs to surface.
        for _ in range(3):
            root.update(); time.sleep(.05)
        assert app.wallpaper_image is not None
    # Canonical values must remain stable even when a nickname matches a UI label.
    raw = tk.StringVar(value="关闭")
    combo = EnumCombo(root, textvariable=raw, values=("关闭", "全体成员"), translate_only={"全体成员"})
    assert combo.display.get() == "关闭"
    combo.destroy()
    app.apply_preferences({**app.preferences, "mode": "light", "wallpaper": ""})
    root.update()
    assert model_room.SURFACE == "#ffffff"
    assert not errors, errors
    app.close()

    from types import SimpleNamespace
    from room_style import configure_palette
    entrypoint = SimpleNamespace(SURFACE='old')
    with patch.dict(sys.modules, {'__main__':entrypoint}):
        configure_palette({'mode':'dark','accent':'#5262d5'})
        assert entrypoint.SURFACE == '#192233', 'The -m EXE entry point must receive palette updates too'

    npm = temporary / "npm"
    package = npm / "node_modules" / "@deepseek-ai" / "dsh"
    package.mkdir(parents=True)
    shim = npm / "dsh.cmd"; shim.write_text("This wrapper must never be run")
    (package / "cli.js").write_text("// fixture")
    (package / "package.json").write_text(json.dumps({"bin": {"dsh": "cli.js"}}))
    with patch("room_agents.shutil.which", return_value=sys.executable):
        command, _ = launcher("dsh", str(shim))
        assert command == (sys.executable, str((package / "cli.js").resolve()))
        (package / "package.json").write_text(json.dumps({"bin": {"dsh": "../../../../escape.js"}}))
        assert launcher("dsh", str(shim))[0] == (), "Reject package paths that escape the installed package"

    desktop = temporary / 'Harness'
    desktop.mkdir()
    executable = desktop / 'DeepSeek Harness.exe'; executable.touch()
    resources = desktop / 'resources'; resources.mkdir()
    (resources / 'app.asar').touch()
    wrapper = resources / 'runtime/cli/bin/dsh.cmd'
    wrapper.parent.mkdir(parents=True); wrapper.write_text('Do not execute this wrapper')
    for selected in (executable, wrapper):
        command, path = desktop_harness(selected)
        assert path == str(executable.resolve())
        assert command[1] == '--expose-internals'
        assert agent_environment(command)['ELECTRON_RUN_AS_NODE'] == '1'
        assert launcher('dsh', str(selected))[0] == command
    from types import SimpleNamespace
    with patch('room_agents.subprocess.run', side_effect=[
        SimpleNamespace(returncode=0, stdout='0.2.1-rc.2', stderr=''),
        SimpleNamespace(returncode=0, stdout='Usage: headless --json --session-id', stderr='')]):
        assert '请更新 Harness' in agent_version(LocalAgent('dsh','Harness',str(executable),'found'))

    calls = []
    class Process:
        returncode = 0
        def __init__(self, args, **kwargs):
            calls.append((args, kwargs)); assert not kwargs.get("shell")
        def communicate(self, prompt=None, timeout=None):
            assert "user topic" in prompt and "context" in prompt
            return "fixture Harness reply", ""
        def poll(self): return 0
        def kill(self): pass
    with patch("room_agents.launcher", return_value=((sys.executable,), sys.executable)), patch("room_agents.subprocess.Popen", Process):
        client = HarnessClient()
        reply = ask_profile(Profile("h", "Harness", "", "configured", transport="dsh-cli"),
                            "user topic", "context", "fixture-key", harness_client=client)
        assert reply.body == "fixture Harness reply"
        args, options = calls[0]
        assert args[args.index("--permission-mode")+1] == "read-only"
        assert args[args.index("--approval-policy")+1] == "never"
        assert options["env"]["DEEPSEEK_API_KEY"] == "fixture-key"
        client.close()
print("PASS: five UI languages, dark/light switching, wallpaper import and restart persistence, draft/history/name preservation, settings navigation, local connection deduplication, npm wrapper resolution, Harness stdin/read-only dispatch, and callback cleanup.")
