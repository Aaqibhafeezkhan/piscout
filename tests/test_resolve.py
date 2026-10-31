import asyncio
import socket

import pytest
from fastapi import HTTPException

from piscout import app as app_module


def _resolve(name):
    return asyncio.run(app_module.api_resolve(name))


def _fake_dns(answers):
    def getaddrinfo(host, port, family=0, type=0, *a):
        if host not in answers:
            raise socket.gaierror("not found")
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (answers[host], port))]
    return getaddrinfo


def test_private_ip_is_accepted_as_is():
    assert _resolve(" 192.168.1.20 ") == {"ip": "192.168.1.20"}


def test_hostname_is_resolved_to_its_private_ip(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _fake_dns({"raspberrypi.local": "192.168.1.31"}))
    assert _resolve("raspberrypi.local") == {"ip": "192.168.1.31"}


def test_public_ip_is_refused():
    with pytest.raises(HTTPException) as e:
        _resolve("8.8.8.8")
    assert e.value.status_code == 400


def test_name_that_resolves_to_a_public_address_is_refused(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _fake_dns({"example.com": "93.184.216.34"}))
    with pytest.raises(HTTPException) as e:
        _resolve("example.com")
    assert e.value.status_code == 400


def test_unknown_name_says_what_to_check(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _fake_dns({}))
    with pytest.raises(HTTPException) as e:
        _resolve("nope.local")
    assert e.value.status_code == 404
    assert "nope.local" in e.value.detail


def test_empty_name_is_refused():
    with pytest.raises(HTTPException) as e:
        _resolve("   ")
    assert e.value.status_code == 400
