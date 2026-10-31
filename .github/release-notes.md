## piscout v0.1.13 (pre-release)

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, multilingual UI (中文 / English / हिन्दी / اردو / العربية / বাংলা / Español, more welcome).

### What changed since v0.1.12
- **Add-ons.** A new *Add-ons* section on a Pi's info page installs common services in one click: **NAS (Samba)**, **Docker**, **fail2ban** and **automatic security updates**. Official apt packages only, and a confirmation lists the steps, ports and risks first. Removing keeps your data. Installing needs sudo, so log in with the password (NAS always needs it). Tested against Ubuntu 24.04 over SSH, **not yet on a real Raspberry Pi**.
- **Scan from the command line** on macOS and Linux: `python -m piscout scan` (also `--network`, `--all`, `--json`).

### Download
`piscout-setup.exe`. Verify it with `piscout-setup.exe.sha256`.

> It is not **code-signed**, so Windows SmartScreen may warn: *More info → Run anyway*.
> It is built by GitHub Actions from this repository's source at the tagged commit.

This is a pre-release because add-ons have not been run on real Raspberry Pi hardware. Everything else is unchanged from v0.1.12.

---

## 繁體中文
相較 v0.1.12：
- **擴充套件**：樹莓派資訊頁新增「擴充套件」，一鍵安裝常見服務：**NAS（Samba）**、**Docker**、**fail2ban**、**自動安全更新**。只用 apt 官方套件，安裝前會先列出要做什麼、開哪些連接埠和風險；移除時保留你的資料。安裝需要 sudo，請用密碼登入（NAS 一定要密碼）。已在 Ubuntu 24.04 上透過 SSH 測試，**還沒在真的樹莓派上測過**。
- **macOS / Linux 命令列掃描**：`python -m piscout scan`（也支援 `--network`、`--all`、`--json`）。

這是預先發行版，因為擴充套件還沒在真實樹莓派上跑過。其他內容與 v0.1.12 相同。檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
