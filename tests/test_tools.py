import http.client
import json
import re
import socket
import threading
import time

import pytest
import uvicorn
from piscout import app as appmod, i18n, remote, tools

CJK = re.compile("[一-鿿]")


def by_id(checks):
    return {c["id"]: c for c in checks}


def test_parse_reads_key_value_lines():
    raw = tools.parse("throttled=0x50005\ntemp=71.2\nfailed=a.service,b.service,\nnoise\n")
    assert raw == {"throttled": "0x50005", "temp": "71.2", "failed": "a.service,b.service,"}


def test_power_levels():
    assert by_id(tools.evaluate({"throttled": "0x0"}))["power"]["level"] == "ok"
    assert by_id(tools.evaluate({"throttled": "0x1"}))["power"]["level"] == "bad"
    assert by_id(tools.evaluate({"throttled": "0x10000"}))["power"]["level"] == "warn"
    # 沒有 vcgencmd（不是樹莓派或讀不到）就不要亂說電源有問題
    assert "power" not in by_id(tools.evaluate({"throttled": ""}))


def test_throttle_and_temperature():
    c = by_id(tools.evaluate({"throttled": "0x4", "temp": "82.0"}))
    assert c["throttle"]["level"] == "bad" and c["temp"]["level"] == "bad"
    assert by_id(tools.evaluate({"temp": "72"}))["temp"]["level"] == "warn"
    assert by_id(tools.evaluate({"temp": "45.5"}))["temp"]["level"] == "ok"


def test_disk_memory_sd_services_ntp():
    c = by_id(tools.evaluate({
        "disk": "96", "memtotal": "1000000", "memavail": "30000", "sderr": "3",
        "failed": "x.service,y.service,", "ntp": "no"}))
    assert c["disk"]["level"] == "bad"
    assert c["mem"]["level"] == "bad"
    assert c["sd"]["level"] == "bad" and "3" in c["sd"]["title"]
    assert c["services"]["level"] == "warn" and "x.service" in c["services"]["title"]
    assert c["ntp"]["level"] == "warn"
    ok = by_id(tools.evaluate({"disk": "40", "memtotal": "1000000", "memavail": "500000",
                               "sderr": "0", "failed": "", "ntp": "yes"}))
    assert all(v["level"] == "ok" for v in ok.values())
    # dmesg 讀不到（-1）時不判斷 SD 卡
    assert "sd" not in by_id(tools.evaluate({"sderr": "-1"}))


def test_garbage_values_do_not_crash():
    assert tools.evaluate({"throttled": "0xZZ", "temp": "hot", "disk": "full", "memtotal": "x", "memavail": "y"}) == []


def test_english_has_no_chinese():
    i18n.set_lang("en")
    try:
        checks = tools.evaluate({
            "throttled": "0x50005", "temp": "81", "disk": "90", "memtotal": "1000", "memavail": "60",
            "sderr": "2", "failed": "a.service,", "ntp": "no"})
        assert checks
        for c in checks:
            assert not CJK.search(c["title"] + c["detail"]), c
        for k, v in tools.ACTIONS.items():
            assert not CJK.search(i18n.tr(v["title"]) + i18n.tr(v["desc"])), k
    finally:
        i18n.set_lang("zh")


class FakeClient:
    def __init__(self, replies):
        self.replies = replies
        self.cmds = []

    def exec_command(self, cmd, timeout=None):
        self.cmds.append(cmd)
        raise AssertionError("tools should go through remote.run")


def test_setup_status_and_apply(monkeypatch):
    calls = []

    def fake_run(client, cmd, sudo_password=None, timeout=60):
        calls.append((cmd, sudo_password))
        if "get_i2c" in cmd:
            return 0, "1\n", ""
        if cmd.startswith("raspi-config nonint do_i2c"):
            return 0, "", ""
        return 0, "0\n", ""

    monkeypatch.setattr(remote, "run", fake_run)
    scripts = []

    def fake_script(client, script, timeout=40):
        scripts.append(script)
        return 0, "\n".join(["i2c=1", "spi=0", "ntp=0", "tools=0", "expand="]), ""

    monkeypatch.setattr(remote, "_run_script", fake_script)
    items = {i["id"]: i for i in tools.setup_status(object())}
    assert len(scripts) == 1                       # 所有項目一次往返查完
    assert items["i2c"]["done"] is False and items["tools"]["done"] is True
    assert items["expand"]["done"] is False
    calls.clear()
    # 套用後會重新檢查狀態；這裡的 get_i2c 還是回 1，所以 done 仍是 False
    r = tools.setup_apply(object(), "i2c", "pw")
    assert r["id"] == "i2c" and r["reboot"] is True
    assert calls[0] == ("raspi-config nonint do_i2c 0", "pw")


def test_setup_apply_failure_and_unknown(monkeypatch):
    monkeypatch.setattr(remote, "run", lambda c, cmd, sudo_password=None, timeout=60: (1, "", "boom"))
    with pytest.raises(remote.RemoteError, match="boom"):
        tools.setup_apply(object(), "ntp", "pw")
    with pytest.raises(remote.RemoteError):
        tools.setup_apply(object(), "rm -rf /", "pw")


def test_actions_are_fixed_and_safe():
    for k, v in tools.ACTIONS.items():
        assert set(v) >= {"title", "desc", "status", "apply", "reboot"}, k
        # 動作指令是寫死的，不含任何要由使用者填的位置
        assert "{" not in v["apply"] and "%s" not in v["apply"], k


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


def post(port, path, body):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
    conn.request("POST", path, body=json.dumps(body).encode(),
                 headers={"Content-Type": "application/json", "X-Piscout-Token": appmod.API_TOKEN})
    r = conn.getresponse()
    r.read()
    conn.close()
    return r.status


def test_endpoints_reject_unknown_action_and_public_hosts(server):
    login = {"username": "pi", "password": "x"}
    assert post(server, "/api/devices/192.168.1.50/setup", {**login, "action": "rm -rf /"}) == 400
    assert post(server, "/api/devices/8.8.8.8/health", login) == 400
    assert post(server, "/api/devices/8.8.8.8/setup", login) == 400
