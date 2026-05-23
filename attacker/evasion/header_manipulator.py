"""
Header Manipulator — Evasion Module
======================================
Generates randomized, realistic HTTP request headers to evade
header-fingerprinting and bot detection systems.

Demonstrates: Request disguising and header variation (MITRE T1036)
"""

import random
from typing import Dict


_ACCEPT_VALUES = [
    "application/json, text/plain, */*",
    "application/json",
    "*/*",
    "application/json;charset=utf-8",
]

_ACCEPT_LANGUAGE_VALUES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.8,en-US;q=0.6",
    "en-US,en;q=0.9,fr;q=0.7",
    "en;q=0.9",
    "en-US",
]

_ACCEPT_ENCODING_VALUES = [
    "gzip, deflate, br",
    "gzip, deflate",
    "br, gzip",
    "identity",
]

_CONNECTION_VALUES = [
    "keep-alive",
    "close",
]

_DEVICE_IDS = [
    "web-browser-{:08x}".format(random.randint(0, 0xFFFFFFFF)),
    "mobile-{:08x}".format(random.randint(0, 0xFFFFFFFF)),
    "desktop-{:08x}".format(random.randint(0, 0xFFFFFFFF)),
]

_ORIGINS = [
    "https://app.example.com",
    "https://portal.bank.com",
    "https://secure.company.io",
    "https://login.service.net",
    None,  # No origin (common for API clients)
]


class HeaderManipulator:
    """
    Generates randomized, realistic HTTP headers to evade detection.

    Real attackers use header manipulation to:
    - Defeat bot detection that checks for consistent headers
    - Spoof browser environments
    - Bypass WAF rules that check for suspicious header patterns
    """

    def __init__(self, rotate: bool = True):
        self._rotate = rotate

    def build_baseline_headers(self) -> Dict[str, str]:
        """Return consistent, normal-looking headers (baseline profile)."""
        return {
            "Accept":           "application/json, text/plain, */*",
            "Accept-Language":  "en-US,en;q=0.9",
            "Accept-Encoding":  "gzip, deflate, br",
            "Connection":       "keep-alive",
            "Cache-Control":    "no-cache",
            "Content-Type":     "application/json",
        }

    def build_evasion_headers(self) -> Dict[str, str]:
        """Return randomized headers to evade fingerprinting."""
        headers = {
            "Accept":           random.choice(_ACCEPT_VALUES),
            "Accept-Language":  random.choice(_ACCEPT_LANGUAGE_VALUES),
            "Accept-Encoding":  random.choice(_ACCEPT_ENCODING_VALUES),
            "Connection":       random.choice(_CONNECTION_VALUES),
            "Content-Type":     "application/json",
        }

        # Randomly include optional headers
        if random.random() > 0.5:
            headers["Cache-Control"] = random.choice(["no-cache", "no-store", "max-age=0"])

        if random.random() > 0.7:
            headers["X-Device-Id"] = random.choice(_DEVICE_IDS)

        origin = random.choice(_ORIGINS)
        if origin:
            headers["Origin"]  = origin
            headers["Referer"] = origin + "/login"

        if random.random() > 0.8:
            headers["DNT"] = "1"

        if random.random() > 0.9:
            headers["Sec-Fetch-Site"] = "same-origin"
            headers["Sec-Fetch-Mode"] = "cors"
            headers["Sec-Fetch-Dest"] = "empty"

        return headers

    def get_headers(self) -> Dict[str, str]:
        """Return headers based on current mode."""
        if self._rotate:
            return self.build_evasion_headers()
        return self.build_baseline_headers()


# Module-level convenience instance
_default_manipulator = HeaderManipulator(rotate=True)


def get_evasion_headers() -> Dict[str, str]:
    return _default_manipulator.build_evasion_headers()


def get_baseline_headers() -> Dict[str, str]:
    return _default_manipulator.build_baseline_headers()
