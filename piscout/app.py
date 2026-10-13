import asyncio
import ipaddress
import json
import re
import secrets
import time
import urllib.request
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import fleet, flasher, i18n, remote, remoteflash, scanner, vault
from .i18n import tr

STATIC = Path(__file__).parent / "static"
AGENT_PORT = 8765
USER_RE = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")

app = FastAPI(title="piscout")

# 每次啟動產生一個隨機 token，只會嵌在我們自己的頁面裡。
# 瀏覽器裡別的網頁讀不到它，就沒辦法呼叫 /api（避免有人從網頁打到本機的服務）。
API_TOKEN = secrets.token_urlsafe(24)
MAC_RE = re.compile(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$")


class LangMiddleware:
    """依 X-Lang / Accept-Language 設定這個請求的語言。
    用純 ASGI 寫，語言才會傳到後面的處理函式（BaseHTTPMiddleware 的做不到）。"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            h = dict(scope["headers"])
            raw = h.get(b"x-lang") or h.get(b"accept-language") or b""
            i18n.set_lang(raw.decode("latin-1"))
        await self.app(scope, receive, send)


app.add_middleware(LangMiddleware)


@app.middleware("http")
async def guard(request, call_next):
    host = (request.headers.get("host") or "").split(":")[0]
    if host not in ("127.0.0.1", "localhost"):
        return JSONResponse({"detail": "forbidden"}, status_code=403)
    if request.url.path.startswith("/api/"):
        given = request.headers.get("x-piscout-token", "")
        if not secrets.compare_digest(given, API_TOKEN):
            return JSONResponse({"detail": "forbidden"}, status_code=403)
    return await call_next(request)
app.mount("/static", StaticFiles(directory=STATIC), name="static")

# 已經登入好、等著前端用 websocket 接上去的 SSH 連線
SESSIONS = {}
SESSION_TTL = 60


class Login(BaseModel):
    username: str
    password: Optional[str] = None
    key_path: Optional[str] = None


class SessionReq(BaseModel):
    kind: str  # terminal / desktop
    username: str
    password: Optional[str] = None
    key_path: Optional[str] = None


class FlashConfig(BaseModel):
    hostname: str = "raspberrypi"
    username: str = "pi"
    password: str
    wifi_ssid: str = ""
    wifi_password: str = ""
    wifi_country: str = "TW"
    timezone: str = "Asia/Taipei"
    keyboard: str = "us"


class RemoteFlashReq(BaseModel):
    host: str
    username: str
    password: Optional[str] = None
    key_path: Optional[str] = None
    image_url: str
    config: FlashConfig


class FlashReq(BaseModel):
    image_url: str
    disk_number: int
    disk_size: int
    verify: bool = True
    config: FlashConfig


def _check_host(host):
    """只允許操作私有網段，避免被拿來打外網。"""
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        raise HTTPException(400, tr("host 必須是 IP"))
    if not ip.is_private:
        raise HTTPException(400, tr("只能操作區網內的位址"))
    return str(ip)


@app.get("/")
def index():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(
        html.replace("__PISCOUT_TOKEN__", API_TOKEN),
        headers={"Cache-Control": "no-store"},
    )


# ------------------------------------------------------------ 帳密儲存

class SavedLogin(BaseModel):
    username: str
    password: Optional[str] = None


def _mac(key):
    key = key.lower()
    if not MAC_RE.match(key):
        raise HTTPException(400, tr("key 必須是 MAC 位址"))
    return key


# ------------------------------------------------------------ 總覽 / 批次操作

class FleetDevice(BaseModel):
    ip: str
    mac: str = ""


class FleetStatsReq(BaseModel):
    devices: list[FleetDevice]


class FleetActionReq(BaseModel):
    action: str
    devices: list[FleetDevice]


def _fleet_devices(items):
    if not items or len(items) > 64:
        raise HTTPException(400, "devices")
    out = []
    for d in items:
        out.append({"ip": _check_host(d.ip), "mac": d.mac.lower()})
    return out


@app.post("/api/fleet/stats")
async def api_fleet_stats(req: FleetStatsReq):
    devices = _fleet_devices(req.devices)
    return {"results": await run_in_threadpool(fleet.stats_many, devices)}


@app.post("/api/fleet/action")
async def api_fleet_action(req: FleetActionReq):
    if req.action not in fleet.ACTIONS:
        raise HTTPException(400, tr("不支援的操作"))
    devices = _fleet_devices(req.devices)
    return {"results": await run_in_threadpool(fleet.act_many, devices, req.action)}


@app.get("/api/vault/{key}")
def api_vault_get(key: str):
    return vault.get(_mac(key)) or {"username": "", "password": None}


@app.put("/api/vault/{key}")
def api_vault_put(key: str, body: SavedLogin):
    vault.put(_mac(key), body.username, body.password)
    return {"ok": True}


@app.delete("/api/vault/{key}")
def api_vault_delete(key: str):
    vault.delete(_mac(key))
    return {"ok": True}


@app.delete("/api/vault")
def api_vault_clear():
    vault.delete(None)
    return {"ok": True}


# ------------------------------------------------------------ 掃描 / 連線

@app.get("/api/scan")
async def api_scan():
    return await run_in_threadpool(scanner.scan)


def _info(host, login):
    client = remote.connect(host, login.username, login.password, login.key_path)
    try:
        return remote.get_info(client)
    finally:
        client.close()


def _install(host, login):
    client = remote.connect(host, login.username, login.password, login.key_path)
    try:
        return remote.install_agent(client, sudo_password=login.password)
    finally:
        client.close()


@app.post("/api/devices/{host}/info")
async def api_info(host: str, login: Login):
    host = _check_host(host)
    try:
        info = await run_in_threadpool(_info, host, login)
    except remote.RemoteError as e:
        raise HTTPException(502, str(e))
    info["model_id"] = flasher.model_id(info.get("model", ""))
    return info


@app.post("/api/devices/{host}/install")
async def api_install(host: str, login: Login):
    host = _check_host(host)
    try:
        ok = await run_in_threadpool(_install, host, login)
    except remote.RemoteError as e:
        raise HTTPException(502, str(e))
    return {"installed": ok}


# ------------------------------------------------------------ 終端機 / 遠端桌面

def _drop(sess):
    try:
        if sess.get("kind") == "desktop":
            remote.stop_desktop(sess["client"])
    finally:
        sess["client"].close()


def _expire_sessions():
    now = time.time()
    for token in [t for t, v in SESSIONS.items() if now - v["created"] > SESSION_TTL]:
        _drop(SESSIONS.pop(token))


def _open_session(host, req):
    client = remote.connect(host, req.username, req.password, req.key_path)
    try:
        port = remote.start_desktop(client) if req.kind == "desktop" else None
    except Exception:
        client.close()
        raise
    return client, port


@app.post("/api/devices/{host}/session")
async def api_session(host: str, req: SessionReq):
    host = _check_host(host)
    if req.kind not in ("terminal", "desktop"):
        raise HTTPException(400, tr("kind 不對"))
    _expire_sessions()
    try:
        client, port = await run_in_threadpool(_open_session, host, req)
    except remote.RemoteError as e:
        raise HTTPException(502, str(e))
    token = secrets.token_urlsafe(16)
    SESSIONS[token] = {
        "client": client, "kind": req.kind, "port": port, "created": time.time(),
    }
    return {"token": token}


async def _pump(ws, chan, on_text=None):
    """chan（paramiko channel）和 websocket 之間搬資料，任何一邊結束就收工。"""
    loop = asyncio.get_running_loop()

    async def chan_to_ws():
        while True:
            data = await loop.run_in_executor(None, chan.recv, 32768)
            if not data:
                return
            await ws.send_bytes(data)

    async def ws_to_chan():
        while True:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                return
            if msg.get("bytes") is not None:
                await loop.run_in_executor(None, chan.sendall, msg["bytes"])
            elif msg.get("text") is not None and on_text:
                on_text(msg["text"])

    tasks = [asyncio.ensure_future(chan_to_ws()), asyncio.ensure_future(ws_to_chan())]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for t in tasks:
            t.cancel()
        chan.close()


def _take_session(token, kind):
    sess = SESSIONS.pop(token, None)
    if sess is None or sess["kind"] != kind:
        return None
    return sess


async def _accept(ws):
    # noVNC 會要求 binary 子協定
    if "binary" in ws.scope.get("subprotocols", []):
        await ws.accept(subprotocol="binary")
    else:
        await ws.accept()


@app.websocket("/ws/terminal/{token}")
async def ws_terminal(ws: WebSocket, token: str, cols: int = 80, rows: int = 24):
    sess = _take_session(token, "terminal")
    if sess is None:
        await ws.close(code=4404)
        return
    await _accept(ws)
    chan = sess["client"].invoke_shell(term="xterm-256color", width=cols, height=rows)

    def on_text(text):
        try:
            m = json.loads(text)
            if m.get("t") == "r":
                chan.resize_pty(width=int(m["c"]), height=int(m["r"]))
        except (ValueError, KeyError, TypeError):
            pass

    try:
        await _pump(ws, chan, on_text)
    finally:
        _drop(sess)
        try:
            await ws.close()
        except RuntimeError:
            pass


@app.websocket("/ws/desktop/{token}")
async def ws_desktop(ws: WebSocket, token: str):
    sess = _take_session(token, "desktop")
    if sess is None:
        await ws.close(code=4404)
        return
    await _accept(ws)
    try:
        chan = sess["client"].get_transport().open_channel(
            "direct-tcpip", ("127.0.0.1", sess["port"]), ("127.0.0.1", 0)
        )
    except Exception:
        _drop(sess)
        await ws.close(code=1011)
        return
    try:
        await _pump(ws, chan)
    finally:
        await run_in_threadpool(_drop, sess)
        try:
            await ws.close()
        except RuntimeError:
            pass


def _fetch_stats(host):
    url = f"http://{host}:{AGENT_PORT}/stats"
    with urllib.request.urlopen(url, timeout=3) as r:
        return json.loads(r.read())


@app.get("/api/devices/{host}/stats")
async def api_stats(host: str):
    host = _check_host(host)
    try:
        return await run_in_threadpool(_fetch_stats, host)
    except OSError:
        raise HTTPException(502, tr("agent 沒有回應"))


# ------------------------------------------------------------ 燒錄

@app.get("/api/flash/drives")
async def api_drives():
    try:
        return {
            "drives": await run_in_threadpool(flasher.list_drives),
            "admin": flasher.is_admin(),
        }
    except flasher.FlashError as e:
        raise HTTPException(500, str(e))


@app.get("/api/flash/images")
async def api_images(model: str = "pi4", purpose: str = "desktop"):
    try:
        images = await run_in_threadpool(flasher.list_images)
    except flasher.FlashError as e:
        raise HTTPException(502, str(e))
    return {
        "images": flasher.recommend(images, model, purpose),
        "models": [{"id": k, "name": v[0]} for k, v in flasher.MODELS.items()],
    }


@app.post("/api/flash/start")
async def api_flash_start(req: FlashReq):
    try:
        job_id = await run_in_threadpool(
            flasher.start_job,
            req.image_url, req.disk_number, req.disk_size,
            req.config.model_dump(), req.verify,
        )
    except flasher.FlashError as e:
        raise HTTPException(400, str(e))
    return {"job": job_id}


@app.post("/api/flash/remote/start")
async def api_flash_remote(req: RemoteFlashReq):
    host = _check_host(req.host)
    login = {"username": req.username, "password": req.password or None,
             "key_path": req.key_path}
    try:
        job_id = await run_in_threadpool(
            remoteflash.start_job, host, login, req.image_url, req.config.model_dump()
        )
    except flasher.FlashError as e:
        raise HTTPException(400, str(e))
    return {"job": job_id}


@app.get("/api/flash/jobs/{job_id}")
def api_flash_job(job_id: str):
    try:
        return flasher.get_job(job_id)
    except flasher.FlashError as e:
        raise HTTPException(404, str(e))
