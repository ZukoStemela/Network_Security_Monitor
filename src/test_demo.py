import sys

import demo


def test_mock_scan_returns_known_and_current_devices():
    known, current = demo.mock_scan()

    assert len(known) == 2
    assert len(current) == 3

    known_macs = {device["mac_address"] for device in known}
    current_macs = {device["mac_address"] for device in current}

    assert known_macs.issubset(current_macs)
    assert "ff:ff:ff:ff:ff:ff" in current_macs


def test_run_mock_demo_prints_scan_and_alerts(monkeypatch, capsys):
    captured_alerts = []

    monkeypatch.setattr(
        demo,
        "generate_alerts_for_new_devices",
        lambda devices: captured_alerts.extend(devices) or ["Test alert"],
    )
    monkeypatch.setattr(
        demo,
        "print_alerts",
        lambda alerts: print(alerts),
    )

    demo.run_mock_demo()

    output = capsys.readouterr().out

    assert "Mock demo: baseline and current scan" in output
    assert "Baseline:" in output
    assert "Current scan:" in output
    assert "192.168.1.99" in output
    assert len(captured_alerts) == 1
    assert captured_alerts[0]["mac_address"] == "ff:ff:ff:ff:ff:ff"


def test_main_runs_mock_mode(monkeypatch):
    called = []

    monkeypatch.setattr(demo, "run_mock_demo", lambda: called.append(True))
    monkeypatch.setattr(sys, "argv", ["demo.py", "--mock"])

    demo.main()

    assert called == [True]


def test_main_without_mock_prints_message(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["demo.py"])

    demo.main()

    output = capsys.readouterr().out

    assert "Live demo not implemented" in output
    assert "Use --mock for a safe demo." in output


def test_standalone_execution_mock_mode(monkeypatch, capsys):
    import runpy

    monkeypatch.setattr(sys, "argv", ["demo.py", "--mock"])

    runpy.run_path("src/demo.py", run_name="__main__")

    output = capsys.readouterr().out

    assert "Mock demo: baseline and current scan" in output
    assert "192.168.1.99" in output
