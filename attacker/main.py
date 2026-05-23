"""
Credential Stuffing Attack Controller
=======================================
Cloud-Native Adversary Simulation Platform

AUTHORIZED USE ONLY: This tool is restricted to authorized local
lab environments. External targets are blocked by safety checks.

Usage:
    python main.py --profile baseline
    python main.py --profile ip_rotation --attack-id demo-bypass-1
    python main.py --profile full_evasion --concurrency 10

MITRE ATT&CK: T1110.004, T1036, T1078
"""

import argparse
import asyncio
import os
import sys

from core.attack_engine   import AttackEngine, PROFILES
from core.credential_loader import load_credentials
from core.worker_manager  import list_profiles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Credential Stuffing Adversary Simulation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Profiles:
  baseline    — No bypass; demonstrates rate-limit blocking
  ip_rotation — X-Forwarded-For spoofing bypass
  ua_rotation — User-Agent rotation bypass
  full_evasion — Combined XFF + UA + jitter bypass
  slow_burn   — Low-and-slow burst evasion

Examples:
  python main.py --profile baseline
  python main.py --profile ip_rotation --attack-id demo-xff-01
  python main.py --profile full_evasion --concurrency 8
        """
    )

    parser.add_argument("--target",         default=os.getenv("TARGET_URL",        "http://nginx/"),
                        help="Target URL (default: http://nginx/)")
    parser.add_argument("--credentials",    default=os.getenv("CREDENTIAL_FILE",   "configs/credentials.txt"),
                        help="Path to credentials file")
    parser.add_argument("--profile",        default=os.getenv("ATTACK_PROFILE",    "baseline"),
                        choices=list(PROFILES.keys()),
                        help="Attack profile to use")
    parser.add_argument("--attack-id",      default=os.getenv("ATTACK_ID",         None),
                        help="Unique ID for this attack run (auto-generated if omitted)")
    parser.add_argument("--concurrency",    default=5, type=int,
                        help="Number of concurrent workers")
    parser.add_argument("--min-delay",      default=None, type=float,
                        help="Minimum delay between requests (seconds)")
    parser.add_argument("--max-delay",      default=None, type=float,
                        help="Maximum delay between requests (seconds)")
    parser.add_argument("--timeout",        default=10,   type=int,
                        help="Request timeout (seconds)")
    parser.add_argument("--report-dir",     default=os.getenv("REPORT_DIR",        "/app/reports"),
                        help="Directory for attack reports")
    parser.add_argument("--allow-lab-host", action="store_true",
                        help="Allow Docker service names as targets (lab use only)")
    parser.add_argument("--list-profiles",  action="store_true",
                        help="List all available attack profiles and exit")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_profiles:
        print("\nAvailable Attack Profiles:")
        print("-" * 60)
        for p in list_profiles():
            print(f"  {p['name']:15s} — {p['description']}")
        print()
        sys.exit(0)

    import uuid
    attack_id = args.attack_id or f"{args.profile}-{uuid.uuid4().hex[:8]}"

    # Resolve profile delays
    profile_defaults = PROFILES.get(args.profile, {})
    min_delay = args.min_delay if args.min_delay is not None else profile_defaults.get("min_delay", 0.05)
    max_delay = args.max_delay if args.max_delay is not None else profile_defaults.get("max_delay", 0.5)

    engine = AttackEngine(
        target_url       = args.target,
        credentials_path = args.credentials,
        profile          = args.profile,
        attack_id        = attack_id,
        concurrency      = args.concurrency,
        min_delay        = min_delay,
        max_delay        = max_delay,
        timeout          = args.timeout,
        report_dir       = args.report_dir,
        allow_lab_host   = args.allow_lab_host,
    )

    # Safety check before doing anything
    engine.safety_check()

    # Load credentials
    engine.load_credentials()

    # Run campaign
    asyncio.run(engine.run_campaign())

    # Generate and display report
    report = engine.generate_report()
    engine.print_summary(report)


if __name__ == "__main__":
    main()
