import ipaddress
import platform
import socket
import subprocess


def get_hostname():
    return socket.gethostname()


def get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    finally:
        sock.close()


def get_route_info():
    if platform.system() == "Windows":
        command = (
            "$r = Get-NetRoute -AddressFamily IPv4 "
            "-DestinationPrefix '0.0.0.0/0' "
            "| Sort-Object RouteMetric "
            "| Select-Object -First 1; "
            "if ($r) { "
            "$a = Get-NetIPAddress "
            "-InterfaceIndex $r.InterfaceIndex "
            "-AddressFamily IPv4 "
            "| Where-Object {$_.IPAddress -notlike '169.254*'} "
            "| Select-Object -First 1; "
            "if ($a) { "
            "'{0}|{1}|{2}|{3}' -f "
            "$r.NextHop, $r.InterfaceAlias, "
            "$a.IPAddress, $a.PrefixLength "
            "} }"
        )

        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            check=True,
        )

        parts = result.stdout.strip().split("|")

        if len(parts) == 4:
            gateway, interface, ip_address, prefix = parts
            return {
                "gateway": gateway,
                "interface": interface,
                "ip_address": ip_address,
                "prefix": int(prefix),
            }

        return {
            "gateway": None,
            "interface": None,
            "ip_address": None,
            "prefix": None,
        }

    result = subprocess.run(
        ["ip", "route"], capture_output=True, text=True, check=True
    )

    for line in result.stdout.splitlines():
        if line.startswith("default"):
            parts = line.split()
            return {
                "gateway": parts[2],
                "interface": parts[4],
                "ip_address": get_local_ip(),
                "prefix": None,
            }

    return {
        "gateway": None,
        "interface": None,
        "ip_address": get_local_ip(),
        "prefix": None,
    }


def get_network(interface):
    if platform.system() == "Windows":
        info = get_route_info()
        ip_address = info["ip_address"]
        prefix = info["prefix"]

        if ip_address and prefix is not None:
            return str(
                ipaddress.ip_interface(f"{ip_address}/{prefix}").network
            )

        return None

    result = subprocess.run(
        ["ip", "-4", "route", "show", "dev", interface],
        capture_output=True,
        text=True,
        check=True,
    )

    for line in result.stdout.splitlines():
        parts = line.split()

        if parts and "/" in parts[0]:
            try:
                return str(ipaddress.ip_network(parts[0], strict=False))
            except ValueError:
                continue

    return None


def get_network_info():
    hostname = get_hostname()
    route_info = get_route_info()
    ip_address = route_info["ip_address"] or get_local_ip()
    network = get_network(route_info["interface"])

    return {
        "hostname": hostname,
        "ip_address": ip_address,
        "gateway": route_info["gateway"],
        "interface": route_info["interface"],
        "network": network,
    }


if __name__ == "__main__":
    network_info = get_network_info()

    print("Network Information")
    print("-------------------")
    print(f"Hostname  : {network_info['hostname']}")
    print(f"IP        : {network_info['ip_address']}")
    print(f"Interface : {network_info['interface']}")
    print(f"Gateway   : {network_info['gateway']}")
    print(f"Network   : {network_info['network']}")
