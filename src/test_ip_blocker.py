import pytest

from ip_blocker import IPBlocker


def test_block_ip():
    blocker = IPBlocker()

    assert blocker.block_ip("192.168.1.50") is True
    assert blocker.is_blocked("192.168.1.50") is True


def test_duplicate_ip_is_not_added_twice():
    blocker = IPBlocker()

    assert blocker.block_ip("192.168.1.50") is True
    assert blocker.block_ip("192.168.1.50") is False
    assert len(blocker.blocked_ips) == 1


def test_unblock_ip():
    blocker = IPBlocker()
    blocker.block_ip("192.168.1.50")

    assert blocker.unblock_ip("192.168.1.50") is True
    assert blocker.is_blocked("192.168.1.50") is False


def test_unblock_unknown_ip():
    blocker = IPBlocker()

    assert blocker.unblock_ip("192.168.1.60") is False


def test_allowed_ip_can_access_network():
    blocker = IPBlocker()

    assert blocker.allow_traffic("192.168.1.20") is True


def test_blocked_ip_is_denied_access():
    blocker = IPBlocker()
    blocker.block_ip("192.168.1.50")

    assert blocker.allow_traffic("192.168.1.50") is False


@pytest.mark.parametrize(
    "ip_address",
    ["invalid", "192.168.1.999", ""],
)
def test_invalid_ip_is_rejected(ip_address):
    blocker = IPBlocker()

    with pytest.raises(ValueError):
        blocker.block_ip(ip_address)


def test_invalid_ip_cannot_be_checked():
    blocker = IPBlocker()

    with pytest.raises(ValueError):
        blocker.is_blocked("not-an-ip")
