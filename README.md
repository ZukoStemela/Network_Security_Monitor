(The file `/home/wtc29/student_work/NSM/README.md` exists, but is empty)
# Network Security Monitor (NSM)

Lightweight network security monitoring and baseline scanner for small networks.

## Summary

NSM discovers devices on a network, builds and stores a baseline of expected devices and behavior, and raises alerts when unexpected changes are detected.

Key modules:
- `scanner.py` — network discovery and device probing
- `device.py`, `device_store.py` — device model and persistent store
- `baseline.py` — baseline creation and comparison logic
- `monitor.py`, `alerts.py` — runtime monitoring and alert generation
- `network.py` — network helpers and utilities
- `main.py` — CLI / entrypoint

## Features

- Discover devices via active scanning
- Build a baseline of known devices (`data/known_devices.json`)
- Monitor network changes and emit alerts
- Simple, testable codebase suitable for extension

## Installation

1. Create a Python 3.10+ virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the main script to perform discovery or monitoring (see help output):

```bash
python src/main.py --help
```

Typical flows:
- Build or update the baseline: `python src/baseline.py`
- Run a scan: `python src/scanner.py`
- Start monitoring: `python src/monitor.py`

## Development

- Tests: `python -m pytest -q`
- Linting/formatting: use your preferred tools (e.g., `black`, `flake8`)

## Contributing

Contributions welcome — open an issue or a PR with a clear description and tests when appropriate.

## License

This project does not include a license file. Add a `LICENSE` if you intend to publish under an open-source license.
