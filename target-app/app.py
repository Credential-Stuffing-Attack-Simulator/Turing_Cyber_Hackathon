"""
Vulnerable Authentication Target Application
============================================
Cloud-Native Credential Stuffing Attack & Rate Limit Bypass
Adversary Simulation Platform

AUTHORIZED USE ONLY: This application is intentionally vulnerable
and is designed exclusively for controlled lab environments,
cybersecurity research, and adversary emulation demonstrations.

Simulates: T1110.004 Credential Stuffing, T1078 Valid Accounts
"""

import hashlib
import json
import os
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, make_response, render_template, request, session

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "INTENTIONALLY-WEAK-KEY-FOR-DEMO")

# ── Configuration ──────────────────────────────────────────────────────────────
DATA_DIR   = Path(os.getenv("LAB_DATA_DIR", "/var/log/lab"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

AUTH_LOG   = DATA_DIR / "auth_events.jsonl"
DEFENSE_MODE = os.getenv("DEFENSE_MODE", "weak")   # "weak" | "improved"

# ── Seeded Demo Users (intentionally simple passwords) ─────────────────────────
import sqlite3

DB_PATH = Path(os.getenv("DB_PATH", "/app/data/users.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SEED_USERS = [
    # Original 6
    ("alice@example.com",       "Spring2026!"),
    ("bob@example.com",         "Password123!"),
    ("charlie@example.com",     "Welcome@123"),
    ("admin@example.com",       "Admin@2026"),
    ("diana@example.com",       "Diana#999"),
    ("eve@example.com",         "Passw0rd!"),
    # Extended 25 — realistic synthetic users
    ("john.smith@gmail.com",    "Football2023!"),
    ("jane.doe@yahoo.com",      "Sunshine99#"),
    ("michael.jones@hotmail.com","Dragon2024@"),
    ("sarah.miller@gmail.com",  "Princess1!"),
    ("david.garcia@outlook.com","Monkey123#"),
    ("emily.brown@icloud.com",  "Qwerty2025!"),
    ("chris.wilson@gmail.com",  "Baseball99@"),
    ("jessica.moore@yahoo.com", "Iloveyou1!"),
    ("matthew.taylor@gmail.com","Shadow2024#"),
    ("amanda.anderson@aol.com", "Welcome99!"),
    ("joshua.thomas@gmail.com", "Summer2024@"),
    ("ashley.jackson@yahoo.com","Letmein1!"),
    ("daniel.white@hotmail.com","Trustno1#"),
    ("brittany.harris@gmail.com","Autumn2023!"),
    ("james.martin@outlook.com","Admin1234@"),
    ("megan.thompson@gmail.com","Spring99#"),
    ("justin.garcia@yahoo.com", "Winter2024!"),
    ("samantha.lee@icloud.com", "Dragon99@"),
    ("robert.clark@gmail.com",  "Passw0rd99!"),
    ("jennifer.lewis@yahoo.com","Flower2024#"),
    ("william.hall@hotmail.com","Guitar2023@"),
    ("lisa.allen@gmail.com",    "Ocean2024!"),
    ("kevin.young@outlook.com", "Thunder99#"),
    ("rachel.king@gmail.com",   "Sunset2024@"),
    ("steven.wright@yahoo.com", "Coffee2023!"),
]


def _hash_password(pw: str) -> str:
    """Intentionally weak SHA-256 (no salt) to demonstrate poor practices."""
    return hashlib.sha256(pw.encode()).hexdigest()


def init_db() -> None:
    """Initialize SQLite database with seeded users."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS login_events (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp    TEXT NOT NULL,
                username     TEXT NOT NULL,
                result       TEXT NOT NULL,
                source_ip    TEXT NOT NULL,
                user_agent   TEXT NOT NULL,
                risk_score   INTEGER NOT NULL
            )
        """)
        for username, password in SEED_USERS:
            try:
                conn.execute(
                    "INSERT INTO users (username, password, created) VALUES (?, ?, ?)",
                    (username, _hash_password(password), datetime.now(timezone.utc).isoformat()),
                )
            except sqlite3.IntegrityError:
                pass  # Already seeded
        conn.commit()


# Initialize DB on startup
init_db()

# ── In-memory behavioral tracking ─────────────────────────────────────────────
ACCOUNT_FAILURES     = defaultdict(lambda: deque(maxlen=50))
FINGERPRINT_FAILURES = defaultdict(lambda: deque(maxlen=50))
IP_FAILURES          = defaultdict(lambda: deque(maxlen=100))


# ── Utility Functions ──────────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def client_ip() -> str:
    """Extract client IP, trusting X-Forwarded-For (intentionally weak in weak mode)."""
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"


def fingerprint() -> str:
    """Generate a request fingerprint from headers."""
    return "|".join([
        request.headers.get("User-Agent",      "unknown"),
        request.headers.get("Accept",           "unknown"),
        request.headers.get("Accept-Language",  "unknown"),
        request.headers.get("X-Device-Id",      "unknown"),
    ])


def log_event(event: dict) -> None:
    """Append structured event to JSONL telemetry log."""
    with AUTH_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")


def risk_score(username: str) -> int:
    """
    Compute behavioral risk score for a login attempt.
    Higher = more suspicious.
    """
    now = time.time()
    window = 300  # 5-minute sliding window

    account_recent = [ts for ts in ACCOUNT_FAILURES[username]   if now - ts < window]
    fp_recent      = [ts for ts in FINGERPRINT_FAILURES[fingerprint()] if now - ts < window]
    ip_recent      = [ts for ts in IP_FAILURES[client_ip()]     if now - ts < window]

    ua_rotated  = request.headers.get("X-UA-Rotated",    "false") == "true"
    ip_rotated  = request.headers.get("X-Proxy-Rotated", "false") == "true"
    xff_present = bool(request.headers.get("X-Forwarded-For"))

    score = (
        len(account_recent) * 12  +
        len(fp_recent)      * 8   +
        len(ip_recent)      * 4   +
        (20 if ua_rotated  else 0) +
        (15 if ip_rotated  else 0) +
        (10 if xff_present else 0)
    )
    return min(score, 100)


def authenticate(username: str, password: str) -> bool:
    """Verify credentials against SQLite database."""
    hashed = _hash_password(password)
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, hashed),
        ).fetchone()
    return row is not None


def persist_event(username: str, result: str, score: int) -> None:
    """Write login event to SQLite."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """INSERT INTO login_events
               (timestamp, username, result, source_ip, user_agent, risk_score)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (now_iso(), username, result, client_ip(),
             request.headers.get("User-Agent", "unknown"), score),
        )
        conn.commit()


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def index():
    """Serve the vulnerable login page."""
    return render_template("login.html", defense_mode=DEFENSE_MODE)


@app.get("/health")
def health():
    """Health check endpoint for Docker."""
    return jsonify({"status": "ok", "defense_mode": DEFENSE_MODE, "timestamp": now_iso()})


@app.post("/api/login")
def api_login():
    """
    Core vulnerable login endpoint.
    Intentionally demonstrates weak authentication protections.

    Weak mode:  Trusts X-Forwarded-For, no adaptive throttling.
    Improved mode: Risk-score-based adaptive blocking.
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    score = risk_score(username)
    ip    = client_ip()
    ua    = request.headers.get("User-Agent", "unknown")
    attack_id = request.headers.get("X-Attack-Id", "unknown")

    # ── IMPROVED MODE: Adaptive risk-based blocking ───────────────────────────
    if DEFENSE_MODE == "improved" and score >= 60:
        event = {
            "timestamp":   now_iso(),
            "event_type":  "blocked",
            "username":    username,
            "source_ip":   ip,
            "user_agent":  ua,
            "risk_score":  score,
            "result":      "blocked_high_risk",
            "defense_mode": DEFENSE_MODE,
            "attack_id":   attack_id,
        }
        log_event(event)
        persist_event(username, "blocked", score)
        return jsonify({
            "error": "Access temporarily restricted",
            "code":  "HIGH_RISK_BLOCKED",
        }), 403

    # ── Credential Verification ───────────────────────────────────────────────
    success = authenticate(username, password)
    result  = "success" if success else "failure"

    # Track failures for behavioral analysis
    if not success:
        ts = time.time()
        ACCOUNT_FAILURES[username].append(ts)
        FINGERPRINT_FAILURES[fingerprint()].append(ts)
        IP_FAILURES[ip].append(ts)

    # ── Structured Telemetry Log ───────────────────────────────────────────────
    event = {
        "timestamp":    now_iso(),
        "event_type":   "login_attempt",
        "username":     username,
        "source_ip":    ip,
        "user_agent":   ua,
        "risk_score":   score,
        "result":       result,
        "defense_mode": DEFENSE_MODE,
        "attack_id":    attack_id,
        "xff_present":  bool(request.headers.get("X-Forwarded-For")),
        "ua_rotated":   request.headers.get("X-UA-Rotated", "false") == "true",
    }
    log_event(event)
    persist_event(username, result, score)

    if success:
        session["user"]     = username
        session["login_ts"] = now_iso()
        return jsonify({
            "status":  "success",
            "message": f"Welcome, {username}",
            "token":   str(uuid.uuid4()),
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.get("/api/status")
def api_status():
    """Return current defense mode and basic stats."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            total   = conn.execute("SELECT COUNT(*) FROM login_events").fetchone()[0]
            success = conn.execute("SELECT COUNT(*) FROM login_events WHERE result='success'").fetchone()[0]
            blocked = conn.execute("SELECT COUNT(*) FROM login_events WHERE result='blocked'").fetchone()[0]
    except Exception:
        total = success = blocked = 0

    return jsonify({
        "defense_mode":     DEFENSE_MODE,
        "total_attempts":   total,
        "successful_logins": success,
        "blocked_attempts": blocked,
        "timestamp":        now_iso(),
    })


@app.get("/api/telemetry")
def api_telemetry():
    """Return recent auth events for dashboard consumption."""
    events = []
    if AUTH_LOG.exists():
        with AUTH_LOG.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    # Return last 200 events
    return jsonify(events[-200:])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
