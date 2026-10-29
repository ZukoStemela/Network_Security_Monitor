import json

import device_store


def test_load_known_devices_returns_empty_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        device_store, "DATA_FILE", str(tmp_path / "missing.json")
    )

    assert device_store.load_known_devices() == []


def test_load_known_devices_reads_json(tmp_path, monkeypatch):
    data_file = tmp_path / "known_devices.json"
    devices = [{"ip_address": "192.168.1.10", "is_gateway": False}]
    data_file.write_text(json.dumps(devices), encoding="utf-8")

    monkeypatch.setattr(device_store, "DATA_FILE", str(data_file))

    assert device_store.load_known_devices() == devices


def test_save_known_devices_creates_directory(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_file = data_dir / "known_devices.json"

    monkeypatch.setattr(device_store, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(device_store, "DATA_FILE", str(data_file))

    devices = [{"ip_address": "192.168.1.10"}]
    device_store.save_known_devices(devices)

    assert data_dir.exists()
    assert json.loads(data_file.read_text(encoding="utf-8")) == devices


def test_save_known_devices_writes_formatted_json(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    data_file = data_dir / "known_devices.json"

    monkeypatch.setattr(device_store, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(device_store, "DATA_FILE", str(data_file))

    device_store.save_known_devices([{"name": "Test device"}])

    content = data_file.read_text(encoding="utf-8")

    assert json.loads(content) == [{"name": "Test device"}]
    assert "\n" in content
