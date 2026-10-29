# Network Security Monitor (NSM)

A lightweight Python-based network monitoring tool that discovers active devices on a local network, checks connectivity, maintains a baseline of known devices, and generates alerts when unexpected devices are detected.

## Overview

Network Security Monitor (NSM) is a defensive cybersecurity project designed to help users understand activity on a local IPv4 network.

The application collects local network information, discovers reachable hosts, checks connectivity, and compares discovered devices against a saved baseline. Potentially new devices are reported so that the user can investigate them.

NSM also includes a mock demonstration mode for testing the alert workflow without scanning a live network.

## Features

- **Network discovery:** Identify active hosts on a local IPv4 network.
- **Network information:** Display the local hostname, IP address, network interface, gateway, and network range.
- **Connectivity monitoring:** Check host reachability, latency, and packet loss.
- **Device identification:** Collect IP and MAC address information where available.
- **Baseline management:** Save and compare known devices using a JSON file.
- **New-device detection:** Identify devices that are not present in the saved baseline.
- **Security alerts:** Generate readable alerts containing device information and role.
- **Interactive baseline protection:** Require explicit confirmation before replacing the saved baseline and additional confirmation when new devices are detected.
- **Mock demonstration:** Demonstrate the detection and alert workflow without live network scanning.
- **Automated testing:** Use pytest to verify application behaviour.
- **Code quality:** Use Black and Flake8 for formatting and linting.

## Project structure

```text
Network_Security_Monitor/
├── data/
│   └── known_devices.json
├── src/
│   ├── alerts.py
│   ├── baseline.py
│   ├── baseline_check.py
│   ├── demo.py
│   ├── device.py
│   ├── device_store.py
│   ├── main.py
│   ├── monitor.py
│   ├── network.py
│   ├── scanner.py
│   └── test_*.py
├── requirements.txt
└── README.md
```

### Main components

| File | Purpose |
|---|---|
| `src/network.py` | Retrieves local network information. |
| `src/scanner.py` | Discovers active hosts on the local network. |
| `src/device.py` | Represents discovered network devices. |
| `src/device_store.py` | Loads and saves device data. |
| `src/baseline.py` | Compares discovered devices with the saved baseline. |
| `src/baseline_check.py` | Runs the baseline-aware scan and handles confirmation prompts. |
| `src/alerts.py` | Formats alerts for newly detected devices. |
| `src/monitor.py` | Checks host connectivity, latency, and packet loss. |
| `src/main.py` | Displays network information and connectivity results. |
| `src/demo.py` | Runs the mock demonstration workflow. |
| `data/known_devices.json` | Stores the baseline of known devices. |

## Requirements

- Python 3.10 or later.
- Git, for cloning the repository.
- Network access and appropriate permissions for live network discovery.
- Operating-system networking utilities where required, such as `ping`, `arp`, and `ip`.
- Python packages listed in `requirements.txt`.

Some discovery results may vary depending on the operating system, network configuration, firewall rules, and device availability.

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/ZukoStemela/Network_Security_Monitor.git
cd Network_Security_Monitor
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## Usage

Run commands from the project's root directory.

### 1. Display network information and connectivity

```powershell
python .\src\main.py
```

Displays available local network details and connectivity information.

### 2. Scan for active devices

```powershell
python .\src\scanner.py
```

Runs the network discovery component to identify reachable devices.

### 3. Check for unexpected devices

```powershell
python .\src\baseline_check.py
```

This workflow compares the current discovery results with the saved baseline.

**Baseline safety process:**

1. Review the detected devices and any reported changes.
2. Type `UPDATE` when prompted to confirm that you want to replace the saved baseline.
3. If new devices are detected, review them and type `TRUST` only if you have verified that all newly detected devices are recognized and authorized.
4. If you decline a confirmation, the baseline remains unchanged.

Updating the baseline replaces the saved device list. Devices that are offline during a scan may be omitted from the new baseline. Review the results carefully before approving an update.

### 4. Run the mock demonstration

```powershell
python .\src\demo.py --mock
```

Demonstrates the monitoring and alert workflow using simulated data, without performing live network discovery.

The mock demonstration is intended for presentations, development, and testing.

## Baseline management

The baseline is stored in:

```text
data/known_devices.json
```

A baseline entry may contain fields such as the following:

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

This is an illustrative example; actual entries depend on the application's device data format.

The application compares discovered devices with the saved baseline. A newly detected MAC address can indicate a change in the network and may generate an alert.

**A new device is not automatically proof of malicious activity.** It may be a legitimate phone, laptop, printer, or another device. Investigate unfamiliar devices before deciding whether to trust them.

## Testing

The project uses pytest for automated tests.

Run the complete test suite:

```powershell
python -m pytest -q
```

Check code style with Flake8:

```powershell
python -m flake8 src
```

Format Python files with Black when needed:

```powershell
python -m black --line-length 79 src
```

### Current test status

The latest recorded test run completed successfully:

```text
95 passed
```

The latest recorded Flake8 check also completed without reporting errors. Run both commands again after making changes to confirm the current state.

## Security and responsible use

- Only scan networks you own or have explicit permission to assess.
- Use the tool for defensive monitoring and authorized security testing.
- Review unfamiliar devices before trusting them.
- Back up important baseline data before replacing it.
- Remember that network discovery is not guaranteed to identify every connected device.
- Treat alerts as indicators that require investigation, not definitive proof of an attack.
- Avoid publishing sensitive network information, including internal IP details, MAC addresses, and device inventories.

## Known limitations

- Host discovery depends on network reachability and operating-system behaviour.
- Firewalls and network isolation may prevent devices from responding to discovery requests.
- MAC address information may be unavailable for some hosts.
- A device's IP address may change over time.
- The baseline is a simple reference list, not a complete intrusion-detection system.
- Mock results are simulated and do not represent actual network activity.

## Future improvements

Potential extensions include:

- A live monitoring dashboard.
- Historical device discovery and event logs.
- Device classification and improved inventory management.
- Configurable alert severity.
- More comprehensive cross-platform testing.
- Exportable monitoring reports.
- Scheduled scans and change notifications.

## Contributing

Contributions and suggestions are welcome.

When modifying the project:

1. Keep changes focused and documented.
2. Add or update tests for new behaviour.
3. Run pytest and Flake8 before committing.
4. Do not include passwords, access tokens, or sensitive network inventories in commits.

## License

No `LICENSE` file is currently documented in this repository. 
