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


# ------------------------------------------------------------------ 終端機回報目前資料夾
# 終端機開好、第一個提示字元出現後，悄悄送一行設定給 shell，讓它每次顯示提示字元時
# 用 OSC 7 回報 $PWD。這一行和它的回音會被吃掉，使用者看不到；之後的 OSC 7 照常轉給畫面。
import re as _re
import time as _time

# 開頭的空白讓它不進 history（Debian 預設 HISTCONTROL=ignoreboth）
INJECT = (
    r''' __pc() { printf '\033]7;file://%s%s\007' "$HOSTNAME" "$PWD"; }; '''
    r'''PROMPT_COMMAND="__pc${PROMPT_COMMAND:+;$PROMPT_COMMAND}"; __pc; '''
    r'''printf '__PISCOUT_%s__\n' READY''' "\n"
).encode()
MARKER = b"__PISCOUT_READY__"
_OSC7 = _re.compile(rb"\x1b\]7;file://[^/\x07\x1b]*(/[^\x07\x1b]*)(?:\x07|\x1b\\)")


class CwdTap:
    def __init__(self, send, now=_time.monotonic):
        self.send, self.now = send, now
        self.state = "wait"      # wait 等第一個提示字元 -> swallow 吃掉設定的回音 -> normal
        self.seen = False
        self.cwd = ""
        self._buf = b""
        self._tail = b""
        self._t0 = 0.0

    def _scan(self, data):
        text = self._tail + data
        for m in _OSC7.finditer(text):
            self.cwd = m.group(1).decode("utf-8", "replace")
        self._tail = text[-512:]

    def feed(self, data):
        """回傳要轉給畫面的資料。"""
        self._scan(data)
        if self.state == "wait":
            self.seen = True
            return data
        if self.state == "swallow":
            self._buf += data
            i = self._buf.find(MARKER)
            if i >= 0:
                j = self._buf.find(b"\n", i)
                if j < 0:
                    return b""      # 標記那一行還沒收完
                rest, self._buf, self.state = self._buf[j + 1:], b"", "normal"
                return b"\r\x1b[2K" + rest      # 新的提示字元蓋掉舊的那行
            if len(self._buf) > 65536:
                out, self._buf, self.state = self._buf, b"", "normal"
                return out
            return b""
        return data

    def idle(self):
        """一段時間沒有輸出時呼叫。回傳要轉給畫面的資料。"""
        if self.state == "wait" and self.seen:
            self.send(INJECT)
            self.state, self._t0 = "swallow", self.now()
        elif self.state == "swallow" and self.now() - self._t0 > 2.0:
            out, self._buf, self.state = self._buf, b"", "normal"
            return out       # 等太久就放行，不要把畫面卡住
        return b""
