#!/usr/bin/env pwsh
##############################################################################
# Demo Automation Script
# Cloud-Native Credential Stuffing Adversary Simulation Platform
##############################################################################

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host ""
    Write-Host "[$Step] $Message" -ForegroundColor Cyan
    Write-Host ("-" * 60) -ForegroundColor DarkGray
}

function Wait-Confirm {
    param([string]$Prompt = "Press ENTER to continue...")
    Write-Host ""
    Write-Host $Prompt -ForegroundColor Yellow
    Read-Host
}

Clear-Host
Write-Host @"

  ██████╗██████╗ ███████╗██████╗ ███████╗███╗   ██╗████████╗██╗ █████╗ ██╗
 ██╔════╝██╔══██╗██╔════╝██╔══██╗██╔════╝████╗  ██║╚══██╔══╝██║██╔══██╗██║
 ██║     ██████╔╝█████╗  ██║  ██║█████╗  ██╔██╗ ██║   ██║   ██║███████║██║
 ██║     ██╔══██╗██╔══╝  ██║  ██║██╔══╝  ██║╚██╗██║   ██║   ██║██╔══██║██║
 ╚██████╗██║  ██║███████╗██████╔╝███████╗██║ ╚████║   ██║   ██║██║  ██║███████╗
  ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝

  Credential Stuffing Attack & Rate Limit Bypass — Adversary Simulation Platform
  MITRE ATT&CK: T1110.004 | T1078 | T1036
  AUTHORIZED USE ONLY: Controlled Lab Environment

"@ -ForegroundColor DarkCyan

# ── Step 1: Build and start services ─────────────────────────────────────────
Write-Step "1/7" "Building and starting Docker services..."
docker-compose up --build -d nginx target-app dashboard

Write-Host "Waiting for services to become healthy..." -ForegroundColor Gray
Start-Sleep -Seconds 15

Write-Host "Service status:" -ForegroundColor Green
docker-compose ps

# ── Step 2: Open browser tabs ─────────────────────────────────────────────────
Write-Step "2/7" "Opening dashboard and login page in browser..."
Start-Process "http://localhost:5001"  # Dashboard
Start-Sleep -Seconds 1
Start-Process "http://localhost:8080"  # Vulnerable login page

Write-Host "Dashboard:   http://localhost:5001" -ForegroundColor Green
Write-Host "Target App:  http://localhost:8080" -ForegroundColor Green

Wait-Confirm "Review the dashboard and login page. Press ENTER to run BASELINE ATTACK (shows blocking)..."

# ── Step 3: Baseline attack (shows blocking) ──────────────────────────────────
Write-Step "3/7" "Running BASELINE attack (no evasion — demonstrates rate limiting blocks)..."
Write-Host "Profile: baseline | XFF: OFF | UA-Rotate: OFF" -ForegroundColor Gray

docker-compose run --rm `
    -e ATTACK_PROFILE=baseline `
    -e ATTACK_ID=demo-baseline-01 `
    attacker

Write-Host ""
Write-Host "Check the dashboard — you should see high BLOCK RATE and 429 responses." -ForegroundColor Yellow

Wait-Confirm "Press ENTER to run XFF BYPASS attack (demonstrates rate limit bypass)..."

# ── Step 4: XFF bypass attack ─────────────────────────────────────────────────
Write-Step "4/7" "Running XFF BYPASS attack (X-Forwarded-For spoofing)..."
Write-Host "Profile: ip_rotation | XFF: ON | UA-Rotate: OFF" -ForegroundColor Gray
Write-Host "Watch the terminal — XFF header changes on every request!" -ForegroundColor Yellow

docker-compose run --rm `
    -e ATTACK_PROFILE=ip_rotation `
    -e ATTACK_ID=demo-xff-bypass-01 `
    attacker

Write-Host ""
Write-Host "Check the dashboard — bypass rate should be HIGH. Credentials cracked!" -ForegroundColor Red

Wait-Confirm "Press ENTER to run FULL EVASION attack (XFF + UA + jitter combined)..."

# ── Step 5: Full evasion attack ───────────────────────────────────────────────
Write-Step "5/7" "Running FULL EVASION attack (all bypass techniques active)..."
Write-Host "Profile: full_evasion | XFF: ON | UA-Rotate: ON | Jitter: ON" -ForegroundColor Gray

docker-compose run --rm `
    -e ATTACK_PROFILE=full_evasion `
    -e ATTACK_ID=demo-full-evasion-01 `
    attacker

Wait-Confirm "Press ENTER to show IMPROVED DEFENSE comparison..."

# ── Step 6: Switch to improved defense mode ───────────────────────────────────
Write-Step "6/7" "Switching to IMPROVED DEFENSE mode..."
Write-Host "Restarting target-app with DEFENSE_MODE=improved..." -ForegroundColor Gray

docker-compose stop target-app
$env:DEFENSE_MODE = "improved"
docker-compose up -d target-app
Start-Sleep -Seconds 10

Write-Host "Running XFF bypass against IMPROVED defenses..." -ForegroundColor Yellow

docker-compose run --rm `
    -e ATTACK_PROFILE=ip_rotation `
    -e ATTACK_ID=demo-improved-defense-01 `
    attacker

Write-Host ""
Write-Host "Improved defenses block significantly more requests!" -ForegroundColor Green
Write-Host "Check the 'Weak vs Improved Defense' chart in the dashboard." -ForegroundColor Yellow

# ── Step 7: Summary ────────────────────────────────────────────────────────────
Write-Step "7/7" "Demo Complete — View final telemetry..."
Write-Host ""
Write-Host "Dashboard:      http://localhost:5001" -ForegroundColor Green
Write-Host "Reports:        docker-compose exec dashboard ls /app/reports" -ForegroundColor Gray
Write-Host ""
Write-Host "Key Takeaways:" -ForegroundColor Cyan
Write-Host "  • XFF-based rate limiting is trivially bypassable" -ForegroundColor White
Write-Host "  • Real-IP rate limiting (binary_remote_addr) defeats XFF spoofing" -ForegroundColor White
Write-Host "  • Combined evasion (XFF + UA + jitter) defeats most simple defenses" -ForegroundColor White
Write-Host "  • Defense-in-depth: MFA + CAPTCHA + risk scoring + rate limiting" -ForegroundColor White
Write-Host ""
Write-Host "MITRE ATT&CK: T1110.004 (Credential Stuffing) | T1036 (Masquerading) | T1078 (Valid Accounts)" -ForegroundColor DarkGray
Write-Host ""

# ── Cleanup option ─────────────────────────────────────────────────────────────
$cleanup = Read-Host "Tear down environment? (y/N)"
if ($cleanup -eq 'y') {
    Write-Host "Stopping and removing containers..." -ForegroundColor Gray
    docker-compose down -v
    Write-Host "Environment cleaned up." -ForegroundColor Green
} else {
    Write-Host "Environment left running. Use 'docker-compose down' to stop." -ForegroundColor Gray
}
