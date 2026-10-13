# Privacy policy / 隱私權政策

Last updated: 2026-10-14

## English

piscout is a desktop application that runs entirely on your computer.

**Data we collect:** none. piscout has no accounts, analytics, telemetry or advertising, and the
author operates no server that receives data from the app.

**What the app does on your machine and network**

- Scans your local network (/24) to find Raspberry Pi devices.
- Connects over SSH to devices you choose, using the username and password you enter.
- If you tick *Remember this login*, the username and password are stored **only on your computer**,
  at `%LOCALAPPDATA%\piscout\vault.json`. Passwords are encrypted with Windows DPAPI and can be
  decrypted only by your Windows account on that computer. You can delete them at any time with
  *Forget saved logins*.
- Downloads Raspberry Pi OS images from official Raspberry Pi domains
  (`raspberrypi.com`, `raspberrypi.org`) and the OS list from `downloads.raspberrypi.org`.
  Those servers see your IP address as in any download; see Raspberry Pi's own privacy policy.
- The built-in web interface listens only on `127.0.0.1` and is not reachable from other devices.

**Wi-Fi and account passwords you type into the flashing form** are written to the SD card's boot
partition as part of the OS configuration (the account password as a hash). They are not sent anywhere else.

**Children:** the app is not directed at children and collects no personal data.

**Changes:** updates to this policy are published in this repository.

**Contact:** open an issue at https://github.com/MilkteaTW1/piscout/issues

## 繁體中文

piscout 是完全在你的電腦上執行的桌面程式。

**我們收集的資料：** 無。程式沒有帳號、分析、遙測或廣告，作者也沒有架設任何接收資料的伺服器。

**程式在你的電腦與網路上做的事**

- 掃描你的區域網路（/24）以找出樹莓派。
- 用你輸入的帳號密碼，以 SSH 連線到你選擇的裝置。
- 如果你勾選「記住這台的帳號密碼」，帳密**只會儲存在你的電腦上**（`%LOCALAPPDATA%\piscout\vault.json`）。
  密碼以 Windows DPAPI 加密，只有同一台電腦上的同一個 Windows 帳號能解開，並可隨時用「清除已存帳密」刪除。
- 從樹莓派官方網域（`raspberrypi.com`、`raspberrypi.org`）下載 Raspberry Pi OS 映像與系統清單，
  這些伺服器會看到你的 IP，與一般下載相同，請參考樹莓派官方的隱私權政策。
- 內建的網頁介面只監聽 `127.0.0.1`，其他裝置無法連入。

**你在燒錄表單輸入的 Wi-Fi 與帳號密碼**會寫入 SD 卡開機分割區作為系統設定（帳號密碼為雜湊值），不會傳送到其他地方。

**兒童：** 本程式不以兒童為對象，也不收集任何個人資料。

**變更：** 政策更新會公布在這個儲存庫。

**聯絡：** 請到 https://github.com/MilkteaTW1/piscout/issues 開 issue。
