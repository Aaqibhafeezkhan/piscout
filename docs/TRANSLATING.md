# Adding a language to piscout

Languages are plain JSON files. **You do not need to change any code**: drop a file into
`piscout/static/locales/` and the language picker (top right of the app) shows it automatically.

The source language is Traditional Chinese (the app's text is written in it). Every translation file uses the
Chinese text as the key and your translation as the value. English (`en.json`) is the reference, copy its meaning.

## Steps

1. Create a template (all sentences listed, values empty):

   ```bash
   python tools/i18n_check.py --new ja 日本語
   ```

   The first argument is the language code (`ja`, `de`, `pt-br`, `zh-cn` ...), the second is the name shown in the
   picker, written in that language.

2. Open `piscout/static/locales/ja.json` and fill in the values. Leave a value empty to skip it; empty ones
   show English instead, so a half-finished translation is already usable.

3. Check your file:

   ```bash
   python tools/i18n_check.py
   ```

   It reports errors (which you must fix) and how many sentences are translated.

4. Try it: run the app from source (`python run_gui.py`, or `PISCOUT_DEMO=1` for a simulated device), pick your
   language, and look at every tab.

5. Open a pull request with the new `.json` file.

## File format

```json
{
  "name": "日本語",
  "ui": {
    "exact": { "連線": "接続" },
    "sub":   [ ["正在檢查…", "確認中…"] ],
    "rx":    [ { "pattern": "^已選 (\\d+) 台$", "replace": "$1 台選択中" } ]
  },
  "backend": { "下載失敗：{e}": "ダウンロード失敗: {e}" }
}
```

- `ui.exact` – the whole text of a label must match. Used for short words.
- `ui.sub` – replaced wherever it appears inside a longer text. Used for sentences.
- `ui.rx` – sentences with numbers or names in them. **Keep `pattern` exactly as in `en.json`**, only write
  `replace`. In `replace`, `$1`, `$2` are the captured parts, and `{{2}}` means "translate captured part 2 as
  well".
- `backend` – messages and errors produced by the program itself. Keep placeholders such as `{e}`, `{host}`,
  `{n}` exactly as they are (the checker verifies this); you may move them around in the sentence.

Tips

- Keep translations short, buttons have little room.
- Do not translate product names (Raspberry Pi, SSH, VNC ...) unless your language normally does.
- A region-specific file (`zh-cn.json`, `pt-br.json`) is used for that region; a generic one (`pt.json`) is used
  for the rest of the language.
- Adding a new sentence to the app? Add it to `en.json` too. Other languages fall back to English until translated.

---

## 新增語言（繁體中文）

語言就是單純的 JSON 檔，**不用改任何程式**：把檔案放進 `piscout/static/locales/`，右上角的語言選單就會自動出現。

1. 產生範本：`python tools/i18n_check.py --new ja 日本語`（語言代碼、選單上顯示的名稱）
2. 打開 `piscout/static/locales/ja.json`，把空的值填上翻譯。空的會顯示英文，所以只翻一半也能用；內容可以參考 `en.json`。
3. 檢查：`python tools/i18n_check.py`，會列出必須修的錯誤與翻譯進度。
4. 從原始碼執行 `python run_gui.py` 切到你的語言看一遍，再送 PR。

`rx` 的 `pattern` 要跟 `en.json` 完全一樣，只改 `replace`；`backend` 裡的 `{e}`、`{host}` 這類變數要原樣保留。
