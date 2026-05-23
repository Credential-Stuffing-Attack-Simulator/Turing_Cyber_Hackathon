# Threat Model Write-Up: Credential Stuffing

*This document is designed to be easily understood by both technical and non-technical readers.*

---

## 🛑 The Non-Technical Explanation (The "Nightclub" Analogy)

Imagine a very exclusive nightclub (your website). The nightclub has a bouncer at the front door (the Rate Limiter). 

The bouncer's rule is simple: **"If one person tries to guess a password more than 5 times in a row, kick them out."**

### How a Normal Attack Fails:
A bad guy puts on a red hat and walks up to the bouncer. He guesses "Password123" (Wrong). He guesses "123456" (Wrong). He does this 5 times. The bouncer says, "You in the red hat! You're guessing too fast. You are blocked." **(This is normal rate limiting).**

### How The "Credential Stuffing Bypass" Works:
The bad guy realizes the bouncer is only looking at *hats* (IP Addresses). So, the bad guy brings a massive bag of 1,000 different hats (Proxy IP addresses). 
1. He puts on a blue hat, guesses once (Wrong), and steps away before the bouncer blocks him.
2. He immediately puts on a green hat, walks back up, and guesses again (Wrong). 
3. He puts on a yellow hat... and so on.

Because the bouncer only blocks people wearing the *same* hat who guess 5 times, the bad guy easily bypasses the security by changing his hat every single time. He can try 10,000 passwords, and the bouncer never stops him.

**This is what our project simulates.** We built the nightclub, we built the bouncer with the bad rule, and we built the attacker with the bag of hats.

---

## 🔍 The Technical Threat Model (STRIDE)

For technical teams, we use the **STRIDE** methodology to categorize the threats to our authentication system.

| Threat Category | How it applies to this project | Our Mitigation |
| :--- | :--- | :--- |
| **S**poofing | The attacker fakes their IP address using the `X-Forwarded-For` header so the server doesn't know who they really are. | We switch to checking the true TCP connection IP (`$binary_remote_addr`) instead of trusting headers. |
| **T**ampering | The attacker tampers with HTTP request headers (like rotating the User-Agent) to look like different web browsers. | We implement "Device Fingerprinting" to see past the fake headers. |
| **R**epudiation | If logs only capture the fake IP, the attacker can deny it was them. | We log both the fake IP and the true IP in our JSON telemetry so we always have the truth. |
| **I**nformation Disclosure | The attacker discovers which passwords are correct. | We implement CAPTCHA and MFA so even a correct password isn't enough to get in. |
| **D**enial of Service | The attacker sends so many login requests that the server crashes. | Even our "improved" defenses use strict burst rate limiting to drop excess traffic instantly. |
| **E**levation of Privilege | The attacker gets into an Admin account using a stolen password. | We use Risk Scoring. If an account has been attacked heavily, we temporarily lock it. |

---

## 🎯 The Primary Threat Actor

*   **Who they are:** Automated botnets and cybercriminal groups.
*   **What they have:** Massive lists of usernames and passwords stolen from other website breaches (like the Yahoo or LinkedIn breaches).
*   **What they want:** To automatically test millions of stolen passwords against *your* website to see if users reused the same password. If they get in, they steal money, data, or computing resources.
*   **How we stop them:** By recognizing that Rate Limiting alone is not enough. We must use Defense-in-Depth (CAPTCHA, Multi-Factor Authentication, and Behavioral Risk Scoring).
