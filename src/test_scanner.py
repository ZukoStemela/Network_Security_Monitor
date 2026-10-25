
import subprocess

from scanner import (
    get_mac_address,
    is_host_alive,
    scan_network,
)


def test_scan_network_returns_active_hosts(monkeypatch):
    monkeypatch.setattr("scanner.is_host_alive", lambda ip: True)
    monkeypatch.setattr(
        "scanner.get_mac_address",
        lambda ip: "aa:bb:cc:dd:ee:ff",
    )

    hosts = scan_network("192.168.1.0/30", "192.168.1.1")

    assert len(hosts) == 2
    assert hosts[0].get_info()["ip_address"] == "192.168.1.1"
    assert hosts[0].get_info()["is_gateway"] is True
    assert hosts[1].get_info()["is_gateway"] is False


def test_scan_network_returns_empty_for_invalid_limit():
    assert scan_network("192.168.1.0/24", "192.168.1.1", 0) == []


def test_scan_network_respects_max_hosts(monkeypatch):
    monkeypatch.setattr("scanner.is_host_alive", lambda ip: True)
    monkeypatch.setattr("scanner.get_mac_address", lambda ip: None)

    hosts = scan_network("192.168.1.0/24", "192.168.1.1", 2)

    assert len(hosts) == 2


def test_scan_network_rejects_invalid_network():
    assert scan_network("invalid-network", "192.168.1.1") == []


def test_scan_network_rejects_invalid_max_hosts():
    assert scan_network("192.168.1.0/24", "192.168.1.1", "5") == []
    assert scan_network("192.168.1.0/24", "192.168.1.1", True) == []


def test_scan_network_rejects_invalid_limits():
    assert scan_network("192.168.1.0/24", "192.168.1.1", 0) == []
    assert scan_network("192.168.1.0/24", "192.168.1.1", 257) == []


def test_scan_network_rejects_invalid_networks():
    assert scan_network("", "192.168.1.1") == []
    assert scan_network("not-a-network", "192.168.1.1") == []
    assert scan_network(None, "192.168.1.1") == []


def test_scan_network_ignores_unreachable_hosts(monkeypatch):
    monkeypatch.setattr("scanner.is_host_alive", lambda ip: False)

    assert scan_network("192.168.1.0/30", "192.168.1.1") == []


def test_scan_network_stops_at_max_hosts(monkeypatch):
    monkeypatch.setattr("scanner.is_host_alive", lambda ip: True)
    monkeypatch.setattr("scanner.get_mac_address", lambda ip: None)

    hosts = scan_network("192.168.1.0/24", "192.168.1.1", max_hosts=2)

    assert len(hosts) == 2


def test_is_host_alive_windows(monkeypatch):
    monkeypatch.setattr("scanner.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0], returncode=0
        ),
    )

    assert is_host_alive("192.168.1.10") is True


def test_is_host_alive_linux(monkeypatch):
    monkeypatch.setattr("scanner.platform.system", lambda: "Linux")
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0], returncode=1
        ),
    )

    assert is_host_alive("192.168.1.10") is False


def test_is_host_alive_handles_command_errors(monkeypatch):
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError()),
    )

    assert is_host_alive("192.168.1.10") is False


def test_is_host_alive_handles_timeout(monkeypatch):
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.TimeoutExpired("ping", 3)
        ),
    )

    assert is_host_alive("192.168.1.10") is False


def test_get_mac_address_windows(monkeypatch):
    monkeypatch.setattr("scanner.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="  192.168.1.10  AA-BB-CC-DD-EE-FF  dynamic",
            stderr="",
        ),
    )

    assert get_mac_address("192.168.1.10") == "aa:bb:cc:dd:ee:ff"


def test_get_mac_address_linux(monkeypatch):
    monkeypatch.setattr("scanner.platform.system", lambda: "Linux")
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="192.168.1.10 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE",
            stderr="",
        ),
    )

    assert get_mac_address("192.168.1.10") == "aa:bb:cc:dd:ee:ff"


def test_get_mac_address_rejects_invalid_mac(monkeypatch):
    monkeypatch.setattr("scanner.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="  192.168.1.10  invalid-mac",
            stderr="",
        ),
    )

    assert get_mac_address("192.168.1.10") is None


def test_get_mac_address_returns_none_when_missing(monkeypatch):
    monkeypatch.setattr("scanner.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0], returncode=0, stdout="", stderr=""
        ),
    )

    assert get_mac_address("192.168.1.10") is None


def test_get_mac_address_handles_command_error(monkeypatch):
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError()),
    )

    assert get_mac_address("192.168.1.10") is None


def test_get_mac_address_handles_timeout(monkeypatch):
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.TimeoutExpired("arp", 3)
        ),
    )

    assert get_mac_address("192.168.1.10") is None


def test_get_mac_address_rejects_invalid_windows_mac(monkeypatch):
    monkeypatch.setattr("scanner.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="  192.168.1.10  invalid-mac",
            stderr="",
        ),
    )

    assert get_mac_address("192.168.1.10") is None


def test_get_mac_address_rejects_invalid_linux_mac(monkeypatch):
    monkeypatch.setattr("scanner.platform.system", lambda: "Linux")
    monkeypatch.setattr(
        "scanner.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="192.168.1.10 dev eth0 lladdr invalid-mac REACHABLE",
            stderr="",
        ),
    )

    assert get_mac_address("192.168.1.10") is None
