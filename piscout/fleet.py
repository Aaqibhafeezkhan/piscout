"""多台樹莓派的總覽與批次操作。

登入資訊一律從 vault 取（用 MAC 當索引），沒存過帳密的就只能走 agent 的 HTTP。
"""
import json
import re
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from . import flasher, remote, vault
from .i18n import get_lang, set_lang, tr

AGENT_PORT = 8765
MAC_RE = re.compile(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$")
ACTIONS = ("reboot", "shutdown", "update", "install_agent")
WORKERS = 8


def _agent_stats(host):
    url = f"http://{host}:{AGENT_PORT}/stats"
    with urllib.request.urlopen(url, timeout=2.5) as r:
        return json.loads(r.read())


def _login(mac):
    saved = vault.get(mac) if MAC_RE.match(mac or "") else None
    if not saved or not saved.get("username"):
        return None
    return saved


_auto_tried = set()


def _auto_install(host, saved):
    """第一次用 SSH 連上就順手把 agent 裝好，之後不用登入也能讀狀態。"""
    try:
        client = remote.connect_saved(host, saved, timeout=8)
        try:
            if not remote.agent_installed(client):
                remote.install_agent(client, sudo_password=saved["password"])
        finally:
            client.close()
    except Exception:
        pass  # 裝不起來不影響其他功能，下次重開程式會再試一次


def stats_one(host, mac, lang):
    set_lang(lang)
    try:
        stats = _agent_stats(host)
        return {"ip": host, "mac": mac, "ok": True, "via": "agent", "stats": stats,
                "model_id": flasher.model_id(stats.get("model", ""))}
    except (OSError, ValueError):
        pass  # agent 沒裝或沒回應，改用 SSH

    saved = _login(mac)
    if not saved or not saved.get("password"):
        return {"ip": host, "mac": mac, "ok": False, "nologin": True,
                "error": tr("沒有儲存帳密")}
    try:
        client = remote.connect_saved(host, saved, timeout=6)
    except remote.RemoteError as e:
        return {"ip": host, "mac": mac, "ok": False, "error": str(e)}
    try:
        info = remote.get_info(client)
        if host not in _auto_tried and not info.get("agent_installed", False):
            _auto_tried.add(host)
            threading.Thread(target=_auto_install, args=(host, saved), daemon=True).start()
        return {"ip": host, "mac": mac, "ok": True, "via": "ssh", "stats": info,
                "model_id": flasher.model_id(info.get("model", ""))}
    except Exception as e:
        return {"ip": host, "mac": mac, "ok": False, "error": str(e)}
    finally:
        client.close()


def stats_many(devices):
    lang = get_lang()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = [pool.submit(stats_one, d["ip"], d.get("mac", ""), lang) for d in devices]
        return [f.result() for f in futs]


def _do(client, action, password):
    if action == "reboot":
        try:
            remote.run(client, "systemctl reboot", sudo_password=password, timeout=15)
        except OSError:
            pass  # 重開機時連線會被切斷
        return ""
    if action == "shutdown":
        try:
            remote.run(client, "systemctl poweroff", sudo_password=password, timeout=15)
        except OSError:
            pass
        return ""
    if action == "update":
        # 更新很久，丟到背景跑，記錄寫在 /tmp/piscout-update.log
        cmd = (
            "sh -c 'nohup sh -c \"apt-get update && DEBIAN_FRONTEND=noninteractive "
            "apt-get -y upgrade\" > /tmp/piscout-update.log 2>&1 &'"
        )
        code, _out, err = remote.run(client, cmd, sudo_password=password, timeout=30)
        if code != 0:
            raise remote.RemoteError(err.strip() or tr("操作逾時"))
        return ""
    if action == "install_agent":
        remote.install_agent(client, sudo_password=password)
        return ""
    raise remote.RemoteError(tr("不支援的操作"))


def act_one(host, mac, action, lang):
    set_lang(lang)
    saved = _login(mac)
    if not saved or not saved.get("password"):
        return {"ip": host, "ok": False, "error": tr("沒有儲存帳密")}
    try:
        client = remote.connect_saved(host, saved, timeout=8)
    except remote.RemoteError as e:
        return {"ip": host, "ok": False, "error": str(e)}
    try:
        _do(client, action, saved["password"])
        return {"ip": host, "ok": True}
    except Exception as e:
        return {"ip": host, "ok": False, "error": str(e)}
    finally:
        try:
            client.close()
        except Exception:
            pass


def act_many(devices, action):
    lang = get_lang()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = [pool.submit(act_one, d["ip"], d.get("mac", ""), action, lang)
                for d in devices]
        return [f.result() for f in futs]
