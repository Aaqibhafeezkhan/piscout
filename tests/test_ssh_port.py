import paramiko
import pytest

from piscout import remote, vault


class _FakeClient:
    calls = []

    def set_missing_host_key_policy(self, policy):
        pass

    def connect(self, host, **kw):
        _FakeClient.calls.append((host, kw))


@pytest.fixture
def fake_ssh(monkeypatch):
    _FakeClient.calls = []
    monkeypatch.setattr(paramiko, "SSHClient", _FakeClient)
    return _FakeClient


def test_connect_defaults_to_port_22(fake_ssh):
    remote.connect("192.168.1.5", "pi", "pw")
    assert fake_ssh.calls[0][1]["port"] == 22


def test_connect_uses_the_given_port_and_key(fake_ssh):
    remote.connect("192.168.1.5", "pi", None, "C:/keys/id_ed25519", port=2222)
    kw = fake_ssh.calls[0][1]
    assert kw["port"] == 2222
    assert kw["key_filename"] == "C:/keys/id_ed25519"


def test_connect_saved_passes_port_and_key(fake_ssh):
    remote.connect_saved("192.168.1.5", {"username": "pi", "password": None,
                                         "key_path": "k", "port": 2200})
    host, kw = fake_ssh.calls[0]
    assert (host, kw["port"], kw["key_filename"], kw["username"]) == ("192.168.1.5", 2200, "k", "pi")


def test_connect_saved_without_port_uses_22(fake_ssh):
    remote.connect_saved("192.168.1.5", {"username": "pi", "password": "pw"})
    assert fake_ssh.calls[0][1]["port"] == 22


def test_vault_keeps_port_and_key_path(monkeypatch, tmp_path):
    monkeypatch.setattr(vault, "_path", lambda: tmp_path / "vault.json")
    vault.put("02:00:c0:a8:01:14", "pi", None, 2222, "C:/keys/id")
    got = vault.get("02:00:c0:a8:01:14")
    assert got["port"] == 2222 and got["key_path"] == "C:/keys/id" and got["username"] == "pi"


def test_vault_entry_saved_before_ports_existed_reads_as_22(monkeypatch, tmp_path):
    monkeypatch.setattr(vault, "_path", lambda: tmp_path / "vault.json")
    (tmp_path / "vault.json").write_text('{"aa:bb:cc:dd:ee:ff": {"username": "pi", "password": null}}', encoding="utf-8")
    got = vault.get("aa:bb:cc:dd:ee:ff")
    assert got["port"] == 22 and got["key_path"] is None
