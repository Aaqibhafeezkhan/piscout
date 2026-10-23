"""Build piscout-setup.exe with the languages found in piscout/static/locales/.

  python packaging/installer/build_installer.py [--version 0.1.8] [--iscc path/to/ISCC.exe]

Each locale file may have an "installer" section:

  "installer": {
    "custom":   { "TaskDesktop": "...", "TaskGroup": "...", "RunApp": "..." },
    "messages": { "ButtonNext": "...", ... }
  }

"custom" holds piscout's own installer texts, "messages" (optional) overrides Inno Setup's standard wizard texts.
For every language the wizard uses Inno Setup's bundled translation when there is one (ja, de, fr ...) and lays the
locale's texts on top. Languages Inno does not ship (zh ...) start from English and use "messages".
The installer picks the language of the user's Windows automatically (English if nothing matches).
"""
import argparse
import json
import locale
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCALES = HERE.parent.parent / "piscout" / "static" / "locales"
OUT = HERE / "generated"

# locale code -> Inno Setup's bundled language file
BUNDLED = {
    "ar": "Arabic", "hy": "Armenian", "pt-br": "BrazilianPortuguese", "bg": "Bulgarian", "ca": "Catalan",
    "co": "Corsican", "cs": "Czech", "da": "Danish", "nl": "Dutch", "fi": "Finnish", "fr": "French",
    "de": "German", "he": "Hebrew", "hu": "Hungarian", "it": "Italian", "ja": "Japanese", "ko": "Korean",
    "no": "Norwegian", "nb": "Norwegian", "pl": "Polish", "pt": "Portuguese", "ru": "Russian", "sk": "Slovak",
    "sl": "Slovenian", "es": "Spanish", "sv": "Swedish", "ta": "Tamil", "th": "Thai", "tr": "Turkish",
    "uk": "Ukrainian",
}
PREFERRED = {"pt": 0x0816, "pt-br": 0x0416, "ja": 0x0411, "zh": 0x0404, "zh-tw": 0x0404, "zh-cn": 0x0804, "en": 0x0409, "no": 0x0414, "nb": 0x0414}


def lcid(code):
    """Windows language id for a locale code like ja, pt-br, zh-cn (None if unknown)."""
    code = code.lower()
    if code in PREFERRED:
        return PREFERRED[code]
    want = code.replace("-", "_")
    for key in sorted(locale.windows_locale):
        name = locale.windows_locale[key].lower()
        if name == want or ("_" not in want and name.split("_")[0] == want):
            return key
    return None


def esc(text):
    """Texts use Inno's own syntax (%1, %n, [name]); a real line break becomes %n."""
    return str(text).replace("\r", "").replace("\n", "%n")


def load_locales():
    found = {}
    for path in sorted(LOCALES.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            found[path.stem.lower()] = data
    return found


def isl_text(code, data):
    inst = data.get("installer") or {}
    lines = []
    if code not in BUNDLED and code != "en":
        lines += ["[LangOptions]", f"LanguageName={esc(data.get('name') or code)}"]
        ident = lcid(code)
        if ident:
            lines.append(f"LanguageID=${ident:04X}")
        lines.append("LanguageCodePage=0")
    messages = {k: v for k, v in (inst.get("messages") or {}).items() if v}
    if messages:
        lines += ["", "[Messages]"] + [f"{k}={esc(v)}" for k, v in messages.items()]
    custom = {k: v for k, v in (inst.get("custom") or {}).items() if v}
    lines += ["", "[CustomMessages]"] + [f"{k}={esc(v)}" for k, v in custom.items()]
    return "\r\n".join(lines) + "\r\n"


def generate():
    """Write generated/<code>.isl and generated/languages.iss; return the language codes."""
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*"):
        old.unlink()
    entries, codes = [], []
    for code, data in load_locales().items():
        # no installer texts and no bundled Inno translation: it would only be English, so leave it out
        if not data.get("installer") and code not in BUNDLED:
            continue
        (OUT / f"{code}.isl").write_text(isl_text(code, data), encoding="utf-8-sig")
        base = "compiler:Languages\\" + BUNDLED[code] + ".isl" if code in BUNDLED else "compiler:Default.isl"
        entries.append(f'Name: "{code.replace("-", "_")}"; MessagesFile: "{base},generated\\{code}.isl"')
        codes.append(code)
    (OUT / "languages.iss").write_text("\r\n".join(entries) + "\r\n", encoding="utf-8")
    return codes


def find_iscc(given):
    candidates = [given] if given else []
    for var, sub in (("LOCALAPPDATA", "Programs"), ("ProgramFiles(x86)", ""), ("ProgramFiles", "")):
        base = os.environ.get(var)
        if base:
            candidates.append(os.path.join(base, sub, "Inno Setup 6", "ISCC.exe"))
    return next((c for c in candidates if c and os.path.exists(c)), None)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="0.0.0")
    ap.add_argument("--iscc")
    ap.add_argument("--no-compile", action="store_true", help="only write the generated language files")
    args = ap.parse_args(argv)
    codes = generate()
    print("installer languages:", ", ".join(codes))
    if args.no_compile:
        return 0
    iscc = find_iscc(args.iscc)
    if not iscc:
        print("ISCC.exe (Inno Setup 6) not found; pass --iscc")
        return 1
    return subprocess.call([iscc, f"/DMyAppVersion={args.version.lstrip('v')}", str(HERE / "piscout.iss")])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
