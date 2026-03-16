# Knowledge Base: Firewall Evasion & Stealth Reconnaissance
**Context:** This document correlates the advanced firewall evasion concepts from cybersecurity literature with the applied methodology in our `Part2_Cybersteps_Analysis.txt` report.

While the reference article discusses highly specific Nmap evasion flags (like fragmentation `-f`, decoys `-D`, and source-port manipulation), the underlying principle is the same: **Firewalls and IDS/IPS systems block unauthorized, noisy, or standard-signature scans.**

In our Cybersteps assessment, we applied foundational evasion and stealth techniques to achieve the same goals: bypassing perimeter defenses, avoiding rate-limiting, and discovering hidden services without triggering alarms.

Here is how our applied approach corresponds to the core concepts of firewall and IDS evasion.

---

## 1. Evading Rate-Based Firewalls and IPS
**The Concept (From Article):** Avoiding detection by IDS and IPS systems is crucial. Security layers often monitor packet rates and block IP addresses that send too many requests too quickly.
**Our Approach:** Moderate Rate / Timing Control
**Implementation:**
- `naabu -rate 2000 -retries 2`
- `nmap -T2` (Polite timing) and bounded RTT timeouts (`--max-rtt-timeout 3s`)

**Why we did it:** Instead of using Decoy scanning (`-D`) to mask our IP, we reduced the *velocity* of our scan. By slowing down (`-T2`), the scan traffic blends into background noise, preventing dynamic firewalls or fail2ban-style IPS from blacklisting our IP before the scan completes. This successfully bypassed any rate-limiting restrictions on the Cybersteps infrastructure.

## 2. Bypassing ICMP / Ping Drops
**The Concept:** Firewalls are strictly configured to block standard discovery probes. If a scanner relies on traditional methods to see if a host is "alive," the firewall drops the packet, and the scanner skips the host.
**Our Approach:** Assumption of Uptime (No-Ping)
**Implementation:** `nmap -Pn`

> **Q: How does the firewall know when it's a ping or not? When packets are dropped is nmap blocked or could you in principle ignore the ping result and just scan away?**
>
> **EN:** A "ping" uses a specific protocol (ICMP) that is different from TCP/UDP. The firewall simply reads the packet header; if it says "ICMP Echo Request", it drops it. Normally, if a ping fails, Nmap assumes the host is dead and stops. But yes, you can ignore the ping result! By using `-Pn`, we tell Nmap to skip the ping entirely and "just scan away," assuming the target is online.
>
> **DE:** Ein „Ping“ nutzt ein spezielles Protokoll (ICMP), das sich von TCP/UDP unterscheidet. Die Firewall liest einfach den Paket-Header; steht dort "ICMP Echo Request", blockiert sie es. Normalerweise denkt Nmap bei einem fehlgeschlagenen Ping, der Host sei offline, und bricht ab. Aber ja, man kann das Ping-Ergebnis ignorieren! Mit `-Pn` sagen wir Nmap, dass es den Ping komplett überspringen und „einfach scannen“ soll, da wir annehmen, dass das Ziel online ist.

**Why we did it:** We combined `Resolve-DnsName` to confirm the target's IP, and then instructed Nmap to skip host discovery (`-Pn`). Many modern firewalls drop ICMP echo requests. By skipping the ping phase, we forced Nmap to scan the target regardless of ICMP filtering, effectively bypassing the first layer of firewall defense.

## 3. Stealth Connection Handling
**The Concept (From Article):** The article highlights the TCP ACK scan (`-sA`) to map out firewall rule sets without establishing a connection.
**Our Approach:** SYN "Half-Open" Scanning
**Implementation:** `nmap -sS`

**Why we did it:** Similar to the ACK scan, the SYN scan (`-sS`) never completes the full TCP 3-way handshake. We send a SYN, receive a SYN/ACK, and then tear it down with an RST. Because the connection is never fully established, many legacy firewalls and application logs do not record the interaction. This is the foundation of non-intrusive, stealthy enumeration.

> **Q: What's RST?**
>
> **EN:** RST stands for "Reset". It's a TCP flag used to instantly kill a connection. Nmap sends "SYN" (Hello?), the server replies "SYN/ACK" (Yes?), and Nmap instantly replies "RST" (Never mind, bye!). Because the final step (ACK) was never sent, the server's application (like a web server) usually ignores the event and doesn't log it.
>
> **DE:** RST steht für „Reset“ (Zurücksetzen). Es ist ein TCP-Flag, das eine Verbindung sofort abbricht. Nmap sendet „SYN“ (Hallo?), der Server antwortet „SYN/ACK“ (Ja?), und Nmap antwortet sofort mit „RST“ (Schon gut, tschüss!). Weil der letzte Schritt (ACK) nie gesendet wurde, ignoriert die Anwendung des Servers das Ereignis meist und speichert es nicht in den Logs.

## 4. Reducing Signature Footprint
**The Concept (From Article):** Firewalls and IDS inspect packet content (which is why fragmentation `-f` is used).
**Our Approach:** Targeted Application Probing
**Implementation:** Running `nmap -sV` **only** on the specifically discovered open ports, rather than the entire port range.

**Why we did it:** Service version detection (`-sV`) sends actual application-level probes (like HTTP GET requests, FTP handshakes, etc.) which are highly visible to Deep Packet Inspection (DPI) firewalls and WAFs. By restricting `-sV` to only the 5 ports we already confirmed open via stealth SYN scans, we drastically reduced our signature footprint, preventing the firewall from detecting a massive wave of malformed application requests.

> **Q: So we first reduced the number of interesting ports but why don't we need to segment is there no gain in doing so?**
>
> **EN:** Packet fragmentation (`-f`) tries to hide malicious payloads by breaking them into tiny pieces so IDS/DPI can't read the whole signature. But since we are only doing normal version detection (no malicious exploits), fragmentation isn't necessary. In fact, modern firewalls often drop fragmented packets by default because attackers use them so often. Using `-f` here would slow us down and likely get us blocked faster.
>
> **DE:** Paketfragmentierung (`-f`) versucht, bösartige Payloads zu verstecken, indem sie in winzige Teile zerlegt werden, sodass IDS/DPI die Signatur nicht lesen können. Da wir jedoch nur normale Versionserkennung machen (keine Exploits), ist Fragmentierung unnötig. Tatsächlich blockieren moderne Firewalls fragmentierte Pakete oft standardmäßig, eben weil Angreifer sie oft nutzen. Hier `-f` zu nutzen, würde uns nur verlangsamen und wahrscheinlich schneller zu einer Blockade führen.
## 5. Mapping Firewall Rules via UDP
**The Concept:** Discovering misconfigurations and understanding how the firewall treats traffic to find hidden loopholes.
**Our Approach:** UDP State Analysis (`open|filtered`)
**Implementation:** `nmap -sU`

**Why we did it:** UDP is connectionless. When we probe a UDP port and receive no response, Nmap flags it as `open|filtered`. In our report, we explicitly analyzed this: it tells us the firewall is likely configured to drop (not reject) unsolicited UDP packets. By mapping these firewall responses (or lack thereof), we gain architectural insights into the target's perimeter defenses.

> **Q: I need clarification. Unsolicited? What architectural insights did we gain? Just the UDP discovery deriving from dropping a packet?**
>
> **EN:** "Unsolicited" means the server didn't ask for the packet; we sent it out of nowhere. The architectural insight is discovering the firewall's *policy*: it is configured to silently "drop" packets (give zero response) instead of "rejecting" them (which would send back an ICMP "Port Unreachable" error). This tells us the target network uses a "Stealth" or "Drop" defensive posture. While this makes UDP scanning annoying (because silence means either "open" or "firewall dropped it"), it reveals exactly how the Blue Team configured their perimeter.
>
> **DE:** „Unsolicited“ (unaufgefordert) bedeutet einfach, dass der Server nicht nach dem Paket gefragt hat; wir haben es aus dem Nichts gesendet. Die architektonische Erkenntnis ist das Entdecken der *Firewall-Richtlinie*: Sie ist so konfiguriert, dass sie Pakete stillschweigend „verwirft“ (keine Antwort gibt), anstatt sie „abzulehnen“ (was einen ICMP-Fehler „Port Unreachable“ zurücksenden würde). Das zeigt uns, dass das Netzwerk eine „Stealth“- oder „Drop“-Verteidigungsstrategie nutzt. Das macht das UDP-Scannen zwar nervig (weil Stille entweder „offen“ oder „von Firewall blockiert“ bedeutet), aber es verrät uns genau, wie das Blue Team den Perimeter konfiguriert hat.
---

## Future Extensibility
If the Cybersteps target were to implement stricter, active blocking mechanisms in the future, we would upgrade our methodology using the exact techniques from the reference article:
1. **`-f` (Fragmentation):** If an inline IPS begins dropping our `-sV` probes based on signature matching.
2. **`--source-port 53`:** If the firewall implements a default-deny policy but misconfigures trust for outgoing DNS traffic.
3. **`-D RND:10` (Decoys):** If the Blue Team begins actively hunting or blocking our specific IP address during the assessment.
4. **`-sI` (Idle Scan):** For ultimate stealth, bouncing our scans off a trusted zombie host on the same network segment.