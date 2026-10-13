# How the demo GIF and screenshots were made

The GIF and screenshots in the README use a **simulated device**, not a real Raspberry Pi.
Every frame says so (orange DEMO banner or a caption).

- `PISCOUT_DEMO=1` makes `/api/scan` return one fake Pi (`127.0.0.1`) instead of scanning the network, and shows the orange DEMO banner.
- `tools/demo_shell.py` is a tiny SSH server on `127.0.0.1:22` that answers a few canned commands (login `pi` / `raspberry`).
- The Flash OS screenshot uses real data: the OS list and recommendation come from the official Raspberry Pi image list.

Reproduce:

```bash
python tools/demo_shell.py            # terminal 1 (port 22 on localhost)
set PISCOUT_DEMO=1                    # terminal 2 (PowerShell: $env:PISCOUT_DEMO="1")
python -m piscout --port 8000
```

Then open http://127.0.0.1:8000 and connect to the demo Pi.
