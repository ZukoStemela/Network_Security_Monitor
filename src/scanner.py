import ipaddress
import subprocess

from network import get_network_info
from device import Device


def is_host_alive(ip_address):
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", str(ip_address)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def get_mac_address(ip_address):
    result = subprocess.run(
        ["ip", "neigh", "show", ip_address],
        capture_output=True,
        text=True
    )

    parts = result.stdout.split()

    if "lladdr" in parts:
        mac_index = parts.index("lladdr") + 1
        return parts[mac_index]

    return None


def scan_network(network, gateway, max_hosts=10):
    network = ipaddress.ip_network(network)

    active_hosts = []

    for index, ip_address in enumerate(network.hosts()):
        if index >= max_hosts:
            break

        ip_address = str(ip_address)

        if is_host_alive(ip_address):
            is_gateway = ip_address == gateway
            mac_address = get_mac_address(ip_address)

            device = Device(
                ip_address,
                is_gateway=is_gateway,
                mac_address=mac_address
            )

            active_hosts.append(device)

    return active_hosts


if __name__ == "__main__":
    network_info = get_network_info()

    network = network_info["network"]
    gateway = network_info["gateway"]

    print("Network Scanner")
    print("---------------")
    print(f"Detected Network: {network}")
    print(f"Gateway: {gateway}")
    print()

    hosts = scan_network(
        network,
        gateway
    )

    print("Active Hosts")
    print("------------")

    if hosts:
        for host in hosts:
            info = host.get_info()

            role = "GATEWAY" if info["is_gateway"] else "HOST"
            mac = info["mac_address"] or "UNKNOWN"

            print(
                f"✓ {info['ip_address']} "
                f"| MAC: {mac} "
                f"| {role}"
            )
    else:
        print("No active hosts found.")

    print()
    print(f"Hosts found: {len(hosts)}")