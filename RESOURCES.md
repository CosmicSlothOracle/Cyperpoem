# Reconnaissance Tools — Resources & Use Cases

Valid, up-to-date links and metadata for every tool and data source used in this project. Use this for attack-surface and subdomain recon; all resources are publicly available and legal for defensive research and authorized testing.

---

## Official resources (validated)

| Tool / resource | Link | Stars | Forks | License | Notes / warnings |
|-----------------|------|-------|-------|---------|------------------|
| **subfinder** | [github.com/projectdiscovery/subfinder](https://github.com/projectdiscovery/subfinder) | ~13.2k | ~1.5k | MIT | None. Passive-only; respect rate limits of built-in sources. |
| **dnsx** | [github.com/projectdiscovery/dnsx](https://github.com/projectdiscovery/dnsx) | ~2.7k | — | MIT | Use with your own resolvers or public ones; avoid abusive query volume. |
| **naabu** | [github.com/projectdiscovery/naabu](https://github.com/projectdiscovery/naabu) | ~5.8k | — | MIT | Port scanning: only use against targets you are authorized to scan. |
| **httpx** | [github.com/projectdiscovery/httpx](https://github.com/projectdiscovery/httpx) | ~9.6k | — | MIT | Probe only in-scope hosts; high concurrency can be noisy. |
| **nuclei** | [github.com/projectdiscovery/nuclei](https://github.com/projectdiscovery/nuclei) | ~27.4k | ~3.3k | MIT | Run only against authorized assets; some templates may trigger WAF/IDS. |
| **findomain** | [github.com/Findomain/Findomain](https://github.com/Findomain/Findomain) | ~3.7k | ~392 | GPL-3.0 | Free vs Plus tiers; API keys needed for some sources. |
| **assetfinder** | [github.com/tomnomnom/assetfinder](https://github.com/tomnomnom/assetfinder) | ~3.5k | — | MIT | Uses passive sources; rate limits apply per upstream. |
| **shuffledns** | [github.com/projectdiscovery/shuffledns](https://github.com/projectdiscovery/shuffledns) | ~1.6k | — | MIT | Requires MassDNS; active brute-force — use only on authorized domains. |
| **crt.sh** | [crt.sh](https://crt.sh/) | N/A | N/A | Sectigo-operated | Certificate Transparency search; no API key for basic use. Query responsibly. |
| **ThreatCrowd** | [API docs](https://www.threatcrowd.org/) / [Search API](https://threatcrowd.blogspot.com/p/api.html) | N/A | N/A | Use policy | Free API; domain/IP/email search. Check current availability. |
| **HackerTarget** | [hackertarget.com](https://hackertarget.com/) — [DNS tools](https://hackertarget.com/dns-lookup/) | N/A | N/A | ToS | Free tier ~50 queries/day; API for DNS/subdomain/host search. |
| **BufferOver** | [tls.bufferover.run](https://tls.bufferover.run/) (DNS/TLS) | N/A | N/A | ToS | Free tier limited; service has been unreliable; have fallbacks (e.g. crt.sh, subfinder). |

*Star/fork counts approximate (GitHub); check repos for latest.*

---

## Use case (one line per tool)

- **subfinder** — Passive subdomain discovery from many online sources; good first step before brute-force.
- **dnsx** — Resolve and validate subdomains at scale; wildcard detection and record-type checks.
- **naabu** — Fast port scan on discovered hosts to map open services (e.g. 80, 443, 8080).
- **httpx** — Probe live HTTP(S) hosts, titles, tech stack; filter “alive” targets for next steps.
- **nuclei** — Template-based vuln checks on web/DNS/network; prioritize critical/high templates.
- **findomain** — Cross-platform subdomain enum via CT and APIs; optional screenshots/monitoring.
- **assetfinder** — Find domains/subdomains tied to a root domain via passive data.
- **shuffledns** — Mass resolve wordlist-based subdomains with wildcard handling; complements passive.
- **crt.sh** — Subdomains from Certificate Transparency logs; no auth, often finds forgotten hosts.
- **ThreatCrowd** — OSINT: related domains, IPs, emails for a given domain or indicator.
- **HackerTarget** — DNS lookups, host search, zone transfer checks via simple API.
- **BufferOver** — TLS/DNS-style API for cert/domain data; use as optional source when available.

---

## Why this stack fits the project

- **Credibility:** All tools are widely used in bug bounty and pentest workflows (ProjectDiscovery suite, crt.sh, established APIs).
- **Legal clarity:** MIT/GPL and public APIs; usage stays within public data and authorized testing when you follow each project’s and provider’s terms.
- **Observable value:** Passive + active + validation (dnsx/httpx) gives a clear picture of *public* attack surface without touching out-of-scope or abusive traffic.
- **Reproducibility:** Install scripts and this resource list let others replicate the same recon pipeline and cite exact tool versions and sources.

Use only on targets you are authorized to test; respect rate limits and program policies (e.g. bug bounty / responsible disclosure).
