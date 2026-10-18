import hashlib
import lzma

import pytest

from piscout import flasher


def _make_xz(tmp_path, size):
    raw = (b"piscout-test-" * 1000)[:1000] * (size // 1000)
    raw += b"x" * (size - len(raw))
    p = tmp_path / "img.xz"
    p.write_bytes(lzma.compress(raw))
    return p, raw


def _cfg(**kw):
    base = dict(
        hostname="mypi", username="pi", password="secret1", wifi_ssid="",
        wifi_password="", wifi_country="TW", timezone="Asia/Taipei", keyboard="us",
    )
    base.update(kw)
    return base


def test_write_and_verify(tmp_path):
    src, raw = _make_xz(tmp_path, 5 * 1024 * 1024 + 123)  # 故意不對齊磁區
    target = tmp_path / "disk.bin"
    target.write_bytes(b"\xff" * len(raw))
    sha = hashlib.sha256(raw).hexdigest()

    seen = []
    n = flasher.write_image(
        src, target, sha, len(raw), lambda p, d, t: seen.append(p), verify=True
    )
    assert n == len(raw)
    assert target.read_bytes()[: len(raw)] == raw
    assert "verify" in seen


def test_bad_readback_reports_location(tmp_path, monkeypatch):
    src, raw = _make_xz(tmp_path, 9 * 1024 * 1024)
    target = tmp_path / "disk.bin"
    target.write_bytes(b"\0" * len(raw))
    sha = hashlib.sha256(raw).hexdigest()
    real_fsync = flasher.os.fsync

    def flaky(fd):  # 模擬壞卡：寫完後第 5 MB 的內容變了
        real_fsync(fd)
        with open(target, "r+b") as f:
            f.seek(5 * 1024 * 1024)
            f.write(b"\xaa")

    monkeypatch.setattr(flasher.os, "fsync", flaky)
    with pytest.raises(flasher.FlashError) as e:
        flasher.write_image(src, target, sha, len(raw), lambda *a: None)
    assert "4 MB" in str(e.value)


def test_wrong_checksum_rejected(tmp_path):
    src, raw = _make_xz(tmp_path, 100_000)
    target = tmp_path / "disk.bin"
    target.write_bytes(b"\0" * len(raw))
    with pytest.raises(flasher.FlashError):
        flasher.write_image(src, target, "0" * 64, len(raw), lambda *a: None)


def test_cloudinit_config():
    pytest.importorskip("passlib")
    f = flasher.make_config(
        "cloudinit-rpi", _cfg(wifi_ssid="home", wifi_password="12345678")
    )
    assert set(f) == {"user-data", "network-config"}
    assert f["user-data"].startswith("#cloud-config")
    assert "hostname: mypi" in f["user-data"]
    assert "ssh_pwauth: true" in f["user-data"]
    assert "secret1" not in f["user-data"]  # 只放雜湊
    assert '"home"' in f["network-config"]


def test_systemd_config():
    pytest.importorskip("passlib")
    f = flasher.make_config("systemd", _cfg())
    assert set(f) == {"custom.toml"}
    assert "[ssh]" in f["custom.toml"] and "enabled = true" in f["custom.toml"]
    assert "[wlan]" not in f["custom.toml"]


@pytest.mark.parametrize(
    "bad",
    [
        {"hostname": "bad host"},
        {"username": "Root"},
        {"password": ""},
        {"timezone": "Asia/Taipei; rm"},
        {"wifi_ssid": "x", "wifi_password": "short"},
    ],
)
def test_validate_rejects(bad):
    with pytest.raises(flasher.FlashError):
        flasher.validate_config(_cfg(**bad))


def test_validate_ok():
    flasher.validate_config(_cfg(wifi_ssid="home", wifi_password="12345678"))
