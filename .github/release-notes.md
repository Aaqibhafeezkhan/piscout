## piscout v0.1.11

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, multilingual UI (中文 / English / हिन्दी / اردو / العربية / বাংলা / Español, more welcome).

### What changed since v0.1.10
- **Spanish (Español) UI**, contributed by @Aaqibhafeezkhan in #17. Thank you! It covers the most visible screens; anything not translated yet shows English. More languages are welcome: see [docs/TRANSLATING.md](docs/TRANSLATING.md) and the open [language issue](https://github.com/MilkteaTW1/piscout/issues/11).
- Releases now ship **only the installer** (`piscout-setup.exe`) and its checksum; the separate single-file exe is gone.
- README: install and download shortcuts at the top, and a funding link.

### Download
`piscout-setup.exe`. Verify it with `piscout-setup.exe.sha256`.

> It is not **code-signed**, so Windows SmartScreen may warn: *More info → Run anyway*.
> It is built by GitHub Actions from this repository's source at the tagged commit.

Everything else is unchanged from v0.1.10, including what was and was not verified on real hardware.

---

## 繁體中文
相較 v0.1.10：新增 **西班牙語（Español）介面**（@Aaqibhafeezkhan，#17），非常感謝！目前涵蓋最常見的畫面，尚未翻譯的文字會顯示英文。
發佈檔現在**只提供安裝程式**（`piscout-setup.exe`）與其校驗檔，不再附單一執行檔。README 也加了安裝與下載捷徑，以及贊助連結。
其他內容與 v0.1.10 相同。檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
