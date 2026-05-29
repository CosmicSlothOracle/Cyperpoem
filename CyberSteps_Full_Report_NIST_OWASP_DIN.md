# Penetration Test Report — CyberStepsVuln (Framework-Aligned)

| Field | Value |
| --- | --- |
| **Target** | Web application at `http://10.10.10.10` (lab VM) |
| **Assessment snapshot** | March–April 2026 |
| **Evidence roots** | Primary: `Cyberlab Report/cybersteps_full_evidence/` — supplementary: `/home/laurin/cosmicdfiscovery/` (upload/LFI transcripts, independent methodology) |
| **Delivered bundle** | `CyberSteps_evidence_bundle.zip` (see Section 10) |
| **Classification** | Confidential — educational / authorized lab use only |
| **Frameworks referenced** | NIST (risk & controls), CVE/CVSS/CWE, DIN EN ISO/IEC 27001 (control themes), OWASP Top 10 / ASVS |

---

## 1. Executive summary

**Purpose**  
This report summarizes security testing of the intentionally vulnerable **CyberStepsVuln** application in an isolated training environment. It is written for stakeholders who need a clear picture of risk, regulatory-relevant control gaps (at a high level), and prioritized hardening.

**What was found (substance)**  
The application exhibits **multiple critical weaknesses** that chain together: unauthenticated or weakly authenticated users can reach **SQL injection**, **broken access control** (forgeable dashboard identity), and—after administrative access—**remote code execution** via upload plus dynamic inclusion, **server-side request forgery (SSRF)**, **XML external entity (XXE)** processing, and **local file inclusion (LFI)** including **unauthenticated** file read via `ThemeLoader.php` using PHP stream wrappers (documented in `evidence_theme_lfi_wrapper.txt`). Host-level **misconfiguration** (e.g. SUID interpreter) allows **privilege escalation to root** once code execution exists. **Information disclosure** (`robots.txt`, password list paths) and **cross-site scripting (XSS)** patterns in the admin UI add further risk.

**Overall posture**  
The system is **not suitable for production**. Confidentiality, integrity, and accountability are **materially compromised** in the lab configuration; availability is at risk after compromise.

**Items explicitly *not* proven in the captured evidence session**  
Per `evidence_suspected_not_fully_proven.txt`: **CSRF** against `passchangedocument.php` (suspected, no PoC in session), **command injection** in `module=fetch` (not confirmed; SSRF was), **session fixation** (not tested), and **additional SQLi** in `Reviews.php` / `Deals.php` (not re-verified with sqlmap in that run). These should be tracked as **follow-up test items**, not as closed findings.

**Recommendations in one line**  
Remediate **injection**, **unsafe inclusion/upload**, and **access control** first; then SSRF/XXE, disclosure, XSS, secrets management, and OS baseline; retest with the same methodology.

---

## 2. Scope, methodology, and limitations

**In scope**  
CyberStepsVuln web surface, discoverable paths, injection and server-side flaw classes, and limited post-exploitation to confirm impact (authorized lab only).

**Methodology**  
Aligned with **OWASP Web Security Testing Guide (WSTG)** practices: reconnaissance, mapping, input testing, authentication/session testing, access control, SSRF/XXE/file handling, and evidence capture (`evidence_*.txt`, attack chain in `evidence_attack_chain_summary.txt`).

**Limitations**  
VM resets change credentials and flags; evidence reflects **point-in-time** proofs. Transcripts from different folders may reflect **different VM snapshots** (e.g. Elias password `5225` in the March‑31 sqlmap bundle vs. older hashes in some `cosmicdfiscovery` logs — always verify against the live target). Internet-facing attack paths were out of scope. Suspected issues without PoC are listed separately (Section 8).

**Supplementary corpus**  
The compact `cybersteps_full_evidence/` run does not include every HTTP transcript (e.g. raw `POST /support.php`). Those are preserved under **`/home/laurin/cosmicdfiscovery/`** — see Section 10.

---

## 3. Risk evaluation

### 3.1 Method (NIST SP 800-30 style)

Risk is described using **likelihood** and **impact** on organizational operations, assets, and individuals, consistent with **NIST SP 800-30** (Guide for Conducting Risk Assessments). Residual risk after fixes must be reassessed.

| Qualitative rating | Meaning (for this report) |
| --- | --- |
| **Critical** | Trivial or reliable path to full application or host compromise, or mass credential/data breach |
| **High** | Serious compromise or major data exposure; often chained from another flaw |
| **Medium** | Realistic exploitation with constraints or moderate business impact |
| **Low** | Limited impact or difficult exploitation |
| **Informational** | Defense-in-depth / hygiene |

**CIA summary (NIST confidentiality / integrity / availability framing)**  

| Pillar | Assessment |
| --- | --- |
| **Confidentiality** | **Failed** — DB contents, files, internal pages, and source/credentials reachable via multiple vectors |
| **Integrity** | **Failed** — SQLi and RCE allow arbitrary data and code changes |
| **Availability** | **At risk** — post-RCE DoS or destructive actions feasible |
| **Accountability** | **Weak** — forgeable dashboard tokens undermine attribution |

### 3.2 NIST Cybersecurity Framework (CSF) 2.0 — high-level gap view

| Function | Observation |
| --- | --- |
| **Govern (GV)** | Lab target; in production would need explicit security requirements and acceptance criteria before release |
| **Identify (ID)** | Asset inventory and data-flow mapping would expose dangerous trust boundaries (upload → include, XML → file) |
| **Protect (PR)** | Missing secure coding controls (parameterization, session management, input validation, upload restrictions) |
| **Detect (DE)** | No evidence of compensating monitoring; exploitation would be noisy but not necessarily detected |
| **Respond (RS)** | Incident playbooks would assume full rebuild if RCE + DB exposure occurred |
| **Recover (RC)** | Credential rotation and re-imaging indicated after any comparable breach |

### 3.3 CVE / CVSS / CWE orientation

**Note:** “CVEE” is interpreted here as **CVE** identifiers and **CVSS** scoring practice. This lab app may not have public CVE entries; the table uses **representative CWE** classes and **indicative CVSS vectors** (Base, v3.1 style) for *planning* severity—actual scores depend on deployment context (network exposure, data sensitivity).

| Finding area | Representative CWE | Typical OWASP category | Indicative severity* |
| --- | --- | --- | --- |
| SQLi (`visiter-newsdesk.php`) | CWE-89 | A03:2021 Injection | **Critical** (AV:N/AC:L/PR:N…) |
| RCE (upload + `loadfile` include) | CWE-434, CWE-98 | A03:2021, A04:2021 | **Critical** |
| Dashboard cookie forgery | CWE-287, CWE-639 | A01:2021 Broken Access Control | **High** |
| SSRF (`module=fetch`) | CWE-918 | A10:2021 SSRF | **High** |
| XXE (`module=import`) | CWE-611 | A05:2021 Security Misconfiguration | **High** |
| LFI / path traversal (`ThemeLoader`, `loadfile`) | CWE-22, CWE-73 | A01:2021, A03:2021 | **High** (ThemeLoader: **unauth** read → higher exposure) |
| Hard-coded DB credentials | CWE-798 | A07:2021 | **High** |
| robots.txt / password list disclosure | CWE-200, CWE-538 | A01:2021, A05:2021 | **Medium** |
| Admin XSS (`innerHTML`) | CWE-79 | A03:2021 | **Medium** |
| SUID interpreter on host | CWE-732 | A05:2021 (deployment) | **High** (chained) |

\*Indicative only; validate with your CVSS calculator for production.

### 3.4 DIN EN ISO/IEC 27001:2022 — Annex A control themes (mapping)

German organizations often implement **DIN EN ISO/IEC 27001** with **Annex A** controls. The following themes apply (not an exhaustive ISMS audit):

| Control theme (Annex A area) | Relevance to findings |
| --- | --- |
| **A.5** Information security policies | Secure SDLC and “no dynamic include of user paths” type rules |
| **A.8** Asset management | Classification of credentials, DB, and upload storage |
| **A.9** Access control | Server-side sessions, RBAC, no client-trusted `uid` |
| **A.10** Cryptography | Proper session tokens, TLS in production; no secrets in source |
| **A.14** System acquisition / development / maintenance | Prepared statements, safe XML, SSRF allow-lists |
| **A.12** Operations security | Hardened OS baseline (no SUID interpreters), separation of upload and execution |
| **A.16** Incident management | Assume breach procedures if SQLi/RCE ever exposed production |

*For formal certification, use the official Annex A statement applicability and SoA.*

### 3.5 OWASP mapping (Top 10 2021 + ASVS intent)

| OWASP Top 10 2021 | Findings |
| --- | --- |
| **A01 Broken Access Control** | Dashboard cookie forgery; LFI/Admin `loadfile` abuse |
| **A02 Cryptographic Failures** | Weak token design; plaintext DB password in source |
| **A03 Injection** | SQLi; XSS pattern |
| **A04 Insecure Design** | Upload + include design; theme loader accepting wrappers |
| **A05 Security Misconfiguration** | XXE-enabled parser; SUID on host; disclosure via `robots.txt` |
| **A06 Vulnerable Components** | (Lab stack; keep patched in real deployments) |
| **A07 Identification / Auth Failures** | Session/token design |
| **A08 Software / Data Integrity** | Unrestricted upload path |
| **A09 Logging / Monitoring** | Not assessed as mature control |
| **A10 SSRF** | `module=fetch` |

**ASVS (Application Security Verification Standard)** — target for rebuild: **V5** (validation), **V7** (access control), **V9** (communications), **V12** (files), **V13** (API), **V14** (configuration), at appropriate level (e.g. Level 2 for internet-facing).

---

## 4. Findings summary (rated)

| ID | Title | Severity | Primary evidence (`cybersteps_full_evidence/`) | Supplementary (`cosmicdfiscovery/`, etc.) |
| --- | --- | --- | --- | --- |
| F-01 | SQL injection — `visiter-newsdesk.php` | Critical | `evidence_sqlmap_visiter_newsdesk.txt` | `output_10.10.10.10/sqli_dump.txt`, `sqli_request.txt` |
| F-02 | RCE — upload + `loadfile` include | Critical | `evidence_lfi_rce_admin_upload.txt` | `upload_debug.txt`, `output_10.10.10.10/upload_response.txt`, `pentest_correction_20260408/command_log.txt`, `pentest_correction_20260408/LEAD_PENTESTER_REVIEW.md` (curl `POST` `support.php`) |
| F-03 | Broken access control — dashboard cookies | High | `evidence_dashboard_idor.txt` | `evidence_20260326/dashboard_authenticated.html`, `master_admin_dashboard.html` |
| F-04 | SSRF — `module=fetch` | High | `evidence_ssrf_fetch_module.txt` | `pentest_correction_20260408/command_log.txt` |
| F-05 | XXE — `module=import` | High | `evidence_xxe_import_module.txt` | — |
| F-06 | LFI — `ThemeLoader.php` / `loadfile` | High | `evidence_theme_lfi_wrapper.txt`, `evidence_lfi_rce_admin_upload.txt` | `pentest_independent_20260408/INDEPENDENT_PENTEST_REPORT.md` (`php://filter` → `support.php` / source recovery) |
| F-07 | Information disclosure | Medium | `evidence_disclosure_robots.txt`, `evidence_gobuster_common.txt` | `evidence_20260326/gobuster_*.txt`, `robots.txt`, `info.txt` |
| F-08 | XSS pattern — admin UI | Medium | `evidence_xss_admin_panel_js.txt` | — |
| F-09 | Host privesc — SUID interpreter | High | `evidence_lfi_rce_admin_upload.txt` | `pentest_correction_20260408/command_log.txt` |
| F-10 | Hard-coded DB credentials | High | `evidence_admin_mysql_hardcoded_review.txt` | `INDEPENDENT_PENTEST_REPORT.md` (LFI + filter methodology); provenance: combine with F-06 transcripts |

---

## 5. Hardening and remediation (prioritized)

### 5.1 P0 — Stop breach paths

1. **SQLi:** Parameterized queries everywhere; strict integer validation for IDs; retest `Reviews.php` / `Deals.php` with sqlmap in a safe environment.  
2. **RCE / LFI:** Never `include`/`require` user-controlled paths; store uploads **outside web root** or strip execution; **disable PHP** in upload directories; allow-list theme names only (no `php://filter`).  
3. **Access control:** Replace cookie `uid` / Base64 `auth_token` with **opaque server-side sessions** (httpOnly, Secure, SameSite); enforce authorization on every action.

### 5.2 P1 — Server-side abuse classes

4. **SSRF:** Allow-list destinations; block link-local and private ranges; no raw `file_get_contents($userUrl)` without policy.  
5. **XXE:** Disable external entities and DTDs on untrusted XML; use safe parser defaults.  
6. **Secrets:** Remove DB passwords from source; use vault/env injection; rotate after any disclosure; least-privilege DB account.

### 5.3 P2 — Disclosure, XSS, and client hardening

7. **robots.txt / static lists:** Do not advertise sensitive paths; remove password corpora from web root.  
8. **XSS:** Avoid `innerHTML` with untrusted data; use encoding/CSP.  
9. **CSRF (follow-up):** For state-changing admin forms (`passchangedocument.php` etc.), implement **synchronizer tokens** or double-submit cookie; verify with PoC.

### 5.4 P3 — Host and operations (NIST SP 800-53 / IEC 27001 operations)

10. **OS baseline:** Remove SUID from interpreters; use vendor-hardened images; segregate web and DB tiers.  
11. **Monitoring:** Log authentication failures, admin actions, and file/upload anomalies (detect function).  
12. **SDLC:** Threat modeling on “upload + render + include” flows; security testing in CI (SAST/DAST where appropriate).

---

## 6. NIST SP 800-53 Rev. 5 — sample control targets (illustrative)

For a production system, teams often map findings to **NIST SP 800-53** controls. Examples:

| Control | Relevance |
| --- | --- |
| **AC-3** Access enforcement | Enforce per-request authorization; fix IDOR |
| **AC-4** Information flow | SSRF restrictions |
| **SI-10** Information input validation | Parameterization, allow-lists |
| **SC-8** Transmission confidentiality / integrity | TLS for production |
| **CM-6** Configuration settings | PHP wrapper/disable dangerous features; XML parser |
| **RA-5** Vulnerability scanning | Regular retest after remediation |

---

## 7. Attack chain (lab) — for awareness

Documented end-to-end path: recon → `robots.txt` / discovery → **ThemeLoader LFI** → **SQLi** user dump → **forged dashboard** → admin login → **LFI+RCE** → **SSRF** / **XXE** → static flags → **SUID privesc** (`evidence_attack_chain_summary.txt`). In production, **any single Critical link** is often enough for unacceptable risk.

---

## 8. Open / suspected items (not closed in evidence)

- CSRF on `passchangedocument.php` / admin forms — **test and document**  
- Command injection in `module=fetch` — **clarify vs SSRF**  
- Session fixation — **test**  
- Additional SQLi surfaces — **verify**

---

## 9. References

- NIST SP 800-30 (risk assessments): https://csrc.nist.gov/publications/detail/sp/800-30/rev-1/final  
- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final  
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework  
- CVE / CWE: https://www.cve.org/ , https://cwe.mitre.org/  
- DIN EN ISO/IEC 27001:2022 (purchase via Beuth/DIN; map Annex A in SoA)  
- OWASP Top 10: https://owasp.org/www-project-top-ten/  
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/  
- OWASP WSTG: https://owasp.org/www-project-web-security-testing-guide/

---

## 10. Evidence corpus

**Download:** `CyberSteps_evidence_bundle.zip` — browse individual files at `evidence.html`.

**Primary bundle (March‑31 evidence run)** — `evidence/cybersteps_full_evidence/`

Includes: `evidence_00_scope_meta.txt`, `evidence_attack_chain_summary.txt`, `evidence_suspected_not_fully_proven.txt`, `evidence_recon_nmap.txt`, `scan_tcp.xml`, `nmap_services.xml`, `evidence_disclosure_robots.txt`, `evidence_theme_lfi_wrapper.txt`, `evidence_gobuster_common.txt`, `evidence_info_hint_sqli.txt`, `evidence_sqlmap_visiter_newsdesk.txt`, `evidence_guest_credentials_status.txt`, `evidence_dashboard_idor.txt`, `evidence_ssrf_fetch_module.txt`, `evidence_xxe_import_module.txt`, `evidence_flags_static_pages.txt`, `evidence_xss_admin_panel_js.txt`, `evidence_admin_mysql_hardcoded_review.txt`, `merged_scan.xml`, `CyberSteps_Evidence_Report.html`.

**Narrative / lab write-up**

`evidence/cybersteps_vm_reset_evidence/Security Assessment Report.md`

**Supplementary transcripts** — `evidence/cosmicdfiscovery/`:

| File | Role |
| --- | --- |
| `upload_debug.txt` | Full HTTP trace: `POST /support.php` (multipart upload) |
| `output_10.10.10.10/upload_response.txt` | Saved upload response body |
| `output_10.10.10.10/sqli_dump.txt` | Extended SQLi / page context (earlier run) |
| `output_10.10.10.10/sqli_request.txt` | Request artifact for SQLi testing |
| `output_10.10.10.10/gobust.txt` | Additional directory enumeration |

Files cited in findings but not recovered from the archive: `evidence_lfi_rce_admin_upload.txt`, `pentest_correction_20260408/`, `pentest_independent_20260408/`.
