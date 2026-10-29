from scanner import scan_network
from network import get_network_info
from baseline import detect_new_devices, update_baseline


def main():
    network_info = get_network_info()

    if not network_info["network"]:
        print("Could not determine the local network. Scan cancelled.")
        return

    print("Scanning local network...")
    devices = scan_network(
        network_info["network"],
        network_info["gateway"],
    )

    new_devices = detect_new_devices(devices)

    if new_devices:
        print("\nNEW DEVICES DETECTED")
        print("---------------------")

        for device in new_devices:
            print(
                f"IP: {device['ip_address']} "
                f"| MAC: {device['mac_address']}"
            )

        print("\nOnly approve devices you recognize " "and trust.")
    else:
        print("\nNo new devices detected.")

    print(f"\nDevices in current scan: {len(devices)}")

    print(
        "\nWARNING: Updating the baseline replaces "
        "the saved list with the current scan."
    )
    print("Devices that are offline may be removed.")

    confirmation = input(
        "\nType UPDATE to replace the saved baseline, "
        "or press Enter to leave it unchanged: "
    ).strip()

    if confirmation == "UPDATE":
        if new_devices:
            approval = input(
                "Confirm that you recognize and trust "
                "all newly detected devices. "
                "Type TRUST to continue: "
            ).strip()

            if approval != "TRUST":
                print("Baseline unchanged.")
                return

        update_baseline(devices)
        print("Baseline updated successfully.")
    else:
        print("Baseline unchanged.")


if __name__ == "__main__":
    main()
