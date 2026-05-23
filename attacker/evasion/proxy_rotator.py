"""
Proxy Rotator — Evasion Module
================================
Simulates distributed attacker infrastructure by rotating
X-Forwarded-For IP addresses on each request.

Demonstrates: Bypass of naive IP-based rate limiting (MITRE T1036)
"""

import random
from typing import Dict


class ProxyRotator:
    """
    Simulates proxy/IP rotation by generating spoofed X-Forwarded-For headers.

    In the real world, attackers use:
    - Residential proxy networks
    - VPN exit nodes
    - Botnets
    - Cloud provider IPs

    This simulation uses synthetic IPs in RFC-1918 private ranges
    to demonstrate the bypass concept safely.
    """

    # Simulated "proxy pool" IP ranges
    _RANGES = [
        (10, 0,   0,   1,   10, 255, 254, 254),   # 10.x.x.x
        (172, 16, 0,   1,   172, 31, 254, 254),    # 172.16-31.x.x
        (192, 168, 0,  1,   192, 168, 254, 254),   # 192.168.x.x
    ]

    def __init__(self, pool_size: int = 1000):
        self._pool = self._generate_pool(pool_size)
        self._index = 0

    def _generate_pool(self, size: int):
        """Pre-generate a pool of fake IP addresses."""
        pool = []
        for _ in range(size):
            r = random.choice(self._RANGES)
            ip = f"{r[0]}.{random.randint(r[1], r[4])}.{random.randint(r[2], r[5])}.{random.randint(r[3], r[6])}"
            pool.append(ip)
        random.shuffle(pool)
        return pool

    def next_ip(self) -> str:
        """Return the next IP from the rotation pool (round-robin)."""
        ip = self._pool[self._index % len(self._pool)]
        self._index += 1
        return ip

    def random_ip(self) -> str:
        """Return a random IP from the pool."""
        return random.choice(self._pool)

    def build_headers(self) -> Dict[str, str]:
        """Build all XFF-related bypass headers."""
        ip = self.next_ip()
        return {
            "X-Forwarded-For":  ip,
            "X-Real-IP":        ip,
            "X-Originating-IP": ip,
            "X-Remote-IP":      ip,
            "X-Remote-Addr":    ip,
            "Forwarded":        f"for={ip}",
            "X-Proxy-Rotated":  "true",
        }


# Module-level convenience instance
_default_rotator = ProxyRotator()


def get_next_ip() -> str:
    return _default_rotator.next_ip()


def get_xff_headers() -> Dict[str, str]:
    return _default_rotator.build_headers()
