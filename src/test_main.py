import main


def test_display_network_info(capsys):
    network_info = {
        "hostname": "TEST-PC",
        "ip_address": "192.168.1.10",
        "interface": "Ethernet",
        "gateway": "192.168.1.1",
        "network": "192.168.1.0/24",
    }

    main.display_network_info(network_info)

    output = capsys.readouterr().out

    assert "SYSTEM INFORMATION" in output
    assert "TEST-PC" in output
    assert "192.168.1.10" in output
    assert "Ethernet" in output
    assert "192.168.1.1" in output
    assert "192.168.1.0/24" in output


def test_display_connectivity_when_gateway_is_online(monkeypatch, capsys):
    network_info = {"gateway": "192.168.1.1"}

    monkeypatch.setattr(
        main,
        "ping_host",
        lambda host: {
            "host": host,
            "reachable": True,
            "latency": 12.5,
            "packet_loss": 0,
        },
    )

    main.display_connectivity(network_info)

    output = capsys.readouterr().out

    assert "CONNECTIVITY" in output
    assert "192.168.1.1" in output
    assert "ONLINE" in output
    assert "12.5 ms" in output
    assert "0%" in output


def test_display_connectivity_when_gateway_is_offline(monkeypatch, capsys):
    network_info = {"gateway": "192.168.1.1"}

    monkeypatch.setattr(
        main,
        "ping_host",
        lambda host: {
            "host": host,
            "reachable": False,
            "latency": None,
            "packet_loss": 100,
        },
    )

    main.display_connectivity(network_info)

    output = capsys.readouterr().out

    assert "CONNECTIVITY" in output
    assert "OFFLINE" in output
    assert "Latency" not in output
    assert "Loss" not in output


def test_display_internet_connectivity_when_online(monkeypatch, capsys):
    monkeypatch.setattr(
        main,
        "ping_host",
        lambda host: {
            "host": host,
            "reachable": True,
            "latency": 20,
            "packet_loss": 5,
        },
    )

    main.display_internet_connectivity()

    output = capsys.readouterr().out

    assert "INTERNET CONNECTIVITY" in output
    assert "1.1.1.1" in output
    assert "ONLINE" in output
    assert "20 ms" in output
    assert "5%" in output


def test_display_internet_connectivity_when_offline(monkeypatch, capsys):
    monkeypatch.setattr(
        main,
        "ping_host",
        lambda host: {
            "host": host,
            "reachable": False,
            "latency": None,
            "packet_loss": 100,
        },
    )

    main.display_internet_connectivity()

    output = capsys.readouterr().out

    assert "INTERNET CONNECTIVITY" in output
    assert "1.1.1.1" in output
    assert "OFFLINE" in output
    assert "Latency" not in output
    assert "Loss" not in output


def test_main_runs_network_and_connectivity_checks(monkeypatch, capsys):
    network_info = {
        "hostname": "TEST-PC",
        "ip_address": "192.168.1.10",
        "interface": "Ethernet",
        "gateway": "192.168.1.1",
        "network": "192.168.1.0/24",
    }

    pinged_hosts = []

    monkeypatch.setattr(main, "get_network_info", lambda: network_info)

    def fake_ping(host):
        pinged_hosts.append(host)
        return {
            "host": host,
            "reachable": True,
            "latency": 10,
            "packet_loss": 0,
        }

    monkeypatch.setattr(main, "ping_host", fake_ping)

    main.main()

    output = capsys.readouterr().out

    assert "NETWORK SECURITY MONITOR" in output
    assert "SYSTEM INFORMATION" in output
    assert "CONNECTIVITY" in output
    assert "INTERNET CONNECTIVITY" in output
    assert "TEST-PC" in output
    assert pinged_hosts == ["192.168.1.1", "1.1.1.1"]


def test_standalone_execution(monkeypatch, capsys):
    import runpy

    import network
    import monitor

    monkeypatch.setattr(
        network,
        "get_network_info",
        lambda: {
            "hostname": "TEST-PC",
            "ip_address": "192.168.1.10",
            "interface": "Ethernet",
            "gateway": "192.168.1.1",
            "network": "192.168.1.0/24",
        },
    )

    monkeypatch.setattr(
        monitor,
        "ping_host",
        lambda host: {
            "host": host,
            "reachable": False,
            "latency": None,
            "packet_loss": 100,
        },
    )

    runpy.run_path("src/main.py", run_name="__main__")

    output = capsys.readouterr().out

    assert "NETWORK SECURITY MONITOR" in output
    assert "TEST-PC" in output
    assert "INTERNET CONNECTIVITY" in output
