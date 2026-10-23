## piscout v0.1.10

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, multilingual UI (中文 / English / हिन्दी / اردو / العربية / বাংলা, more welcome).

### What changed since v0.1.9
- **Urdu (اردو) and Arabic (العربية) UI**, contributed by @Aaqibhafeezkhan in #13 and #14. **Bengali (বাংলা) UI**, contributed by @rahul05ranjan in #15. Thank you! They cover the most visible screens; anything not translated yet shows English. Both Urdu and Arabic are right-to-left and were not checked for right-to-left layout, so text may look off in places: please report it. More languages are welcome: see [docs/TRANSLATING.md](docs/TRANSLATING.md) and the open [language issue](https://github.com/MilkteaTW1/piscout/issues/11).
- **Compute Module 5 and Raspberry Pi 500** are now recognised as Pi 5 class boards, so they get the 64-bit Pi 5 image (a Compute Module 5 used to be offered the 32-bit Pi 1 image), contributed by @rahul05ranjan in #16.
- The installer now picks Portuguese (Brazil) and Japanese automatically when Windows uses them.

### Download
`piscout-setup.exe` (recommended) or the single-file `piscout.exe`. Verify with the `.sha256` files.

> Neither is **code-signed**, so Windows SmartScreen may warn: *More info → Run anyway*.
> They are built by GitHub Actions from this repository's source at the tagged commit.

Everything else is unchanged from v0.1.9, including what was and was not verified on real hardware.

---

## 繁體中文
相較 v0.1.9：新增 **烏爾都語（اردو）、阿拉伯語（العربية）介面**（@Aaqibhafeezkhan，#13、#14）與 **孟加拉語（বাংলা）介面**（@rahul05ranjan，#15），非常感謝！目前涵蓋最常見的畫面，尚未翻譯的文字會顯示英文。烏爾都語和阿拉伯語是由右至左的語言，尚未檢查版面是否正常，若有異常請回報。
另外 **Compute Module 5 與 Raspberry Pi 500** 現在會被辨識為 Pi 5 等級，使用 64 位元的 Pi 5 映像（過去 Compute Module 5 會被給 32 位元的 Pi 1 映像）（@rahul05ranjan，#16）。安裝程式在 Windows 使用葡萄牙語（巴西）或日語時也會自動選用該語言。
其他內容與 v0.1.9 相同。檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
