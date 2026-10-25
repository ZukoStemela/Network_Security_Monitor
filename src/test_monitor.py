
import subprocess

from monitor import ping_host


def test_ping_host_unreachable(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr("monitor.subprocess.run", fake_run)

    result = ping_host("192.168.1.1")

    assert result == {
        "host": "192.168.1.1",
        "reachable": False,
        "latency": None,
        "packet_loss": None,
    }


def test_ping_host_reachable_with_statistics(monkeypatch):
    output = (
        "4 packets transmitted, 4 received, 0% packet loss\n"
        "rtt min/avg/max/mdev = 10.1/12.5/15.2/1.1 ms\n"
    )

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=output,
            stderr="",
        )

    monkeypatch.setattr("monitor.subprocess.run", fake_run)

    result = ping_host("1.1.1.1")

    assert result["host"] == "1.1.1.1"
    assert result["reachable"] is True
    assert result["latency"] == 12.5
    assert result["packet_loss"] == 0.0


def test_ping_host_reachable_without_statistics(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="Ping completed, but no statistics were reported.",
            stderr="",
        )

    monkeypatch.setattr("monitor.subprocess.run", fake_run)

    result = ping_host("example.test")

    assert result["reachable"] is True
    assert result["latency"] is None
    assert result["packet_loss"] is None


def test_ping_host_reads_packet_loss(monkeypatch):
    output = (
        "2 packets transmitted, 1 received, 50% packet loss\n"
        "rtt min/avg/max/mdev = 5.0/7.5/10.0/2.0 ms\n"
    )

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=output,
            stderr="",
        )

    monkeypatch.setattr("monitor.subprocess.run", fake_run)

    result = ping_host("192.168.1.10")

    assert result["reachable"] is True
    assert result["latency"] == 7.5
    assert result["packet_loss"] == 50.0
