
import platform
import re
import subprocess


def ping_host(host):
    system = platform.system().lower()

    if system == "windows":
        command = ["ping", "-n", "4", "-w", "2000", host]
    else:
        command = ["ping", "-c", "4", "-W", "2", host]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=12
        )
    except (subprocess.TimeoutExpired, OSError):
        return {
            "host": host,
            "reachable": False,
            "latency": None,
            "packet_loss": None
        }

    output = result.stdout + result.stderr

    if system == "windows":
        latency_match = re.search(
            r"Average\s*=\s*(\d+)\s*ms",
            output,
            re.IGNORECASE
        )
        loss_match = re.search(
            r"\((\d+)%\s*loss\)",
            output,
            re.IGNORECASE
        )
    else:
        latency_match = re.search(
            r"(?:rtt|round-trip).*?=\s*[\d.]+/([\d.]+)",
            output
        )
        loss_match = re.search(
            r"([\d.]+)%\s*packet loss",
            output
        )

    reachable = result.returncode == 0

    return {
        "host": host,
        "reachable": reachable,
        "latency": (
            float(latency_match.group(1))
            if latency_match
            else None
        ),
        "packet_loss": (
            float(loss_match.group(1))
            if loss_match
            else (0.0 if reachable else 100.0)
        )
    }


if __name__ == "__main__":
    gateway_result = ping_host("172.30.4.1")
    internet_result = ping_host("1.1.1.1")

    print("Connectivity Test")
    print("------------------")

    for label, result in [
        ("Gateway", gateway_result),
        ("Internet", internet_result)
    ]:
        print(f"\n{label}")
        print(f"Host        : {result['host']}")
        print(f"Reachable   : {result['reachable']}")
        print(f"Latency     : {result['latency']} ms")
        print(f"Packet Loss : {result['packet_loss']}%")
