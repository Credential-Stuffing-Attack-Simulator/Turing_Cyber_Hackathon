"""
User-Agent Manager — Evasion Module
=====================================
Rotates browser fingerprints to evade User-Agent-based bot detection.

Demonstrates: Browser impersonation and masquerading (MITRE T1036)
"""

import random
from typing import Optional

try:
    from fake_useragent import UserAgent as _FakeUA
    _fake_ua = _FakeUA()
except Exception:
    _fake_ua = None


# Curated browser fingerprint pool — realistic modern browser UAs
BROWSER_FINGERPRINTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Firefox on Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # Mobile Chrome
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.82 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

# Baseline UA (used in non-rotation profiles)
BASELINE_UA = BROWSER_FINGERPRINTS[0]


class UserAgentManager:
    """Manages User-Agent rotation with optional fake_useragent integration."""

    def __init__(self, use_fake_ua: bool = True):
        self._use_fake = use_fake_ua and _fake_ua is not None
        self._pool     = BROWSER_FINGERPRINTS[:]
        random.shuffle(self._pool)
        self._index    = 0

    def next_ua(self) -> str:
        """Return the next User-Agent in rotation."""
        if self._use_fake:
            try:
                return _fake_ua.random
            except Exception:
                pass
        ua = self._pool[self._index % len(self._pool)]
        self._index += 1
        return ua

    def random_ua(self) -> str:
        """Return a random User-Agent."""
        if self._use_fake:
            try:
                return _fake_ua.random
            except Exception:
                pass
        return random.choice(self._pool)

    def baseline_ua(self) -> str:
        """Return the consistent baseline UA (non-rotation mode)."""
        return BASELINE_UA

    def build_headers(self, rotate: bool = True) -> dict:
        """Build User-Agent related headers."""
        ua = self.next_ua() if rotate else self.baseline_ua()
        headers = {
            "User-Agent":     ua,
            "Accept":         "application/json, text/plain, */*",
            "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8", "en;q=0.5"]) if rotate else "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        }
        if rotate:
            headers["X-UA-Rotated"] = "true"
        return headers


# Module-level convenience instance
_default_manager = UserAgentManager()


def get_random_ua() -> str:
    return _default_manager.next_ua()


def get_ua_headers(rotate: bool = True) -> dict:
    return _default_manager.build_headers(rotate)
