
import scanner
from device import Device


def test_scan_network_returns_active_hosts(monkeypatch):
    monkeypatch.setattr(
        scanner,
        "is_host_alive",
        lambda ip: ip == "192.168.1.1",
    )
    monkeypatch.setattr(
        scanner,
        "get_mac_address",
        lambda ip: "aa:bb:cc:dd:ee:01",
    )

    devices = scanner.scan_network(
        "192.168.1.0/30",
        "192.168.1.1",
        max_hosts=2,
    )

    assert len(devices) == 1
    assert devices[0].ip_address == "192.168.1.1"
    assert devices[0].is_gateway is True
    assert devices[0].mac_address == "aa:bb:cc:dd:ee:01"


def test_scan_network_returns_empty_for_invalid_limit():
    assert scanner.scan_network("192.168.1.0/24", None, max_hosts=0) == []
    assert scanner.scan_network("192.168.1.0/24", None, max_hosts=-1) == []


def test_scan_network_respects_max_hosts(monkeypatch):
    monkeypatch.setattr(scanner, "is_host_alive", lambda ip: True)
    monkeypatch.setattr(scanner, "get_mac_address", lambda ip: None)

    devices = scanner.scan_network(
        "192.168.1.0/29",
        None,
        max_hosts=2,
    )

    assert len(devices) == 2
