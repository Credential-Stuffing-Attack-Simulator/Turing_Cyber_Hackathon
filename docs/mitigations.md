# Mitigations Guide

## Cloud-Native Credential Stuffing Attack & Rate Limit Bypass
## Defense Recommendations

---

## Vulnerability 1: XFF-Based Rate Limiting (Critical)

**Description:** Using `X-Forwarded-For` as the nginx rate limit key allows
attackers to bypass rate limiting by rotating the header value.

**Vulnerable configuration:**
```nginx
limit_req_zone $http_x_forwarded_for zone=login_weak:10m rate=5r/s;
```

**Fixed configuration:**
```nginx
# Rate limit by the actual TCP connection source IP (not spoofable)
limit_req_zone $binary_remote_addr zone=login_strong:10m rate=2r/m;
```

**Severity:** Critical  
**Effort to fix:** Low  
**MITRE:** T1110.004

---

## Vulnerability 2: No Multi-Factor Authentication

**Description:** Single-factor (password-only) authentication means valid
credentials are sufficient to authenticate without any additional challenge.

**Fix:** Implement TOTP (Google Authenticator) or FIDO2/WebAuthn second factor.

**Severity:** High  
**MITRE:** T1078

---

## Vulnerability 3: No CAPTCHA on Login

**Description:** No bot challenge allows fully automated credential stuffing.

**Fix:** Add CAPTCHA (hCaptcha, Cloudflare Turnstile, or Google reCAPTCHA v3)
after 3 consecutive failures from the same session.

**Severity:** High

---

## Vulnerability 4: Predictable, Simple Passwords

**Description:** Seeded users use simple, dictionary-attackable passwords.

**Fix:**
- Enforce strong password policies (12+ chars, uppercase, numbers, symbols)
- Check against HaveIBeenPwned API on registration and password change
- Implement password strength meter in UI

**Severity:** High

---

## Vulnerability 5: No Adaptive Risk-Based Authentication

**Description:** The "weak" mode ignores behavioral risk signals entirely.

**Fix:** Enable `DEFENSE_MODE=improved` which activates adaptive blocking
based on the risk scoring engine (account failure rate, fingerprint tracking,
header rotation detection).

```bash
docker-compose up -e DEFENSE_MODE=improved target-app
```

**Severity:** Medium

---

## Defense-in-Depth Recommended Stack

| Layer | Control | Implementation |
|-------|---------|---------------|
| **Network** | Real-IP rate limiting | nginx `$binary_remote_addr` |
| **Network** | GeoIP blocking | nginx GeoIP2 module |
| **Application** | CAPTCHA | hCaptcha / Turnstile |
| **Application** | MFA | TOTP / FIDO2 |
| **Application** | Risk scoring | Behavioral analytics |
| **Application** | Account lockout | 5 failures → 15 min lock |
| **Data** | Credential monitoring | HaveIBeenPwned API |
| **Monitoring** | Anomaly detection | SIEM alerting on 429 spikes |
