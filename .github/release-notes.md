## piscout v0.1.2 (early release)

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, bilingual UI (中文 / English).

### What changed since v0.1.1
- **Fixed local SD card flashing failing at the read-back check.** The partition table is now written last, so Windows no longer mounts the new volumes while the image is still being written. Data is flushed before verifying, verification runs per 4 MB block, and a failure now tells you roughly where it happened.
- **Simpler Flash OS tab.** Only the common fields are shown (SD card, model, user, password, Wi-Fi). Remote re-imaging, OS variants and hostname/timezone/keyboard sit in collapsible sections.
- Local SD flashing is now verified on real hardware (Raspberry Pi 3 Model B booted and the configured login worked).

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
早期版本。相較 v0.1.1：**修正本機 SD 卡燒錄在讀回校驗失敗的問題**（分割表改為最後才寫入，避免 Windows 在寫入途中掛載新磁碟區；校驗改為逐塊比對，失敗時會指出大約的位置）；**燒錄頁面簡化**，只顯示常用欄位，其餘收進摺疊區。
本機 SD 卡燒錄已在真機驗證（Raspberry Pi 3 Model B 燒完可開機，並能以設定的帳號登入）。**尚未在真機驗證：**遠端重灌的完整寫入（進階功能，預設關閉）、其他型號。
檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
