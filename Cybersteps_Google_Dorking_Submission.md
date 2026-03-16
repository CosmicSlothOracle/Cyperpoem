# Cybersteps Google Dorking & Passive OSINT Submission

## Scope and ethics
- Target adapted from Uber to `cybersteps.de` per task request.
- Method: **passive only** (Google dorks / search operators, public web pages, public third-party profiles).
- No exploitation, no login bypass, no intrusive scanning in this document.

---

## 1) Official documents (PDF/official docs)

### Dorks used
- `site:cybersteps.de filetype:pdf`
- `site:cybersteps.de inurl:wp-content/uploads filetype:pdf`
- `site:cybersteps.de filetype:docx OR filetype:xlsx OR filetype:ppt OR filetype:pdf`
- Fallback legal-document dork: `site:cybersteps.de (impressum OR imprint OR datenschutz OR privacy OR terms)`

### Findings
- No indexed PDF/Office documents were found via dorks at time of research.
- One official public document selected: **Impressum**
  - URL: `https://cybersteps.de/de/impressum/`
  - Contains legal identity, managers, registry, address, VAT, contact.

### What this dork targets strategically
- `filetype:` dorks target downloadable artifacts often containing richer metadata than HTML pages.
- Legal-doc dorks (`impressum/imprint`) target high-value corporate identity information.

---

## 2) Engineering insights (security + engineering context)

### Dorks used
- `site:cybersteps.de engineering security`
- `site:cybersteps.de/blog security`

### One title found
- **USB Rubber Ducky: The Dangerous Keystroke Injection Tool Every Defender Should Know**
  - URL: `https://cybersteps.de/blog/usb-rubber-ducky/`

### What insight this provides
- Shows practical emphasis on endpoint and physical-security attack paths (HID trust abuse, keystroke injection, defensive controls).
- Indicates curriculum/content style is hands-on and operational, not only theory.

---

## 3) Public tech talks / presentations

### Dorks used
- `site:slideshare.net cybersteps.de OR "Cybersteps" presentation`
- `"Aviram Rispler" presentation OR webinar`
- `site:cybersteps.de "Meet the Team"`

### Findings
- No clearly attributable SlideShare deck specifically tied to Cybersteps was found.
- Public “talk-style” content on official site:
  - **Meet the Team: A Talk with Aviram Rispler, Cybersteps CEO**
    `https://cybersteps.de/blog/meet-the-team-a-talk-with-aviram-rispler-cybersteps-ceo/`
  - **Cyber Interview: Stefan Pezulat, Cybersteps GM**
    `https://cybersteps.de/blog/interview-stefan-general-manager/`

### Why these are useful
- Reveal leadership background, market strategy, training model, and hiring narrative.
- Even when slide decks are absent, interview-style public content still gives strategic organizational context.

---

## 4) API chatter on developer communities

### Dorks used
- `site:stackoverflow.com "cybersteps"`
- `site:github.com "cybersteps" "api" "cybersteps.de"`
- `"app.cybersteps.de" "api"`

### Findings
- No strong direct Stack Overflow/GitHub API discussions tied to `cybersteps.de` were found.
- Related platforms discovered:
  - `https://app.cybersteps.de/`
  - `https://learn.cybersteps.de/`

### What technical details API chatter *could* reveal (if present)
- Endpoint naming conventions, auth models, SDK patterns, rate limits, error behavior, token handling, and integration pitfalls.
- In this case, absence of indexed chatter is itself a signal (lower public developer leakage).

---

## 5) Hypothetical leak significance

If a dork exposed a document like `internal_strategy_notes_DO_NOT_DISTRIBUTE.docx` on `cybersteps.de`, it would be significant because it could reveal:
- internal plans, hiring strategy, partnerships, financial assumptions;
- competitive intelligence and reputational risk;
- possible personal/business data handling issues;
- potential legal/compliance implications (confidentiality, data protection).

Even without exploitability, this is a high-impact information exposure event.

---

## Extra OSINT questions (Cybersteps-focused)

## How many people work at Cybersteps?
- Public LinkedIn company page snapshot (fetched) states: **“11 employees”**.
- Source: `https://www.linkedin.com/company/cybersteps/`
- Confidence: **Medium** (platform-reported, time-dependent).

## Who are the people?
Publicly named on official pages:
- **Aviram Rispler** — Co-founder/CEO
  (`/about-us/`, `/de/ueber-uns/`, interview pages)
- **Roman Dvorkin** — Co-founder / Head of Academics
  (`/about-us/`, `/de/ueber-uns/`, Impressum as Geschäftsführer)
- **Stefan Pezulat** — General Manager
  (`/blog/interview-stefan-general-manager/`, `/for-employers/`, `/for-case-workers/`)
- **Adam** — Pentester/cybersecurity writer (blog author profile context)
  (`/blog/usb-rubber-ducky/`)

Note: This is a list of **publicly visible** names, not a full HR roster.

## Where is the company based?
- **Cybersteps GmbH**
- **Schloßstraße 50, 12165 Berlin, Germany**
- Handelsregister: **HRB 269982 B** (Amtsgericht Berlin-Charlottenburg)
- Source: `https://cybersteps.de/de/impressum/`

## Government relations: what is public?
From official site content:
- AZAV-certified training provider (certified by CERTQUA).
- Program promoted as fundable via **Agentur für Arbeit** / **Jobcenter** (Bildungsgutschein context).
- Dedicated page for case workers and repeated references to public funding pathways.
- Source pages:
  - `https://cybersteps.de/de/impressum/`
  - `https://cybersteps.de/bildungsgutschein/`
  - `https://cybersteps.de/for-case-workers/`
  - `https://cybersteps.de/blog/agentur-fur-arbeit-it-weiterbildungen/`

Interpretation:
- This indicates **institutional funding/program interface**, not evidence of ownership/control by government.

## Security concerns or praise (passive findings only)

### Concerns
- Multiple public-facing subdomains (`app`, `learn`, `ai-challenge`) increase external footprint and phishing/brand impersonation surface.
- Publicly visible leadership/staff identities may be leveraged in social engineering.
- No direct API chatter found; this is neutral-positive, but hidden exposure cannot be excluded without authenticated/internal testing.

### Positive signals
- Strong legal transparency (Impressum, contact, registry, VAT).
- Clear compliance positioning (AZAV references, quality/audit messaging).
- No obvious indexed PDF/Office-document leakage found via basic dorks at assessment time.

---

## Final note
- This report is a **point-in-time passive OSINT snapshot**. Search indexing changes over time, so reruns can produce different results.
