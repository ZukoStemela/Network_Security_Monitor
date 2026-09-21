from typing import List, Dict


def format_device_alert(device: Dict) -> str:
    mac = device.get("mac_address") or "UNKNOWN"
    ip = device.get("ip_address") or "UNKNOWN"
    role = "GATEWAY" if device.get("is_gateway") else "HOST"

    return f"NEW DEVICE: {ip} | MAC: {mac} | ROLE: {role}"


def generate_alerts_for_new_devices(devices: List[Dict]) -> List[str]:
    """Given a list of device dicts (as returned by `Device.get_info()`),
    return a list of human-readable alert strings.
    """
    if not devices:
        return []

    return [format_device_alert(d) for d in devices]


def print_alerts(alerts: List[str]) -> None:
    if not alerts:
        print("No alerts.")
        return

    print("ALERTS")
    print("------")
    for a in alerts:
        print(a)


__all__ = [
    "format_device_alert",
    "generate_alerts_for_new_devices",
    "print_alerts",
]
