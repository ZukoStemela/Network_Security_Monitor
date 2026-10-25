
import ipaddress
import platform
import re
import subprocess

from device import Device


DEFAULT_MAX_HOSTS = 10
MAX_ALLOWED_HOSTS = 256


def is_host_alive(ip_address):
    if platform.system() == "Windows":
        command = ["ping", "-n", "1", "-w", "1000", str(ip_address)]
    else:
        command = ["ping", "-c", "1", "-W", "1", str(ip_address)]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
            check=False,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def get_mac_address(ip_address):
    if platform.system() == "Windows":
        command = ["arp", "-a", str(ip_address)]
    else:
        command = ["ip", "neigh", "show", str(ip_address)]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if platform.system() == "Windows":
        for line in result.stdout.splitlines():
            parts = line.split()

            if len(parts) >= 2 and parts[0] == str(ip_address):
                mac = parts[1].replace("-", ":").lower()

                if re.fullmatch(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", mac):
                    return mac
    else:
        parts = result.stdout.split()

        if "lladdr" in parts:
            mac = parts[parts.index("lladdr") + 1].lower()

            if re.fullmatch(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", mac):
                return mac

    return None


def scan_network(network, gateway, max_hosts=DEFAULT_MAX_HOSTS):
    if not isinstance(max_hosts, int) or isinstance(max_hosts, bool):
        return []

    if max_hosts <= 0 or max_hosts > MAX_ALLOWED_HOSTS:
        return []

    if not isinstance(network, str) or not network.strip():
        return []

    try:
        network = ipaddress.ip_network(network, strict=False)
    except ValueError:
        return []

    active_hosts = []

    for index, ip_address in enumerate(network.hosts()):
        if index >= max_hosts:
            break

        ip_address = str(ip_address)

        if is_host_alive(ip_address):
            active_hosts.append(
                Device(
                    ip_address,
                    is_gateway=ip_address == gateway,
                    mac_address=get_mac_address(ip_address),
                )
            )

    return active_hosts


def main():
    from network import get_network_info

    network_info = get_network_info()
    network = network_info["network"]
    gateway = network_info["gateway"]

    print("Network Scanner")
    print("---------------")
    print(f"Detected Network: {network}")
    print(f"Gateway: {gateway}")
    print()

    if not network:
        print("Could not determine the network. Scan cancelled.")
        return

    hosts = scan_network(network, gateway)

    print("Active Hosts")
    print("------------")

    for host in hosts:
        info = host.get_info()
        role = "GATEWAY" if info["is_gateway"] else "HOST"
        mac = info["mac_address"] or "UNKNOWN"

        print(f"{info['ip_address']} | MAC: {mac} | {role}")

    print()
    print(f"Hosts found: {len(hosts)}")


if __name__ == "__main__":
    main()
