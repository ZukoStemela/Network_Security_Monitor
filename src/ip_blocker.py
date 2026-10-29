"""Simulated IP blocking for security testing."""

import ipaddress


class IPBlocker:
    """Maintain a blocklist and check simulated network access."""

    def __init__(self):
        self.blocked_ips = set()

    def _validate_ip(self, ip_address):
        try:
            return str(ipaddress.ip_address(ip_address))
        except ValueError:
            raise ValueError("Invalid IP address.") from None

    def block_ip(self, ip_address):
        """Block an IP address. Return True if newly blocked."""
        ip_address = self._validate_ip(ip_address)

        if ip_address in self.blocked_ips:
            return False

        self.blocked_ips.add(ip_address)
        return True

    def unblock_ip(self, ip_address):
        """Remove an IP from the blocklist."""
        ip_address = self._validate_ip(ip_address)

        if ip_address not in self.blocked_ips:
            return False

        self.blocked_ips.remove(ip_address)
        return True

    def is_blocked(self, ip_address):
        """Check whether an IP address is blocked."""
        ip_address = self._validate_ip(ip_address)
        return ip_address in self.blocked_ips

    def allow_traffic(self, ip_address):
        """Simulate an access-control decision."""
        return not self.is_blocked(ip_address)
