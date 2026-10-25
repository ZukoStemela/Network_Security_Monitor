(The file `/home/wtc29/student_work/NSM/README.md` exists, but is empty)
# Network Security Monitor

A lightweight Python-based tool for monitoring a local network, identifying active hosts, comparing the current device list against a saved baseline, and alerting on unexpected changes.

## Overview

Network Security Monitor (NSM) is designed for small home or office networks where it is useful to maintain awareness of connected devices. It gathers local network information, scans the active IPv4 range, resolves device MAC addresses, and compares the results against a trusted baseline stored in `data/known_devices.json`.

The project is intentionally lightweight and script-driven, making it easy to understand, extend, and test. It is useful as a baseline security utility or as a starting point for a more advanced network monitoring system.

## Features

- Detect local hostname, IP address, gateway, interface, and network range
- Discover active devices on the local network
- Ping hosts to check connectivity and latency
- Resolve MAC addresses for known active hosts
- Store a baseline of trusted devices in JSON
- Detect new devices against the stored baseline
- Format human-readable alerts for suspicious or unexpected additions
- Provide a mock demo mode for safe testing without live network access

## Project structure

- `src/network.py` — determines local network information and routing data
- `src/scanner.py` — scans the local network and identifies active hosts
- `src/device.py` — device model used during discovery
- `src/device_store.py` — loads and saves the stored baseline
- `src/baseline.py` — compares scans to known devices and updates the baseline
- `src/alerts.py` — formats detection alerts for output
- `src/monitor.py` — connectivity checks for hosts and gateways
- `src/main.py` — entry point that prints key network and connectivity information
- `src/baseline_check.py` — baseline-aware scan that reports new devices
- `src/demo.py` — mock demo workflow for demonstration purposes
- `data/known_devices.json` — persistent baseline of known devices
- `tests/` — project test suite (via `src/test_*.py` files in this repo)

## Requirements

- Python 3.10+
- Access to local network tools available on the host OS (`ping`, `arp`, `ip`, etc.)
- Optional: a Linux/macOS or Windows environment with networking enabled

## Installation

1. Clone the repository.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Network overview

```bash
python src/main.py
```

This prints local machine information, gateway connectivity, and internet reachability.

### Scan for active hosts

```bash
python src/scanner.py
```

This identifies the devices currently reachable on the local network.

### Detect unexpected devices and update the baseline

```bash
python src/baseline_check.py
```

This compares the latest scan to the stored baseline, displays any new devices, and writes the current scan to `data/known_devices.json`.

### Run the mock demo

```bash
python src/demo.py --mock
```

This demonstrates alert generation without making live network calls.

## Baseline behaviour

The baseline is a JSON list of known devices, with each entry containing values such as:

```json
[
  {
    "ip_address": "192.168.1.10",
    "mac_address": "aa:bb:cc:dd:ee:ff",
    "status": "ACTIVE",
    "is_gateway": false
  }
]
```

Each scan checks whether a device MAC address already exists in the baseline. If a MAC address is new, it is treated as a potential security change and can be surfaced as an alert.

## Development

Run the test suite:

```bash
python -m pytest -q
```

Recommended tooling:

```bash
pip install black flake8
```

## Contributing

Contributions are welcome. If you add new functionality, please include a clear description of the change and ensure relevant tests still pass.

## License

This repository does not currently contain a `LICENSE` file. If you plan to distribute or publish the project, add an appropriate open-source licence before doing so.
