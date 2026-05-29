---
title: Penetration Test Report
subtitle: CyberStepsVuln Web Application
client: Module Lab (Educational)
target: 10.10.10.10
author: Laurin
date: 2026-03-31
classification: Confidential — Educational use only
---

## Cover Page


| Field               | Value                                                     |
| ------------------- | --------------------------------------------------------- |
| **Report title**    | Penetration Test Report — CyberStepsVuln                  |
| **Target**          | Web application at `http://10.10.10.10` (VMware lab host) |
| **Assessment date** | 31 March 2026                                             |
| **Report version**  | 1.0                                                       |
| **Classification**  | Confidential                                              |


*This assessment was performed in an isolated training environment against an intentionally vulnerable application. Findings must not be used to justify testing third-party systems without authorization.*



## 1. Executive Summary

**What we tested**  
We reviewed the security of a custom website running on a single server in your training network. The review looked at how the site handles logins, user data, file uploads, and links to other pages and internal services.

**Overall posture**  
The application is **not safe for production use**. Several serious design flaws allow an attacker who can reach the website to read private data, act as an administrator without a real password, run commands on the server, and reach internal pages that should not be exposed to the internet.

**What matters most (in plain terms)**  

- **User database exposure:** A mistake in one news page lets anyone pull usernames and passwords from the database.  
- **Fake “admin” access:** The member dashboard trusts easy-to-forge browser cookies, so an attacker can view another user’s account without logging in properly.  
- **Server takeover:** After gaining admin access to the site, an attacker can upload a disguised script and run it, then elevate to full system control because a maintenance tool was left in an unsafe configuration.

**Business risk**  
If this were a real customer-facing product, you would face **loss of all customer credentials**, **complete website defacement**, **data theft**, and **regulatory exposure** depending on the data held. In the lab, these issues are expected; in production they would be emergencies.

**Recommended priority**  
Treat **database injection**, **unauthenticated file execution**, and **broken access control** as the first items to fix before any public release. Secondary items include secret data in public files, unsafe file fetching from the internet, and weak XML handling.

*This summary intentionally avoids technical product names and vulnerability catalogue numbers so non-technical readers can follow the message.*



## 2. Scope and Methodology

### 2.1 Scope (aligned with lab brief)

**In scope**


| Area                            | Description                                                    |
| ------------------------------- | -------------------------------------------------------------- |
| CyberStepsVuln web application  | All pages, forms, parameters, and behaviour on the VM          |
| Hidden directories and services | Anything discoverable by enumeration on the target             |
| Web vulnerability classes       | Injection, access control, misconfiguration, server-side flaws |
| Server-side readable assets     | Configuration and source exposed through flaws                 |


**Out of scope**


| Area                                        | Reason                     |
| ------------------------------------------- | -------------------------- |
| Third-party CDNs (Bootstrap, jQuery, fonts) | Not operated by the target |
| Social engineering                          | Not part of assessment     |
| Physical security                           | Not applicable             |


### 2.2 Methodology

Testing followed a structured web assessment approach comparable to the OWASP Web Security Testing Guide: network service identification, content discovery, mapping inputs, testing for injection and access control defects, server-side issues (request forgery, XML, file inclusion), and limited post-exploitation to confirm impact. Testing was performed **only** from an authorized attacker workstation on the same lab network (`10.10.10.0/24`).

### 2.3 Limitations

- Credentials and flags can change when the VM is reset; all proofs in the appendix reflect the **assessment snapshot dated above**.  
- Screenshots referenced in this document must be captured during live testing and inserted where marked `[Screenshot]`.  
- External attack paths (e.g. internet-based scanning) were not in scope.



## 3. Risk rating scale


| Rating            | Definition                                            | Typical response time     |
| ----------------- | ----------------------------------------------------- | ------------------------- |
| **Critical**      | Immediate full compromise or mass data breach         | Fix immediately           |
| **High**          | Strong likelihood of serious data loss or admin abuse | Fix within days           |
| **Medium**        | Exploitable with constraints or limited impact        | Fix in next release cycle |
| **Low**           | Minor issue or hard-to-exploit                        | Schedule with backlog     |
| **Informational** | Hardening or transparency issue                       | Best practice             |


**Residual risk note:** Even after fixes, regular retesting and secure development practices are required.



## 4. Findings summary (rated)


| ID   | Title                                                 | Severity     | Component                                             |
| ---- | ----------------------------------------------------- | ------------ | ----------------------------------------------------- |
| F-01 | SQL injection in news desk                            | **Critical** | `visiter-newsdesk.php` — `id`                         |
| F-02 | Remote code execution via upload + file include       | **Critical** | `support.php`, `Admin.php` — `loadfile`               |
| F-03 | Weak dashboard session / IDOR                         | **High**     | `/dashboard/` — cookies `uid`, `auth_token`           |
| F-04 | Server-side request forgery (internal pivot)          | **High**     | `Admin.php` — `module=fetch`, `img_url`               |
| F-05 | XML external entity (XXE)                             | **High**     | `Admin.php` — `module=import`, `xml_data`             |
| F-06 | Local file inclusion / path abuse                     | **High**     | `Admin.php` — `loadfile`; `ThemeLoader.php` — `theme` |
| F-07 | Sensitive data exposure (`robots.txt`, password list) | **Medium**   | `/robots.txt`, `/decoda9013smith21985.txt`            |
| F-08 | Cross-site scripting (DOM / reflected pattern)        | **Medium**   | `Admin.php` — profile UI (`Able()` / `innerHTML`)     |
| F-09 | Privilege escalation on host (SUID interpreter)       | **High**     | OS — `/usr/bin/python3.8`                             |
| F-10 | Hard-coded database credentials in application source | **High**     | `Admin.php` (disclosed via F-06 / code review)        |


*Minimum lab requirement (≥5 documented issues): satisfied.*



## 5. Detailed findings

### F-01 — SQL injection (Critical)

**Description**  
The `id` parameter of the visitor news desk is concatenated into a database query without safe parameter binding. An attacker can alter the query to read arbitrary tables.

**Affected component**  
`GET http://10.10.10.10/visiter-newsdesk.php?id=`

**Proof of concept (reproducible)**  

1. Identify the parameter: open `visiter-newsdesk.php?id=1` in the browser.
2. Run an automated database extraction against `id` (lab-authorized target only).
3. Observe full dump of table `TechNation.Users` including administrator email and password hash/plaintext field.

**Sample command output (abbreviated)**  

```
Database: TechNation
Table: Users
| 2 | eliasv@cyberstepsvuln.com | ... | 1 | LB&MG$sm2zkLz57k | Vais | Elias |
```

*Note: After a VM reset, passwords may differ; always verify against your current dump.*

**[Screenshot]** Browser or tool output showing successful extraction of the `Users` table.

**Impact**  
Complete compromise of application accounts; direct path to administrative functions.

**Risk evaluation**  

- **Likelihood:** High (trivial to automate once found)  
- **Impact:** Critical (full data confidentiality breach)  
- **Overall:** **Critical**

**Remediation**  
Use **parameterized queries (prepared statements)** for every query involving `id`. Validate `id` as a strict integer server-side before use. Apply the same pattern to all similar endpoints (`Reviews.php`, `Deals.php`, etc.).

---

### F-02 — Remote code execution via unrestricted upload + include (Critical)

**Description**  
The support form accepts file uploads into a predictable directory. The administrative “load file” feature uses dynamic inclusion of paths supplied by the user, which executes PHP when a uploaded script is referenced.

**Affected components**  

- `POST http://10.10.10.10/support.php` — file field `image`  
- `GET http://10.10.10.10/Admin.php` — `module=upload`, `loadfile=`

**Proof of concept**  

1. Authenticate as admin (credentials obtained via F-01 or legitimate test account).
2. Create a small PHP webshell, rename to `cmd.jpg`.
3. Upload via `support.php`.
4. Call `Admin.php` with `loadfile=<upload_dir>/cmd.jpg&cmd=whoami`.
5. Observe `www-data` in the output block.

**[Screenshot]** Upload success message and admin panel output showing command result.

**Impact**  
Full operating-system command execution as the web server account; foundation for lateral movement and data exfiltration.

**Risk evaluation**  

- **Likelihood:** High after admin access  
- **Impact:** Critical  
- **Overall:** **Critical**

**Remediation**  

- Never `include` user-controlled paths. Use **allow-lists** and serve uploads **outside the web root** or without execution.  
- Enforce **content inspection** and **extension + MIME** checks; store files under random names.  
- Disable PHP execution in upload directories.

---

### F-03 — Broken access control / weak dashboard tokens (High)

**Description**  
The dashboard trusts client-supplied `uid` and a Base64-encoded `auth_token` that encodes role and user identity without integrity protection.

**Affected component**  
`GET http://10.10.10.10/dashboard/` — cookies `uid`, `auth_token`

**Proof of concept**  

1. Set cookies: `uid=23` and `auth_token=YWRtaW46RWxpYXM6MjM=` (Base64 of `admin:Elias:23`).
2. Request `/dashboard/`.
3. Observe privileged content including flag marker in the page.

**[Screenshot]** Developer tools showing set cookies and resulting dashboard content.

**Impact**  
Any user who can edit cookies can impersonate another account, including high-privilege profiles.

**Risk evaluation**  

- **Likelihood:** High  
- **Impact:** High (account takeover)  
- **Overall:** **High**

**Remediation**  
Issue **server-side session IDs** only; validate every request against the session store. If tokens are needed, use **signed** (HMAC) or **encrypted** tokens with server secret rotation.

---

### F-04 — Server-side request forgery (High)

**Description**  
The “fetch image” function retrieves arbitrary URLs supplied by the user and returns content to the browser, including loopback addresses.

**Affected component**  
`GET http://10.10.10.10/Admin.php` — `module=fetch`, `img_url`

**Proof of concept**  

1. Authenticate as admin.
2. Request internal URL, e.g. `img_url=http://127.0.0.1/internal-status.php`.
3. Observe JSON-style internal status and sensitive markers in the response body.

**[Screenshot]** Admin fetch form and response snippet.

**Impact**  
Scan or abuse internal HTTP services, steal internal-only tokens, map internal topology.

**Risk evaluation**  

- **Likelihood:** Medium (requires admin session)  
- **Impact:** High  
- **Overall:** **High**

**Remediation**  
Use an **allow-list** of hosts; block private IP ranges; prefer server-side downloads via a dedicated service with policy. Do not pass raw user URLs to `file_get_contents` without validation.

---

### F-05 — XML external entity injection (High)

**Description**  
XML import enables external entities, allowing the server to resolve file paths and embed file contents into parsed output.

**Affected component**  
`POST http://10.10.10.10/Admin.php` — `module=import`, body `xml_data`

**Proof of concept**  

1. Authenticate as admin.
2. POST XML with `<!ENTITY xxe SYSTEM "file:///etc/hostname">` and reference `&xxe;` in an element.
3. Observe hostname value in “Parsed Data”.

**[Screenshot]** Import form and parsed output.

**Impact**  
Read arbitrary files readable by the web process; potential for further abuse depending on parser settings.

**Risk evaluation**  

- **Likelihood:** Medium  
- **Impact:** High  
- **Overall:** **High**

**Remediation**  
Disable external entities (`libxml_disable_entity_loader(true)` where appropriate), use safe parsers, validate XML schemas, reject DTDs in untrusted input.

---

### F-06 — Local file inclusion / unsafe theme loading (High)

**Description**  
Administrative file load and theme loader accept attacker-influenced paths or wrappers, leaking system files or source.

**Affected components**  

- `Admin.php` — `loadfile`  
- `ThemeLoader.php` — `theme` (e.g. `php://filter/...`)

**Proof of concept**  

1. As admin, `loadfile=/etc/passwd` — observe passwd contents in output.
2. `ThemeLoader.php?theme=php://filter/convert.base64-encode/resource=/etc/hostname` — decode Base64 blob to recover hostname.

**[Screenshot]** Theme preview showing encoded blob.

**Impact**  
Source code and configuration disclosure; supports chain exploitation.

**Risk evaluation**  

- **Likelihood:** High (with admin)  
- **Impact:** High  
- **Overall:** **High**

**Remediation**  
Remove user input from `include`/`require`. Use fixed template paths only. Disable dangerous URL wrappers in PHP configuration where feasible.

---

### F-07 — Information disclosure (Medium)

**Description**  
`robots.txt` advertises paths to a large password prototype file and experimental endpoints, easing attacker reconnaissance.

**Affected assets**  
`/robots.txt`, `/decoda9013smith21985.txt`, `/ThemeLoader.php`

**Proof of concept**  
`curl -s http://10.10.10.10/robots.txt` — observe listed paths.

**[Screenshot]** Browser view of robots.txt.

**Impact**  
Accelerates password guessing and discovery of non-linked functionality.

**Risk evaluation**  

- **Likelihood:** High  
- **Impact:** Medium  
- **Overall:** **Medium**

**Remediation**  
Remove sensitive paths from robots; do not store password corpora in the web root; restrict experimental features.

---

### F-08 — Cross-site scripting pattern (Medium)

**Description**  
Admin UI builds HTML via string concatenation into `innerHTML` using profile field values, enabling script injection if values contain markup.

**Affected component**  
`Admin.php` — client-side `Able('home')` and related logic.

**Proof of concept**  

1. Store payload in profile fields (if persisted) or simulate in dev tools.
2. Trigger profile view; observe script execution context.

**[Screenshot]** Console / rendered alert (safe lab payload).

**Impact**  
Session abuse in admin browser, defacement, phishing within trusted UI.

**Risk evaluation**  

- **Likelihood:** Medium  
- **Impact:** Medium  
- **Overall:** **Medium**

**Remediation**  
Use `textContent` or framework escaping; enforce output encoding server-side; Content-Security-Policy.

---

### F-09 — Host privilege escalation — SUID interpreter (High)

**Description**  
The server ships with an interpreter marked set-user-ID root, allowing escalation from web shell to root.

**Affected component**  
OS binary `/usr/bin/python3.8` (SUID)

**Proof of concept**  
From confirmed web command execution, run the interpreter with `setuid(0)` and invoke `id` — observe effective user root.

**[Screenshot]** Command output showing `uid=0(root)`.

**Impact**  
Full host compromise, persistence, access to all local data.

**Risk evaluation**  

- **Likelihood:** High after F-02  
- **Impact:** Critical at OS layer  
- **Overall:** **High** (chained; standalone misconfiguration)

**Remediation**  
Remove SUID from interpreters; use dedicated privilege boundaries (sudo with policies, capabilities). Re-image lab VMs with hardened baselines for production analogues.

---

### F-10 — Hard-coded database credentials (High)

**Description**  
Application source contains plaintext database user and password for a privileged MySQL account.

**Affected component**  
`Admin.php` (retrieved via code disclosure chain)

**Proof of concept**  
Obtain source via F-06 / filter wrappers; locate `mysqli_connect` parameters.

**Impact**  
Direct database access from compromised app host; credential reuse risk.

**Risk evaluation**  

- **Likelihood:** Medium (after code leak)  
- **Impact:** High  
- **Overall:** **High**

**Remediation**  
Use environment variables or secret managers; least-privilege DB users; rotate credentials after any disclosure.



## 6. Overall risk commentary


| Theme               | Comment                                                                    |
| ------------------- | -------------------------------------------------------------------------- |
| **Confidentiality** | Broken: database and files readable through multiple paths.                |
| **Integrity**       | Broken: attacker can modify data via DB and run arbitrary code.            |
| **Availability**    | At risk: DoS via heavy queries or destructive commands once RCE is gained. |
| **Accountability**  | Weak: forgeable dashboard identity undermines audit trails.                |


**Conclusion for stakeholders:** The system demonstrates **multiple critical chains** from a single injection flaw to full server control. Remediation must be **defence in depth**: fix injection and inclusion first, then access control, SSRF/XXE, and host hardening.



## 7. Appendix A — Collected lab flags (evidence index)


| Flag                                       | Retrieval summary                                     |
| ------------------------------------------ | ----------------------------------------------------- |
| `FLAG{y0u_f0und_th3_s3cr3t_p4g3}`          | `GET /topsecret.html`                                 |
| `FLAG{s0urc3_c0d3_r3v34ls_4ll}`            | same                                                  |
| `FLAG{css_s3l3ct_r3v3als_s3cr3ts}`         | same                                                  |
| `FLAG{4dm1n_byp4ss_sqli_w0rks}`            | same                                                  |
| `FLAG{r34d_th3_f00t3r_c0mm3nt_t00}`        | same                                                  |
| `FLAG{d1r_bru3f0rc3_0nly_raft_l4rg3_w1ns}` | `GET /classifiedadmin/`                               |
| `FLAG{c00k13_bru73_f0rc3_m4st3r}`          | Forged dashboard cookies                              |
| `FLAG{SSRF_INTERNAL_PIVOT_SUCCESS}`        | Admin fetch to `http://127.0.0.1/internal-status.php` |


*Full command transcripts: files `evidence_*.txt` in `cybersteps_vm_reset_evidence/` and HTML export `CyberSteps_Reset_Report.html`.*

## 8. Appendix B — Tool output references

Raw outputs are **not** duplicated here as findings; they are preserved as evidence:

- `scan_tcp.xml`, `nmap_services.xml` — port scan  
- `evidence_sqlmap_users_dump.txt` — database dump proof  
- `evidence_lfi_upload_rce.txt` — LFI / RCE / privesc  
- `evidence_flags_*.txt` — per-flag capture  
- `evidence_xxe_import.txt` — XXE file-read proof  
- `merged_scan.xml` / `CyberSteps_Reset_Report.html` — structured evidence bundle  
- `**Security_Assessment_Report.pdf*`* — this document, rendered for submission (`python3 build_report_pdf.py`)

## 9. Appendix C — References

- OWASP Web Security Testing Guide: [https://owasp.org/www-project-web-security-testing-guide/](https://owasp.org/www-project-web-security-testing-guide/)  
- OWASP Top 10 (access control, injection, SSRF, etc.)  
- Lab brief: CyberStepsVuln scope and deliverable requirements (module materials)

---

*End of report.*