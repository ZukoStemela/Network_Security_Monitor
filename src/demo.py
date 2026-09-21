"""Demo runner for NSM.

Usage:
 - `python src/demo.py --mock` : run a mocked demo (no network calls)
 - `python src/demo.py` : run a live quick-run (may require root/network tools)
"""
import argparse
import json
from alerts import generate_alerts_for_new_devices, print_alerts


def mock_scan():
    # Return two known devices and one new device
    known = [
        {"ip_address": "192.168.1.1", "mac_address": "aa:aa:aa:aa:aa:01", "is_gateway": True},
        {"ip_address": "192.168.1.2", "mac_address": "aa:aa:aa:aa:aa:02", "is_gateway": False},
    ]

    current = known + [
        {"ip_address": "192.168.1.99", "mac_address": "ff:ff:ff:ff:ff:ff", "is_gateway": False}
    ]

    return known, current


def run_mock_demo():
    known, current = mock_scan()

    print("Mock demo: baseline and current scan")
    print("Baseline:")
    print(json.dumps(known, indent=2))
    print("\nCurrent scan:")
    print(json.dumps(current, indent=2))

    new = [d for d in current if d["mac_address"] not in {k["mac_address"] for k in known}]

    alerts = generate_alerts_for_new_devices(new)
    print() 
    print_alerts(alerts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Run a mocked demo")

    args = parser.parse_args()

    if args.mock:
        run_mock_demo()
    else:
        print("Live demo not implemented here. Use --mock for a safe demo.")


if __name__ == "__main__":
    main()
