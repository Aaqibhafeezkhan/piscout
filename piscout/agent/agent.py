"""裝在樹莓派上的小程式，只用標準函式庫。

  python3 agent.py --once    印一次狀態 JSON 就結束
  python3 agent.py           在 8765 埠開 HTTP，GET /stats 取得狀態
"""
import json
import os
import shutil
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8765


def _read(path):
    try:
        with open(path) as f:
            return f.read().strip().strip("\x00")
    except OSError:
        return ""


def _os_name():
    for line in _read("/etc/os-release").splitlines():
        if line.startswith("PRETTY_NAME="):
            return line.split("=", 1)[1].strip('"')
    return ""


def _meminfo():
    info = {}
    for line in _read("/proc/meminfo").splitlines():
        key, _, rest = line.partition(":")
        parts = rest.split()
        if parts:
            info[key] = int(parts[0]) // 1024  # kB -> MB
    return info


def _load():
    try:
        return [round(x, 2) for x in os.getloadavg()]
    except (AttributeError, OSError):
        return [0, 0, 0]


def collect():
    mem = _meminfo()
    disk = shutil.disk_usage("/")
    temp = _read("/sys/class/thermal/thermal_zone0/temp")
    uptime = _read("/proc/uptime").split()
    return {
        "hostname": socket.gethostname(),
        "model": _read("/proc/device-tree/model"),
        "os": _os_name(),
        "uptime_s": int(float(uptime[0])) if uptime else None,
        "load": _load(),
        "cpu_temp_c": round(int(temp) / 1000, 1) if temp.isdigit() else None,
        "mem_total_mb": mem.get("MemTotal"),
        "mem_free_mb": mem.get("MemAvailable"),
        "disk_total_gb": round(disk.total / 1e9, 1),
        "disk_used_gb": round(disk.used / 1e9, 1),
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/stats":
            self.send_error(404)
            return
        body = json.dumps(collect()).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def main():
    if "--once" in sys.argv:
        print(json.dumps(collect()))
        return
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
