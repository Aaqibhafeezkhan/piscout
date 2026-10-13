"""Simulated Raspberry Pi shell, used only to record the README demo.

It is NOT a real device: it answers a handful of canned commands over SSH so the
terminal UI can be shown without exposing a real Pi. Run it together with
PISCOUT_DEMO=1 (see docs/DEMO.md). Login: pi / raspberry.
"""
import socket
import threading

import paramiko

HOST_KEY = paramiko.RSAKey.generate(2048)
PROMPT = b"\x1b[1;32mpi@raspberrypi\x1b[0m:\x1b[1;34m~\x1b[0m $ "

MOTD = (
    b"Linux raspberrypi 6.12.34+rpt-rpi-v8 aarch64\r\n"
    b"\r\n"
    b"Simulated demo shell: this is not a real Raspberry Pi.\r\n\r\n"
)

COMMANDS = {
    "uname -a": "Linux raspberrypi 6.12.34+rpt-rpi-v8 #1 SMP PREEMPT Debian aarch64 GNU/Linux",
    "hostname": "raspberrypi",
    "cat /proc/device-tree/model": "Raspberry Pi 4 Model B Rev 1.4",
    "vcgencmd measure_temp": "temp=47.2'C",
    "uptime": " 10:42:07 up 3 days,  4:11,  1 user,  load average: 0.05, 0.03, 0.01",
    "free -h": ("               total        used        free      shared  buff/cache   available\r\n"
                "Mem:           3.7Gi       412Mi       2.9Gi        36Mi       470Mi       3.2Gi"),
    "df -h /": ("Filesystem      Size  Used Avail Use% Mounted on\r\n"
                "/dev/mmcblk0p2   29G  4.2G   23G  16% /"),
    "ls": "Desktop  Documents  Downloads  Music  Pictures  Public  Templates  Videos",
}


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.shell = threading.Event()

    def check_auth_password(self, username, password):
        ok = username == "pi" and password == "raspberry"
        return paramiko.AUTH_SUCCESSFUL if ok else paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED if kind == "session" else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(self, *a):
        return True

    def check_channel_shell_request(self, channel):
        self.shell.set()
        return True

    def check_channel_window_change_request(self, *a):
        return True


def serve_client(conn):
    t = paramiko.Transport(conn)
    t.add_server_key(HOST_KEY)
    srv = Server()
    t.start_server(server=srv)
    chan = t.accept(20)
    if chan is None or not srv.shell.wait(10):
        return
    chan.send(MOTD + PROMPT)
    line = b""
    while True:
        data = chan.recv(1024)
        if not data:
            break
        for b in data:
            c = bytes([b])
            if c in (b"\r", b"\n"):
                chan.send(b"\r\n")
                cmd = line.decode(errors="replace").strip()
                line = b""
                if cmd:
                    out = COMMANDS.get(cmd, f"bash: {cmd.split()[0]}: command not found")
                    chan.send(out.encode() + b"\r\n")
                chan.send(PROMPT)
            elif c in (b"\x7f", b"\x08"):
                if line:
                    line = line[:-1]
                    chan.send(b"\x08 \x08")
            elif b >= 32:
                line += c
                chan.send(c)
    t.close()


def main(port=22):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port))
    s.listen(5)
    print(f"demo shell listening on 127.0.0.1:{port} (pi / raspberry)", flush=True)
    while True:
        c, _ = s.accept()
        threading.Thread(target=serve_client, args=(c,), daemon=True).start()


if __name__ == "__main__":
    main()
