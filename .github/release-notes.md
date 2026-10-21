## piscout v0.1.7

Windows desktop tool for Raspberry Pi on your LAN: auto-discovery, built-in SSH terminal, remote desktop, overview and batch actions, SD card flashing, multilingual UI (中文 / English, more welcome).

### What changed since v0.1.6
- **Paste into the terminal from other windows**: Ctrl+V (or Shift+Insert) pastes what you copied anywhere on your PC; right-click pastes (or copies if text is selected); Ctrl+C copies a selection (without a selection it still interrupts the program).
- **Languages are now plain files**: translations moved to `piscout/static/locales/*.json`. Adding a language needs **no code**, see [docs/TRANSLATING.md](docs/TRANSLATING.md). A checker (`tools/i18n_check.py`) and a template generator are included, and untranslated sentences fall back to English. Want to add yours? [Issue #11](https://github.com/MilkteaTW1/piscout/issues/11).

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
相較 v0.1.6：**可以從別的視窗貼進終端機**：Ctrl+V（或 Shift+Insert）貼上電腦上任何地方複製的文字；右鍵有選取就複製、沒選取就貼上；選取後 Ctrl+C 複製（沒選取時仍是中斷程式）。
**語言改成獨立檔案**：翻譯搬到 `piscout/static/locales/*.json`，新增語言不用寫程式，見 [docs/TRANSLATING.md](docs/TRANSLATING.md)；附檢查工具與範本產生器，沒翻的句子會顯示英文。想新增你的語言？見 [issue #11](https://github.com/MilkteaTW1/piscout/issues/11)。
本機 SD 卡燒錄已在真機驗證（Raspberry Pi 3 Model B）。**尚未在真機驗證：**遠端重灌的完整寫入（進階功能，預設關閉）、其他型號。
檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。
