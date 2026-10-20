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
