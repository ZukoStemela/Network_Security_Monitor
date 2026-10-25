
import runpy
import socket
import subprocess

import network


def test_get_hostname(monkeypatch):
    monkeypatch.setattr(network.socket, "gethostname", lambda: "test-pc")

    assert network.get_hostname() == "test-pc"


def test_get_local_ip(monkeypatch):
    class FakeSocket:
        def connect(self, address):
            assert address == ("8.8.8.8", 80)

        def getsockname(self):
            return ("192.168.1.10", 0)

        def close(self):
            pass

    monkeypatch.setattr(
        network.socket,
        "socket",
        lambda *args: FakeSocket(),
    )

    assert network.get_local_ip() == "192.168.1.10"


def test_get_route_info_windows(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Windows")

    class FakeResult:
        stdout = "192.168.1.1|Ethernet|192.168.1.10|24"

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    result = network.get_route_info()

    assert result == {
        "gateway": "192.168.1.1",
        "interface": "Ethernet",
        "ip_address": "192.168.1.10",
        "prefix": 24,
    }


def test_get_route_info_windows_missing_route(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Windows")

    class FakeResult:
        stdout = ""

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    assert network.get_route_info() == {
        "gateway": None,
        "interface": None,
        "ip_address": None,
        "prefix": None,
    }


def test_get_route_info_linux(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Linux")

    class FakeResult:
        stdout = "default via 192.168.1.1 dev eth0 proto dhcp\n"

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )
    monkeypatch.setattr(
        network,
        "get_local_ip",
        lambda: "192.168.1.10",
    )

    assert network.get_route_info() == {
        "gateway": "192.168.1.1",
        "interface": "eth0",
        "ip_address": "192.168.1.10",
        "prefix": None,
    }


def test_get_route_info_linux_no_default_route(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Linux")

    class FakeResult:
        stdout = "192.168.1.0/24 dev eth0\n"

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )
    monkeypatch.setattr(
        network,
        "get_local_ip",
        lambda: "192.168.1.10",
    )

    assert network.get_route_info() == {
        "gateway": None,
        "interface": None,
        "ip_address": "192.168.1.10",
        "prefix": None,
    }


def test_get_network_windows(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        network,
        "get_route_info",
        lambda: {
            "gateway": "192.168.1.1",
            "interface": "Ethernet",
            "ip_address": "192.168.1.10",
            "prefix": 24,
        },
    )

    assert network.get_network("Ethernet") == "192.168.1.0/24"


def test_get_network_windows_missing_ip(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        network,
        "get_route_info",
        lambda: {
            "gateway": None,
            "interface": None,
            "ip_address": None,
            "prefix": None,
        },
    )

    assert network.get_network(None) is None


def test_get_network_linux(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Linux")

    class FakeResult:
        stdout = "192.168.1.0/24 dev eth0 proto kernel\n"

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    assert network.get_network("eth0") == "192.168.1.0/24"


def test_get_network_linux_invalid_route(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Linux")

    class FakeResult:
        stdout = (
            "not-a-network/24 dev eth0\n"
            "192.168.1.0/24 dev eth0\n"
        )

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    assert network.get_network("eth0") == "192.168.1.0/24"


def test_get_network_linux_no_network(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Linux")

    class FakeResult:
        stdout = "default via 192.168.1.1 dev eth0\n"

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    assert network.get_network("eth0") is None


def test_get_network_info(monkeypatch):
    monkeypatch.setattr(network, "get_hostname", lambda: "test-pc")
    monkeypatch.setattr(
        network,
        "get_route_info",
        lambda: {
            "gateway": "192.168.1.1",
            "interface": "Ethernet",
            "ip_address": "192.168.1.10",
            "prefix": 24,
        },
    )
    monkeypatch.setattr(
        network,
        "get_network",
        lambda interface: "192.168.1.0/24",
    )

    result = network.get_network_info()

    assert result == {
        "hostname": "test-pc",
        "ip_address": "192.168.1.10",
        "gateway": "192.168.1.1",
        "interface": "Ethernet",
        "network": "192.168.1.0/24",
    }


def test_get_network_info_falls_back_to_local_ip(monkeypatch):
    monkeypatch.setattr(network, "get_hostname", lambda: "test-pc")
    monkeypatch.setattr(
        network,
        "get_route_info",
        lambda: {
            "gateway": None,
            "interface": None,
            "ip_address": None,
            "prefix": None,
        },
    )
    monkeypatch.setattr(
        network,
        "get_local_ip",
        lambda: "192.168.1.10",
    )
    monkeypatch.setattr(
        network,
        "get_network",
        lambda interface: None,
    )

    result = network.get_network_info()

    assert result["ip_address"] == "192.168.1.10"
    assert result["network"] is None


def test_get_network_info_uses_local_ip_when_route_ip_is_missing(
    monkeypatch,
):
    monkeypatch.setattr(network, "get_hostname", lambda: "test-pc")
    monkeypatch.setattr(
        network,
        "get_route_info",
        lambda: {
            "gateway": "192.168.1.1",
            "interface": "eth0",
            "ip_address": None,
            "prefix": None,
        },
    )
    monkeypatch.setattr(
        network,
        "get_local_ip",
        lambda: "192.168.1.10",
    )
    monkeypatch.setattr(
        network,
        "get_network",
        lambda interface: "192.168.1.0/24",
    )

    result = network.get_network_info()

    assert result["ip_address"] == "192.168.1.10"
    assert result["network"] == "192.168.1.0/24"



def test_standalone_network_execution(monkeypatch, capsys):
    monkeypatch.setattr(
        network.socket,
        "gethostname",
        lambda: "test-pc",
    )

    monkeypatch.setattr(
        network.platform,
        "system",
        lambda: "Windows",
    )

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="192.168.1.1|Ethernet|192.168.1.10|24",
            stderr="",
        ),
    )

    runpy.run_path("src/network.py", run_name="__main__")

    output = capsys.readouterr().out

    assert "Network Information" in output
    assert "Hostname  : test-pc" in output
    assert "IP        : 192.168.1.10" in output
    assert "Interface : Ethernet" in output
    assert "Gateway   : 192.168.1.1" in output
    assert "Network   : 192.168.1.0/24" in output


    runpy.run_path("src/network.py", run_name="__main__")

    output = capsys.readouterr().out

    assert "Network Information" in output
    assert "Hostname  : test-pc" in output
    assert "IP        : 192.168.1.10" in output
    assert "Interface : Ethernet" in output
    assert "Gateway   : 192.168.1.1" in output
    assert "Network   : 192.168.1.0/24" in output
