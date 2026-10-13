# piscout

> Raspberry Pi LAN manager for Windows: auto-discovery, built-in SSH terminal, remote desktop, and remote re-imaging.

`raspberry-pi` `raspberry-pi-os` `network-scanner` `lan-discovery` `fleet-management`
`ssh-terminal` `remote-desktop` `vnc` `sd-card` `flasher` `imager` `netboot` `pxe`
`mdns` `fastapi` `pywebview` `windows` `desktop-app`

Managing a few Raspberry Pis usually means digging IPs out of the router, opening SSH
windows and pulling SD cards to re-flash them. piscout puts all of that in one window:

- **Auto-discovery** – scans the LAN on launch and recognizes Raspberry Pis
- **Built-in terminal** – click *Connect*, enter the login, and get an SSH terminal inside the app
- **Remote desktop** – view and control the Pi's desktop through the SSH tunnel
- **Remote re-imaging** – write a new OS to the Pi's own SD card without taking it out, with a recommended OS for the model
- **Local flashing** – or flash an SD card inserted into this computer
- **Overview and batch actions** – temperature / load / memory of every Pi at a glance; reboot, shut down or update several at once
- **Saved logins** – encrypted with Windows DPAPI; the model is detected automatically
- **Bilingual UI** – follows the system language (中文 / English), switchable at any time
- All OS images come from the official Raspberry Pi website and are verified with SHA-256

It is an early version. Scanning, the terminal, the overview and agent stats are tested
on real hardware; remote desktop, remote re-imaging and local flashing still need more
real-device validation (see below).

## Usage

Download `piscout.exe` from [Releases](../../releases) (or build it yourself, see below) and run it. Windows will ask for administrator rights because
writing to disks requires it. The file is not code-signed, so SmartScreen may warn you
("More info → Run anyway").

**Remote re-imaging requires a Pi that still boots and has SSH enabled.** A completely
blank SD card cannot be seen on the network by any software; flash it once from this
computer, after which it can be re-imaged remotely.

How remote re-imaging works:

1. The PC downloads the official image and writes the boot settings straight into the image's boot partition while decompressing
2. `dd`, `dash` and `sha256sum` (with their libraries) are copied into the Pi's RAM (`/dev/shm`), so nothing depends on the SD card that is about to be overwritten
3. The image is streamed over SSH to the boot disk
4. The first part is read back and hashed; **the Pi only reboots if it matches**

> Overwriting the disk of a running system is inherently risky. If power or the network
> drops mid-write, the card will not boot and must be re-flashed from a computer.

## Run from source

Requires Python 3.9+, Windows 10/11 (WebView2 is built in on Windows 11).

```bash
git clone https://github.com/<your-account>/piscout.git
cd piscout
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_gui.py
```

Build an exe: `pip install pyinstaller` then `build.bat`. Run tests: `pytest`.

## How it differs from other tools

| Tool | Discovery | Terminal | Remote desktop | Flash | Re-image without removing the card |
|---|---|---|---|---|---|
| [Raspberry Pi Imager](https://github.com/raspberrypi/rpi-imager) | | | | local SD card | |
| Angry IP Scanner / nmap scripts | IP list only | | | | |
| Raspberry Pi Connect | | | cloud, account needed | | |
| **piscout** | ✓ | ✓ | ✓ | ✓ | ✓ |

piscout does not replace Imager. Imager writes an image to a card; piscout handles what
comes after the card is already in the Pi: find it, log in, see its screen, change its OS.

## FAQ

**How do I find the IP address of a Raspberry Pi on my network from Windows?**
Open piscout; it scans your /24 on launch and flags Raspberry Pis by MAC prefix and mDNS name.

**Can I get an SSH terminal and a remote desktop for my Pi in one app?**
Yes. After logging in, the terminal (xterm.js) and the desktop (noVNC over an SSH tunnel) are tabs in the same window. The desktop needs Raspberry Pi OS with the Wayland desktop (wayvnc); Lite has no desktop.

**Can I reinstall Raspberry Pi OS without taking the SD card out?**
Yes, if the Pi still boots and SSH is enabled: piscout streams the official image over SSH to the Pi's own boot disk and verifies it before rebooting. It cannot help a blank card that has never booted; flash that one once from your computer.

**How does it choose which OS to install?**
It reads the model (from `/proc/device-tree/model` after login) and picks the matching official image: the 64-bit desktop edition for Pi 3 and newer, the 32-bit edition for older boards, or the Lite edition if you choose a terminal-only setup. It refuses an image the board cannot run.

**Is it a replacement for Raspberry Pi Imager?**
No. Use Imager to write a card in your computer. piscout is for managing Pis that are already on the network, and also includes a local flasher for convenience.

**Does it work on Linux or macOS?**
Not yet; the app and the local flasher target Windows. The scanner, terminal and remote-flash modules are plain Python and could be ported.

**Is it safe to expose?**
It binds to `127.0.0.1` only. Do not publish its port. See the security notes above.

## Security notes

- The UI service binds to `127.0.0.1` only; API calls need a per-launch random token, and terminal/desktop sessions use one-time tokens
- Passwords are stored with Windows DPAPI (bound to your Windows account and PC)
- SSH host keys are accepted on first use (`AutoAddPolicy`); harden this if you use it beyond a home LAN
- Remote desktop starts an unauthenticated VNC bound to `127.0.0.1` on the Pi, reachable only through the SSH tunnel, and stops it when the session closes
- Boot-settings passwords are stored hashed; the Wi-Fi password is plain text in the boot partition (format limitation)
- Only private IPs are accepted; images are only downloaded from Raspberry Pi domains
- Only scan networks you own

## Status and roadmap

Tested: LAN scan and Pi detection, built-in terminal, overview via agent, image pre-processing and boot-settings injection, the Pi-side write script's flow and verification (simulated locally), unit tests.

**Not yet verified on real hardware:** the actual remote write, remote desktop, local SD flashing.

- [ ] Validate the three items above on real devices and publish the results per model
- [ ] Network install (netboot) for blank cards: works out of the box on Pi 3B+, needs a one-time bootloader change on Pi 4/5
- [ ] Remote desktop for X11 / RealVNC systems
- [ ] SSH host-key pinning
- [ ] Linux / macOS local flashing
