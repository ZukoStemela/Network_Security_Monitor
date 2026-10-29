
import platform
import re
import subprocess

def ping_host(host):
    """Ping a host and extract reachability, latency, and packet loss."""
    import re
    import platform
    import subprocess

    if platform.system().lower() == "windows":
        command = ["ping", "-n", "4", "-w", "2000", host]
    else:
        command = ["ping", "-c", "4", "-W", "2", host]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=12,
        )
    except (subprocess.TimeoutExpired, OSError):
        return {
            "host": host,
            "reachable": False,
            "latency": None,
            "packet_loss": None,
        }

    output = (
        (getattr(result, "stdout", "") or "")
        + "\n"
        + (getattr(result, "stderr", "") or "")
    )

    packet_loss = None
    loss_match = re.search(
        r"(\d+(?:\.\d+)?)%\s*packet loss",
        output,
        re.IGNORECASE,
    )
    if loss_match:
        packet_loss = float(loss_match.group(1))

    latency = None
    latency_match = re.search(
        r"(?:rtt|round-trip)\s+min/avg/max"
        r"(?:/mdev|/stddev)?\s*=\s*"
        r"[\d.]+/([\d.]+)/",
        output,
        re.IGNORECASE,
    )
    if latency_match:
        latency = float(latency_match.group(1))

    return {
        "host": host,
        "reachable": result.returncode == 0,
        "latency": latency,
        "packet_loss": packet_loss,
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
