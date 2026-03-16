# The B52 Recon Metric 2.0 — Complete Specification
## "From Beverage Theory to Orbital Mechanics"

**Version:** 2.0 (Evolution)
**Codename:** SLOT MACHINE APOCRYPHON
**Philosophy:** *A finding is not a number. It is a convergence of forces. When the tumblers align, you know.*

---

## Executive Summary

The GoldenB52Ratio evolves from a 2-axis beverage metaphor into a multi-factor reconnaissance calculus. The new metric preserves the memorable weirdness (stars, orbs, flying cash) while introducing mathematical rigor through layered composites.

**The Slot Machine Principle:** Each factor is a tumbler. When they lock into position, the final CALL reveals itself with the satisfying mechanical certainty of a jackpot.

---

## Part I: The Five Primary Factors

### 1. NOISE — The Visibility Index ★
*How bright does this light shine in the darkness?*

**Scale:** 1–5 wanted-style stars
**Symbol Family:** Siren-stars (✦ ✧ ⭐ ★ ✶) — generic, not trademarked
**Inverse Logic:** Higher stars = MORE detectable = WORSE for stealth

| Level | Stars | Name | Operational Reality | Evidence Marker |
|-------|-------|------|---------------------|-----------------|
| 1 | ☆ | Ghost | No packets sent. Pure OSINT, third-party data, cached records. | Shodan history, passive DNS |
| 2 | ☆☆ | Whisper | Normal user traffic. Manual browsing, standard headers, human timing. | Browser-similar request patterns |
| 3 | ☆☆☆ | Murmur | Automated but polite. Slow scans, rate-limited, widely distributed. | 1 req/sec, randomized delays |
| 4 | ☆☆☆☆ | Siren | Aggressive automation. Fast scans, repeated probes, signature-heavy. | >1000 req/min, identical fingerprints |
| 5 | ☆☆☆☆☆ | Beacon | Direct exploitation. Payloads, crashes, file system modifications. | Shell commands, auth attempts, errors |

**Key Insight:** Noise is about DETECTABILITY, not effort. A single SQLi payload can be quieter than a slow port scan if it blends into normal traffic.

---

### 2. INTELLIGENCE — The Orb of Potential 🔮
*What could we learn if we reached into the dark?*

**Scale:** 1–5 crystal/orb states
**Symbol Family:** Crystal ball progression (⚪ 🔮 🔮✨ 🔮✨✨ 🔮✨✨✨)
**Metaphor:** The Palantir — seeing stones of varying clarity. Higher = clearer vision, more control.

| Level | Orb | Name | Intelligence Depth | Attack Path |
|-------|-----|------|-------------------|-------------|
| 1 | ⚪ | Veiled | Nothing actionable. Banner noise, filtered ports, false positives. | None — dead end |
| 2 | 🔮 | Clouded | Mapping intel. Versions, paths, technology fingerprint. | Recon expansion only |
| 3 | 🔮✨ | Glimmering | Access to non-critical data. LFI, directory listings, logs. | Lateral recon, credential hunting |
| 4 | 🔮✨✨ | Radiant | User-level compromise. Shell access, session hijacking, data exfil. | Direct exploitation chain |
| 5 | 🔮✨✨✨ | Chosen | Total infrastructure control. Domain admin, persistence, golden tickets. | Full kill chain, APT potential |

**Visual Language:**
- Level 1: Dull stone, no glow
- Level 3: Faint inner light, swirling mist
- Level 5: Blinding core radiance, liquid light dripping

---

### 3. LIKELIHOOD — The Probability Spectrum %
*What do the archives say about surface, circumstance, and season?*

**Format:** Percentage BANDS, not fragile exact numbers
**Source Model:** Historical incident data for same service/version/exposure pattern
**Presentation:** Gradient arc with labeled zones

| Band | Label | Evidence Required | Confidence Anchors |
|------|-------|-------------------|-------------------|
| 5–15% | Lunar | Novel configuration, no historical precedent. | "First observed in the wild" |
| 15–35% | Dusk | Similar surfaces attacked, but different context. | CVE exists, no active exploitation observed |
| 35–55% | Twilight | Same service attacked this year, similar exposure. | Shodan shows 10k+ similar endpoints, some exploited |
| 55–75% | Dawn | Direct precedent — same version, same misconfiguration. | ExploitDB entries, botnet targeting this stack |
| 75–90% | Solar | Actively exploited in the wild RIGHT NOW. | CISA KEV listed, ransomware targeting, honeypot hits |

**Critical Note:** This is NOT prediction. It is frequency analysis. We are not claiming "this will happen" — we are stating "when similar targets were attacked, this was the observed frequency."

---

### 4. DAMAGE — The Cash Cascade 💸
*If the dam breaks, how much washes away?*

**Scale:** 1–10 flying money bundles
**Symbol Family:** Cash stacks with increasing chaos (💵 → 💸💸 → 💸💸💸💨💨)
**Max State:** 10 = "CEO is now eating garbage and fighting raccoons"

| Level | Bundles | Name | Business Impact | Regulatory Trigger |
|-------|---------|------|-----------------|-------------------|
| 1 | 💵 | Pebble | Negligible. Test system, no customer data. | None |
| 2–3 | 💵💵 | Ripple | Minor inconvenience. Staging environment disrupted. | Internal only |
| 4–5 | 💸💸 | Stream | Moderate operational impact. Some customer-facing degradation. | SLA breach possible |
| 6–7 | 💸💸💨 | Torrent | Major breach. PII exposed, service disruption >24h. | GDPR/CCPA notification required |
| 8–9 | 💸💸💨💨 | Flood | Critical infrastructure compromise. Mass data exfiltration. | Stock-moving event |
| 10 | 💨💨💨💸💸💸💨💨💨 | Abyss | Existential threat. Company-ending breach. CEO resigns. | Bankruptcy/consulting fees |

**Visual Chaos Principle:**
- Low levels: Neat stacks
- Mid levels: Some bills fluttering
- High levels: Full hurricane of cash, bills flying in all directions

---

### 5. CONFIDENCE — The Oracle's Certainty 🎲
*How much should we trust these tumblers?*

**Scale:** 0–100% with named bands
**Dual Nature:** Modifies both SIGNAL and THREAT calculations
**Honesty Metric:** Explicitly encodes uncertainty

| Band | % | Name | Self-Awareness | Display Treatment |
|------|---|------|----------------|-----------------|
| 0–20 | 🎲 | Hallucinating | "I am an AI. This might be pattern-matching noise." | Ghosted, low opacity, warning stripe |
| 20–40 | 🎲🎲 | Shaky | "Single source, unverified, plausible but unconfirmed." | Dashed borders, question marks |
| 40–60 | 🎲🎲🎲 | Plausible | "Multiple indicators align, but no direct confirmation." | Standard weight |
| 60–80 | 🎲🎲🎲🎲 | Locked-In | "Verified through active probing. Evidence is solid." | Bold, crisp display |
| 80–100 | 🎲🎲🎲🎲🎲 | The Chosen One | "Neo-in-the-Matrix certainty. Multiple independent confirmations." | Glow effect, slow-motion aura |

**Critical Function:** Confidence does not change raw evidence. It changes how much we trust the composite calculation. A high-Threat finding with 15% Confidence gets a different CALL than the same finding with 90% Confidence.

---

## Part II: The Three Composite Outputs

### SIGNAL — Noise × Intelligence
*Is this worth paying attention to?*

**Formula:** `SIGNAL = NOISE_LEVEL × INTELLIGENCE_LEVEL`
**Range:** 1–25
**Interpretation:**
- 1–5: Background radiation (LOW SIGNAL)
- 6–12: Interesting but not urgent (MEDIUM SIGNAL)
- 13–20: Actionable intelligence (HIGH SIGNAL)
- 21–25: Drop everything and look (MAXIMUM SIGNAL)

**Visual Gradient:** The Signal output uses a diagonal sweep from bottom-left (low noise, low intel) to top-right (high noise, high intel). But because we want LOW noise and HIGH intel, the sweet spot is actually the top-left quadrant of the 5×5 matrix.

**The Signal Paradox:** The best findings have LOW Noise and HIGH Intelligence — but that produces a middling Signal score (e.g., 2 × 5 = 10). Therefore, Signal is only ONE input to the final Call. The slot machine considers all tumblers.

---

### THREAT — Likelihood × Damage × Confidence
*How dangerous is this, really?*

**Formula:** `THREAT = (LIKELIHOOD_MIDPOINT × DAMAGE) × (CONFIDENCE / 100)`
**Example:** 45% likelihood (band 35–55%, midpoint 45), Damage 7, Confidence 70%
`THREAT = (45 × 7) × 0.70 = 220.5` (normalized to 0–100 scale: 22.05)

**The Confidence Dampener:** Confidence acts as a reality check. A 100% damage/100% likelihood finding with 10% confidence is treated as low-priority because we don't trust our own assessment.

**Visual:** Thermometer-style bar that fills based on normalized threat score. Color transitions: Blue → Yellow → Orange → Red → Purple (critical).

---

### CALL — The Slot Machine Lock-In
*What should a beginner actually DO?*

**The Jackpot Moment:** When all factors are assessed, the CALL tumbler locks into place with satisfying mechanical finality. This is the B52 Ratio's ultimate output.

| CALL | Color | Symbol | Action | Criteria |
|------|-------|--------|--------|----------|
| IGNORE | 🟢 | 🚫➜ /dev/null | Acknowledge and move on. Not worth cycles. | Signal < 6 OR Confidence < 20% |
| NOTE | 🔵 | 📌📝 | Log for pattern analysis. May become relevant. | Signal 6–10, Threat < 20 |
| VALIDATE | 🟡 | 🔍⚡ | Active confirmation needed. Safe probing authorized. | Signal > 10, Confidence 40–60% |
| TRIAGE | 🟠 | ⚠️🚦 | Priority queue. Develop exploitation hypothesis. | Threat 20–50, Confidence > 60% |
| ESCALATE | 🔴 | 🚨📡 | Immediate analyst attention. Potential critical. | Threat 50–75, Confidence > 70% |
| PANIC | 💀 | ☠️🔥 | All hands. Incident response mode. | Threat > 75, Confidence > 80% |

**The Visual Lock-In:** When CALL is calculated, the interface animates:
1. All five factor tumblers spin
2. Each locks with a mechanical "CLACK" sound (visual)
3. The CALL indicator pulses three times
4. Final state: The CALL word appears in bold, surrounded by the five factor icons

---

## Part III: Symbol Grammar & Visual System

### The Symbol Alphabet

```
NOISE:      ☆ ☆☆ ☆☆☆ ☆☆☆☆ ☆☆☆☆☆
INTEL:      ⚪ 🔮 🔮✨ 🔮✨✨ 🔮✨✨✨
LIKELIHOOD: ◐ ◑ ◒ ◓ ●
DAMAGE:     💵 💵💵 💸💸 💸💸💨 💨💨💨💸💸💸💨💨💨
CONFIDENCE: 🎲 🎲🎲 🎲🎲🎲 🎲🎲🎲🎲 🎲🎲🎲🎲🎲
```

### Compact Notation

Every finding can be expressed in the B52 Glyph:

**Format:** `[NOISE][INTEL] [LIKELIHOOD] [DAMAGE] [CONFIDENCE] → [CALL]`

**Example:** `☆☆☆ 🔮✨ ◑ 💸💸 🎲🎲🎲 → VALIDATE`

Translation:
- Noise 3 (Murmur — automated but polite)
- Intelligence 3 (Glimmering — non-critical data access possible)
- Likelihood 15–35% (Dusk)
- Damage 4–5 (Stream — moderate impact)
- Confidence 40–60% (Plausible)
- CALL: VALIDATE — needs active confirmation

---

## Part IV: Calibration Set — Five Real Ports

### Port 21/tcp FTP (ProFTPD 1.2.10)

```
NOISE:       ☆☆☆☆ (4 — Siren) — Banner grab is detectable
INTEL:       🔮✨✨ (4 — Radiant) — Anonymous login could yield shell
LIKELIHOOD:  ◓ (55–75% Dawn) — Legacy FTP actively targeted
DAMAGE:      💸💸💨 (7 — Torrent) — PII exposure, service compromise
CONFIDENCE:  🎲🎲🎲🎲 (75% — Locked-In) — Banner verified, version confirmed
SIGNAL:      4 × 4 = 16 (HIGH)
THREAT:      (65 × 7) × 0.75 = 341 → 34.1% of max
CALL:        TRIAGE
```

**Glyph:** `☆☆☆☆ 🔮✨✨ ◓ 💸💸💨 🎲🎲🎲🎲 → TRIAGE`

---

### Port 22/tcp SSH (OpenSSH 8.9p1)

```
NOISE:       ☆☆☆ (3 — Murmur) — Version banner standard
INTEL:       🔮✨✨ (4 — Radiant) — Shell if creds obtained
LIKELIHOOD:  ◐ (5–15% Lunar) — Recent version, no major CVEs
DAMAGE:      💸💸💨 (7 — Torrent) — Full system compromise
CONFIDENCE:  🎲🎲🎲🎲 (80% — Locked-In) — Banner verified
SIGNAL:      3 × 4 = 12 (MEDIUM-HIGH)
THREAT:      (10 × 7) × 0.80 = 56 → 5.6% of max
CALL:        NOTE
```

**Glyph:** `☆☆☆ 🔮✨✨ ◐ 💸💸💨 🎲🎲🎲🎲 → NOTE`

---

### Port 80/tcp HTTP (Apache 2.4.6)

```
NOISE:       ☆☆ (2 — Whisper) — Normal HTTP traffic
INTEL:       🔮✨ (3 — Glimmering) — Web exploitation path
LIKELIHOOD:  ◒ (35–55% Twilight) — Apache 2.4.6 has known issues
DAMAGE:      💸💸 (5 — Stream) — Web layer compromise, data breach
CONFIDENCE:  🎲🎲🎲🎲 (85% — Locked-In) — Server header confirmed
SIGNAL:      2 × 3 = 6 (MEDIUM — but exploitable path)
THREAT:      (45 × 5) × 0.85 = 191 → 19.1% of max
CALL:        VALIDATE
```

**Glyph:** `☆☆ 🔮✨ ◒ 💸💸 🎲🎲🎲🎲 → VALIDATE`

---

### Port 1080/tcp SOCKS-like

```
NOISE:       ☆☆☆ (3 — Murmur) — NSE probing detectable
INTEL:       🔮✨ (3 — Glimmering) — Proxy pivot potential
LIKELIHOOD:  ◑ (15–35% Dusk) — Proxy abuse context-dependent
DAMAGE:      💸💸 (4 — Stream) — Lateral movement enabler
CONFIDENCE:  🎲🎲🎲 (55% — Plausible) — Behavior observed, purpose unclear
SIGNAL:      3 × 3 = 9 (MEDIUM)
THREAT:      (25 × 4) × 0.55 = 55 → 5.5% of max
CALL:        NOTE
```

**Glyph:** `☆☆☆ 🔮✨ ◑ 💸💸 🎲🎲🎲 → NOTE`

---

### Port 3389/tcp RDP

```
NOISE:       ☆☆☆☆ (4 — Siren) — RDP negotiation signature
INTEL:       🔮✨✨ (4 — Radiant) — Desktop access, lateral base
LIKELIHOOD:  ◓ (55–75% Dawn) — Exposed RDP constantly attacked
DAMAGE:      💸💸💨 (8 — Flood) — Ransomware entry point
CONFIDENCE:  🎲🎲🎲🎲 (90% — The Chosen One) — Protocol confirmed
SIGNAL:      4 × 4 = 16 (HIGH)
THREAT:      (65 × 8) × 0.90 = 468 → 46.8% of max
CALL:        ESCALATE
```

**Glyph:** `☆☆☆☆ 🔮✨✨ ◓ 💸💸💨 🎲🎲🎲🎲🎲 → ESCALATE`

---

## Part V: Anti-Fake-Precision Manifesto

### What We Do NOT Claim

1. **Exact percentages:** Likelihood bands are 20% wide. We do not pretend to know if it's 42% vs 43%.
2. **Predictive certainty:** "55–75% likelihood" means "historically, 55–75% of similar surfaces were attacked." It does not mean "this specific target has a 65% chance of being breached tomorrow."
3. **Immutable scores:** All values are reassessable. New evidence shifts the tumblers.
4. **Universal applicability:** This metric is calibrated for reconnaissance-phase findings. It does not apply to post-exploitation or physical security.

### What We DO Claim

1. **Relative prioritization:** Given limited analyst time, this finding should be examined before that finding.
2. **Structured reasoning:** Every score has explicit evidence criteria. Disagreement is welcome and traceable.
3. **Uncertainty encoding:** The Confidence factor makes our doubt visible rather than hiding it.
4. **Action guidance:** The CALL output gives beginners a clear next step without requiring expert intuition.

---

## Part VI: Visual Dashboard Specification

### Layout: The Slot Machine Console

```
┌─────────────────────────────────────────────────────────────────┐
│  ★ B52 RECON METRIC v2.0 ★          [Target: scanme.cybersteps.de] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│    │  NOISE  │  │  INTEL  │  │  LIKELY │  │ DAMAGE  │  │  CONF   │  │
│    │  ☆☆☆☆  │  │  🔮✨✨  │  │   ◓    │  │ 💸💸💨  │  │ 🎲🎲🎲🎲 │  │
│    │  Siren  │  │ Radiant │  │  Dawn  │  │ Torrent │  │ Locked  │  │
│    └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
│         ▓▓            ▓▓           ▓▓          ▓▓           ▓▓     │
│         ▓▓            ▓▓           ▓▓          ▓▓           ▓▓     │
│    ════════════════════════════════════════════════════════     │
│                                                                 │
│    SIGNAL:  ████████████████░░░░░░  16/25 (HIGH)               │
│    THREAT:  ██████████████░░░░░░░░░░  34% (MODERATE)           │
│                                                                 │
│    ╔═══════════════════════════════════════════════════════╗   │
│    ║                                                         ║   │
│    ║   ★ CALL ★   →   T R I A G E   ←   ★ CALL ★            ║   │
│    ║                                                         ║   │
│    ║   [Priority queue. Develop exploitation hypothesis.]    ║   │
│    ║                                                         ║   │
│    ╚═══════════════════════════════════════════════════════╝   │
│                                                                 │
│    Compact Glyph: ☆☆☆☆ 🔮✨✨ ◓ 💸💸💨 🎲🎲🎲🎲 → TRIAGE       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### The Tumbler Animation

When a finding is assessed:

1. **Spin Phase (500ms):** All five factor displays show cycling symbols
2. **Lock Phase (100ms each, staggered):** Each tumbler locks left-to-right with visual "CLACK"
3. **Calculation Phase (300ms):** Signal and Threat bars animate to final position
4. **Reveal Phase (400ms):** CALL box pulses, final recommendation appears

### Color System

| Element | Color | Hex |
|---------|-------|-----|
| Cosmic background | Deep void | #0a0a0f |
| Glass cards | Frosted black | rgba(0,0,0,0.6) |
| Signal gradient | Cyan → Emerald | #58a6ff → #34d399 |
| Threat gradient | Amber → Crimson → Violet | #e3b341 → #ff4444 → #d2a8ff |
| CALL ignore | Forest | #7ee787 |
| CALL note | Ocean | #79c0ff |
| CALL validate | Sun | #e3b341 |
| CALL triage | Flame | #f0883e |
| CALL escalate | Blood | #ff4444 |
| CALL panic | Void | #d2a8ff (ultraviolet panic) |

---

## Part VII: Integration into Part 2 Report

### Per-Port Summary Format

Replace the current `[ Level: Flaming Absynth 🔥🍸 ]` with:

```
[ B52v2: ☆☆☆ 🔮✨ ◑ 💸💸 🎲🎲🎲 → NOTE ]
  ││││   │││  │   │││   │││
  ││││   │││  │   │││   └── Confidence: Plausible (55%)
  ││││   │││  │   └── Damage: Stream (4)
  ││││   │││  └── Likelihood: Dusk (15–35%)
  ││││   └── Intelligence: Glimmering (3)
  │││└── Detection: Murmur (3)
  ││└── Escalation: NOTE (log for patterns)
```

### Rationale Inclusion Rules

1. **Compact display:** Only the glyph and one-line CALL meaning in the port header
2. **Full rationale:** Available on hover/click in HTML version
3. **Evidence links:** Each factor score links to specific evidence file
4. **Confidence caveats:** Explicit note when Confidence < 60%

---

## Part VIII: The B52 Ratio — Mathematical Definition

### Formal Calculus

Given:
- N ∈ {1,2,3,4,5} (Noise)
- I ∈ {1,2,3,4,5} (Intelligence)
- L ∈ {0.10, 0.25, 0.45, 0.65, 0.825} (Likelihood midpoint of band)
- D ∈ {1,2,3,4,5,6,7,8,9,10} (Damage)
- C ∈ [0.0, 1.0] (Confidence as decimal)

**Signal:**
```
S = N × I
Signal_Band = floor(S / 5)  → 1–5 scale for display
```

**Threat:**
```
T_raw = (L × D) × C
T_normalized = min(T_raw / 8.25, 1.0)  → 0–100% scale
```
*(8.25 = max possible: 0.825 × 10 × 1.0)*

**B52 Ratio (final score):**
```
B52 = (S × 4) + T_normalized × 100
Range: 4–200 (practical: 4–150)
```

**CALL Determination:**
```python
def determine_call(S, T_normalized, C):
    if S < 6 or C < 0.20:
        return "IGNORE"
    elif S < 10 and T_normalized < 0.20:
        return "NOTE"
    elif C < 0.60:
        return "VALIDATE"
    elif T_normalized < 0.50:
        return "TRIAGE"
    elif T_normalized < 0.75:
        return "ESCALATE"
    else:
        return "PANIC"
```

---

## Appendix A: The Legend for Beginners

### One-Page Cheat Sheet

```
┌────────────────────────────────────────────────────────────────┐
│            THE B52 RECON METRIC — QUICK REFERENCE             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ★ NOISE (How visible are you?)                               │
│  ☆      Ghost     — No contact at all                         │
│  ☆☆     Whisper   — Look like a normal user                   │
│  ☆☆☆    Murmur    — Automated but polite                      │
│  ☆☆☆☆   Siren     — Aggressive, they might notice             │
│  ☆☆☆☆☆  Beacon    — Loud, active attacks                      │
│                                                                │
│  🔮 INTELLIGENCE (What could you learn?)                      │
│  ⚪     Veiled    — Nothing useful                            │
│  🔮     Clouded   — Just mapping info                         │
│  🔮✨    Glimmering — Some data access                        │
│  🔮✨✨   Radiant   — Shell/compromise possible                │
│  🔮✨✨✨  Chosen    — Total control                            │
│                                                                │
│  % LIKELIHOOD (History says...)                               │
│  ◐  5–15%  Lunar  — Rare, unusual setup                       │
│  ◑ 15–35%  Dusk   — Possible but not common                   │
│  ◒ 35–55%  Twilight — Happens sometimes                       │
│  ◓ 55–75%  Dawn   — Common attack target                      │
│  ● 75–90%  Solar  — Actively exploited now                    │
│                                                                │
│  💸 DAMAGE (If this breaks...)                                │
│  💵     Pebble    — Test system, no harm                      │
│  💵💵💵  Stream   — Some operational impact                     │
│  💸💸💨  Torrent  — Major breach, notify regulators             │
│  💨💨💨  Abyss    — Company-ending, CEO resigns               │
│                                                                │
│  🎲 CONFIDENCE (Trust the reading?)                           │
│  🎲         Hallucinating — Might be wrong                      │
│  🎲🎲🎲      Plausible     — Seems right                       │
│  🎲🎲🎲🎲    Locked-In     — Pretty sure                       │
│  🎲🎲🎲🎲🎲   Chosen One   — Neo-in-the-Matrix certain          │
│                                                                │
│  → CALL (What to do)                                          │
│  🟢 IGNORE    — Not worth your time                            │
│  🔵 NOTE      — Log it, check later                            │
│  🟡 VALIDATE  — Needs active testing                           │
│  🟠 TRIAGE    — Priority for exploitation                      │
│  🔴 ESCALATE  — Alert the team NOW                             │
│  💀 PANIC     — All hands, incident response                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Appendix B: Glossary of Absurd Terms

| Term | Meaning |
|------|---------|
| Slot Machine Lock-In | The moment all factors align and the CALL reveals itself |
| The Chosen One | 80–100% confidence — Neo dodging bullets level certainty |
| CEO Eating Garbage | Damage level 10 — total existential business threat |
| Tumbler | One of the five primary factors (visual metaphor) |
| Glyph | The compact symbolic notation for a finding |
| The Signal Paradox | Best findings have low noise + high intel = middling signal score |
| Cosmic Shell | The starfield background visual from original B52 |
| Mechanical Certainty | The satisfying finality of the CALL output |

---

**End of Specification**

*"The novice sees chaos. The master sees tumblers. When they align, act without hesitation."*
