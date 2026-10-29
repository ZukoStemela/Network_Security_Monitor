import baseline
from device import Device


def test_detect_new_devices(monkeypatch):
    known_devices = [
        {
            "ip_address": "192.168.1.2",
            "mac_address": "aa:bb:cc:dd:ee:01",
            "status": "ACTIVE",
            "is_gateway": False,
        }
    ]

    monkeypatch.setattr(
        baseline,
        "load_known_devices",
        lambda: known_devices,
    )

    current_devices = [
        Device(
            "192.168.1.2",
            mac_address="aa:bb:cc:dd:ee:01",
        ),
        Device(
            "192.168.1.3",
            mac_address="aa:bb:cc:dd:ee:02",
        ),
    ]

    new_devices = baseline.detect_new_devices(current_devices)

    assert len(new_devices) == 1
    assert new_devices[0]["ip_address"] == "192.168.1.3"


def test_detect_new_devices_when_none_are_new(monkeypatch):
    monkeypatch.setattr(
        baseline,
        "load_known_devices",
        lambda: [
            {
                "ip_address": "192.168.1.2",
                "mac_address": "aa:bb:cc:dd:ee:01",
            }
        ],
    )

    current_devices = [
        Device(
            "192.168.1.2",
            mac_address="aa:bb:cc:dd:ee:01",
        )
    ]

    assert baseline.detect_new_devices(current_devices) == []


def test_update_baseline(monkeypatch):
    saved_devices = []

    monkeypatch.setattr(
        baseline,
        "save_known_devices",
        lambda devices: saved_devices.extend(devices),
    )

    current_devices = [
        Device(
            "192.168.1.5",
            is_gateway=True,
            mac_address="aa:bb:cc:dd:ee:05",
        )
    ]

    baseline.update_baseline(current_devices)

    assert len(saved_devices) == 1
    assert saved_devices[0]["ip_address"] == "192.168.1.5"
    assert saved_devices[0]["is_gateway"] is True
