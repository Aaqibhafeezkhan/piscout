## piscout v0.1.8

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, multilingual UI (中文 / English, more welcome).

### What changed since v0.1.7
- **Installer**: `piscout-setup.exe` installs per user (no administrator rights), adds a Start menu entry and an optional desktop shortcut, and shows up in Settings > Apps. The wizard follows your Windows language (built from the language files, so contributed languages show up in it too).
- **Updates inside the app**: when a newer release exists, a bar appears; *Update now* downloads the installer, verifies its SHA-256, installs and restarts the app. You can skip a version or turn the check off (`PISCOUT_NO_UPDATE_CHECK=1`). See [PRIVACY](docs/PRIVACY.md).

### Download
`piscout-setup.exe` (recommended) or the single-file `piscout.exe`. Verify with the `.sha256` files.

> Neither is **code-signed**, so Windows SmartScreen may warn: *More info → Run anyway*.
> They are built by GitHub Actions from this repository's source at the tagged commit.

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
相較 v0.1.7：
**安裝程式** `piscout-setup.exe`：安裝在你自己的帳號下（不需要系統管理員權限），有開始功能表項目與可選的桌面捷徑，也會出現在「設定 > 應用程式」；安裝畫面跟著你的 Windows 語言（由語言檔產生，別人貢獻的語言也會出現在安裝畫面）。
**在程式裡更新**：有新版本時會出現提示條，按「立即更新」會下載安裝程式、核對 SHA-256、安裝並自動重開。可略過某一版或關閉檢查（`PISCOUT_NO_UPDATE_CHECK=1`），見 [隱私權政策](docs/PRIVACY.md)。
本機 SD 卡燒錄已在真機驗證（Raspberry Pi 3 Model B）。**尚未在真機驗證：**遠端重灌的完整寫入（進階功能，預設關閉）、其他型號。
檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
