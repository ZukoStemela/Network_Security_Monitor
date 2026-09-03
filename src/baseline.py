from device_store import load_known_devices, save_known_devices


def device_to_dict(device):
    return device.get_info()


def detect_new_devices(current_devices):
    known_devices = load_known_devices()

    known_macs = {
        device["mac_address"]
        for device in known_devices
        if device.get("mac_address")
    }

    new_devices = []

    for device in current_devices:
        info = device_to_dict(device)

        mac = info.get("mac_address")

        if mac and mac not in known_macs:
            new_devices.append(info)

    return new_devices


def update_baseline(current_devices):
    devices = [
        device_to_dict(device)
        for device in current_devices
    ]

    save_known_devices(devices)