# Demo Walkthrough — 7 Minute Script

## Cloud-Native Credential Stuffing Attack & Rate Limit Bypass Adversary Simulation

---

## Pre-Demo Setup (2 min before demo)

```powershell
# 1. Navigate to project directory
cd credential-stuffing-platform

# 2. Start the full platform
docker-compose up --build -d nginx target-app dashboard

# 3. Verify all services healthy
docker-compose ps

# 4. Open dashboard (in browser)
start http://localhost:5001

# 5. Open vulnerable login page (in browser)
start http://localhost:8080
```

Wait for all services to show `healthy` before starting the demo.

---

## DEMO FLOW

### ⏱ 00:00 — Introduction (1 min)

**Say:**
> "This is a controlled adversary simulation demonstrating how modern credential stuffing attacks bypass weak cloud-native authentication controls."

**Show:** The login page at `http://localhost:8080`
- Point to the **WEAK DEFENSES ACTIVE** badge
- Explain the synthetic users seeded in the database
- Mention: "In the real world, attackers use breached credential databases. We use synthetic credentials for safe demonstration."

**Key point:** MITRE T1110.004 — Credential Stuffing

---

### ⏱ 01:00 — Demonstrate Weak Rate Limiting (1.5 min)

**Say:**
> "The nginx proxy has a rate limit configured — but it's using X-Forwarded-For for the limit key. This is a critical misconfiguration."

**Show nginx.conf key line:**
```nginx
limit_req_zone $http_x_forwarded_for zone=login_weak:10m rate=5r/s;
```

**Say:**
> "This means every unique X-Forwarded-For value gets its OWN rate limit bucket. An attacker who rotates their XFF header gets a fresh bucket on every request."

**Run baseline attack (to show blocking works without evasion):**
```powershell
docker-compose run --rm `
  -e ATTACK_PROFILE=baseline `
  -e ATTACK_ID=demo-baseline-01 `
  attacker
```

**Show dashboard:** Requests being blocked with 429s. Point to the block rate metric.

---

### ⏱ 02:30 — Launch Bypass Attack (2 min)

**Say:**
> "Now watch what happens when the attacker rotates their IP using X-Forwarded-For spoofing."

**Run XFF bypass attack:**
```powershell
docker-compose run --rm `
  -e ATTACK_PROFILE=ip_rotation `
  -e ATTACK_ID=demo-xff-bypass-01 `
  attacker
```

**Watch the terminal:**
- Point to the XFF IP values changing on each request
- Point to HTTP 200 responses instead of 429s

**Show dashboard:**
- Block rate dropping significantly
- Successful logins appearing in green
- Valid credentials section showing cracked accounts
- Timeline chart showing the bypass in action

**Say:**
> "The attacker cracked X of Y credentials. The rate limit was completely bypassed."

---

### ⏱ 04:30 — Full Evasion Attack (1.5 min)

**Say:**
> "Let's go further. Full evasion combines XFF rotation, User-Agent rotation, and timing jitter."

```powershell
docker-compose run --rm `
  -e ATTACK_PROFILE=full_evasion `
  -e ATTACK_ID=demo-full-evasion-01 `
  attacker
```

**Show dashboard:** The attack timeline, bypass rate, and evasion profiles chart.

---

### ⏱ 06:00 — Mitigation (1 min)

**Say:**
> "The fix is simple but critical. You must rate-limit by the real client IP, not the X-Forwarded-For header."

**Show the nginx.conf improved zone:**
```nginx
# WEAK (bypassable)
limit_req_zone $http_x_forwarded_for zone=login_weak:10m rate=5r/s;

# IMPROVED (not bypassable)  
limit_req_zone $binary_remote_addr zone=login_strong:10m rate=2r/m;
```

**Show the Flask risk scoring:**
> "Combined with behavioral risk scoring in the application layer — tracking account failures, fingerprint patterns, and header rotation signals — the platform becomes significantly more resilient."

**Show the Weak vs Improved comparison chart in the dashboard.**

**Conclude:**
> "Mitigations: Real-IP rate limiting, MFA, risk-based adaptive blocking, CAPTCHA, and credential breach monitoring. No single control is sufficient — defense in depth is required."

---

## Terminal Commands Reference

| Action | Command |
|--------|---------|
| Start platform | `docker-compose up -d nginx target-app dashboard` |
| Run baseline attack | `docker-compose run --rm -e ATTACK_PROFILE=baseline attacker` |
| Run XFF bypass | `docker-compose run --rm -e ATTACK_PROFILE=ip_rotation attacker` |
| Run full evasion | `docker-compose run --rm -e ATTACK_PROFILE=full_evasion attacker` |
| View dashboard | `http://localhost:5001` |
| View login page | `http://localhost:8080` |
| View logs | `docker-compose logs -f target-app` |
| Stop all | `docker-compose down` |
| Reset telemetry | `docker-compose down -v && docker-compose up -d` |
