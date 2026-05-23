"""
Jitter Engine — Evasion Module
================================
Implements timing randomization to evade burst-based rate limiting.

Demonstrates: Low-and-slow attack patterns that bypass request-rate detection.
"""

import asyncio
import random
import time
from typing import Optional


class JitterEngine:
    """
    Adds human-like timing jitter between requests.

    Evasion strategies:
    - Gaussian jitter: Natural bell-curve distribution
    - Uniform jitter:  Random flat distribution
    - Adaptive jitter: Increases delay on 429 responses
    - Burst pattern:   Small groups with longer pauses between groups
    """

    def __init__(
        self,
        min_delay:   float = 0.1,
        max_delay:   float = 1.0,
        strategy:    str   = "uniform",
        burst_size:  int   = 5,
        burst_pause: float = 3.0,
    ):
        self.min_delay   = min_delay
        self.max_delay   = max_delay
        self.strategy    = strategy
        self.burst_size  = burst_size
        self.burst_pause = burst_pause
        self._request_count = 0
        self._adaptive_multiplier = 1.0

    def _compute_delay(self) -> float:
        """Compute the next delay based on the active strategy."""
        if self.strategy == "gaussian":
            mean  = (self.min_delay + self.max_delay) / 2
            sigma = (self.max_delay - self.min_delay) / 4
            delay = random.gauss(mean, sigma)
            return max(self.min_delay, min(self.max_delay, delay))

        elif self.strategy == "burst":
            self._request_count += 1
            if self._request_count % self.burst_size == 0:
                return self.burst_pause  # Pause between bursts
            return random.uniform(self.min_delay / 10, self.min_delay)

        elif self.strategy == "adaptive":
            return random.uniform(self.min_delay, self.max_delay) * self._adaptive_multiplier

        else:  # uniform
            return random.uniform(self.min_delay, self.max_delay)

    async def wait(self) -> float:
        """Async wait with computed jitter. Returns actual delay used."""
        delay = self._compute_delay()
        await asyncio.sleep(delay)
        return delay

    def wait_sync(self) -> float:
        """Synchronous wait with computed jitter."""
        delay = self._compute_delay()
        time.sleep(delay)
        return delay

    def on_rate_limited(self) -> None:
        """Called when a 429 is received — increases adaptive delay."""
        if self.strategy == "adaptive":
            self._adaptive_multiplier = min(self._adaptive_multiplier * 1.5, 10.0)

    def on_success(self) -> None:
        """Called on successful attempt — gradually reduces adaptive delay."""
        if self.strategy == "adaptive":
            self._adaptive_multiplier = max(self._adaptive_multiplier * 0.9, 1.0)


def uniform_jitter(min_s: float, max_s: float) -> float:
    """Simple uniform random jitter (convenience function)."""
    return random.uniform(min_s, max_s)


async def async_jitter(min_s: float, max_s: float) -> None:
    """Async sleep with uniform jitter."""
    await asyncio.sleep(random.uniform(min_s, max_s))
