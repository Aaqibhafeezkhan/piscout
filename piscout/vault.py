"""儲存各台樹莓派的登入帳密。

密碼用 Windows DPAPI 加密，只有同一個 Windows 使用者在同一台電腦上才解得開，
檔案複製到別的電腦或別的帳號就是一堆亂碼。非 Windows 只存帳號，不存密碼。
"""
import base64
import ctypes
import json
import os
import threading
from ctypes import wintypes
from pathlib import Path

_lock = threading.Lock()


class _Blob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _dpapi(data, protect):
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    src = _Blob(len(data), ctypes.cast(ctypes.create_string_buffer(data, len(data)),
                                       ctypes.POINTER(ctypes.c_char)))
    out = _Blob()
    fn = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
    if not fn(ctypes.byref(src), None, None, None, None, 0, ctypes.byref(out)):
        raise OSError("DPAPI 失敗")
    try:
        return ctypes.string_at(out.pbData, out.cbData)
    finally:
        kernel32.LocalFree(out.pbData)


def _path():
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".config")
    d = Path(base) / "piscout"
    d.mkdir(parents=True, exist_ok=True)
    return d / "vault.json"


def _load():
    try:
        return json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save(data):
    p = _path()
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(p)


def put(key, username, password, port=22, key_path=None):
    with _lock:
        data = _load()
        entry = {"username": username, "password": None, "port": int(port or 22), "key_path": key_path or None}
        if password and os.name == "nt":
            blob = _dpapi(password.encode("utf-8"), True)
            entry["password"] = base64.b64encode(blob).decode()
        data[key] = entry
        _save(data)


def get(key):
    with _lock:
        entry = _load().get(key)
    if not entry:
        return None
    password = None
    if entry.get("password") and os.name == "nt":
        try:
            password = _dpapi(base64.b64decode(entry["password"]), False).decode("utf-8")
        except (OSError, ValueError):
            password = None  # 換了電腦或帳號就解不開，當作沒存
    return {"username": entry.get("username", ""), "password": password,
            "key_path": entry.get("key_path"), "port": entry.get("port") or 22}


def delete(key=None):
    with _lock:
        if key is None:
            _save({})
            return
        data = _load()
        data.pop(key, None)
        _save(data)
