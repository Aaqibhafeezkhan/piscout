"""讓 AI 助手操作樹莓派的 MCP 伺服器（stdio，只用標準函式庫）。

用法：python -m piscout.mcp
提供兩個工具：pi_list（掃描區網）、pi_run（在樹莓派上執行指令）。
帳密一律從 piscout 存的 vault 取，AI 看不到密碼。輸出刻意精簡以節省 token。
"""
import ipaddress
import json
import sys

from . import remote, scanner, vault

MAX_OUT = 3000
_clients = {}

TOOLS = [
    {"name": "pi_list",
     "description": "Scan the LAN for Raspberry Pis. One line each: ip hostname ssh-open.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "pi_run",
     "description": "Run a shell command on a Raspberry Pi (login saved in piscout). Returns exit code and trimmed output.",
     "inputSchema": {"type": "object", "required": ["host", "cmd"], "properties": {
         "host": {"type": "string", "description": "IP of the Pi"},
         "cmd": {"type": "string"},
         "timeout": {"type": "integer", "description": "seconds, default 30"}}}},
]


def _client(host):
    if not ipaddress.ip_address(host).is_private:
        raise ValueError("only private LAN addresses are allowed")
    c = _clients.get(host)
    if c and c.get_transport() and c.get_transport().is_active():
        return c
    mac = scanner.read_arp().get(host, "")
    if not mac:  # ARP 表裡還沒有這台，掃一次再查
        scanner.scan()
        mac = scanner.read_arp().get(host, "")
    saved = vault.get(mac) if mac else None
    if not saved:
        raise ValueError("no saved login for this device; save one in piscout first")
    c = _clients[host] = remote.connect(host, saved["username"], saved.get("password"))
    return c


def _trim(s):
    return s if len(s) <= MAX_OUT else "…" + s[-MAX_OUT:]


def call(name, a):
    if name == "pi_list":
        rows = [f"{d['ip']} {d['hostname'] or '-'} ssh={'y' if d['ssh_open'] else 'n'}"
                for d in scanner.scan()["devices"] if d["is_pi"]]
        return "\n".join(rows) or "no Raspberry Pi found"
    if name == "pi_run":
        code, out, err = remote.run(_client(a["host"]), a["cmd"], timeout=a.get("timeout", 30))
        return _trim(f"exit {code}\n{out}{('[stderr] ' + err) if err else ''}".rstrip())
    raise ValueError("unknown tool")


def handle(msg):
    m, i = msg.get("method"), msg.get("id")
    if m == "initialize":
        return {"protocolVersion": msg["params"].get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}}, "serverInfo": {"name": "piscout", "version": "0.1"}}
    if m == "tools/list":
        return {"tools": TOOLS}
    if m == "tools/call":
        p = msg["params"]
        try:
            text, bad = call(p["name"], p.get("arguments") or {}), False
        except Exception as e:
            text, bad = str(e), True
        return {"content": [{"type": "text", "text": text}], "isError": bad}
    if i is not None:
        return {}


def _std_handles():
    """視窗模式的 exe 沒有 sys.stdin/stdout，改成直接接父行程給的管線。"""
    import ctypes
    import msvcrt
    import os

    def open_(kind, mode):
        h = ctypes.windll.kernel32.GetStdHandle(kind)
        return os.fdopen(msvcrt.open_osfhandle(h, os.O_RDONLY if mode == "r" else 0), mode,
                         encoding="utf-8", closefd=False)
    return open_(-10, "r"), open_(-11, "w")


def main():
    inp, out = (sys.stdin, sys.stdout) if sys.stdin and sys.stdout else _std_handles()
    sys.stdout = out
    for line in inp:
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        res = handle(msg)
        if msg.get("id") is not None and res is not None:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": res}) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
