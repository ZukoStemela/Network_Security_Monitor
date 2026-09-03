import socket
import subprocess


def get_hostname():
    return socket.gethostname()


def get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.connect(("8.8.8.8", 80))
        ip_address = sock.getsockname()[0]
    finally:
        sock.close()

    return ip_address


def get_route_info():
    result = subprocess.run(
        ["ip", "route"],
        capture_output=True,
        text=True,
        check=True
    )

    for line in result.stdout.splitlines():
        if line.startswith("default"):
            parts = line.split()

            gateway = parts[2]
            interface = parts[4]

            return {
                "gateway": gateway,
                "interface": interface
            }

    return {
        "gateway": None,
        "interface": None
    }


def get_network(interface):
    result = subprocess.run(
        ["ip", "-4", "route", "show", "dev", interface],
        capture_output=True,
        text=True,
        check=True
    )

    for line in result.stdout.splitlines():
        parts = line.split()

        if parts and "/" in parts[0]:
            return parts[0]

    return None


def get_network_info():
    hostname = get_hostname()
    ip_address = get_local_ip()
    route_info = get_route_info()

    network = get_network(route_info["interface"])

    return {
        "hostname": hostname,
        "ip_address": ip_address,
        "gateway": route_info["gateway"],
        "interface": route_info["interface"],
        "network": network
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