from scanner import scan_network
from network import get_network_info
from baseline import detect_new_devices, update_baseline


network_info = get_network_info()

devices = scan_network(
    network_info["network"],
    network_info["gateway"]
)

new_devices = detect_new_devices(devices)

if new_devices:
    print("NEW DEVICES DETECTED")
    print("---------------------")

    for device in new_devices:
        print(
            f"IP: {device['ip_address']} "
            f"| MAC: {device['mac_address']}"
        )
else:
    print("No new devices detected.")

update_baseline(devices)

print()
print(f"Devices in current scan: {len(devices)}")