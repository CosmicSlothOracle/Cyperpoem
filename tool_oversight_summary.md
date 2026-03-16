# Quick Tool Oversight

**Picked tools:** `subfinder`, `findomain`, `assetfinder`, `shuffledns`, custom async enum + `aiodns`, `dnsx`, `httpx`, `naabu`, `nuclei` (+ CT: `crt.sh`, APIs: ThreatCrowd/HackerTarget/BufferOver).

**Why these:** Passive sources + brute-force + fast validation reduce blind spots and false positives.

**Value for public observation of the repo/domain surface:**
Finds what is publicly reachable, confirms what is real, fingerprints exposed services, and prioritizes likely weak points (dev/staging/legacy hosts) for safer follow-up testing.
