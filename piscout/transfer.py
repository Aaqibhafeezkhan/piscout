"""把電腦上的檔案丟進視窗，經 SFTP 傳到樹莓派。

終端機分頁：傳到這個終端機的 shell 目前所在的資料夾。
遠端桌面分頁：傳到桌面（找不到就用家目錄）。
目標資料夾一律由這裡在樹莓派上決定，前端只能給檔名，不能指定路徑。
"""
import posixpath
import re

from . import remote

# 在樹莓派上找出「這條 SSH 連線的終端機 shell」目前的資料夾：
# 用這條連線的來源埠找到 sshd 行程，再找它底下有 tty 的 shell，讀 /proc/<pid>/cwd。
CWD_SH = r"""
PORT={port}
pid=$(ss -tnpH 2>/dev/null | grep ":$PORT " | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)
if [ -n "$pid" ]; then
  sp=$(ps -o pid=,tty= --ppid "$pid" 2>/dev/null | awk '$2 != "?" {{print $1; exit}}')
  if [ -n "$sp" ]; then readlink "/proc/$sp/cwd" 2>/dev/null; exit 0; fi
fi
echo "$HOME"
"""

DESK_SH = r"""
d=$(xdg-user-dir DESKTOP 2>/dev/null)
[ -n "$d" ] && [ "$d" != "$HOME" ] || d="$HOME/Desktop"
mkdir -p "$d" 2>/dev/null && echo "$d" || echo "$HOME"
"""

_BAD = re.compile("[" + chr(0) + "-" + chr(31) + chr(127) + "/" + chr(92) + chr(92) + "]")


def safe_name(name):
    """只留檔名：去掉路徑、控制字元，空的或 . / .. 一律拒絕。"""
    name = _BAD.sub("_", (name or "").replace("\\", "/").split("/")[-1]).strip()
    if name in ("", ".", ".."):
        raise ValueError("bad file name")
    return name[:200]


def unique_name(name, exists):
    """已存在就改成 name (1).ext，不覆蓋對方原本的檔案。"""
    if not exists(name):
        return name
    stem, dot, ext = name.rpartition(".")
    if not dot or not stem:
        stem, ext = name, ""
    else:
        ext = "." + ext
    for i in range(1, 1000):
        cand = f"{stem} ({i}){ext}"
        if not exists(cand):
            return cand
    raise ValueError("too many files with the same name")


def _first_line(client, script):
    code, out, _ = remote.run(client, script, timeout=15)
    line = out.strip().splitlines()[0].strip() if out.strip() else ""
    return line if line.startswith("/") else ""


def term_dir(term_client):
    """term_client 是終端機分頁那條連線；沒有就回空字串，由呼叫端改用家目錄。"""
    if term_client is None:
        return ""
    port = term_client.get_transport().sock.getsockname()[1]
    return _first_line(term_client, CWD_SH.format(port=port))


def desk_dir(client):
    return _first_line(client, DESK_SH)


def home_dir(client):
    return _first_line(client, 'echo "$HOME"') or "/tmp"


def target_dir(client, mode, term_client=None):
    d = (term_dir(term_client) if mode == "term" else desk_dir(client)) or home_dir(client)
    return posixpath.normpath(d)
