# Architecture Overview

## Cloud-Native Credential Stuffing Attack & Rate Limit Bypass
## Adversary Simulation Platform

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Docker Network: attack-net                    │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │  🔥 Attacker │───▶│ 🛡️  Nginx   │───▶│  🎯 Target Flask App │  │
│  │  (asyncio)  │    │ (:8080)     │    │  (:5000, internal)  │  │
│  │  aiohttp    │    │ Rate Limit  │    │  SQLite + JSONL log │  │
│  └─────────────┘    │ XFF Bypass  │    └──────────┬──────────┘  │
│                     └─────────────┘               │             │
│                           │                       │             │
│                    /var/log/lab/ (shared volume)   │             │
│                    ├── auth_events.jsonl ◀─────────┘             │
│                    └── nginx_access.jsonl                        │
│                           │                                      │
│                    ┌──────▼──────────┐                          │
│                    │ 📊 Dashboard     │                          │
│                    │ (:5001)          │                          │
│                    │ Chart.js + Flask │                          │
│                    └─────────────────┘                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## Service Responsibilities

| Service | Role | Technology | Port |
|---------|------|-----------|------|
| **nginx** | Reverse proxy with intentionally weak XFF-based rate limiting | nginx 1.25 | 8080 (ext) |
| **target-app** | Vulnerable Flask authentication target with SQLite + JSONL logging | Python/Flask | 5000 (int) |
| **dashboard** | Real-time telemetry aggregation + Chart.js visualization | Python/Flask | 5001 (ext) |
| **attacker** | Async credential stuffing engine with 5 evasion profiles | Python asyncio/aiohttp | (none) |

---

## Evasion Architecture

| Module | File | Technique |
|--------|------|-----------|
| Proxy Rotator | `attacker/evasion/proxy_rotator.py` | X-Forwarded-For spoofing |
| UA Manager | `attacker/evasion/useragent_manager.py` | Browser User-Agent rotation |
| Jitter Engine | `attacker/evasion/jitter_engine.py` | Timing randomization |
| Session Rotator | `attacker/evasion/session_rotator.py` | Cookie/session rotation |
| Header Manipulator | `attacker/evasion/header_manipulator.py` | Header fingerprint variation |

---

## Attack Profiles

| Profile | XFF Spoof | UA Rotate | Timing | Concurrency | Purpose |
|---------|-----------|-----------|--------|------------|---------|
| `baseline` | ❌ | ❌ | 50–150ms | 5 | Demonstrates blocking |
| `ip_rotation` | ✅ | ❌ | 50–200ms | 10 | XFF bypass demo |
| `ua_rotation` | ❌ | ✅ | 100–500ms | 5 | UA evasion demo |
| `full_evasion` | ✅ | ✅ | 200ms–1s | 8 | Full bypass demo |
| `slow_burn` | ✅ | ✅ | 1–3s | 2 | Low-and-slow demo |

---

## Telemetry Pipeline

```
Attacker → HTTP POST /api/login → Nginx → Flask Target
                                              │
                                              ├── /var/log/lab/auth_events.jsonl
                                              └── /app/data/users.db (SQLite)

Nginx → /var/log/lab/nginx_access.jsonl

Attacker → /app/reports/{attack_id}.json
         → /app/reports/{attack_id}.csv

Dashboard reads ─── all of the above → /api/metrics → Chart.js
```
