import baseline_check


def setup_baseline_check(monkeypatch, devices, new_devices):
    monkeypatch.setattr(
        baseline_check,
        "get_network_info",
        lambda: {
            "network": "192.168.1.0/24",
            "gateway": "192.168.1.1",
        },
    )
    monkeypatch.setattr(
        baseline_check,
        "scan_network",
        lambda network, gateway: devices,
    )
    monkeypatch.setattr(
        baseline_check,
        "detect_new_devices",
        lambda scanned: new_devices,
    )


def test_main_reports_new_devices(monkeypatch, capsys):
    devices = [
        {
            "ip_address": "192.168.1.10",
            "mac_address": "AA:BB:CC:DD:EE:FF",
        }
    ]

    setup_baseline_check(monkeypatch, devices, devices)

    updated = []
    monkeypatch.setattr(
        baseline_check,
        "update_baseline",
        lambda scanned: updated.extend(scanned),
    )

    answers = iter(["UPDATE", "TRUST"])
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers),
    )

    baseline_check.main()

    output = capsys.readouterr().out

    assert "NEW DEVICES DETECTED" in output
    assert "192.168.1.10" in output
    assert "Baseline updated successfully." in output
    assert updated == devices


def test_main_reports_no_new_devices(monkeypatch, capsys):
    devices = [
        {
            "ip_address": "192.168.1.20",
            "mac_address": "11:22:33:44:55:66",
        }
    ]

    setup_baseline_check(monkeypatch, devices, [])

    updated = []
    monkeypatch.setattr(
        baseline_check,
        "update_baseline",
        lambda scanned: updated.extend(scanned),
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "UPDATE",
    )

    baseline_check.main()

    output = capsys.readouterr().out

    assert "No new devices detected." in output
    assert "Baseline updated successfully." in output
    assert updated == devices


def test_main_handles_empty_scan(monkeypatch, capsys):
    setup_baseline_check(monkeypatch, [], [])

    updated = []
    monkeypatch.setattr(
        baseline_check,
        "update_baseline",
        lambda scanned: updated.extend(scanned),
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "",
    )

    baseline_check.main()

    output = capsys.readouterr().out

    assert "No new devices detected." in output
    assert "Devices in current scan: 0" in output
    assert "Baseline unchanged." in output
    assert updated == []


def test_main_leaves_baseline_unchanged_when_update_declined(
    monkeypatch, capsys
):
    devices = [
        {
            "ip_address": "192.168.1.10",
            "mac_address": "AA:BB:CC:DD:EE:FF",
        }
    ]

    setup_baseline_check(monkeypatch, devices, [])

    updated = []
    monkeypatch.setattr(
        baseline_check,
        "update_baseline",
        lambda scanned: updated.extend(scanned),
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "",
    )

    baseline_check.main()

    assert "Baseline unchanged." in capsys.readouterr().out
    assert updated == []


def test_main_rejects_untrusted_new_devices(monkeypatch, capsys):
    devices = [
        {
            "ip_address": "192.168.1.99",
            "mac_address": "FF:FF:FF:FF:FF:FF",
        }
    ]

    setup_baseline_check(monkeypatch, devices, devices)

    updated = []
    monkeypatch.setattr(
        baseline_check,
        "update_baseline",
        lambda scanned: updated.extend(scanned),
    )

    answers = iter(["UPDATE", "NO"])
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers),
    )

    baseline_check.main()

    assert "Baseline unchanged." in capsys.readouterr().out
    assert updated == []


def test_main_cancels_when_network_is_unavailable(monkeypatch, capsys):
    monkeypatch.setattr(
        baseline_check,
        "get_network_info",
        lambda: {"network": "", "gateway": None},
    )

    baseline_check.main()

    assert "Scan cancelled." in capsys.readouterr().out
