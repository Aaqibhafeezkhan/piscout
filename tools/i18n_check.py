"""檢查語言檔，或產生新語言的空白範本。

  python tools/i18n_check.py                  檢查 piscout/static/locales/ 裡所有語言檔
  python tools/i18n_check.py --new ja 日本語   產生 ja.json 範本（所有句子都列好，值是空的）

空的值代表「還沒翻」，程式會先顯示英文。做法見 docs/TRANSLATING.md。
"""
import json
import re
import sys
from pathlib import Path

LOCALES = Path(__file__).resolve().parent.parent / "piscout" / "static" / "locales"
FIELD = re.compile(r"\{(\w*)\}")
DOLLAR = re.compile(r"\$(\d)")
BRACE2 = re.compile(r"\{\{(\d)\}\}")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fields(text):
    return sorted(FIELD.findall(text.replace("{{", "").replace("}}", "")))


def check(code, data, en):
    """回傳 (錯誤清單, 還沒翻的數量)。錯誤會讓程式顯示錯的內容，一定要修。"""
    errors, missing = [], 0
    if not isinstance(data, dict):
        return [f"{code}: top level must be an object"], 0
    if not str(data.get("name") or "").strip():
        errors.append(f'{code}: "name" is required (the name shown in the language picker)')
    ui, be = data.get("ui") or {}, data.get("backend") or {}

    exact = ui.get("exact") or {}
    for zh, tr in exact.items():
        if not isinstance(tr, str):
            errors.append(f"{code}: ui.exact[{zh!r}] must be a string")
        elif not tr:
            missing += 1
    for zh in (en["ui"].get("exact") or {}):
        if zh not in exact:
            missing += 1

    subs = ui.get("sub") or []
    seen = set()
    for i, pair in enumerate(subs):
        if not (isinstance(pair, list) and len(pair) == 2 and all(isinstance(x, str) for x in pair)):
            errors.append(f"{code}: ui.sub[{i}] must be [chinese, translation]")
            continue
        seen.add(pair[0])
        if not pair[1]:
            missing += 1
    missing += sum(1 for zh, _ in en["ui"].get("sub", []) if zh not in seen)

    en_rx = {r["pattern"]: r for r in en["ui"].get("rx", [])}
    own_rx = {}
    for i, r in enumerate(ui.get("rx") or []):
        if not (isinstance(r, dict) and isinstance(r.get("pattern"), str) and isinstance(r.get("replace"), str)):
            errors.append(f"{code}: ui.rx[{i}] must be {{pattern, replace}}")
            continue
        own_rx[r["pattern"]] = r
        if r["pattern"] not in en_rx:
            errors.append(f"{code}: ui.rx[{i}] pattern is not in en.json (keep the Chinese pattern exactly): {r['pattern']}")
            continue
        if not r["replace"]:
            missing += 1
            continue
        groups = re.compile(r["pattern"]).groups
        for n in DOLLAR.findall(r["replace"]) + BRACE2.findall(r["replace"]):
            if int(n) < 1 or int(n) > groups:
                errors.append(f"{code}: ui.rx[{i}] uses group {n} but the pattern only has {groups}")
    missing += sum(1 for p in en_rx if p not in own_rx)

    for zh, tr in be.items():
        if not isinstance(tr, str):
            errors.append(f"{code}: backend[{zh[:30]!r}] must be a string")
        elif not tr:
            missing += 1
        elif fields(tr) != fields(zh):
            errors.append(f"{code}: backend placeholders differ: {zh[:40]!r} has {fields(zh)}, translation has {fields(tr)}")
    missing += sum(1 for zh in en["backend"] if zh not in be)
    return errors, missing


def skeleton(name, en):
    return {
        "name": name,
        "ui": {
            "exact": {zh: "" for zh in en["ui"].get("exact", {})},
            "sub": [[zh, ""] for zh, _ in en["ui"].get("sub", [])],
            "rx": [{"pattern": r["pattern"], "replace": ""} for r in en["ui"].get("rx", [])],
        },
        "backend": {zh: "" for zh in en["backend"]},
    }


def main(argv):
    en = load(LOCALES / "en.json")
    if argv[:1] == ["--new"]:
        if len(argv) != 3 or not re.fullmatch(r"[a-z]{2,3}(-[a-z0-9]{2,8})?", argv[1].lower()):
            print("usage: python tools/i18n_check.py --new <code like ja or pt-br> <language name>")
            return 2
        target = LOCALES / (argv[1].lower() + ".json")
        if target.exists():
            print(f"{target} already exists")
            return 1
        target.write_text(json.dumps(skeleton(argv[2], en), ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"created {target}\nFill in the empty values; empty ones show English. Then run this tool again to check.")
        return 0
    bad = 0
    for path in sorted(LOCALES.glob("*.json")):
        try:
            data = load(path)
        except ValueError as e:
            print(f"{path.name}: not valid JSON: {e}")
            bad += 1
            continue
        errors, missing = check(path.stem, data, en)
        total = len(en["ui"].get("exact", {})) + len(en["ui"].get("sub", [])) + len(en["ui"].get("rx", [])) + len(en["backend"])
        print(f"{path.name}: {total - min(missing, total)}/{total} translated, {len(errors)} error(s)")
        for e in errors:
            print("  ERROR", e)
        bad += len(errors)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
