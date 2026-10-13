import hashlib
import lzma
import struct

import pytest

pytest.importorskip("pyfatfs")

from pyfatfs.PyFat import PyFat
from pyfatfs.PyFatFS import PyFatFS

from piscout import remoteflash
from piscout.flasher import CHUNK, FlashError

PART_START = 8192  # 磁區，跟官方映像一樣放在 4 MiB 處
FAT_SIZE = 64 * 1024 * 1024
TAIL = 9 * 1024 * 1024 + 512 * 3  # 故意不是 4 MiB 的倍數


def make_image(tmp_path):
    """做一個小的假映像：MBR + FAT32 開機分割區（內含舊的 user-data）+ 後面一堆資料。"""
    fat = tmp_path / "fat.img"
    with open(fat, "wb") as f:
        f.truncate(FAT_SIZE)
    pf = PyFat()
    pf.mkfs(str(fat), PyFat.FAT_TYPE_FAT32, size=FAT_SIZE, label="bootfs")
    pf.close()
    fs = PyFatFS(str(fat))
    fs.writetext("user-data", "# 舊的內容\n")
    fs.writetext("cmdline.txt", "console=serial0,115200\n")
    fs.close()

    mbr = bytearray(512)
    mbr[0x1BE + 4] = 0x0C
    struct.pack_into("<II", mbr, 0x1BE + 8, PART_START, FAT_SIZE // 512)
    mbr[510:512] = b"\x55\xaa"
    raw = bytes(mbr) + b"\0" * (PART_START * 512 - 512) + fat.read_bytes()
    raw += bytes((i * 7) % 251 for i in range(1000)) * (TAIL // 1000) + b"z" * (TAIL % 1000)
    xz = tmp_path / "img.xz"
    xz.write_bytes(lzma.compress(raw))
    return xz, raw


def run(tmp_path, files):
    xz, raw = make_image(tmp_path)
    work = tmp_path / "work"
    work.mkdir()
    sha = hashlib.sha256(raw).hexdigest()
    prepared = remoteflash.prepare_image(
        xz, len(raw), sha, files, work, lambda *a: None
    )
    stream = b"".join(remoteflash.stream_image(xz, prepared))
    return raw, prepared, stream


def test_stream_has_config_and_rest_untouched(tmp_path):
    files = {"user-data": "#cloud-config\nhostname: mypi\n", "network-config": "x: 1\n"}
    raw, prepared, stream = run(tmp_path, files)

    assert len(stream) == len(raw)
    head_len = prepared["head_len"]
    assert stream[head_len:] == raw[head_len:]  # 後段原封不動
    assert stream[:head_len] != raw[:head_len]  # 前段被寫入設定

    out = tmp_path / "out.img"
    out.write_bytes(stream)
    fs = PyFatFS(str(out), offset=PART_START * 512, read_only=True)
    try:
        assert fs.readtext("user-data") == files["user-data"]  # 舊的被覆蓋
        assert fs.readtext("network-config") == files["network-config"]
        assert fs.readtext("cmdline.txt").startswith("console=")  # 原本的檔案還在
    finally:
        fs.close()


def test_prefix_hash_matches_stream(tmp_path):
    _, prepared, stream = run(tmp_path, {"user-data": "a\n"})
    n = prepared["prefix_len"]
    assert n % CHUNK == 0 and n > 0
    assert hashlib.sha256(stream[:n]).hexdigest() == prepared["prefix_sha"]


def test_bad_source_checksum_rejected(tmp_path):
    xz, raw = make_image(tmp_path)
    work = tmp_path / "w"
    work.mkdir()
    with pytest.raises(FlashError):
        remoteflash.prepare_image(xz, len(raw), "0" * 64, {"a": "b"}, work, lambda *a: None)


def test_non_mbr_rejected():
    with pytest.raises(FlashError):
        remoteflash._partition1(b"\0" * 512)


def test_interpret_output():
    remoteflash._interpret("READY\nDD 0\nSUM abc\nOK\n")
    with pytest.raises(FlashError):
        remoteflash._interpret("DD 0\nSUM abc\nMISMATCH\n")
    with pytest.raises(FlashError):
        remoteflash._interpret("DD 1\nLOG dd: failed\nFAIL\n")
