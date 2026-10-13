# Third-party notices

piscout bundles these front-end libraries under `piscout/static/vendor/`.
Each keeps its own license file next to the code.

| Library | Version | License | Used for |
|---|---|---|---|
| [xterm.js](https://github.com/xtermjs/xterm.js) | 5.5.0 | MIT | built-in SSH terminal |
| [@xterm/addon-fit](https://github.com/xtermjs/xterm.js) | 0.10.0 | MIT | terminal auto-resize |
| [noVNC](https://github.com/novnc/noVNC) | 1.5.0 | MPL-2.0 (core), see its LICENSE.txt | remote desktop viewer |

Python dependencies (FastAPI, uvicorn, websockets, paramiko, zeroconf, passlib,
pyfatfs, pywebview) are installed from PyPI and are not redistributed in this repository.
