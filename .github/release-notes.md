## piscout v0.1.14 (pre-release)

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, multilingual UI (中文 / English / हिन्दी / اردو / العربية / বাংলা / Español, more welcome).

### What changed since v0.1.12
- **Add-ons tab.** Install common services on a Pi in one click: **NAS (Samba)**, **Docker**, **fail2ban**, **automatic security updates**. Official apt packages only; a confirmation lists the steps, ports and risks first; removing keeps your data. Installing needs sudo, so log in with the password (NAS always needs it). Tested against Ubuntu 24.04 over SSH, **not yet on a real Raspberry Pi**. Want to write one? See [#23](https://github.com/MilkteaTW1/piscout/issues/23): a bot verifies contributed add-ons by really installing and removing them.
- **Update settings.** The header shows the current version and an *Updates* panel: be told about new versions, **download and install automatically**, or never check (no contact with GitHub). You can also include **pre-releases**, and *Check now* forces a refresh.
- **Scan from the command line** on macOS and Linux: `python -m piscout scan` (also `--network`, `--all`, `--json`).

### Download
`piscout-setup.exe`. Verify it with `piscout-setup.exe.sha256`.

> It is not **code-signed**, so Windows SmartScreen may warn: *More info → Run anyway*.
> It is built by GitHub Actions from this repository's source at the tagged commit.

Pre-release because add-ons have not run on real Raspberry Pi hardware and automatic installation has not been tried across a real upgrade. Everything else is unchanged from v0.1.12.

---

## 繁體中文
相較 v0.1.12：
- **擴充套件分頁**：一鍵在樹莓派上安裝常見服務：**NAS（Samba）**、**Docker**、**fail2ban**、**自動安全更新**。只用 apt 官方套件；安裝前先列出步驟、連接埠和風險；移除時保留你的資料。安裝需要 sudo，請用密碼登入（NAS 一定要密碼）。已在 Ubuntu 24.04 上透過 SSH 測試，**還沒在真的樹莓派上測過**。想自己寫？見 [#23](https://github.com/MilkteaTW1/piscout/issues/23)：投稿的擴充套件會由機器人真的安裝、移除來驗證。
- **更新設定**：標題列顯示目前版本，並有「更新設定」：只提醒、**自動下載並安裝**、或完全不檢查（不連 GitHub）。也可以選擇**包含預先發行版**，「立即檢查」會強制重新查詢。
- **macOS / Linux 命令列掃描**：`python -m piscout scan`（也支援 `--network`、`--all`、`--json`）。

這是預先發行版，因為擴充套件還沒在真實樹莓派上跑過，自動安裝也還沒實際跨版本升級試過。其他內容與 v0.1.12 相同。檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
