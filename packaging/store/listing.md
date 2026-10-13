# Microsoft Store listing (draft)

Copy these into Partner Center. Review before submitting.

## Product name
piscout

## Category
Developer tools (alternative: Utilities & tools)

## Short description (≤ 100 chars)
- en-US: Find, connect to and manage Raspberry Pis on your network.
- zh-TW: 找出並管理區網裡的樹莓派：SSH 終端機、遠端桌面、燒錄。

## Description
### en-US
piscout is a Raspberry Pi manager for Windows.

- Auto-discovery: scans your local network on launch and recognises Raspberry Pis.
- Built-in SSH terminal: log in and work inside the app, no separate window.
- Remote desktop: view and control the Pi's desktop through the SSH tunnel (Raspberry Pi OS with desktop).
- Overview and batch actions: see temperature, load and memory of several Pis; reboot, shut down or update them together.
- SD card flasher: write Raspberry Pi OS (official images, SHA-256 verified) with hostname, user, Wi-Fi and SSH preset, with a recommended OS for your model.
- Saved logins are encrypted with Windows DPAPI and stay on your computer.
- English and Traditional Chinese, detected automatically.

Notes: remote re-imaging of a running Pi is an advanced, off-by-default feature with real risks (see the README).
No data is collected. Open source (MIT): https://github.com/MilkteaTW1/piscout

### zh-TW
piscout 是 Windows 上的樹莓派管理工具。

- 自動掃描：一打開就掃描區網並辨識樹莓派
- 內建 SSH 終端機：登入後直接在程式裡操作，不用另外開視窗
- 遠端桌面：經 SSH 通道查看並操作樹莓派桌面（需 Raspberry Pi OS 桌面版）
- 總覽與批次操作：一次看多台的溫度、負載、記憶體，並可批次重開機、關機、更新
- SD 卡燒錄：寫入官方 Raspberry Pi OS（SHA-256 校驗），預先設定主機名稱、帳號、Wi-Fi 與 SSH，並依型號給出建議
- 儲存的帳密以 Windows DPAPI 加密，只存在你的電腦
- 自動偵測繁體中文與英文

注意：遠端重灌執行中的樹莓派是進階功能，預設關閉，有實際風險（詳見 README）。
不收集任何資料。開放原始碼（MIT）：https://github.com/MilkteaTW1/piscout

## What's new (v0.1.1)
- en-US: Remote re-imaging is now an advanced, off-by-default feature. Clearer connection errors. No administrator rights needed unless you flash an SD card.
- zh-TW: 遠端重灌改為進階功能、預設關閉；連線錯誤更清楚；只有燒錄 SD 卡才需要系統管理員權限。

## Keywords (≤ 7)
raspberry pi, ssh, network scanner, sd card, remote desktop, vnc, flasher

## Privacy policy URL
https://github.com/MilkteaTW1/piscout/blob/main/docs/PRIVACY.md

## Website / support
- Website: https://github.com/MilkteaTW1/piscout
- Support: https://github.com/MilkteaTW1/piscout/issues

## Age rating
All ages, no user-generated content, no purchases.

## Notes for certification
- The app is a packaged Win32 app (`runFullTrust`). It needs full trust because it opens raw SSH connections,
  scans the local network, and (optional feature) writes an OS image to a removable SD card.
- It collects no data and has no accounts; see the privacy policy.
- Capabilities: `internetClient` (download official Raspberry Pi OS images and the OS list),
  `privateNetworkClientServer` (scan the LAN and connect to the user's own Raspberry Pi over SSH/VNC).
- To review without a Raspberry Pi: start the app with the environment variable `PISCOUT_DEMO=1` to get a simulated device
  (clearly labelled), or just open the *Flash OS* tab, which uses the real official OS list.
- Writing to an SD card only happens after an explicit two-step confirmation and only to removable disks, never the system disk.
