# Demo Stability & Quick Recovery Guide

## Cloud-Native Credential Stuffing Attack & Rate Limit Bypass
## Adversary Simulation Platform

---

This guide provides rapid recovery procedures in case of unexpected failures during the live hackathon demonstration.

## 🚨 Emergency Restart Procedures

### 1. Full Platform Hard Reset
If the dashboard stops updating, Nginx fails to route, or the Flask target app becomes unresponsive, perform a full hard reset. This takes ~15 seconds.

```powershell
# Stop all containers and delete volumes (wipes database and logs)
docker-compose down -v

# Rebuild and start fresh
docker-compose up --build -d nginx target-app dashboard
```

### 2. Restarting the Dashboard Only
If Chart.js hangs or the `/api/metrics` endpoint fails:

```powershell
docker-compose restart dashboard
```
*Wait 5 seconds, then hard-refresh the browser (Ctrl+F5).*

### 3. Restarting the Target App Only
If logins timeout or the SQLite database locks:

```powershell
docker-compose restart target-app
```

---

## 🛠️ Common Issues & Troubleshooting

### Issue: "Attack Engine says Connection Refused"
**Cause:** Nginx proxy is down or the target-app is unhealthy.
**Fix:** 
1. Check health: `docker-compose ps`
2. View Nginx logs: `docker-compose logs --tail 20 nginx`
3. Restart proxy: `docker-compose restart nginx`

### Issue: "Dashboard shows no data after running attack"
**Cause:** Telemetry volume synchronization delay or log file lock.
**Fix:**
1. Wait 5 seconds (auto-refresh interval).
2. Manually refresh the browser.
3. Verify attack ran successfully: check the terminal output for `[SUCCESS]` or `[BLOCKED]`.

### Issue: "Docker Compose command not found"
**Cause:** Docker Desktop is not running or not in PATH.
**Fix:** Start Docker Desktop from the Windows Start Menu and wait for the engine to initialize.

---

## 🛡️ Fallback Demo Strategy (If Docker Fails)

If the local Docker environment completely crashes during the presentation and cannot be recovered within 30 seconds, seamlessly transition to the **Static Asset Fallback**:

1. **Do not panic.** Acknowledge the lab environment issue gracefully ("As happens in live security labs...").
2. **Switch to Screenshots:** Open the `screenshots/` directory.
3. **Continue the Narrative:**
   - Open `screenshots/architecture.png` to explain the system design.
   - Open `screenshots/login.png` to show the vulnerable target.
   - Open `screenshots/terminal.png` to explain how the attack engine uses async workers and XFF rotation.
   - Open `screenshots/dashboard.png` to show the resulting telemetry, bypass rate, and risk scoring.
4. **Reference Code:** Open `nginx/nginx.conf` and `target-app/app.py` in VS Code to explain the exact misconfiguration and mitigation, shifting the focus to the engineering and architecture.
