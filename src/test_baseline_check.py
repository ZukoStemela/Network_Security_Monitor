
import baseline_check


def test_main_cancels_when_network_is_unknown(monkeypatch, capsys):
    monkeypatch.setattr(
        baseline_check,
        "get_network_info",
        lambda: {"network": "", "gateway": ""},
    )

    def fail_scan(*args, **kwargs):
        raise AssertionError("Scanner should not run")

    monkeypatch.setattr(baseline_check, "scan_network", fail_scan)

    baseline_check.main()

    output = capsys.readouterr().out

    assert "Could not determine the local network" in output


def test_main_reports_new_devices(monkeypatch, capsys):
    devices = [
        {"ip_address": "192.168.1.10", "mac_address": "AA:BB:CC:DD:EE:FF"}
    ]

    monkeypatch.setattr(
        baseline_check,
        "get_network_info",
        lambda: {"network": "192.168.1.0/24", "gateway": "192.168.1.1"},
    )
    monkeypatch.setattr(
        baseline_check, "scan_network", lambda network, gateway: devices
    )
    monkeypatch.setattr(
        baseline_check, "detect_new_devices", lambda scanned: scanned
    )

    updated = []
    monkeypatch.setattr(
        baseline_check, "update_baseline", lambda scanned: updated.extend(scanned)
    )

    baseline_check.main()

    output = capsys.readouterr().out

    assert "NEW DEVICES DETECTED" in output
    assert "192.168.1.10" in output
    assert "AA:BB:CC:DD:EE:FF" in output
    assert "Devices in current scan: 1" in output
    assert updated == devices


def test_main_reports_no_new_devices(monkeypatch, capsys):
    devices = [
        {"ip_address": "192.168.1.20", "mac_address": "11:22:33:44:55:66"}
    ]

    monkeypatch.setattr(
        baseline_check,
        "get_network_info",
        lambda: {"network": "192.168.1.0/24", "gateway": "192.168.1.1"},
    )
    monkeypatch.setattr(
        baseline_check, "scan_network", lambda network, gateway: devices
    )
    monkeypatch.setattr(
        baseline_check, "detect_new_devices", lambda scanned: []
    )

    updated = []
    monkeypatch.setattr(
        baseline_check, "update_baseline", lambda scanned: updated.extend(scanned)
    )

    baseline_check.main()

    output = capsys.readouterr().out

    assert "No new devices detected." in output
    assert "Devices in current scan: 1" in output
    assert updated == devices


def test_main_handles_empty_scan(monkeypatch, capsys):
    monkeypatch.setattr(
        baseline_check,
        "get_network_info",
        lambda: {"network": "192.168.1.0/24", "gateway": "192.168.1.1"},
    )
    monkeypatch.setattr(
        baseline_check, "scan_network", lambda network, gateway: []
    )
    monkeypatch.setattr(
        baseline_check, "detect_new_devices", lambda scanned: []
    )

    updated = []
    monkeypatch.setattr(
        baseline_check, "update_baseline", lambda scanned: updated.extend(scanned)
    )

    baseline_check.main()

    output = capsys.readouterr().out

    assert "No new devices detected." in output
    assert "Devices in current scan: 0" in output
    assert updated == []

def test_standalone_execution(monkeypatch, capsys):
    import runpy

    monkeypatch.setattr(
        "network.get_network_info",
        lambda: {"network": "", "gateway": ""},
    )

    runpy.run_path("src/baseline_check.py", run_name="__main__")

    output = capsys.readouterr().out
    assert "Could not determine the local network" in output