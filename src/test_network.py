
import subprocess

import network


def test_get_hostname(monkeypatch):
    monkeypatch.setattr(network.socket, "gethostname", lambda: "TEST-PC")

    assert network.get_hostname() == "TEST-PC"


def test_get_local_ip(monkeypatch):
    class FakeSocket:
        def connect(self, address):
            assert address == ("8.8.8.8", 80)

        def getsockname(self):
            return ("192.168.1.10", 12345)

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

    class Result:
        stdout = "192.168.1.1|Ethernet|192.168.1.10|24"

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    info = network.get_route_info()

    assert info["gateway"] == "192.168.1.1"
    assert info["interface"] == "Ethernet"
    assert info["ip_address"] == "192.168.1.10"
    assert info["prefix"] == 24


def test_get_route_info_windows_missing_route(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Windows")

    class Result:
        stdout = ""

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    info = network.get_route_info()

    assert info == {
        "gateway": None,
        "interface": None,
        "ip_address": None,
        "prefix": None,
    }


def test_get_route_info_linux(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: type(
            "Result",
            (),
            {"stdout": "default via 192.168.1.1 dev eth0\n"},
        )(),
    )
    monkeypatch.setattr(
        network,
        "get_local_ip",
        lambda: "192.168.1.10",
    )

    info = network.get_route_info()

    assert info["gateway"] == "192.168.1.1"
    assert info["interface"] == "eth0"
    assert info["ip_address"] == "192.168.1.10"
    assert info["prefix"] is None


def test_get_route_info_linux_no_default_route(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: type(
            "Result", (), {"stdout": "192.168.1.0/24 dev eth0\n"}
        )(),
    )
    monkeypatch.setattr(
        network,
        "get_local_ip",
        lambda: "192.168.1.10",
    )

    info = network.get_route_info()

    assert info["gateway"] is None
    assert info["interface"] is None
    assert info["ip_address"] == "192.168.1.10"


def test_get_network_windows(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        network,
        "get_route_info",
        lambda: {
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
        lambda: {"ip_address": None, "prefix": None},
    )

    assert network.get_network("Ethernet") is None


def test_get_network_linux(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Linux")

    class Result:
        stdout = (
            "default via 192.168.1.1 dev eth0\n"
            "192.168.1.0/24 dev eth0 proto kernel\n"
        )

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    assert network.get_network("eth0") == "192.168.1.0/24"


def test_get_network_linux_invalid_route(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Linux")

    class Result:
        stdout = (
            "not-a-network dev eth0\n"
            "192.168.1.0/24 dev eth0\n"
        )

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    assert network.get_network("eth0") == "192.168.1.0/24"


def test_get_network_linux_no_network(monkeypatch):
    monkeypatch.setattr(network.platform, "system", lambda: "Linux")

    class Result:
        stdout = "default via 192.168.1.1 dev eth0\n"

    monkeypatch.setattr(
        network.subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    assert network.get_network("eth0") is None


def test_get_network_info(monkeypatch):
    monkeypatch.setattr(network, "get_hostname", lambda: "TEST-PC")
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

    info = network.get_network_info()

    assert info == {
        "hostname": "TEST-PC",
        "ip_address": "192.168.1.10",
        "gateway": "192.168.1.1",
        "interface": "Ethernet",
        "network": "192.168.1.0/24",
    }


def test_get_network_info_falls_back_to_local_ip(monkeypatch):
    monkeypatch.setattr(network, "get_hostname", lambda: "TEST-PC")
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
    monkeypatch.setattr(network, "get_network", lambda interface: None)

    info = network.get_network_info()

    assert info["ip_address"] == "192.168.1.10"
    assert info["network"] is None
