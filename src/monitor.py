import subprocess
import re


def ping_host(host):
    result = subprocess.run(
        ["ping", "-c", "4", "-W", "2", host],
        capture_output=True,
        text=True
    )

    output = result.stdout

    if result.returncode != 0:
        return {
            "host": host,
            "reachable": False,
            "latency": None,
            "packet_loss": None
        }

    latency = re.search(
        r"rtt min/avg/max/mdev = [\d.]+/([\d.]+)",
        output
    )

    packet_loss = re.search(
        r"(\d+(?:\.\d+)?)% packet loss",
        output
    )

    return {
        "host": host,
        "reachable": True,
        "latency": float(latency.group(1)) if latency else None,
        "packet_loss": float(packet_loss.group(1)) if packet_loss else None
    }

if __name__ == "__main__":
    gateway_result = ping_host("172.30.4.1")
    internet_result = ping_host("1.1.1.1")

    print("Connectivity Test")
    print("------------------")

    print("\nGateway")
    print(f"Host        : {gateway_result['host']}")
    print(f"Reachable   : {gateway_result['reachable']}")
    print(f"Latency     : {gateway_result['latency']} ms")
    print(f"Packet Loss : {gateway_result['packet_loss']}%")

    print("\nInternet")
    print(f"Host        : {internet_result['host']}")
    print(f"Reachable   : {internet_result['reachable']}")
    print(f"Latency     : {internet_result['latency']} ms")
    print(f"Packet Loss : {internet_result['packet_loss']}%")