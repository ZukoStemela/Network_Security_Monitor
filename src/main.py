from network import get_network_info
from monitor import ping_host


def display_network_info(network_info):
    print("SYSTEM INFORMATION")
    print("------------------")
    print(f"Hostname  : {network_info['hostname']}")
    print(f"IP        : {network_info['ip_address']}")
    print(f"Interface : {network_info['interface']}")
    print(f"Gateway   : {network_info['gateway']}")
    print(f"Network   : {network_info['network']}")


def display_connectivity(network_info):
    gateway = network_info["gateway"]

    result = ping_host(gateway)

    print("\nCONNECTIVITY")
    print("------------")
    print(f"Gateway   : {result['host']}")
    print(f"Status    : {'ONLINE' if result['reachable'] else 'OFFLINE'}")

    if result["reachable"]:
        print(f"Latency   : {result['latency']} ms")
        print(f"Loss      : {result['packet_loss']}%")

def display_internet_connectivity():
    internet_host = "1.1.1.1"

    result = ping_host(internet_host)

    print("\nINTERNET CONNECTIVITY")
    print("---------------------")
    print(f"Host      : {result['host']}")
    print(f"Status    : {'ONLINE' if result['reachable'] else 'OFFLINE'}")

    if result["reachable"]:
        print(f"Latency   : {result['latency']} ms")
        print(f"Loss      : {result['packet_loss']}%")


def main():
    print("=" * 40)
    print("       NETWORK SECURITY MONITOR")
    print("=" * 40)
    print()

    network_info = get_network_info()

    display_network_info(network_info)
    display_connectivity(network_info)
    display_internet_connectivity()

    print()
    print("=" * 40)


if __name__ == "__main__":
    main()