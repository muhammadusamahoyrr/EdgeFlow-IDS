"""ARP watcher: parsing tcpdump lines and the alert rules."""
import pytest

from arp_watch import PROTECTED, ArpState, parse_line, parse_protect

ROUTER_IP, ROUTER_MAC = next(iter(PROTECTED.items()))
ATTACKER = "dc:a6:32:dc:27:d5"


def reply(ip, mac, ts="1.0", src="aa:aa:aa:aa:aa:aa"):
    return (f"{ts} {src} > bb:bb:bb:bb:bb:bb, ethertype ARP (0x0806), length 42: "
            f"Reply {ip} is-at {mac}, length 28")


def request(tell, src_mac, who="192.168.137.50", ts="2.0", target=""):
    target = f" ({target})" if target else ""
    return (f"{ts} {src_mac} > ff:ff:ff:ff:ff:ff, ethertype ARP (0x0806), length 60: "
            f"Request who-has {who}{target} tell {tell}, length 46")


def test_reply_binding():
    assert parse_line(reply("192.168.137.9", "AA:BB:CC:DD:EE:FF")) == \
        (1.0, "192.168.137.9", "aa:bb:cc:dd:ee:ff")


def test_request_announces_its_sender():
    line = request("192.168.137.100", "00:17:88:60:d6:4f", target="28:6d:97:9e:f4:d5")
    assert parse_line(line) == (2.0, "192.168.137.100", "00:17:88:60:d6:4f")


def test_probe_announces_nothing():
    assert parse_line(request("0.0.0.0", "00:17:88:60:d6:4f")) is None


def test_replies_only_ignores_requests():
    assert parse_line(request("192.168.137.100", "00:17:88:60:d6:4f"), replies_only=True) is None
    assert parse_line(reply("192.168.137.9", "aa:bb:cc:dd:ee:ff"), replies_only=True) is not None


def test_other_lines_ignored():
    assert parse_line("1.0 aa:aa:aa:aa:aa:aa > bb:bb:bb:bb:bb:bb, ethertype IPv4, length 60") is None


def test_spoofed_router_reply_is_high():
    alerts = ArpState().check(*parse_line(reply(ROUTER_IP, ATTACKER))[1:])
    assert ("gateway_ip_spoof", "high", ATTACKER, [ROUTER_IP, ROUTER_MAC]) in alerts


def test_forged_request_from_router_ip_is_high():
    # A request claiming to come from the router poisons the caches of every host that hears it.
    alerts = ArpState().check(*parse_line(request(ROUTER_IP, ATTACKER))[1:])
    assert [a[:2] for a in alerts] == [("gateway_ip_spoof", "high")]


def test_router_itself_raises_nothing():
    state = ArpState()
    assert state.check(ROUTER_IP, ROUTER_MAC) == []
    assert state.check(*parse_line(request(ROUTER_IP, ROUTER_MAC))[1:]) == []


def test_alerts_are_not_repeated():
    state = ArpState()
    assert state.check(ROUTER_IP, ATTACKER)
    assert state.check(ROUTER_IP, ATTACKER) == []


def test_info_rules():
    state = ArpState()
    state.check("192.168.137.5", "11:11:11:11:11:11")
    kinds = {a[0] for a in state.check("192.168.137.5", "22:22:22:22:22:22")}
    assert kinds == {"ip_rebound_to_new_mac"}
    kinds = {a[0] for a in state.check("192.168.137.6", "22:22:22:22:22:22")}
    assert kinds == {"mac_claims_multiple_ips"}


def test_parse_protect():
    assert parse_protect(None) == PROTECTED
    assert parse_protect(["10.0.0.1=AA:BB:CC:DD:EE:FF"]) == {"10.0.0.1": "aa:bb:cc:dd:ee:ff"}
    for bad in ["10.0.0.1", "10.0.0.1=zz:bb:cc:dd:ee:ff", "router=aa:bb:cc:dd:ee:ff"]:
        with pytest.raises(ValueError):
            parse_protect([bad])
