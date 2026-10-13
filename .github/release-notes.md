## piscout v0.1.0 (early release)

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, remote re-imaging, overview and batch actions, bilingual UI (中文 / English).

### Download
`piscout.exe` (below). Verify with `piscout.exe.sha256`. The app asks for administrator rights because writing to disks requires it.

> The exe is **not code-signed**, so Windows SmartScreen may warn: *More info → Run anyway*.
> It is built by GitHub Actions from this repository's source at the tagged commit.

### Verified on real hardware
- LAN scan and Raspberry Pi detection
- Built-in SSH terminal
- Overview / agent stats

### Not yet verified on real hardware
- **Remote re-imaging** (writing a new OS to the Pi's own SD card over SSH)
- Remote desktop
- Local SD card flashing

Remote re-imaging overwrites the disk of a running system. If power or the network drops mid-write, the card will not boot and must be re-flashed from a computer. **Have a card reader or a spare SD card before trying it.**

### Not possible
A completely blank SD card that has never booted cannot be reached over the network by any software; flash it once from a computer.

---

## 繁體中文
早期版本。已在真機驗證：區網掃描、內建終端機、總覽。**尚未在真機驗證：**遠端重灌、遠端桌面、本機 SD 卡燒錄。
遠端重灌會覆寫執行中系統的磁碟，中途斷電或斷網會讓那張卡開不了機，請先準備讀卡機或備用的卡。
檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
