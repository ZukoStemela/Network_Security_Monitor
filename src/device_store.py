import json
import os


# Compute data file path relative to this file, not the current working directory.
ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, "data")
DATA_FILE = os.path.join(DATA_DIR, "known_devices.json")


def load_known_devices():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_known_devices(devices):
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(DATA_FILE, "w") as file:
        json.dump(devices, file, indent=4)