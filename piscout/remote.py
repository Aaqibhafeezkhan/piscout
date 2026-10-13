"""透過 SSH 操作樹莓派：讀系統資訊、安裝 agent。"""
import json
from pathlib import Path

import paramiko

from .i18n import tr

AGENT_SRC = Path(__file__).parent / "agent" / "agent.py"
REMOTE_DIR = "/opt/piscout"
SERVICE = "piscout-agent"

UNIT = f"""[Unit]
Description=piscout agent
After=network-online.target

[Service]
ExecStart=/usr/bin/python3 {REMOTE_DIR}/agent.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""


class RemoteError(Exception):
    pass


def connect(host, username, password=None, key_path=None, timeout=8):
    client = paramiko.SSHClient()
    # 區網內第一次連線，沒辦法事先知道 host key，所以直接接受
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            host,
            username=username,
            password=password or None,
            key_filename=key_path or None,
            timeout=timeout,
            banner_timeout=timeout,
            allow_agent=not password,
            look_for_keys=not password,
        )
    except paramiko.AuthenticationException:
        raise RemoteError(tr("帳號或密碼不對（或這台沒開密碼登入）"))
    except (OSError, paramiko.SSHException) as e:
        raise RemoteError(tr("連不上 {host}：{e}", host=host, e=e))
    return client


def run(client, cmd, sudo_password=None, timeout=60):
    if sudo_password is not None:
        cmd = f"sudo -S -p '' {cmd}"
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    if sudo_password is not None:
        stdin.write(sudo_password + "\n")
        stdin.flush()
    code = stdout.channel.recv_exit_status()
    return code, stdout.read().decode(errors="replace"), stderr.read().decode(
        errors="replace"
    )


VNC_PORT = 5911
VNC_CONF = "/tmp/piscout-wayvnc.conf"

# 在使用者自己的桌面 session 裡起一個只聽 127.0.0.1 的 wayvnc，
# 不改系統設定、不需要 sudo；連線一律走 SSH 通道，所以不用另外做驗證。
START_VNC = f"""
U=$(id -u)
export XDG_RUNTIME_DIR=/run/user/$U
for s in /run/user/$U/wayland-*; do
  case "$s" in *.lock) ;; *) export WAYLAND_DISPLAY=$(basename "$s"); break ;; esac
done
if [ -z "$WAYLAND_DISPLAY" ]; then echo NO_DISPLAY; exit 0; fi
command -v wayvnc >/dev/null 2>&1 || {{ echo NO_WAYVNC; exit 0; }}
if ss -ltn 2>/dev/null | grep -q ':{VNC_PORT} '; then echo READY; exit 0; fi
printf 'address=127.0.0.1\nport={VNC_PORT}\nenable_auth=false\n' > {VNC_CONF}
setsid nohup wayvnc -C {VNC_CONF} 127.0.0.1 {VNC_PORT} >/tmp/piscout-wayvnc.log 2>&1 < /dev/null &
for i in 1 2 3 4 5 6 7 8; do
  sleep 1
  if ss -ltn 2>/dev/null | grep -q ':{VNC_PORT} '; then echo READY; exit 0; fi
done
echo FAILED
tail -5 /tmp/piscout-wayvnc.log
"""


def start_desktop(client):
    """確保 Pi 上有可以連的 VNC，回傳 Pi 端的 port。"""
    code, out, err = _run_script(client, START_VNC)
    first = out.strip().splitlines()[:1]
    status = first[0] if first else ""
    if status == "READY":
        return VNC_PORT
    if status == "NO_DISPLAY":
        raise RemoteError(tr(
            "找不到桌面 session。這台可能是 Lite 版（沒有桌面），或桌面還沒登入完成，請稍等一下再試。"
        ))
    if status == "NO_WAYVNC":
        raise RemoteError(tr(
            "這台沒有 wayvnc，可能是沒有桌面環境，或用的是舊的 X11 桌面。"
            "建議重新燒錄 Raspberry Pi OS 桌面版（64-bit）。"
        ))
    raise RemoteError(tr("遠端桌面啟動失敗：{why}",
                         why=out.strip() or err.strip() or tr("原因不明")))


def stop_desktop(client):
    try:
        run(client, "pkill -f '[p]iscout-wayvnc.conf'", timeout=10)  # [] 避免殺到自己
    except Exception:
        pass


def _run_script(client, script, timeout=40):
    stdin, stdout, stderr = client.exec_command("sh -s", timeout=timeout)
    stdin.write(script)
    stdin.channel.shutdown_write()
    code = stdout.channel.recv_exit_status()
    return code, stdout.read().decode(errors="replace"), stderr.read().decode(
        errors="replace"
    )


def _put_agent(client):
    sftp = client.open_sftp()
    try:
        sftp.put(str(AGENT_SRC), "/tmp/piscout_agent.py")
    finally:
        sftp.close()


def agent_installed(client):
    code, out, _ = run(client, f"systemctl is-active {SERVICE}")
    return out.strip() == "active"


def get_info(client):
    _put_agent(client)
    code, out, err = run(client, "python3 /tmp/piscout_agent.py --once")
    if code != 0:
        raise RemoteError(tr("讀取系統資訊失敗：{why}",
                             why=err.strip() or tr("這台沒有 python3？")))
    info = json.loads(out)
    info["agent_installed"] = agent_installed(client)
    return info


def install_agent(client, sudo_password=None):
    _put_agent(client)
    sftp = client.open_sftp()
    try:
        with sftp.open("/tmp/piscout-agent.service", "w") as f:
            f.write(UNIT)
    finally:
        sftp.close()

    steps = [
        f"mkdir -p {REMOTE_DIR}",
        f"cp /tmp/piscout_agent.py {REMOTE_DIR}/agent.py",
        f"cp /tmp/piscout-agent.service /etc/systemd/system/{SERVICE}.service",
        "systemctl daemon-reload",
        f"systemctl enable --now {SERVICE}",
    ]
    for step in steps:
        code, _, err = run(client, step, sudo_password=sudo_password)
        if code != 0:
            raise RemoteError(tr("安裝失敗（{step}）：{err}", step=step, err=err.strip()))
    return agent_installed(client)
