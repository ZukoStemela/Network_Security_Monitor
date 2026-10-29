
from alerts import (
    format_device_alert,
    generate_alerts_for_new_devices,
    print_alerts,
)


def test_generate_alerts_empty():
    assert generate_alerts_for_new_devices([]) == []


def test_generate_alerts_basic():
    devices = [
        {
            "ip_address": "192.168.1.10",
            "mac_address": "aa:bb:cc:dd:ee:ff",
            "is_gateway": False,
        }
    ]

    alerts = generate_alerts_for_new_devices(devices)

    assert len(alerts) == 1
    assert "192.168.1.10" in alerts[0]
    assert "aa:bb:cc:dd:ee:ff" in alerts[0]
    assert "HOST" in alerts[0]


def test_format_device_alert_gateway():
    device = {
        "ip_address": "192.168.1.1",
        "mac_address": "aa:bb:cc:dd:ee:01",
        "is_gateway": True,
    }

    alert = format_device_alert(device)

    assert alert == (
        "NEW DEVICE: 192.168.1.1 | "
        "MAC: aa:bb:cc:dd:ee:01 | ROLE: GATEWAY"
    )


def test_format_device_alert_missing_details():
    alert = format_device_alert({})

    assert alert == "NEW DEVICE: UNKNOWN | MAC: UNKNOWN | ROLE: HOST"


def test_print_alerts(capsys):
    print_alerts(["New device detected"])

    output = capsys.readouterr().out

    assert "ALERTS" in output
    assert "------" in output
    assert "New device detected" in output


def test_print_alerts_empty(capsys):
    print_alerts([])

    assert capsys.readouterr().out == "No alerts.\n"
