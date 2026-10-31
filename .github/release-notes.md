## piscout v0.1.12

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, multilingual UI (中文 / English / हिन्दी / اردو / العربية / বাংলা / Español, more welcome).

### What changed since v0.1.11
- **Add a Pi by hand.** If the scan cannot see your Pi (router AP isolation, another subnet), type its IP or name (for example `raspberrypi.local`) under the scan bar and connect directly. Only private-network addresses are accepted. Manual entries are remembered, tagged "Added manually", and can be removed.
- **Custom SSH port and key file.** The login form has an "Advanced" section for the SSH port and a key file path (the password field is then the key's passphrase). Both are saved with the login, so the overview, MCP and remote flash use them too. Tested against a local SSH server on port 2222.
- **Faster start.** The app is now packaged as a folder instead of one self-extracting exe: the window appears in about 1.5 s instead of about 2.2 s (median of 5 runs on one machine), and the installer is smaller (20.8 MB instead of 25.6 MB). Memory is unchanged (about 490 MB, mostly WebView2). Your saved logins are kept.
- README: a translation progress chart.

### Download
`piscout-setup.exe`. Verify it with `piscout-setup.exe.sha256`.

> It is not **code-signed**, so Windows SmartScreen may warn: *More info → Run anyway*.
> It is built by GitHub Actions from this repository's source at the tagged commit.

Not verified on real hardware: connecting through a custom SSH port or key to a real Raspberry Pi (tested against a local SSH test server only), and a clean-PC install of the new folder layout (tested by installing and uninstalling on the development machine). Everything else is unchanged from v0.1.11.

---

## 繁體中文
相較 v0.1.11：
- **手動新增樹莓派**：掃不到時（路由器 AP 隔離、跨網段），在掃描列下面輸入 IP 或名稱（例如 `raspberrypi.local`）就能直接連線，只接受區網位址。手動新增的裝置會被記住、標示「手動新增」，也可以移除。
- **自訂 SSH 連接埠與金鑰檔**：登入表單新增「進階」，可填 SSH 連接埠和金鑰檔路徑（此時密碼欄是金鑰的密語），會和帳密一起儲存，總覽、MCP、遠端重灌也會使用。已用本機 2222 埠的測試 SSH 伺服器驗證。
- **啟動更快**：改成資料夾版打包，不再每次啟動先自我解壓縮：視窗出現約 1.5 秒（原本約 2.2 秒，同一台電腦各測 5 次的中位數），安裝檔也縮小（20.8 MB，原本 25.6 MB）。記憶體不變（約 490 MB，大多是 WebView2）。已儲存的帳密會保留。
- README 加了翻譯進度圖。

尚未在真實硬體驗證：用自訂連接埠或金鑰連到真的樹莓派（只用本機 SSH 測試伺服器測過）、以及全新電腦上安裝資料夾版（只在開發用電腦上安裝、解除安裝測過）。其他內容與 v0.1.11 相同。檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
