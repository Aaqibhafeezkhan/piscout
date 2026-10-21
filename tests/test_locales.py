import http.client
import importlib.util
import json
import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn

from piscout import app as appmod, i18n

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("i18n_check", ROOT / "tools" / "i18n_check.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def test_every_shipped_locale_is_valid():
    en = checker.load(checker.LOCALES / "en.json")
    files = sorted(checker.LOCALES.glob("*.json"))
    assert files, "no locale files found"
    for path in files:
        errors, _ = checker.check(path.stem, checker.load(path), en)
        assert errors == [], errors


def test_checker_catches_bad_placeholders_and_rx_groups():
    en = checker.load(checker.LOCALES / "en.json")
    bad = checker.skeleton("Bad", en)
    zh = next(k for k in en["backend"] if "{e}" in k)
    bad["backend"][zh] = "no placeholder here"
    rx = bad["ui"]["rx"][3]            # "磁碟 (\d+)" 只有一個群組
    rx["replace"] = "Disk $1 and $2"
    errors, _ = checker.check("bad", bad, en)
    assert any("placeholders differ" in e for e in errors)
    assert any("group 2" in e for e in errors)
    unnamed = checker.skeleton("", en)
    assert any('"name" is required' in e for e in checker.check("x", unnamed, en)[0])


@pytest.fixture
def fake_ja(monkeypatch):
    ja = {"name": "日本語", "ui": {}, "backend": {
        "請設定密碼": "パスワードを設定してください",
        "下載失敗：{e}": "ダウンロード失敗: {e}",
        "連不上 {host}：{e}": "壞れた {oops}",           # 變數寫錯
    }}
    monkeypatch.setitem(i18n.LOCALES, "ja", ja)
    yield
    i18n.set_lang("zh")


def test_new_language_is_picked_up_with_english_fallback(fake_ja):
    assert i18n.resolve("ja-JP,ja;q=0.9") == "ja"
    assert i18n.resolve("xx") == "en"                  # 沒有的語言用英文
    assert i18n.resolve("") == "zh"
    assert i18n.resolve("zh-HK") == "zh"
    assert {"code": "ja", "name": "日本語"} in i18n.languages()
    i18n.set_lang("ja")
    assert i18n.tr("請設定密碼") == "パスワードを設定してください"
    assert i18n.tr("下載失敗：{e}", e="x") == "ダウンロード失敗: x"
    # 這個語言沒翻的句子，先用英文
    assert i18n.tr("沒有這個工作") == "No such job"
    # 翻譯檔把變數寫錯，不能讓請求出錯：退回中文原文
    assert i18n.tr("連不上 {host}：{e}", host="h", e="e") == "連不上 h：e"


def test_region_specific_locale_beats_generic_chinese(monkeypatch):
    monkeypatch.setitem(i18n.LOCALES, "zh-cn", {"name": "简体中文", "backend": {}})
    assert i18n.resolve("zh-CN") == "zh-cn"
    assert i18n.resolve("zh-TW") == "zh"


def test_broken_locale_file_is_skipped(tmp_path):
    (tmp_path / "ok.json").write_text(json.dumps({"name": "Ok"}), encoding="utf-8")
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    (tmp_path / "list.json").write_text("[1, 2]", encoding="utf-8")
    assert list(i18n.load_locales(tmp_path)) == ["ok"]


@pytest.fixture(scope="module")
def server():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    srv = uvicorn.Server(uvicorn.Config(appmod.app, host="127.0.0.1", port=port, log_config=None))
    threading.Thread(target=srv.run, daemon=True).start()
    while not srv.started:
        time.sleep(0.05)
    yield port
    srv.should_exit = True


def test_i18n_data_script_lists_locales(server):
    conn = http.client.HTTPConnection("127.0.0.1", server, timeout=10)
    conn.request("GET", "/i18n-data.js")
    r = conn.getresponse()
    body = r.read().decode("utf-8")
    conn.close()
    assert r.status == 200 and "javascript" in r.getheader("Content-Type")
    assert body.startswith("window.PISCOUT_LOCALES = ")
    data = json.loads(body[len("window.PISCOUT_LOCALES = "):-1])
    assert data["en"]["name"] == "English"
    assert data["en"]["ui"]["exact"]["連線"] == "Connect"
    assert "backend" not in data["en"]              # 後端訊息不用送給前端
