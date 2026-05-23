"""
Telemetry Dashboard Backend
============================
Cloud-Native Credential Stuffing Attack & Rate Limit Bypass
Adversary Simulation Platform

Reads structured JSONL telemetry from the shared log volume
and serves aggregated metrics to the Chart.js dashboard frontend.
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template

app = Flask(__name__)

# ── Telemetry paths (shared volume mount) ──────────────────────────────────────
DATA_DIR   = Path(os.getenv("LAB_DATA_DIR",  "/var/log/lab"))
REPORT_DIR = Path(os.getenv("REPORT_DIR",    "/app/reports"))


# ── File readers ───────────────────────────────────────────────────────────────

def _read_jsonl(path: Path, max_lines: int = 5000) -> List[Dict]:
    """Read a JSONL file safely, returning a list of parsed dicts."""
    events = []
    if not path.exists():
        return events
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except Exception:
        pass
    return events[-max_lines:]  # Keep last N events


def _read_reports(directory: Path) -> List[Dict]:
    """Read all JSON attack reports from the reports directory."""
    reports = []
    if not directory.exists():
        return reports
    for f in sorted(directory.glob("*.json")):
        try:
            with f.open("r", encoding="utf-8") as fh:
                reports.append(json.loads(fh.read()))
        except Exception:
            pass
    return reports


# ── Metric Aggregation ─────────────────────────────────────────────────────────

def _aggregate_metrics(auth_events: List[Dict], nginx_events: List[Dict], reports: List[Dict]) -> Dict:
    """Aggregate all telemetry into dashboard metrics."""

    # ── Auth event counters ───────────────────────────────────────────────────
    result_counts   = Counter(e.get("result", "unknown")          for e in auth_events)
    profile_counts  = Counter(e.get("attack_profile", "unknown")  for e in auth_events if "attack_id" in e)
    ip_counts       = Counter(e.get("source_ip", "unknown")       for e in auth_events)
    ua_counts       = Counter(e.get("user_agent", "unknown")[:60] for e in auth_events)
    attack_ids      = Counter(e.get("attack_id", "unknown")       for e in auth_events if e.get("attack_id") != "unknown")

    # ── Nginx event counters ──────────────────────────────────────────────────
    nginx_status    = Counter(str(e.get("status", "?"))           for e in nginx_events)
    nginx_blocked   = sum(1 for e in nginx_events if str(e.get("status")) == "429")
    xff_used        = sum(1 for e in nginx_events if e.get("xff") and e["xff"] != "-")

    # ── Timeline: group by minute ─────────────────────────────────────────────
    timeline: Dict[str, Dict] = defaultdict(lambda: {"total": 0, "success": 0, "blocked": 0, "failure": 0})
    for e in auth_events:
        ts = e.get("timestamp", "")
        if ts and len(ts) >= 16:
            minute = ts[:16]  # "2026-05-23T12:34"
            timeline[minute]["total"]   += 1
            result = e.get("result", "")
            if result in ("success", "blocked", "failure"):
                timeline[minute][result] += 1

    timeline_sorted = sorted(timeline.items())
    timeline_labels = [t[0] for t in timeline_sorted]
    timeline_total  = [t[1]["total"]   for t in timeline_sorted]
    timeline_success = [t[1]["success"] for t in timeline_sorted]
    timeline_blocked = [t[1]["blocked"] for t in timeline_sorted]
    timeline_failure = [t[1]["failure"] for t in timeline_sorted]

    # ── Risk score distribution ───────────────────────────────────────────────
    risk_buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for e in auth_events:
        score = e.get("risk_score", 0)
        if score <= 20:   risk_buckets["0-20"]   += 1
        elif score <= 40: risk_buckets["21-40"]  += 1
        elif score <= 60: risk_buckets["41-60"]  += 1
        elif score <= 80: risk_buckets["61-80"]  += 1
        else:             risk_buckets["81-100"] += 1

    # ── Report summaries ──────────────────────────────────────────────────────
    report_summaries = []
    for r in reports[-10:]:  # Last 10 reports
        s = r.get("summary", {})
        report_summaries.append({
            "attack_id":    r.get("attack_id", "?"),
            "profile":      r.get("profile",   "?"),
            "total":        s.get("total_attempts", 0),
            "success":      s.get("successful_logins", 0),
            "blocked":      s.get("blocked_attempts", 0),
            "bypass_rate":  s.get("bypass_rate", 0),
            "block_rate":   s.get("block_rate",  0),
        })

    total_attempts = len(auth_events)
    successful     = result_counts.get("success", 0)
    blocked        = result_counts.get("blocked", 0) + nginx_blocked
    failed         = result_counts.get("failure", 0)
    bypass_rate    = round(successful / total_attempts * 100, 1) if total_attempts else 0
    block_rate     = round(blocked    / total_attempts * 100, 1) if total_attempts else 0

    return {
        "summary": {
            "total_attempts":    total_attempts,
            "successful_logins": successful,
            "blocked_attempts":  blocked,
            "failed_attempts":   failed,
            "nginx_blocked":     nginx_blocked,
            "xff_used":          xff_used,
            "bypass_rate":       bypass_rate,
            "block_rate":        block_rate,
            "unique_ips":        len(ip_counts),
            "unique_profiles":   len(attack_ids),
        },
        "timeline": {
            "labels":   timeline_labels,
            "total":    timeline_total,
            "success":  timeline_success,
            "blocked":  timeline_blocked,
            "failure":  timeline_failure,
        },
        "distributions": {
            "results":     dict(result_counts.most_common(10)),
            "nginx_status": dict(nginx_status.most_common(10)),
            "top_ips":     dict(ip_counts.most_common(10)),
            "top_uas":     dict(ua_counts.most_common(5)),
            "risk_scores": risk_buckets,
        },
        "reports":   report_summaries,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def index():
    """Serve the telemetry dashboard."""
    return render_template("index.html")


@app.get("/api/metrics")
def metrics():
    """Return aggregated platform metrics as JSON."""
    auth_events  = _read_jsonl(DATA_DIR / "auth_events.jsonl")
    nginx_events = _read_jsonl(DATA_DIR / "nginx_access.jsonl")
    reports      = _read_reports(REPORT_DIR)
    return jsonify(_aggregate_metrics(auth_events, nginx_events, reports))


@app.get("/api/events/auth")
def auth_events():
    """Return recent raw auth events."""
    events = _read_jsonl(DATA_DIR / "auth_events.jsonl")
    return jsonify(events[-100:])


@app.get("/api/events/nginx")
def nginx_events():
    """Return recent raw nginx access events."""
    events = _read_jsonl(DATA_DIR / "nginx_access.jsonl")
    return jsonify(events[-100:])


@app.get("/api/reports")
def reports():
    """Return all attack report summaries."""
    return jsonify(_read_reports(REPORT_DIR))


@app.get("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
