"""Offline V0.7 contract and connection-manager checks. Never calls paid APIs."""
import json
import os
import sys
import threading
import tkinter as tk
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK.parent))
from model_room import RoomWindow, describe_call
from room_core import RoomStore, ReplyError
from room_providers import Profile, ask_profile, discover_models, load_profiles, save_profiles
from room_presets import FORMATS, PRESETS
from room_settings import ConnectionWindow
from room_claude import ClaudeCodeClient


class Server(BaseHTTPRequestHandler):
    requests = []
    def do_GET(self):
        assert self.headers.get("Authorization") == "Bearer fixture-key"
        assert self.headers.get("anthropic-version") == "2026-10-21"
        assert self.headers.get("anthropic-workspace-id") == "wrkspc_fixture"
        self.requests.append(self.path)
        self.respond({"data": [{"id": "claude-two" if "after_id=" in self.path else "claude-one"}],
                      "has_more": "after_id=" not in self.path, "last_id": "claude-one"})
    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        assert self.path == "/v1/messages"
        assert payload["thinking"] == {"type": "adaptive"}
        assert payload["output_config"] == {"effort": "high"}
        assert payload["messages"][0]["role"] == "user"
        assert "other member" in payload["messages"][0]["content"]
        assert self.headers.get("anthropic-workspace-id") == "wrkspc_fixture"
        self.respond({"id": "msg_fixture", "model": payload["model"],
                      "content": [{"type": "thinking", "thinking": "internal"}, {"type": "text", "text": "真实协议测试"}],
                      "stop_reason": "end_turn", "usage": {"input_tokens": 19, "output_tokens": 7}})
    def respond(self, body):
        data = json.dumps(body).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self, *_):
        pass


class FakeCLI:
    command = None
    received = None
    def __init__(self, command, **kwargs):
        self.command = FakeCLI.command = command
        assert kwargs.get("shell") in (None, False)
        assert "DEEPSEEK_API_KEY" not in kwargs["env"]
        assert "OPENAI_API_KEY" not in kwargs["env"]
        self.returncode = 0
    def communicate(self, text=None, timeout=None):
        FakeCLI.received = text
        return json.dumps({"result": "CLI adapter works", "is_error": False,
                           "usage": {"input_tokens": 10, "output_tokens": 4}}), ""
    def poll(self):
        return 0
    def kill(self):
        pass


with TemporaryDirectory(dir=WORK) as temporary:
    os.environ["MODELROOM_DATA_DIR"] = temporary
    store = RoomStore(Path(temporary))
    server = ThreadingHTTPServer(("127.0.0.1", 0), Server)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    profile = Profile("fixture", "Claude test", f"http://127.0.0.1:{server.server_port}/v1", "claude-one",
                      "claude-adaptive", "high", transport="anthropic", workspace="wrkspc_fixture")
    assert discover_models(profile, "fixture-key") == ("claude-one", "claude-two")
    reply = ask_profile(profile, "hello", "other member", "fixture-key")
    assert reply.body == "真实协议测试" and reply.details["prompt_tokens"] == 19
    assert replace(profile, thinking="off").options()[0]["thinking"] == {"type": "disabled"}
    legacy = replace(profile, protocol="claude-budget", thinking="on").options()[0]
    assert 1024 <= legacy["thinking"]["budget_tokens"] < legacy["max_tokens"]
    cli_profile = Profile("cli", "Claude Code", "", "sonnet", transport="claude-cli")
    client = ClaudeCodeClient()
    with patch("room_agents.launcher", return_value=((sys.executable,), sys.executable)), patch("room_claude.subprocess.Popen", FakeCLI):
        result = client.ask(cli_profile, "hello & no shell", "reference")
    assert result.body == "CLI adapter works"
    assert FakeCLI.command[FakeCLI.command.index("--tools")+1] == ""
    assert FakeCLI.command[FakeCLI.command.index("--disallowedTools")+1] == "*"
    assert "hello & no shell" in FakeCLI.received and "hello & no shell" not in FakeCLI.command
    client.close()
    old = Profile("old", "Existing", "https://example.com/v1", "old-model")
    # Real persisted v0.6 rows have no transport/workspace fields.
    store.set_settings(providers=json.dumps([{"id": old.id, "name": old.name, "base": old.base,
                                              "model": old.model, "models": [], "protocol": "auto", "thinking": "default"}]))
    assert load_profiles(store)[0].transport == "openai"
    save_profiles(store, [old, profile, cli_profile], old.id)
    assert load_profiles(store)[1].workspace == "wrkspc_fixture"
    root = tk.Tk(); root.attributes("-alpha", 0)
    errors = []
    root.report_callback_exception = lambda *args: errors.append(args)
    room = RoomWindow(root, store)
    settings = ConnectionWindow(room, describe_call)
    root.update()
    assert settings.canvas.master.winfo_children()[0].winfo_reqwidth() >= 7, "Scrollbar must be visible"
    assert len(PRESETS) == 22
    for preset in PRESETS:
        settings.preset_name.set(preset.name)
        if preset.transport == "codex-cli":
            settings.apply_preset()
            assert settings.tabs.index(settings.tabs.select()) == 2
            continue
        settings.tabs.select(0)
        settings.key.configure(state="normal"); settings.key.insert(0, "must-not-transfer")
        settings.apply_preset()
        root.update()
        assert not settings.key.get()
        assert settings.current.id not in {p.id for p in room.profiles}
        assert settings.address.get() == preset.base
        assert FORMATS[settings.transport.get()] == preset.transport
        assert len(load_profiles(store)) == 3, "Applying a preset must not save or replace anything"
    settings.preset_name.set("Claude / Anthropic API"); settings.apply_preset()
    settings.workspace.set("wrkspc_fixture"); settings.model.set("claude-one")
    settings.save_profile()
    assert any(p.transport == "anthropic" and p.workspace == "wrkspc_fixture" for p in load_profiles(store))
    settings.window.destroy()
    assert not errors, errors
    room.close()
    server.shutdown(); server.server_close()
print("PASS: 22 presets, v0.6 profile migration, no overwrite or key transfer, native Claude model pagination/messages/thinking, CLI stdin/no-shell/tool restrictions, and UI save/reload.")
