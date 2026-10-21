"""讀取這台 Windows 電腦剪貼簿裡的文字，讓終端機可以直接貼上別的視窗複製的內容。

內嵌的瀏覽器元件對剪貼簿的權限不穩定（會跳詢問或直接拒絕），所以由程式自己讀。
只讀文字，而且只回傳給帶著本機 token 的請求。
"""
import sys
import time

MAX_CHARS = 1_000_000
CF_UNICODETEXT = 13


def get_text():
    """剪貼簿裡的文字；不是 Windows、沒有文字或讀不到就回空字串。"""
    if sys.platform != "win32":
        return ""
    import ctypes
    from ctypes import wintypes

    user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.GetClipboardData.argtypes = [wintypes.UINT]
    user32.GetClipboardData.restype = wintypes.HANDLE
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = wintypes.LPVOID
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]

    for _ in range(10):                 # 剪貼簿被別的程式短暫佔用時重試
        if user32.OpenClipboard(None):
            break
        time.sleep(0.02)
    else:
        return ""
    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return ""
        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            return ""
        try:
            return ctypes.wstring_at(pointer)[:MAX_CHARS]
        finally:
            kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()
