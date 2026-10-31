"""Draws how much of the UI each language covers, as docs/i18n-status.svg (shown in the README).

  python tools/i18n_status.py

Uses the same counting as tools/i18n_check.py. Run it after a locale changes and commit the new image.
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n_check as chk  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "docs" / "i18n-status.svg"
ROW, LABEL, BAR, WIDTH = 30, 150, 300, 640


def stats():
    en = chk.load(chk.LOCALES / "en.json")
    total = len(en["ui"].get("exact", {})) + len(en["ui"].get("sub", [])) + len(en["ui"].get("rx", [])) + len(en["backend"])
    rows = []
    for path in sorted(chk.LOCALES.glob("*.json")):
        data = chk.load(path)
        if path.stem in ("zh", "en"):      # zh is the source text, en has every sentence
            done = total
        else:
            _, missing = chk.check(path.stem, data, en)
            done = total - min(missing, total)
        rows.append((str(data.get("name") or path.stem), path.stem, done))
    rows.sort(key=lambda r: (-r[2], r[1]))
    return rows, total


def svg(rows, total):
    height = 20 + ROW * len(rows) + 10
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="Translation status">',
        "<style>",
        ".t{font:14px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#24292f}.m{fill:#57606a;font-size:12px}",
        ".bg{fill:#eaeef2}.fg{fill:#2da44e}",
        "@media (prefers-color-scheme: dark){.t{fill:#e6edf3}.m{fill:#9198a1}.bg{fill:#30363d}.fg{fill:#3fb950}}",
        "</style>",
    ]
    for i, (name, code, done) in enumerate(rows):
        y = 20 + i * ROW
        share = done / total
        out.append(f'<text class="t" x="0" y="{y + 14}">{escape(name)} <tspan class="m">{escape(code)}</tspan></text>')
        out.append(f'<rect class="bg" x="{LABEL}" y="{y + 3}" width="{BAR}" height="14" rx="7"/>')
        if done:
            out.append(f'<rect class="fg" x="{LABEL}" y="{y + 3}" width="{max(14, round(BAR * share))}" height="14" rx="7"/>')
        out.append(f'<text class="m" x="{LABEL + BAR + 12}" y="{y + 14}">{done}/{total} ({round(share * 100)}%)</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    rows, total = stats()
    OUT.write_text(svg(rows, total), encoding="utf-8")
    print(f"wrote {OUT} ({len(rows)} languages)")
