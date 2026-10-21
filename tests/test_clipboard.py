import http.client
import json
import socket
import sys
import threading
import time

import pytest
import uvicorn

from piscout import app as appmod, clipboard


def test_get_text_returns_a_string():
    assert isinstance(clipboard.get_text(), str)


def test_non_windows_returns_empty(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    assert clipboard.get_text() == ""


@pytest.fixture(scope="module")
def server():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    srv = uvicorn.Server(uvicorn.Config(appmod.app, host="127.0.0.1", port=port, log_config=None))
    threading.Thread(target=srv.run, daemon=True).start()
    while not srv.started:
        time.sleep(0.05)
    yield port
    srv.should_exit = True


def get(port, token):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request("GET", "/api/clipboard", headers={"X-Piscout-Token": token} if token else {})
    r = conn.getresponse()
    body = r.read()
    conn.close()
    return r.status, body


def test_clipboard_endpoint_needs_the_token_and_returns_text(server, monkeypatch):
    monkeypatch.setattr(appmod.clipboard, "get_text", lambda: "hello 你好")
    assert get(server, None)[0] == 403
    assert get(server, "wrong")[0] == 403
    status, body = get(server, appmod.API_TOKEN)
    assert status == 200 and json.loads(body) == {"text": "hello 你好"}
