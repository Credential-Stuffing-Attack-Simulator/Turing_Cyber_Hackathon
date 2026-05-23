"""
Session Rotator — Evasion Module
===================================
Rotates HTTP session cookies and request tokens to evade
session-based detection and tracking.

Demonstrates: Session variation as an evasion technique.
"""

import random
import string
import uuid
from http.cookiejar import CookieJar
from typing import Dict, Optional


def _random_token(length: int = 32) -> str:
    """Generate a random alphanumeric token."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def _random_session_id() -> str:
    """Generate a session ID resembling common web framework formats."""
    return uuid.uuid4().hex


class SessionRotator:
    """
    Manages session/cookie rotation to evade session-tracking defenses.

    In real attacks, session rotation:
    - Prevents correlation of attempts by session ID
    - Bypasses per-session rate limiting
    - Defeats simple bot detection based on session continuity
    """

    def __init__(self, rotate_every: int = 1):
        """
        Args:
            rotate_every: Number of requests before rotating session.
                         1 = rotate on every request (maximum evasion)
        """
        self._rotate_every    = rotate_every
        self._request_count   = 0
        self._current_session = self._new_session()

    def _new_session(self) -> Dict[str, str]:
        """Generate a fresh session context."""
        return {
            "session_id":  _random_session_id(),
            "csrf_token":  _random_token(24),
            "request_id":  str(uuid.uuid4()),
            "client_id":   _random_token(16),
        }

    def next_session(self) -> Dict[str, str]:
        """Return current session, rotating if threshold reached."""
        self._request_count += 1
        if self._request_count % self._rotate_every == 0:
            self._current_session = self._new_session()
        return self._current_session

    def build_headers(self) -> Dict[str, str]:
        """Build session-related request headers."""
        sess = self.next_session()
        return {
            "X-Request-ID":    sess["request_id"],
            "X-Client-ID":     sess["client_id"],
            "X-CSRF-Token":    sess["csrf_token"],
            "X-Session-Token": sess["session_id"],
        }

    def build_cookies(self) -> Dict[str, str]:
        """Build rotated cookie dict."""
        sess = self.next_session()
        return {
            "session":    sess["session_id"],
            "csrf_token": sess["csrf_token"],
        }


# Module-level convenience instance
_default_rotator = SessionRotator(rotate_every=1)


def get_session_headers() -> Dict[str, str]:
    return _default_rotator.build_headers()


def get_fresh_cookies() -> Dict[str, str]:
    return _default_rotator.build_cookies()
