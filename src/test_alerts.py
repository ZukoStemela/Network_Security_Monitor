from alerts import generate_alerts_for_new_devices


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
