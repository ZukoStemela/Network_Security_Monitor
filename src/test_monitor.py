import platform
import re
import subprocess


def ping_host(host):
    """Ping a host and return reachability, latency, and packet loss."""
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
            timeout=12,
        )
    except (subprocess.TimeoutExpired, OSError):
        return {
            "host": host,
            "reachable": False,
            "latency": None,
            "packet_loss": None,
        }

    stdout = getattr(result, "stdout", "") or ""
    stderr = getattr(result, "stderr", "") or ""
    output = stdout + "\n" + stderr

    # Determine whether the host responded.
    reachable = result.returncode == 0

    # Extract packet loss.
    packet_loss = None

    if system == "windows":
        loss_match = re.search(
            r"\((\d+(?:\.\d+)?)%\s*loss\)",
            output,
            re.IGNORECASE,
        )

        if not loss_match:
            loss_match = re.search(
                r"Lost\s*=\s*\d+\s*\((\d+(?:\.\d+)?)%\s*loss\)",
                output,
                re.IGNORECASE,
            )

        if loss_match:
            packet_loss = float(loss_match.group(1))

        else:
            sent_received = re.search(
                r"Sent\s*=\s*(\d+),\s*"
                r"Received\s*=\s*(\d+),\s*"
                r"Lost\s*=\s*(\d+)",
                output,
                re.IGNORECASE,
            )

            if sent_received:
                sent = int(sent_received.group(1))
                lost = int(sent_received.group(3))

                if sent > 0:
                    packet_loss = lost / sent * 100

    else:
        loss_match = re.search(
            r"(\d+(?:\.\d+)?)%\s*packet loss",
            output,
            re.IGNORECASE,
        )

        if loss_match:
            packet_loss = float(loss_match.group(1))

    # Extract average latency.
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

    else:
        # Windows normally reports "Average = 12ms".
        windows_latency = re.search(
            r"Average\s*=\s*(\d+(?:\.\d+)?)\s*ms",
            output,
            re.IGNORECASE,
        )

        if windows_latency:
            latency = float(windows_latency.group(1))

        else:
            # Fallback for individual responses such as "time=12.5 ms".
            times = re.findall(
                r"time\s*[=<]\s*(\d+(?:\.\d+)?)\s*ms",
                output,
                re.IGNORECASE,
            )

            if times:
                latency_values = [float(value) for value in times]
                latency = sum(latency_values) / len(latency_values)

    # If the output doesn't report packet loss, use a safe fallback.
    if packet_loss is None and result.returncode == 0:
        packet_loss = 0.0
    elif packet_loss is None and result.returncode != 0:
        packet_loss = 100.0

    return {
        "host": host,
        "reachable": reachable,
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
        ("Internet", internet_result),
    ]:
        print(f"\n{label}")
        print(f"Host        : {result['host']}")
        print(f"Reachable   : {result['reachable']}")
        print(f"Latency     : {result['latency']} ms")
        print(f"Packet Loss : {result['packet_loss']}%")
