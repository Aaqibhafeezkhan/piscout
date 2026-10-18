"""桌面視窗版：在本機開一個只聽 127.0.0.1 的服務，再用原生視窗包起來。"""
import socket
import sys
import threading
import time

import uvicorn

from .app import app


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main():
    if "--mcp" in sys.argv:  # 給 AI 助手用：piscout.exe --mcp
        from . import mcp
        return mcp.main()
    import webview

    port = _free_port()
    # log_config=None：打包成無主控台的 exe 之後 stdout 不存在，預設的 log 設定會出錯
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_config=None)
    )
    threading.Thread(target=server.run, daemon=True).start()

    deadline = time.time() + 15
    while not server.started and time.time() < deadline:
        time.sleep(0.05)

    webview.create_window(
        "piscout", f"http://127.0.0.1:{port}",
        width=1040, height=780, min_size=(760, 560),
    )
    webview.start()
    server.should_exit = True


if __name__ == "__main__":
    main()
