# 🎯 Credential Stuffing Attack & Rate Limit Bypass
## Cloud-Native Adversary Simulation Platform

> **Turing Cyber Hackathon — Offensive Security Track**  
> Enterprise-grade adversary emulation platform demonstrating MITRE ATT&CK T1110.004

---

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-1.25-009639?logo=nginx&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![MITRE](https://img.shields.io/badge/MITRE_ATT%26CK-T1110.004-red)

---

## ⚠️ Authorized Use Only

This platform is designed **exclusively** for:
- Controlled local lab environments
- Cybersecurity research and adversary emulation
- Authentication security testing
- Rate-limit evaluation in isolated Docker networks

**This tool does NOT:**
- Use real leaked credentials
- Target public IP addresses
- Connect to external proxy networks
- Store any real user data

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Docker Network: attack-net                    │
│                                                                 │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐ │
│  │  🔥 Attacker │──▶│  🛡️ Nginx    │──▶│  🎯 Flask Target    │ │
│  │  asyncio    │   │  :8080       │   │  :5000 (internal)   │ │
│  │  5 profiles │   │  XFF bypass  │   │  SQLite + JSONL     │ │
│  └─────────────┘   └──────────────┘   └──────────┬──────────┘ │
│                                                   │            │
│                         /var/log/lab/ (shared)    │            │
│                         ├── auth_events.jsonl ◀───┘            │
│                         └── nginx_access.jsonl                 │
│                                   │                            │
│                         ┌─────────▼──────────┐               │
│                         │  📊 Dashboard       │               │
│                         │  :5001              │               │
│                         │  Chart.js + Flask   │               │
│                         └────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

## 🎭 MITRE ATT&CK Coverage

| Technique | ID | Implementation |
|-----------|-----|---------------|
| Credential Stuffing | **T1110.004** | Async aiohttp engine with 20-pair synthetic credential list |
| Valid Accounts | **T1078** | Real-time success detection + valid credential logging |
| Masquerading | **T1036** | User-Agent rotation + X-Forwarded-For IP spoofing |

---

## 📸 Screenshots

### Telemetry Dashboard
![Dashboard](/screenshots/dashboard.png)

### Vulnerable Target Application
![Login Page](/screenshots/login.png)

### Architecture Diagram
![Architecture Diagram](/screenshots/architecture.png)

### Attack Execution
![Attacker Terminal](/screenshots/terminal.png)

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (Windows/macOS/Linux)
- Docker Compose v2.x
- PowerShell 7+ (for demo script on Windows)

### 1. Start the Platform

```bash
# Clone or navigate to the project
cd credential-stuffing-platform

# Start all services (nginx + target + dashboard)
docker-compose up --build -d nginx target-app dashboard

# Verify health
docker-compose ps
```

### 2. Open the Demo Environment

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:5001 | Real-time attack telemetry |
| **Login Page** | http://localhost:8080 | Vulnerable target application |

### 3. Run Attack Campaigns

```bash
# Baseline: No evasion — demonstrates rate limiting works
docker-compose run --rm -e ATTACK_PROFILE=baseline attacker

# XFF Bypass: Spoofs X-Forwarded-For — defeats IP-based rate limiting
docker-compose run --rm -e ATTACK_PROFILE=ip_rotation attacker

# UA Rotation: Rotates browser User-Agent — evades UA-based detection
docker-compose run --rm -e ATTACK_PROFILE=ua_rotation attacker

# Full Evasion: XFF + UA + jitter — complete bypass demonstration
docker-compose run --rm -e ATTACK_PROFILE=full_evasion attacker

# Slow Burn: Low-and-slow — evades burst detection
docker-compose run --rm -e ATTACK_PROFILE=slow_burn attacker
```

### 4. Run the Full Demo Script (Windows)

```powershell
.\scripts\demo.ps1
```

---

## 📁 Repository Structure

```
credential-stuffing-platform/
├── attacker/                      # Async credential stuffing engine
│   ├── main.py                    # CLI entrypoint with argparse
│   ├── core/
│   │   ├── attack_engine.py       # Main async engine (5 profiles)
│   │   ├── credential_loader.py   # Credential file parser
│   │   └── worker_manager.py      # Profile management
│   ├── evasion/
│   │   ├── proxy_rotator.py       # X-Forwarded-For IP rotation
│   │   ├── useragent_manager.py   # Browser UA rotation
│   │   ├── jitter_engine.py       # Timing randomization
│   │   ├── session_rotator.py     # Cookie/session rotation
│   │   └── header_manipulator.py  # Header fingerprint variation
│   ├── configs/
│   │   └── credentials.txt        # 20 synthetic credential pairs
│   ├── Dockerfile
│   └── requirements.txt
│
├── target-app/                    # Vulnerable Flask authentication target
│   ├── app.py                     # Flask app with SQLite + JSONL logging
│   ├── templates/
│   │   └── login.html             # Cybersecurity-themed login UI
│   ├── Dockerfile
│   └── requirements.txt
│
├── nginx/                         # Reverse proxy (intentionally weak config)
│   ├── nginx.conf                 # XFF-based rate limiting (bypassable)
│   └── Dockerfile
│
├── dashboard/                     # Real-time telemetry dashboard
│   ├── app.py                     # Flask backend with metrics aggregation
│   ├── templates/
│   │   └── index.html             # Chart.js dark dashboard UI
│   ├── Dockerfile
│   └── requirements.txt
│
├── docs/
│   ├── architecture.md            # System design and data flow
│   ├── mitre_mapping.md           # ATT&CK technique mappings
│   ├── mitigations.md             # Defense recommendations
│   └── demo-walkthrough.md        # 7-minute demo script
│
├── scripts/
│   └── demo.ps1                   # Full demo automation (PowerShell)
│
└── docker-compose.yml             # Complete orchestration (4 services)
```

---

## ⚔️ Attack Profiles

| Profile | XFF Spoof | UA Rotate | Timing | Workers | Demonstrates |
|---------|-----------|-----------|--------|---------|-------------|
| `baseline` | ❌ | ❌ | 50–150ms | 5 | Rate limiting blocks without evasion |
| `ip_rotation` | ✅ | ❌ | 50–200ms | 10 | XFF spoofing bypasses IP rate limit |
| `ua_rotation` | ❌ | ✅ | 100–500ms | 5 | UA rotation evades bot detection |
| `full_evasion` | ✅ | ✅ | 200ms–1s | 8 | Combined bypass — most effective |
| `slow_burn` | ✅ | ✅ | 1–3s | 2 | Low-and-slow evades burst detection |

---

## 📊 Dashboard Metrics

The dashboard at `http://localhost:5001` displays:

- **KPI Cards**: Total attempts, successful logins, blocked requests, bypass rate
- **Attack Timeline**: Real-time chart of attempt outcomes per minute
- **Result Distribution**: Donut chart — success / blocked / failed
- **Risk Score Distribution**: Behavioral anomaly scoring (0–100)
- **Nginx HTTP Status Codes**: 200 vs 429 vs 401 distribution
- **Bypass vs Block Rate**: Effectiveness gauge
- **Top Spoofed Source IPs**: XFF header rotation visualization
- **Weak vs Improved Defense**: Side-by-side comparison
- **Attack Campaign Reports**: Historical report table

---

## 🛡️ Defense Modes

**Weak Mode (default):** Trusts XFF for rate limiting — easily bypassed

```bash
DEFENSE_MODE=weak docker-compose up target-app
```

**Improved Mode:** Risk-score-based adaptive blocking — much more effective

```bash
DEFENSE_MODE=improved docker-compose up target-app
```

---

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFENSE_MODE` | `weak` | Target app defense mode (`weak` or `improved`) |
| `ATTACK_PROFILE` | `baseline` | Attack profile for attacker container |
| `ATTACK_ID` | auto | Unique ID for attack run |
| `TARGET_URL` | `http://nginx/` | Target URL for attacker |
| `CREDENTIAL_FILE` | `configs/credentials.txt` | Path to credential list |

---

## 🔐 Seeded Demo Credentials (Synthetic)

| Email | Password | Status |
|-------|----------|--------|
| alice@example.com | Spring2026! | ✅ Valid |
| bob@example.com | Password123! | ✅ Valid |
| charlie@example.com | Welcome@123 | ✅ Valid |
| admin@example.com | Admin@2026 | ✅ Valid |
| diana@example.com | Diana#999 | ✅ Valid |
| eve@example.com | Passw0rd! | ✅ Valid |

---

## 📖 Documentation

- [Architecture](docs/architecture.md) — System design, service responsibilities, telemetry pipeline
- [MITRE ATT&CK Mapping](docs/mitre_mapping.md) — Technique IDs, bypass techniques, mitigations
- [Mitigations Guide](docs/mitigations.md) — Defense recommendations with code examples
- [Demo Walkthrough](docs/demo-walkthrough.md) — 7-minute demo script with talking points

---

## 🧹 Teardown

```bash
# Stop services
docker-compose down

# Stop and remove all data (volumes)
docker-compose down -v

# Remove built images
docker-compose down --rmi all
```

---

*This project is built for the Turing Cyber Hackathon — Offensive Security Track.*  
*Controlled lab environment. Authorized use only.*
