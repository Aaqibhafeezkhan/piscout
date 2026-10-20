## piscout v0.1.5 (early release)

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, bilingual UI (中文 / English).

### What changed since v0.1.4
- **Drag and drop files** onto the window to upload them over SFTP, with a progress bar. In the terminal tab they land in the folder your shell is currently in; in the remote desktop tab they go to the desktop.
- **VS Code-style suggestions in the terminal**: a popup appears while you type (commands, files, folders). Up/Down to choose, Tab to accept, Esc to close. Focus stays in the terminal.
- **Startup is faster**: the Pis seen last time are shown immediately, the scan runs in the background (cards are marked "last seen" / "not found this time").
- The status bubble can be dragged anywhere (double-click to reset).
- Tab completion now flashes the terminal border instead of beeping.

### Download
`piscout.exe` (below). Verify with `piscout.exe.sha256`.

> The exe is **not code-signed**, so Windows SmartScreen may warn: *More info → Run anyway*.
> It is built by GitHub Actions from this repository's source at the tagged commit.

### Verified on real hardware
Raspberry Pi 3 Model B Rev 1.2, Raspberry Pi OS (Debian 12 Bookworm):
- LAN scan and Raspberry Pi detection
- SSH login, system info, agent install
- Built-in terminal (commands run, tested by the author)
- Remote desktop (tested by the author)
- Overview / agent stats
- Local SD card flashing (the Pi booted, the configured user could log in)

### Not yet verified on real hardware
- **A completed remote re-imaging run** (the first attempt was interrupted, see Known risks). It is an advanced feature and off by default.
- Other Raspberry Pi models

### Not possible
A completely blank SD card that has never booted cannot be reached over the network by any software; flash it once from a computer.

---

## 繁體中文
早期版本。相較 v0.1.4：**拖曳檔案到視窗即可上傳（有進度條）**，終端機分頁傳到 shell 目前所在的資料夾，遠端桌面分頁傳到桌面；**終端機輸入時會跳出像 VS Code 的補齊選單**（上下鍵選、Tab 接受、Esc 關閉）；**啟動時先顯示上次的樹莓派，背景再掃描**；系統資訊泡泡可以拖動；Tab 補齊改用框線閃爍取代響鈴。
本機 SD 卡燒錄已在真機驗證（Raspberry Pi 3 Model B）。**尚未在真機驗證：**遠端重灌的完整寫入（進階功能，預設關閉）、其他型號。
檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
