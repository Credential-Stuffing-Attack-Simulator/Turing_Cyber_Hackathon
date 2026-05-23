# Hackathon Presentation Flow

**Time Allotted:** 5-7 minutes

## 1. Introduction (0:00 - 1:00)

*   **Hook:** "Modern web applications are increasingly vulnerable to credential stuffing attacks. While organizations often rely on rate limiting as a defense, these controls are frequently misconfigured and easily bypassed."
*   **Problem Statement:** "Attackers use sophisticated techniques to evade detection, such as rotating IP addresses and browser fingerprints. Naive rate limiting, especially when relying on easily spoofed headers, is insufficient."
*   **Our Solution:** "We've built an enterprise-grade, cloud-native Adversary Simulation Platform to demonstrate these bypass techniques and evaluate the effectiveness of different mitigation strategies."
*   **Show:** Briefly display the Architecture Diagram (`/screenshots/architecture.png`) to give an overview of the platform (Attack Engine, Nginx Proxy, Vulnerable Target, Telemetry Dashboard).

## 2. Demonstrating the Vulnerability (1:00 - 2:30)

*   **Setup:** Point out that the target application (`http://localhost:8080`) is currently running with "Weak Defenses Active".
*   **The Flaw:** Explain that the Nginx reverse proxy is configured to rate limit based on the `X-Forwarded-For` header. Show the vulnerable config snippet: `limit_req_zone $http_x_forwarded_for zone=login_weak:10m rate=5r/s;`. Emphasize that this header is controlled by the client.
*   **Baseline Attack:** Run the `baseline` attack profile.
    *   *Command:* `docker-compose run --rm -e ATTACK_PROFILE=baseline attacker`
    *   *Narrative:* "First, we run a naive attack without any evasion. As expected, the rate limit kicks in, and the requests are blocked."
*   **Show Dashboard:** Switch to the Telemetry Dashboard (`http://localhost:5001`). Point out the high "Block Rate" and the spike in 429 HTTP status codes.

## 3. Bypassing the Defenses (2:30 - 4:30)

*   **The Exploit:** "Now, let's see how an attacker bypasses this weak configuration."
*   **IP Rotation Attack:** Run the `ip_rotation` attack profile.
    *   *Command:* `docker-compose run --rm -e ATTACK_PROFILE=ip_rotation attacker`
    *   *Narrative:* "This profile spoofs a different IP address in the `X-Forwarded-For` header for every request. Because Nginx is tracking limits per unique XFF value, the attacker never hits the limit."
*   **Show Terminal:** Show the attacker terminal output (`/screenshots/terminal.png`), highlighting the changing `XFF=` values and the `HTTP 200` successes.
*   **Show Dashboard:** Return to the dashboard.
    *   Point out the dramatically lower "Block Rate" and the spike in "Successful Logins" (the bypass).
    *   Highlight the "Top Spoofed Source IPs" chart showing the rotating addresses.
    *   Point out the "Valid Credentials Found" section in the terminal or report table, demonstrating successful credential stuffing.
*   **Full Evasion (Optional, if time permits):** Mention that the platform also supports full evasion (rotating User-Agents, adding timing jitter) to bypass more advanced bot detection.

## 4. Mitigations and Defense-in-Depth (4:30 - 6:00)

*   **The Fix:** "How do we prevent this?"
*   **Improved Configuration:** Show the corrected Nginx config: `limit_req_zone $binary_remote_addr zone=login_strong:10m rate=2r/m;`. Explain that `$binary_remote_addr` uses the actual TCP connection IP, which cannot be spoofed via headers.
*   **Enable Improved Mode:** Switch the target application to "Improved Defenses".
    *   *Command:* `docker-compose stop target-app; $env:DEFENSE_MODE="improved"; docker-compose up -d target-app`
*   **Risk Scoring:** Explain that the "Improved" mode also enables behavioral risk scoring in the Flask application (tracking account failures, fingerprinting).
*   **Re-run Attack:** Briefly run the `ip_rotation` attack again against the improved defenses.
*   **Show Dashboard:** Show the "Weak vs Improved Defense" comparison chart, highlighting the significantly higher block rate.

## 5. Conclusion (6:00 - 7:00)

*   **Key Takeaways:**
    *   Rate limiting is only as strong as the identifier it uses. Trusting client-provided headers (like XFF) is a critical vulnerability.
    *   Attackers have access to cheap, distributed infrastructure and sophisticated tools.
    *   Defense-in-depth is essential (Real-IP rate limiting, behavioral scoring, MFA, CAPTCHA).
*   **Platform Value:** "This simulation platform provides a safe, controlled environment for security teams to understand these attacks, test their defenses, and validate their monitoring capabilities."
*   **Q&A:** Open the floor for questions.
