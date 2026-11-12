"""Serve invitation-scoped group chat to browsers on the local network."""

import ipaddress
import json
import queue
import re
import secrets
import socket
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


LAN_NETWORKS = tuple(ipaddress.ip_network(value) for value in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "169.254.0.0/16", "127.0.0.0/8",
))
ROUTE = re.compile(r"^/r/([\w-]{32})(?:/(join|state|messages))?/?$")
ONLINE_FOR = 30


def is_lan_ip(value):
    try:
        ip = ipaddress.IPv4Address(value)
    except ValueError:
        return False
    return any(ip in network for network in LAN_NETWORKS)


def local_addresses():
    addresses = set()
    try:
        addresses.update(socket.gethostbyname_ex(socket.gethostname())[2])
    except OSError:
        pass
    # UDP connect chooses a local interface without sending a packet.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("192.0.2.1", 9))
            addresses.add(probe.getsockname()[0])
    except OSError:
        pass
    return tuple(sorted(ip for ip in addresses if is_lan_ip(ip) and not ip.startswith("127."))) + ("127.0.0.1",)


@dataclass
class Guest:
    name: str
    seen: float
    sent: float = 0


@dataclass
class Invite:
    room: str
    token: str
    after: int
    sessions: dict[str, Guest] = field(default_factory=dict)
    state: dict = field(default_factory=dict)


class LanHub:
    def __init__(self):
        self.lock = threading.Lock()
        self.server = None
        self.invites = {}
        self.inbox = queue.Queue(maxsize=160)

    @property
    def address(self):
        return self.server.server_address if self.server else None

    def start(self, host, port):
        if self.server:
            return
        if not is_lan_ip(host) or not 0 <= port <= 65535:
            raise ValueError("请选择本机的局域网 IPv4 地址和有效端口。")
        page = Path(__file__).with_name("lan_room.html").read_bytes()
        self.server = ThreadingHTTPServer((host, port), RoomHandler)
        self.server.hub = self
        self.server.page = page
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.15}, daemon=True).start()

    def invite(self, room, after):
        with self.lock:
            if invite := next((item for item in self.invites.values() if item.room == room), None):
                return invite
            token = secrets.token_urlsafe(24)
            invite = Invite(room, token, after)
            self.invites[token] = invite
            return invite

    def link(self, room):
        host = self.address
        with self.lock:
            token = next((item.token for item in self.invites.values() if item.room == room), None)
        return f"http://{host[0]}:{host[1]}/r/{token}" if host and token else ""

    def revoke(self, room):
        with self.lock:
            self.invites = {token: invite for token, invite in self.invites.items() if invite.room != room}

    def share_cutoff(self, room):
        with self.lock:
            return next((item.after for item in self.invites.values() if item.room == room), None)

    def publish(self, room, state):
        with self.lock:
            for invite in self.invites.values():
                if invite.room == room:
                    invite.state = state

    def guests(self, room):
        with self.lock:
            invite = next((item for item in self.invites.values() if item.room == room), None)
            return self.online(invite) if invite else ()

    @staticmethod
    def online(invite):
        now = time.monotonic()
        return tuple(guest.name for guest in invite.sessions.values() if now - guest.seen <= ONLINE_FOR)

    def close(self):
        if self.server:
            with self.lock:
                self.invites.clear()
            self.server.shutdown()
            self.server.server_close()
            self.server = None


class RoomHandler(BaseHTTPRequestHandler):
    timeout = 7
    server_version = "ModelRoom"
    sys_version = ""

    def log_message(self, *_args):
        pass

    def reply(self, status, data, content_type="application/json; charset=utf-8"):
        payload = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; "
                         "style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (OSError, TimeoutError):
            pass

    def error(self, status, text):
        self.reply(status, {"error": text})

    def route(self):
        host, port = self.server.server_address
        authority = f"{host}:{port}"
        if not is_lan_ip(self.client_address[0]) or self.headers.get("Host") != authority:
            self.error(403, "仅允许使用程序生成的局域网链接。")
            return None
        origin = self.headers.get("Origin")
        if origin and origin != f"http://{authority}":
            self.error(403, "不允许跨站请求。")
            return None
        try:
            match = ROUTE.fullmatch(urlsplit(self.path).path)
        except ValueError:
            match = None
        if not match:
            self.error(404, "邀请不存在。")
        return match

    def request_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 18_000 or self.headers.get_content_type() != "application/json":
                raise ValueError
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError
            return body
        except (OSError, ValueError, UnicodeError):
            self.error(400, "无效或过大的请求。")
            return None

    def do_GET(self):
        if (match := self.route()) is None:
            return
        token, action = match.groups()
        hub = self.server.hub
        with hub.lock:
            invite = hub.invites.get(token)
            guest = invite.sessions.get(self.session()) if invite else None
            if invite and guest and action == "state":
                guest.seen = time.monotonic()
                state = {**invite.state, "guests": hub.online(invite), "you": guest.name}
        if not invite:
            self.error(404, "邀请已失效。请向主持人索取新的链接。")
        elif action is None:
            self.reply(200, self.server.page, "text/html; charset=utf-8")
        elif action != "state":
            self.error(405, "不支持此请求方式。")
        elif guest is None:
            self.error(401, "请先输入昵称加入。")
        else:
            self.reply(200, state)

    def session(self):
        return self.headers.get("Authorization", "").removeprefix("Bearer ")

    def do_POST(self):
        if (match := self.route()) is None:
            return
        token, action = match.groups()
        if action not in {"join", "messages"}:
            self.error(405, "不支持此请求方式。")
            return
        if (body := self.request_json()) is None:
            return
        hub = self.server.hub
        with hub.lock:
            invite = hub.invites.get(token)
            if not invite:
                status, result = 404, {"error": "邀请已失效。"}
            elif action == "join":
                status, result = self.join(invite, body)
            else:
                status, result = self.post(hub, invite, body)
        self.reply(status, result)

    def join(self, invite, body):
        name = body.get("name")
        name = " ".join(name.split()) if isinstance(name, str) else ""
        if not name or len(name) > 24:
            return 400, {"error": "昵称应为 1–24 个字符。"}
        now = time.monotonic()
        invite.sessions = {key: guest for key, guest in invite.sessions.items() if now - guest.seen < 7200}
        if len(invite.sessions) >= 24:
            return 409, {"error": "当前邀请的访客席位已满。"}
        if any(guest.name.casefold() == name.casefold() and now - guest.seen <= ONLINE_FOR
               for guest in invite.sessions.values()):
            return 409, {"error": "此昵称已有在线访客，请换一个。"}
        session = secrets.token_urlsafe(24)
        invite.sessions[session] = Guest(name, now)
        return 200, {"session": session}

    def post(self, hub, invite, body):
        session = self.session()
        guest = invite.sessions.get(session)
        if guest is None:
            return 401, {"error": "请先加入。"}
        text = body.get("text")
        text = text.strip() if isinstance(text, str) else ""
        if not text or len(text) > 4000:
            return 400, {"error": "发言应为 1–4000 个字符。"}
        now = time.monotonic()
        if now - guest.sent < 0.45:
            return 429, {"error": "发送太快，请稍后重试。"}
        try:
            hub.inbox.put_nowait((invite.room, guest.name, text))
        except queue.Full:
            return 503, {"error": "主机忙，请稍后再试。"}
        guest.seen = guest.sent = now
        return 202, {"ok": True}
