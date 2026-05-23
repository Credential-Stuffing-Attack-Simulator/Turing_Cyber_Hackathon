# MITRE ATT&CK Mapping

## Cloud-Native Credential Stuffing Adversary Simulation

---

| Technique | ID | Tactic | Implementation |
|-----------|-----|--------|----------------|
| **Credential Stuffing** | T1110.004 | Credential Access | `attacker/core/attack_engine.py` — loads synthetic credential pairs from `configs/credentials.txt` and submits via async HTTP POST to the login endpoint |
| **Valid Accounts** | T1078 | Persistence / Initial Access | `target-app/app.py` — detects 200 OK + `"status":"success"` response as valid credential confirmation; engine logs `successful_logins` to JSON report |
| **Masquerading** | T1036 | Defense Evasion | `evasion/useragent_manager.py` — rotates browser User-Agents to impersonate legitimate browser traffic; `evasion/proxy_rotator.py` — rotates X-Forwarded-For to impersonate distributed IPs |

---

## Defense Bypass Techniques Demonstrated

| Bypass Technique | Attack Module | Defense Defeated |
|------------------|--------------|-----------------|
| **XFF IP Spoofing** | `proxy_rotator.py` | IP-based rate limiting (nginx `limit_req_zone $http_x_forwarded_for`) |
| **User-Agent Rotation** | `useragent_manager.py` | Simple UA-based bot detection |
| **Request Timing Jitter** | `jitter_engine.py` | Burst-rate detection (requests per second threshold) |
| **Session Token Rotation** | `session_rotator.py` | Per-session rate limiting and tracking |
| **Header Fingerprint Variation** | `header_manipulator.py` | Header-consistency-based bot fingerprinting |

---

## Mitigations (NIST SP 800-63 + OWASP)

| Control | Description | Effectiveness |
|---------|-------------|--------------|
| **Real-IP Rate Limiting** | Use `$binary_remote_addr` not `$http_x_forwarded_for` as rate limit key | Defeats XFF spoofing |
| **CAPTCHA** | Add CAPTCHA on repeated failure | Defeats automated stuffing |
| **MFA** | Require TOTP or FIDO2 second factor | Makes valid credentials useless |
| **Credential Breach Monitoring** | Check HaveIBeenPwned API on login | Blocks known-breached passwords |
| **Risk-Based Authentication** | Block high risk_score requests adaptively | Defeats behavioral evasion |
| **Device Fingerprinting** | Track browser fingerprints beyond UA | Defeats simple UA rotation |
