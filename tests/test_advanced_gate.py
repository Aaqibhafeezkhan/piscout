import asyncio

import pytest
from fastapi import HTTPException

from piscout import app as app_module
from piscout import i18n


def _req(**kw):
    base = dict(host="192.168.0.5", username="pi", image_url="https://downloads.raspberrypi.com/x.img.xz",
                config=app_module.FlashConfig(password="pw"))
    base.update(kw)
    return app_module.RemoteFlashReq(**base)


def test_remote_flash_refused_without_risk_ack():
    i18n.set_lang("en")
    with pytest.raises(HTTPException) as e:
        asyncio.run(app_module.api_flash_remote(_req()))
    assert e.value.status_code == 400
    assert "advanced feature" in e.value.detail
    i18n.set_lang("zh")


def test_risk_ack_defaults_to_false():
    assert _req().risk_ack is False


def test_connect_errors_have_next_step():
    from piscout import remote
    i18n.set_lang("en")
    assert "SSH is not enabled" in remote.connect_error_message("192.168.0.9", ConnectionRefusedError("refused"))
    assert "timed out" in remote.connect_error_message("192.168.0.9", TimeoutError("timed out"))
    assert "closed the SSH connection" in remote.connect_error_message(
        "192.168.0.9", Exception("Error reading SSH protocol banner[WinError 10054]"))
    assert "not found" in remote.connect_error_message("192.168.0.9", OSError("[WinError 10051] unreachable"))
    i18n.set_lang("zh")
