## piscout v0.1.1 (early release)

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, bilingual UI (中文 / English).

### What changed since v0.1.0
- **Remote re-imaging is now an advanced feature, off by default.** It must be enabled with a switch on the *Flash OS* tab, and the backend refuses it without that confirmation. See *Known risks* in the README: the first real-hardware attempt was interrupted and left an SD card unbootable.
- **Administrator rights are no longer required to start the app.** Only local SD card flashing needs them; the app offers a "Restart as administrator" button there.
- Clearer connection errors that say what to do next (SSH not enabled, timeout, connection dropped, device not found).
- README now has a demo GIF, screenshots and a Known risks section; README text and roadmap are consistent with what is implemented.

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

### Not yet verified on real hardware
- **A completed remote re-imaging run** (the first attempt was interrupted, see Known risks)
- Local SD card flashing

### Not possible
A completely blank SD card that has never booted cannot be reached over the network by any software; flash it once from a computer.

---

## 繁體中文
早期版本。相較 v0.1.0：**遠端重灌改為進階功能、預設關閉**（第一次真機嘗試被中斷，讓一張 SD 卡開不了機，詳見 README「已知風險」）；
啟動不再要求系統管理員（只有本機燒錄才需要，並提供重新啟動按鈕）；連線錯誤會說明下一步；README 補上示範 GIF 與截圖。
已在真機驗證（Raspberry Pi 3 Model B、Raspberry Pi OS Bookworm）：區網掃描、SSH 登入與系統資訊、內建終端機、遠端桌面、總覽。**尚未在真機驗證：**遠端重灌的完整寫入、本機 SD 卡燒錄。
檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
