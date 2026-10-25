import monitor
import runpy


def test_ping_host_when_host_is_unreachable(monkeypatch):
    class FakeResult:
        returncode = 1
        stdout = ""
        stderr = "Request timed out"

    def fake_run(command, capture_output, text):
        assert command == ["ping", "-c", "4", "-W", "2", "192.168.1.1"]
        assert capture_output is True
        assert text is True
        return FakeResult()

    monkeypatch.setattr(monitor.subprocess, "run", fake_run)

    result = monitor.ping_host("192.168.1.1")

    assert result == {
        "host": "192.168.1.1",
        "reachable": False,
        "latency": None,
        "packet_loss": None,
    }


def test_ping_host_when_host_is_reachable(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = (
            "4 packets transmitted, 4 received, 0% packet loss\n"
            "rtt min/avg/max/mdev = 10.0/12.5/15.0/1.2 ms"
        )

    monkeypatch.setattr(
        monitor.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    result = monitor.ping_host("192.168.1.1")

    assert result["host"] == "192.168.1.1"
    assert result["reachable"] is True
    assert result["latency"] == 12.5
    assert result["packet_loss"] == 0.0


def test_ping_host_when_latency_and_packet_loss_are_missing(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = "Ping completed but statistics were unavailable"

    monkeypatch.setattr(
        monitor.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    result = monitor.ping_host("example.test")

    assert result == {
        "host": "example.test",
        "reachable": True,
        "latency": None,
        "packet_loss": None,
    }


def test_ping_host_parses_decimal_packet_loss(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = (
            "2 packets transmitted, 1 received, 25.5% packet loss\n"
            "rtt min/avg/max/mdev = 8.0/9.5/11.0/1.0 ms"
        )

    monkeypatch.setattr(
        monitor.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    result = monitor.ping_host("192.168.1.5")

    assert result["reachable"] is True
    assert result["latency"] == 9.5
    assert result["packet_loss"] == 25.5


def test_standalone_monitor_execution(monkeypatch, capsys):
    pinged_hosts = []

    class FakeResult:
        returncode = 0
        stdout = (
            "4 packets transmitted, 4 received, 0% packet loss\n"
            "rtt min/avg/max/mdev = 10.0/12.5/15.0/1.2 ms"
        )

    def fake_run(command, **kwargs):
        host = command[-1]
        pinged_hosts.append(host)
        return FakeResult()

    monkeypatch.setattr(monitor.subprocess, "run", fake_run)

    runpy.run_module("monitor", run_name="__main__")

    output = capsys.readouterr().out

    assert "Connectivity Test" in output
    assert "Gateway" in output
    assert "Internet" in output
    assert pinged_hosts == ["172.30.4.1", "1.1.1.1"]
