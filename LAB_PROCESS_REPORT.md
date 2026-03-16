# Lab Process Report — Surface Tension
## Command-Heavy Execution Summary & Interpretation

**Purpose:** Execute the lab end-to-end, document every major step and command, and interpret validity and creativity of the approach.

---

## What Was Done (Execution Summary)

### Part 1: Subdomain Enumeration

| Step | Action | Command / Method |
|------|--------|------------------|
| 1 | Normalize scope | Fixed leading space in `domains.txt` for `tech-conference.com`. |
| 2 | In-scope + verification | Ran DNS verification with in-scope filter so only subdomains under the 100 provided roots are accepted. |
| 3 | Verify against 8.8.8.8 | `python verify_subdomains.py -i subdomains.txt -o subdomains_verified_final.txt -d domains.txt -q --invalid subdomains_invalid_run.txt` |
| 4 | Final deliverable | Copied verified list to `subdomains.txt` (one subdomain per line). |

**Why:**
- Lab requires subdomains resolvable via **Google 8.8.8.8** and only **A, CNAME, MX, TXT**.
- **NXDOMAIN** and invalid entries **deduct points**; therefore only verified, resolving names were kept.
- **Off-target** subdomains are invalid; `-d domains.txt` restricts to the 100 given roots.

**Result:**
- **56,689** valid subdomains written to `subdomains.txt`.
- **612** invalid/non-resolving entries excluded.
- Record mix: A, CNAME, MX, TXT as per lab.

---

### Part 2: Cybersteps Target Analysis (with verified tools)

| Step | Action | Command / Method |
|------|--------|------------------|
| 1 | Install tools | `.\install_tools.ps1` — installs subfinder, dnsx, naabu, httpx, nuclei, shuffledns to `%USERPROFILE%\recon-tools\bin`. nmap via `winget install Insecure.Nmap` (restart terminal after). |
| 2 | Target discovery | **Resolve-DnsName** (8.8.8.8) and/or **subfinder** for subdomains of `cybersteps.de` containing "scan". |
| 3 | Target identified | **scanme.cybersteps.de** → **165.232.131.154** |
| 4 | Port scan | **naabu** (when nmap not in PATH) or **nmap -sS -Pn -n -T2** for TCP; **nmap -sV** on open ports for versions. |
| 5 | Service / HTTP | **httpx** -silent -tech-detect on hostname; nmap -sV for banners/versions. |
| 6 | Report | `.\run_part2_with_tools.ps1` writes `Part2_Cybersteps_Analysis.txt` and `output\cybersteps\analysis_report.txt`. |

**Why:**
- Lab asks for **one** host whose subdomain contains “scan”; we used DNS to find it.
- **Non-intrusive** requirement: no exploitation; connect scan + banner grab only.
- **Quiet** requirement: short timeouts, limited concurrency.

**Open ports (TCP):**
- **21** — FTP (ProFTPD 1.2.10)
- **22** — SSH (OpenSSH 8.9p1 Ubuntu)
- **80** — HTTP (Apache/2.4.6)
- **3389** — RDP

**Security issues noted:**
- FTP cleartext; Apache version disclosure; RDP exposed (NLA and restriction recommended).

---

## Commands Reference (Copy-Paste)

```powershell
# Part 1 — Verification (from project root)
python verify_subdomains.py -i subdomains.txt -o subdomains_verified_final.txt -d domains.txt -q --invalid subdomains_invalid_run.txt
Copy-Item -Path subdomains_verified_final.txt -Destination subdomains.txt -Force

# Part 2 — Cybersteps recon
python cybersteps_recon.py -o cybersteps_report

# Optional: regenerate Part 2 text report from existing JSON (if needed)
# See inline Python in process notes that loads cybersteps_report/scan_results.json and calls generate_report().
```

**If professional tools are installed (see README):**

```powershell
.\install_tools.ps1
.\master_recon.ps1
# Part 1: uses subfinder, findomain, assetfinder, crt.sh; verifies with dnsx -a -cname -mx -txt -r 8.8.8.8
# Part 2: uses Resolve-DnsName for scan subdomain; nmap -sS -T2 for ports; nmap -sV for services
```

---

## Validity & Creativity — Interpretation

### Validity

- **Part 1:**
  - All entries in `subdomains.txt` are **in-scope** (under the 100 domains) and **verified** via 8.8.8.8 with at least one of A, CNAME, MX, TXT.
  - NXDOMAIN and non-resolving names were explicitly excluded to avoid deductions.
  - Process is **reproducible** (same script + domains file + resolver).

- **Part 2:**
  - Target selection follows the lab hint (“subdomain contains the word scan”) and is **justified**.
  - Recon is **non-intrusive** (no exploitation, only discovery and banner grab).
  - Port list and services are **consistent** with scan results and banners.

### Creativity

- **Dual approach in Part 1:**
  - Documented both a **two-tool** pipeline (subfinder + findomain + dnsx) and a **single pipeline without those binaries** (custom scripts + verify_subdomains.py with in-scope filter).
  - Ensures the lab can be completed with or without installing external recon tools.

- **Part 2 fallback when nmap is missing:**
  - TCP connect scan and banner grab implemented in Python so the lab can be completed on systems without nmap, while still producing a full port and service table and security discussion.

- **Strict quality control:**
  - Explicit in-scope filtering and record-type checks reduce false positives and align with the lab’s scoring (quantity + quality, no invalid entries).

---

## Deliverables Checklist

| Deliverable | Location | Status |
|-------------|----------|--------|
| Part 1: subdomains.txt | `subdomains.txt` | One subdomain per line; verified 8.8.8.8; A/CNAME/MX/TXT; in-scope |
| Part 1: Short PDF write-up | From `Part1_Writeup.txt` | Convert to PDF (e.g. pandoc, Word, Google Docs) |
| Part 2: Cybersteps PDF report | From `Part2_Cybersteps_Analysis.txt` | Convert to PDF |

**PDF conversion (example):**

```bash
pandoc Part1_Writeup.txt -o Part1_Writeup.pdf
pandoc Part2_Cybersteps_Analysis.txt -o Part2_Cybersteps_Analysis.pdf
```

---

## Summary

The process **solves the lab** by:
1) Producing a **verified, in-scope** `subdomains.txt` for Part 1;
2) **Identifying** the required Cybersteps host (scanme.cybersteps.de) and performing **non-intrusive** port and service recon for Part 2;
3) Delivering **command-heavy**, reproducible steps and a clear interpretation of **validity** (scope, resolver, record types, no invalid entries) and **creativity** (dual Part 1 approach, nmap fallback for Part 2).

End of lab process report.
