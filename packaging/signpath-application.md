# Code signing application notes (SignPath Foundation, free for open source)

Apply at https://signpath.org/ (Foundation program). Account creation and the application are done by the
project owner. This page collects the facts they usually ask for.

| Question | Answer |
|---|---|
| Project name | piscout |
| Repository | https://github.com/MilkteaTW1/piscout |
| License | MIT (OSI approved) |
| What it does | Windows tool to discover, SSH into, view the desktop of and flash Raspberry Pis |
| Maintainer | MilkteaTW1 |
| Build system | GitHub Actions (`.github/workflows/release.yml`), built from the tagged commit on `windows-latest` |
| Artifacts to sign | `piscout.exe` (PyInstaller one-file build) |
| Reproducible from source | `pip install -r requirements.txt pyinstaller` then `build.bat` |
| Third-party code | xterm.js (MIT), noVNC (MPL-2.0), listed in `THIRD_PARTY_NOTICES.md` |
| Telemetry / data collection | None (see `docs/PRIVACY.md`) |
| Release page | https://github.com/MilkteaTW1/piscout/releases |

## Things to be aware of
- PyInstaller executables are frequently flagged by antivirus heuristics; keep releases built by CI only.
- Signing removes the "unknown publisher" label, but SmartScreen reputation still builds up with downloads.
- After approval the workflow needs a signing step (SignPath GitHub Action) before publishing the release.
