import json
import os


DATA_FILE = "../data/known_devices.json"


def load_known_devices():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_known_devices(devices):
    with open(DATA_FILE, "w") as file:
        json.dump(devices, file, indent=4)