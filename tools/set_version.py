"""把版本號寫進 piscout/__init__.py 和 pyproject.toml（發佈流程用 tag 呼叫，程式才知道自己是哪一版）。

  python tools/set_version.py v0.1.8
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [
    (ROOT / "piscout" / "__init__.py", r'(?m)^__version__ = ".*"$', '__version__ = "{v}"'),
    (ROOT / "pyproject.toml", r'(?m)^version = ".*"$', 'version = "{v}"'),
]


def main(argv):
    m = re.fullmatch(r"v?(\d+\.\d+\.\d+)", argv[0]) if argv else None
    if not m:
        print("usage: python tools/set_version.py v1.2.3")
        return 2
    for path, pattern, line in TARGETS:
        text = path.read_text(encoding="utf-8")
        new, n = re.subn(pattern, line.format(v=m.group(1)), text, count=1)
        if n != 1:
            print(f"version line not found in {path}")
            return 1
        path.write_text(new, encoding="utf-8", newline="")
    print("version set to", m.group(1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
