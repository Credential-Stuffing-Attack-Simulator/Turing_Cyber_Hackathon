"""
Worker Manager — Core Module
Manages async worker pools and attack profile descriptions.
"""

from .attack_engine import PROFILES


def describe_profile(name: str) -> dict:
    """Return profile metadata for a given attack profile name."""
    profile = PROFILES.get(name)
    if not profile:
        return {"error": f"Unknown profile: {name}", "available": list(PROFILES.keys())}
    return {"name": name, **profile}


def list_profiles() -> list:
    """Return all available attack profiles with descriptions."""
    return [
        {"name": name, **data}
        for name, data in PROFILES.items()
    ]
