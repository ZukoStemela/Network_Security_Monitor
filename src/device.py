class Device:

    def __init__(self, ip_address, is_gateway=False, mac_address=None):
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.is_gateway = is_gateway
        self.status = "ACTIVE"

    def get_info(self):
        return {
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "status": self.status,
            "is_gateway": self.is_gateway
        }