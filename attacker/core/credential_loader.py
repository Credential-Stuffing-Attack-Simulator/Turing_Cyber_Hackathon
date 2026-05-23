"""
Credential Loader — Core Module
Loads and validates credential pairs from flat-file wordlists.
"""

from pathlib import Path
from typing import List, Tuple


def load_credentials(path: str) -> List[Tuple[str, str]]:
    """
    Load credential pairs from a flat text file.

    Format:
        username:password
        # Lines starting with # are ignored

    Returns:
        List of (username, password) tuples
    """
    credentials = []
    file_path   = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Credential file not found: {path}")

    with file_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                print(f"[!] Skipping malformed line {line_no}: {line!r}")
                continue
            username, password = line.split(":", 1)
            username = username.strip()
            password = password.strip()
            if username and password:
                credentials.append((username, password))

    return credentials
