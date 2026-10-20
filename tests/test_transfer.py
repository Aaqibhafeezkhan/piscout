import os
import shutil
import subprocess

import pytest
import http.client
import json
import socket
import threading
import time

import uvicorn

from piscout import app as app_module
from piscout import transfer

BASH = shutil.which("bash")


def test_safe_name_strips_paths_and_rejects_empty():
    assert transfer.safe_name("a/b" + chr(92) + "c d.txt") == "c d.txt"
    assert transfer.safe_name(".." + chr(92) + ".." + chr(92) + "x") == "x"
    assert transfer.safe_name("x" + chr(0) + "y") == "x_y"
    for bad in ("", ".", "..", "/"):
        with pytest.raises(ValueError):
            transfer.safe_name(bad)


def test_unique_name_never_overwrites():
    taken = {"a.txt", "a (1).txt", "noext"}
    assert transfer.unique_name("a.txt", taken.__contains__) == "a (2).txt"
    assert transfer.unique_name("noext", taken.__contains__) == "noext (1)"
    assert transfer.unique_name("new.bin", taken.__contains__) == "new.bin"


@pytest.mark.skipif(BASH is None, reason="needs bash")
def test_cwd_script_picks_the_shell_with_a_tty(tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "ss").write_text("#!/bin/sh\necho 'ESTAB 0 0 10.0.0.2:22 10.0.0.9:51000 users:((\"sshd\",pid=777,fd=4))'\n")
    # 第一行是 exec 通道的 bash（沒有 tty），第二行才是終端機的 shell
    (bindir / "ps").write_text("#!/bin/sh\nprintf '800 ?\n801 pts/0\n'\n")
    (bindir / "readlink").write_text("#!/bin/sh\n[ \"$1\" = /proc/801/cwd ] && echo /home/pi/project\n")
    for f in bindir.iterdir():
        f.chmod(0o755)
    env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ["PATH"], HOME="/home/pi")
    out = subprocess.run([BASH, "-c", transfer.CWD_SH.format(port=51000)], env=env,
                         capture_output=True, text=True).stdout.strip()
    assert out == "/home/pi/project"
    out = subprocess.run([BASH, "-c", transfer.CWD_SH.format(port=40000)], env=env,
                         capture_output=True, text=True).stdout.strip()
    assert out == "/home/pi"  # 找不到這條連線，退回家目錄


class FakeFile:
    def __init__(self, fs, path):
        self.fs, self.path = fs, path
        self.fs[path] = b""

    def set_pipelined(self, v):
        pass

    def write(self, data):
        self.fs[self.path] += data

    def close(self):
        pass


class FakeSftp:
    def __init__(self, fs):
        self.fs = fs

    def stat(self, path):
        if path not in self.fs:
            raise IOError("no such file")

    def open(self, path, mode):
        return FakeFile(self.fs, path)

    def posix_rename(self, a, b):
        self.fs[b] = self.fs.pop(a)

    def remove(self, path):
        self.fs.pop(path, None)

    def close(self):
        pass


class FakeClient:
    def __init__(self, fs):
        self.fs = fs

    def open_sftp(self):
        return FakeSftp(self.fs)

    def close(self):
        pass


@pytest.fixture(scope="module")
def server():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    srv = uvicorn.Server(uvicorn.Config(app_module.app, host="127.0.0.1", port=port, log_config=None))
    threading.Thread(target=srv.run, daemon=True).start()
    while not srv.started:
        time.sleep(0.05)
    yield port
    srv.should_exit = True


def call(port, method, path, body=None, token=True):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
    headers = {"X-Piscout-Token": app_module.API_TOKEN} if token else {}
    if isinstance(body, dict):
        body = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    conn.request(method, path, body=body, headers=headers)
    r = conn.getresponse()
    data = r.read()
    conn.close()
    try:
        return r.status, json.loads(data)
    except ValueError:
        return r.status, data


def test_upload_flow_renames_and_avoids_overwrite(monkeypatch, server):
    fs = {"/home/pi/proj/a.txt": b"old"}
    monkeypatch.setattr(app_module.remote, "connect", lambda *a, **k: FakeClient(fs))
    monkeypatch.setattr(app_module.transfer, "target_dir", lambda client, mode, term=None: "/home/pi/proj")
    st, j = call(server, "POST", "/api/devices/192.168.0.5/upload",
                 {"mode": "term", "username": "pi", "password": "x"})
    assert st == 200 and j["dir"] == "/home/pi/proj"
    token = j["token"]
    body = b"x" * (3 * 1024 * 1024 + 5)
    st, j = call(server, "POST", f"/api/upload/{token}?name=a.txt", body)
    assert st == 200
    assert j == {"path": "/home/pi/proj/a (1).txt", "size": len(body)}
    assert fs["/home/pi/proj/a.txt"] == b"old"          # 原本的檔案沒被蓋掉
    assert fs["/home/pi/proj/a (1).txt"] == body
    assert not any(k.endswith(".piscout-part") for k in fs)
    st, j = call(server, "POST", f"/api/upload/{token}?name=..%2F..%2Fetc%2Fpasswd", b"hi")
    assert j["path"] == "/home/pi/proj/passwd"          # 路徑被去掉，只剩檔名
    assert call(server, "DELETE", f"/api/upload/{token}")[0] == 200
    assert call(server, "POST", f"/api/upload/{token}?name=z", b"1")[0] == 404


def test_upload_requires_token_and_private_host(server):
    req = {"mode": "term", "username": "p"}
    assert call(server, "POST", "/api/devices/192.168.0.5/upload", req, token=False)[0] in (401, 403)
    assert call(server, "POST", "/api/devices/8.8.8.8/upload", req)[0] >= 400


def test_cwd_tap_hides_setup_and_tracks_directory():
    sent, clock = [], [0.0]
    tap = transfer.CwdTap(sent.append, now=lambda: clock[0])
    assert tap.idle() == b""                       # 還沒有任何輸出，不能先送設定
    banner = tap.feed(b"Linux raspberrypi\r\nmilktea@pi:~ $ ")
    assert banner == b"Linux raspberrypi\r\nmilktea@pi:~ $ "   # 提示字元照常顯示
    assert tap.idle() == b"" and sent == [transfer.INJECT]      # 安靜了才送設定
    # 回音、OSC 7、標記行都不能出現在畫面上；新的提示字元蓋掉舊的
    assert tap.feed(b" __pc() { printf ... }; PROMPT_COMMAND=...\r\n") == b""
    assert tap.feed(b"\x1b]7;file://pi/home/milktea\x07__PISCOUT_RE") == b""
    shown = tap.feed(b"ADY__\r\nmilktea@pi:~ $ ")
    assert shown == b"\r\x1b[2Kmilktea@pi:~ $ "
    assert tap.cwd == "/home/milktea"
    # 之後每個提示字元的 OSC 7 照常記錄並轉給畫面
    out = tap.feed(b"\x1b]7;file://pi/home/milktea/Downloads\x07milktea@pi:~/Downloads $ ")
    assert tap.cwd == "/home/milktea/Downloads" and b"Downloads $" in out


def test_cwd_tap_handles_spaces_and_split_chunks():
    tap = transfer.CwdTap(lambda b: None)
    tap.state = "normal"
    tap.feed(b"\x1b]7;file://pi/home/milktea/My Fil")
    tap.feed(b"es\x07$ ")
    assert tap.cwd == "/home/milktea/My Files"


def test_cwd_tap_does_not_stall_when_marker_never_comes():
    clock = [0.0]
    tap = transfer.CwdTap(lambda b: None, now=lambda: clock[0])
    tap.feed(b"$ ")
    tap.idle()                                     # 送出設定
    assert tap.feed(b"bash: something odd\r\n") == b""
    clock[0] = 3.0
    assert tap.idle() == b"bash: something odd\r\n"   # 超過 2 秒就放行，畫面不會卡住
    assert tap.feed(b"$ ") == b"$ "


def test_pump_injects_once_and_hides_it(monkeypatch):
    import asyncio
    import queue

    class FakeChan:
        def __init__(self):
            self.q, self.sent, self.closed = queue.Queue(), [], False

        def settimeout(self, t):
            self.t = t

        def recv(self, n):
            try:
                return self.q.get(timeout=0.05)
            except queue.Empty:
                if self.closed:
                    return b""
                raise socket.timeout()

        def send(self, data):
            self.sent.append(data)
            # 假裝 shell 收到設定後：回音、OSC 7、標記、新的提示字元
            self.q.put(b" __pc() ...\r\n\x1b]7;file://pi/home/milktea/Downloads\x07__PISCOUT_READY__\r\n$ ")

        def sendall(self, data):
            pass

        def close(self):
            self.closed = True

    class FakeWs:
        def __init__(self):
            self.out = b""

        async def send_bytes(self, data):
            self.out += data

        async def receive(self):
            await asyncio.sleep(3600)

    async def run():
        chan, ws = FakeChan(), FakeWs()
        tap = transfer.CwdTap(chan.send)
        chan.q.put(b"Welcome\r\n$ ")
        task = asyncio.ensure_future(app_module._pump(ws, chan, None, tap))
        for _ in range(100):
            await asyncio.sleep(0.05)
            if tap.state == "normal":
                break
        chan.closed = True
        await asyncio.wait_for(task, 5)
        return chan, ws, tap

    chan, ws, tap = asyncio.run(run())
    assert len(chan.sent) == 1 and chan.sent[0] == transfer.INJECT      # 只送一次設定
    assert ws.out == b"Welcome\r\n$ " + b"\r\x1b[2K$ "                  # 使用者只會看到提示字元
    assert tap.cwd == "/home/milkteatw/Downloads".replace("milkteatw", "milktea")
