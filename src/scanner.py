
import ipaddress
import platform
import re
import subprocess

from device import Device


MAX_ALLOWED_HOSTS = 256


def is_host_alive(ip_address):
    """Return True when the host replies to ping."""
    if platform.system() == "Windows":
        command = ["ping", "-n", "1", "-w", "700", str(ip_address)]
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
    """Return a validated MAC address when available."""
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


def get_confirmed_neighbors(network):
    """Return IPs with usable MAC addresses in the neighbor table."""
    confirmed = set()

    if platform.system() != "Windows":
        return confirmed

    try:
        result = subprocess.run(
            ["arp", "-a"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return confirmed

    for line in result.stdout.splitlines():
        parts = line.split()

        if len(parts) < 3:
            continue

        try:
            address = ipaddress.ip_address(parts[0])
        except ValueError:
            continue

        mac = parts[1].replace("-", ":").lower()

        if (
            address in network
            and address not in (network.network_address, network.broadcast_address)
            and re.fullmatch(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", mac)
            and mac != "ff:ff:ff:ff:ff:ff"
        ):
            confirmed.add(str(address))

    return confirmed


def scan_network(network, gateway, max_hosts=MAX_ALLOWED_HOSTS):
    """Scan a bounded local subnet using ping and neighbor information."""
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

    if network.version != 4:
        return []

    candidates = list(network.hosts())[:max_hosts]
    gateway_ip = None

    try:
        parsed_gateway = ipaddress.ip_address(gateway)
        if parsed_gateway in network:
            gateway_ip = str(parsed_gateway)
    except ValueError:
        pass

    if gateway_ip and ipaddress.ip_address(gateway_ip) in candidates:
        candidates.remove(ipaddress.ip_address(gateway_ip))

    if gateway_ip:
        candidates.insert(0, ipaddress.ip_address(gateway_ip))

    confirmed_neighbors = get_confirmed_neighbors(network)
    active_hosts = {}

    # Test the gateway and addresses that Windows has neighbor entries for.
    priority_ips = set(confirmed_neighbors)
    if gateway_ip:
        priority_ips.add(gateway_ip)

    for address in candidates:
        ip = str(address)
        if ip in priority_ips and is_host_alive(ip):
            active_hosts[ip] = True

    # Probe remaining addresses in the local subnet.
    for address in candidates:
        ip = str(address)

        if ip in active_hosts:
            continue

        if is_host_alive(ip):
            active_hosts[ip] = True

    devices = []

    for ip in sorted(active_hosts, key=ipaddress.ip_address):
        devices.append(
            Device(
                ip,
                is_gateway=(ip == gateway_ip),
                mac_address=get_mac_address(ip),
            )
        )

    return devices


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

    print("Scanning the local subnet. This may take a few minutes...")
    hosts = scan_network(network, gateway)

    print()
    print("Active Hosts")
    print("------------")

    if not hosts:
        print("No hosts replied to ping.")
    else:
        for host in hosts:
            info = host.get_info()
            role = "GATEWAY" if info["is_gateway"] else "HOST"
            mac = info["mac_address"] or "UNKNOWN"
            print(f"{info['ip_address']} | MAC: {mac} | {role}")

    print()
    print(f"Hosts confirmed by ping: {len(hosts)}")
    print("Note: Devices that block ping may not appear.")


if __name__ == "__main__":
    main()
