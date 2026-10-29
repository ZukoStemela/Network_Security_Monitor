import runpy
import subprocess
from types import SimpleNamespace

import pytest

import network
import scanner


def test_scan_network_returns_active_hosts(monkeypatch):
    monkeypatch.setattr(
        scanner, "is_host_alive", lambda ip: ip == "192.168.1.1"
    )
    monkeypatch.setattr(
        scanner, "get_mac_address", lambda ip: "aa:bb:cc:dd:ee:ff"
    )

    hosts = scanner.scan_network("192.168.1.0/29", "192.168.1.1")

    assert len(hosts) == 1
    info = hosts[0].get_info()
    assert info["ip_address"] == "192.168.1.1"
    assert info["is_gateway"] is True
    assert info["mac_address"] == "aa:bb:cc:dd:ee:ff"


@pytest.mark.parametrize("limit", ["10", 1.5, None, True, False])
def test_scan_network_returns_empty_for_invalid_limit(limit):
    assert scanner.scan_network("192.168.1.0/24", "192.168.1.1", limit) == []


def test_scan_network_respects_max_hosts(monkeypatch):
    checked = []

    def fake_is_host_alive(ip):
        checked.append(ip)
        return True

    monkeypatch.setattr(scanner, "is_host_alive", fake_is_host_alive)
    monkeypatch.setattr(scanner, "get_mac_address", lambda ip: None)

    hosts = scanner.scan_network("192.168.1.0/24", "192.168.1.1", max_hosts=3)

    assert len(checked) == 3
    assert len(hosts) == 3


def test_scan_network_rejects_invalid_network():
    assert scanner.scan_network("not-a-network", "192.168.1.1") == []


@pytest.mark.parametrize("limit", [0, -1, scanner.MAX_ALLOWED_HOSTS + 1])
def test_scan_network_rejects_invalid_max_hosts(limit):
    assert scanner.scan_network("192.168.1.0/24", "192.168.1.1", limit) == []


@pytest.mark.parametrize("limit", [0, -5, 999])
def test_scan_network_rejects_invalid_limits(limit):
    assert scanner.scan_network("192.168.1.0/24", "192.168.1.1", limit) == []


@pytest.mark.parametrize(
    "network_value",
    ["", "   ", "invalid", "192.168.1.999/24"],
)
def test_scan_network_rejects_invalid_networks(network_value):
    assert scanner.scan_network(network_value, "192.168.1.1") == []


def test_scan_network_ignores_unreachable_hosts(monkeypatch):
    monkeypatch.setattr(scanner, "is_host_alive", lambda ip: False)
    monkeypatch.setattr(
        scanner,
        "get_mac_address",
        lambda ip: pytest.fail(
            "MAC lookup should not run for unreachable hosts"
        ),
    )

    assert scanner.scan_network("192.168.1.0/29", "192.168.1.1") == []


def test_scan_network_stops_at_max_hosts(monkeypatch):
    checked = []

    def fake_is_host_alive(ip):
        checked.append(ip)
        return False

    monkeypatch.setattr(scanner, "is_host_alive", fake_is_host_alive)

    scanner.scan_network("192.168.1.0/24", "192.168.1.1", max_hosts=2)

    assert len(checked) == 2


def test_is_host_alive_windows(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0),
    )

    assert scanner.is_host_alive("192.168.1.1") is True


def test_is_host_alive_linux(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0),
    )

    assert scanner.is_host_alive("192.168.1.1") is True


@pytest.mark.parametrize("system", ["Windows", "Linux"])
def test_is_host_alive_handles_command_errors(monkeypatch, system):
    monkeypatch.setattr(scanner.platform, "system", lambda: system)

    def raise_os_error(*args, **kwargs):
        raise OSError("Command unavailable")

    monkeypatch.setattr(scanner.subprocess, "run", raise_os_error)

    assert scanner.is_host_alive("192.168.1.1") is False


def test_is_host_alive_handles_timeout(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Windows")

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("ping", 3)

    monkeypatch.setattr(scanner.subprocess, "run", raise_timeout)

    assert scanner.is_host_alive("192.168.1.1") is False


def test_get_mac_address_windows(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout="192.168.1.10  AA-BB-CC-DD-EE-FF  dynamic\n"
        ),
    )

    assert scanner.get_mac_address("192.168.1.10") == "aa:bb:cc:dd:ee:ff"


def test_get_mac_address_linux(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout=(
                "192.168.1.10 dev eth0 lladdr " "aa:bb:cc:dd:ee:ff REACHABLE"
            )
        ),
    )

    assert scanner.get_mac_address("192.168.1.10") == "aa:bb:cc:dd:ee:ff"


def test_get_mac_address_rejects_invalid_mac(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout="192.168.1.10 dev eth0 lladdr invalid-mac REACHABLE"
        ),
    )

    assert scanner.get_mac_address("192.168.1.10") is None


def test_get_mac_address_returns_none_when_missing(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout=""),
    )

    assert scanner.get_mac_address("192.168.1.10") is None


def test_get_mac_address_handles_command_error(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Linux")

    def raise_os_error(*args, **kwargs):
        raise OSError("Command unavailable")

    monkeypatch.setattr(scanner.subprocess, "run", raise_os_error)

    assert scanner.get_mac_address("192.168.1.10") is None


def test_get_mac_address_handles_timeout(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Linux")

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("ip", 3)

    monkeypatch.setattr(scanner.subprocess, "run", raise_timeout)

    assert scanner.get_mac_address("192.168.1.10") is None


def test_get_mac_address_rejects_invalid_windows_mac(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout="192.168.1.10  invalid-mac dynamic\n"
        ),
    )

    assert scanner.get_mac_address("192.168.1.10") is None


def test_get_mac_address_rejects_invalid_linux_mac(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout="192.168.1.10 dev eth0 lladdr not-a-mac REACHABLE"
        ),
    )

    assert scanner.get_mac_address("192.168.1.10") is None


def test_get_mac_address_handles_linux_without_lladdr(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout="192.168.1.10 dev eth0 REACHABLE"
        ),
    )

    assert scanner.get_mac_address("192.168.1.10") is None


def test_get_mac_address_handles_linux_without_matching_entry(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout=(
                "192.168.1.10 dev eth0 lladdr " "aa:bb:cc:dd:ee:ff REACHABLE"
            )
        ),
    )

    # The current Linux implementation reads the MAC from lladdr
    # without validating the IP address in the output.
    assert scanner.get_mac_address("192.168.1.20") == "aa:bb:cc:dd:ee:ff"


def test_get_mac_address_ignores_windows_entry_for_another_ip(monkeypatch):
    monkeypatch.setattr(scanner.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        scanner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout="192.168.1.20  AA-BB-CC-DD-EE-FF dynamic\n"
        ),
    )

    assert scanner.get_mac_address("192.168.1.10") is None


def test_scan_network_does_not_add_mac_for_unreachable_host(monkeypatch):
    monkeypatch.setattr(scanner, "is_host_alive", lambda ip: False)
    monkeypatch.setattr(
        scanner,
        "get_mac_address",
        lambda ip: pytest.fail("MAC lookup should not run"),
    )

    assert scanner.scan_network("192.168.1.0/29", "192.168.1.1") == []


def test_standalone_scanner_execution(monkeypatch, capsys):
    monkeypatch.setattr(
        network,
        "get_network_info",
        lambda: {
            "network": "192.168.1.0/30",
            "gateway": "192.168.1.1",
        },
    )
    monkeypatch.setattr(scanner.platform, "system", lambda: "Windows")

    def fake_subprocess_run(command, **kwargs):
        if command[0] == "ping":
            return SimpleNamespace(returncode=0, stdout="")

        if command[0] == "arp":
            ip_address = command[-1]
            return SimpleNamespace(
                returncode=0,
                stdout=f"{ip_address} AA-BB-CC-DD-EE-FF dynamic\n",
            )

        raise AssertionError(f"Unexpected command: {command}")

    # The runpy script uses the shared subprocess module, so this
    # prevents real ping and ARP commands during the standalone test.
    monkeypatch.setattr(scanner.subprocess, "run", fake_subprocess_run)

    runpy.run_path("src/scanner.py", run_name="__main__")

    output = capsys.readouterr().out
    assert "Network Scanner" in output
    assert "Detected Network: 192.168.1.0/30" in output
    assert "Active Hosts" in output
    assert "192.168.1.1" in output
    assert "MAC: aa:bb:cc:dd:ee:ff" in output
    assert "GATEWAY" in output
    assert "Hosts found: 2" in output


def test_standalone_execution_without_network(monkeypatch, capsys):
    monkeypatch.setattr(
        network,
        "get_network_info",
        lambda: {"network": "", "gateway": ""},
    )

    runpy.run_path("src/scanner.py", run_name="__main__")

    output = capsys.readouterr().out
    assert "Network Scanner" in output
    assert "Could not determine the network. Scan cancelled." in output
