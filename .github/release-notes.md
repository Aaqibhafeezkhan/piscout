## piscout v0.1.4 (early release)

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, bilingual UI (中文 / English).

### What changed since v0.1.3
- **The status bubble now appears only while you are connected**, shows the device you are connected to, and refreshes every 20 seconds using the login you typed (no saved login or agent needed). It can still be collapsed to a small chip.
- Fixed the bubble being cut off in narrow windows.
- If saving a login fails, the app now tells you instead of failing silently.
- Since v0.1.2: the agent installs itself after the first login, and `piscout.exe --mcp` starts an MCP server so AI assistants can list and operate your Pis (see README).

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
早期版本。相較 v0.1.3：**右上角的系統資訊泡泡改為只在連線時出現**，顯示你正在連的那台，並以你輸入的帳密每 20 秒更新（不需要已存帳密或 agent），仍可收合；修正泡泡在窄視窗被切掉的問題；帳密存檔失敗時會提示。
自 v0.1.2 起：agent 在第一次登入後自動安裝，`piscout.exe --mcp` 可啟動 MCP 伺服器讓 AI 助手列出並操作你的樹莓派（見 README）。
本機 SD 卡燒錄已在真機驗證（Raspberry Pi 3 Model B）。**尚未在真機驗證：**遠端重灌的完整寫入（進階功能，預設關閉）、其他型號。
檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
