## piscout v0.1.6

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, bilingual UI (中文 / English).

### What changed since v0.1.5
- **Health check in plain words**: under-voltage, overheating, SD card errors, full disk, low memory, failed services and a wrong clock are checked every minute while you are connected. Problems show up as short warnings in the status bubble (click one for the advice); the bubble now starts collapsed and shows ⚠️/❌ next to the temperature. Read-only.
- **Quick setup** on the *System info* tab: enable I2C / SPI and time sync, install common tools (htop, git, tree, ncdu, curl), expand the filesystem. A fixed list of actions only.
- **Much faster system info**: reuses the terminal's SSH connection, uploads the agent only once, and reads the quick-setup state in one round trip.
- MCP gets a read-only `pi_health` tool.
- Tab no longer moves focus out of the terminal when you accept a suggestion.

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
相較 v0.1.5：**白話健康檢查**（電源不足、過熱、SD 卡錯誤、磁碟快滿、記憶體不足、服務失敗、時間不準），連線時每分鐘檢查，有問題會以簡短警告顯示在狀態泡泡裡（點一下看建議）；泡泡預設縮小，溫度旁會有 ⚠️/❌ 提醒；只讀取，不改設定。
**快速設定**（系統資訊分頁）：開啟 I2C / SPI 與時間同步、安裝常用工具、擴展檔案系統，只提供固定清單的動作。
**系統資訊大幅變快**：重用終端機的 SSH 連線、agent 只上傳一次、快速設定狀態一次查完。MCP 新增唯讀的 `pi_health`。接受補齊建議時，Tab 不會再把焦點移出終端機。
本機 SD 卡燒錄已在真機驗證（Raspberry Pi 3 Model B）。**尚未在真機驗證：**遠端重灌的完整寫入（進階功能，預設關閉）、其他型號。
檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
