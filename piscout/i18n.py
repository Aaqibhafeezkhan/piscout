"""後端訊息的語言切換。

程式裡的訊息直接用中文寫（中文是原文，也是預設語言）。其他語言放在
piscout/static/locales/<語言代碼>.json，用中文原文當 key；想新增語言只要放一個檔案進去，
不用改程式。格式與做法見 docs/TRANSLATING.md。

語言由每個請求的 X-Lang / Accept-Language 決定，背景工作會在建立時記下來。
某句沒翻的話先用英文，英文也沒有才顯示中文原文。
"""
import contextvars
import json
from pathlib import Path

LOCALES_DIR = Path(__file__).parent / "static" / "locales"
SOURCE = "zh"
SOURCE_NAME = "繁體中文"

_lang = contextvars.ContextVar("piscout_lang", default=SOURCE)


def load_locales(directory=LOCALES_DIR):
    """讀取所有語言檔，回傳 {代碼: 內容}。壞掉的檔案略過，不要讓整個程式起不來。"""
    found = {}
    for path in sorted(Path(directory).glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and path.stem.lower() != SOURCE:   # zh.json 只放安裝程式用的文字
            found[path.stem.lower()] = data
    return found


LOCALES = load_locales()
EN = LOCALES.get("en", {}).get("backend", {})


def languages():
    """給語言選單用：[{code, name}]，中文在最前面。"""
    rows = [{"code": SOURCE, "name": SOURCE_NAME}]
    for code, data in LOCALES.items():
        rows.append({"code": code, "name": str(data.get("name") or code)})
    return rows


def resolve(value):
    """把 'en-US,en;q=0.9'、'zh-TW'、'pt-BR' 這類字串換成有的語言代碼。"""
    tags = [t.split(";")[0].strip().lower() for t in (value or "").split(",")]
    tags = [t for t in tags if t]
    if not tags:
        return SOURCE
    for tag in tags:
        if tag in LOCALES:
            return tag
        if tag.startswith("zh"):
            return SOURCE
        base = tag.split("-")[0]
        if base in LOCALES:
            return base
    return "en" if "en" in LOCALES else SOURCE


def set_lang(value):
    _lang.set(resolve(value))


def get_lang():
    return _lang.get()


def _lookup(lang, zh):
    for code in (lang, "en"):
        text = LOCALES.get(code, {}).get("backend", {}).get(zh)
        if text:
            return text
    return zh


def tr(zh, **kw):
    lang = _lang.get()
    s = zh if lang == SOURCE else _lookup(lang, zh)
    if not kw:
        return s
    try:
        return s.format(**kw)
    except (KeyError, IndexError, ValueError):
        return zh.format(**kw)      # 翻譯檔寫錯變數時退回原文，不要讓請求出錯
