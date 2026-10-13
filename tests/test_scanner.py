from piscout.scanner import PI_OUIS, normalize_mac, parse_arp

WINDOWS = """
Interface: 192.168.1.20 --- 0x7
  Internet Address      Physical Address      Type
  192.168.1.1           a4-2b-b0-11-22-33     dynamic
  192.168.1.37          dc-a6-32-0a-bc-de     dynamic
  192.168.1.255         ff-ff-ff-ff-ff-ff     static
  224.0.0.22            01-00-5e-00-00-16     static
"""

LINUX = """
? (192.168.1.1) at a4:2b:b0:11:22:33 [ether] on eth0
raspberrypi.lan (192.168.1.37) at dc:a6:32:0a:bc:de [ether] on eth0
? (192.168.1.50) at <incomplete> on eth0
"""

MACOS = "? (192.168.1.37) at dc:a6:32:a:bc:de on en0 ifscope [ethernet]"


def test_parse_windows():
    t = parse_arp(WINDOWS)
    assert t == {
        "192.168.1.1": "a4:2b:b0:11:22:33",
        "192.168.1.37": "dc:a6:32:0a:bc:de",
    }


def test_parse_linux_skips_incomplete():
    t = parse_arp(LINUX)
    assert set(t) == {"192.168.1.1", "192.168.1.37"}


def test_parse_macos_short_octet():
    assert parse_arp(MACOS)["192.168.1.37"] == "dc:a6:32:0a:bc:de"


def test_pi_detected_by_oui():
    mac = parse_arp(LINUX)["192.168.1.37"]
    assert mac[:8] in PI_OUIS
    assert normalize_mac("B8-27-EB-1-2-3") == "b8:27:eb:01:02:03"
