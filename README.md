# Project R&E: Surface Tension - Attack Surface Analysis

**Built on the collective work of the security community**

This project leverages the industry's most sophisticated open-source reconnaissance tools, developed by leading security researchers and organizations worldwide.

## Philosophy

> "Standing on the shoulders of giants"

Instead of reinventing the wheel with custom scripts, we harness the power of battle-tested tools that have been refined by thousands of security professionals:

- **OWASP Amass** - The most comprehensive attack surface mapping tool
- **ProjectDiscovery Suite** - Enterprise-grade reconnaissance tools
- **Tom Nomnom's tools** - Elegant, efficient utilities
- **Nmap** - The gold standard for network scanning

## Project Structure

```
Project R&E Surface Tension/
├── domains.txt                 # 100 root domains for enumeration
├── requirements.txt              # Python dependencies (for helpers)
├── README.md                   # This file
│
├── install_tools.ps1           # Automatic tool installation (Windows)
├── install_tools.sh            # Automatic tool installation (Linux/Mac)
│
├── master_recon.ps1            # Complete workflow (Windows PowerShell)
├── master_recon.sh             # Complete workflow (Linux/Mac Bash)
│
├── workflow.py                 # Legacy: Custom Python workflow
├── subdomain_enum.py           # Legacy: Custom enumeration
├── alt_enum.py                 # Legacy: Alternative sources
├── verify_subdomains.py        # Legacy: DNS verification
├── cybersteps_recon.py         # Legacy: Target reconnaissance
├── generate_pdf.py             # Report generator
│
└── output/                     # Generated data (created at runtime)
    ├── subdomains.txt          # Final verified subdomains
    ├── cybersteps/             # Target analysis data
    │   ├── analysis_report.txt # Human-readable report
    │   ├── portscan.xml        # Nmap port scan results
    │   ├── services.xml        # Service detection results
    │   └── ...
    └── ...
```

## Recommended Approach: Professional Tools

### Quick Start (Windows)

```powershell
# 1. Install professional reconnaissance tools
.\install_tools.ps1

# 2. Run complete workflow
.\master_recon.ps1

# 3. Generate PDF reports
python generate_pdf.py --all
```

### Quick Start (Linux/Mac)

```bash
# 1. Install tools
chmod +x install_tools.sh master_recon.sh
./install_tools.sh

# 2. Run complete workflow
./master_recon.sh

# 3. Generate reports
python3 generate_pdf.py --all
```

## Tools Used

### Subdomain Enumeration

| Tool | Author/Source | Purpose | Strengths |
|------|---------------|---------|-----------|
| **amass** | OWASP | Attack surface mapping | 100+ data sources, comprehensive |
| **subfinder** | ProjectDiscovery | Passive subdomain discovery | Fast, reliable, recursive |
| **findomain** | Findomain | Cross-platform enumeration | Extremely fast, lightweight |
| **assetfinder** | Tom Hudson | Related domain discovery | Simple, effective |
| **crt.sh** | Certificate Transparency | CT log queries | Historical data |

### DNS Verification

| Tool | Purpose | Why It's Best |
|------|---------|---------------|
| **dnsx** | DNS resolution | High-performance, wildcard filtering |
| **massdns** | Bulk DNS resolution | Speed: 100k+ queries/second |
| **shuffledns** | MassDNS wrapper | Wildcard detection, resolvers management |

### Port Scanning & Service Detection

| Tool | Purpose | Why It's Best |
|------|---------|---------------|
| **nmap** | Network scanning | Industry standard, comprehensive |
| **naabu** | Fast port scanning | SYN/CONNECT support, CDN bypass |
| **httpx** | HTTP probing | Technology detection, fast verification |

### Optional: Vulnerability Detection

| Tool | Purpose |
|------|---------|
| **nuclei** | Template-based vulnerability scanning |
| **naabu+nmap** | Complete port + service detection |

## Detailed Workflow

### Part 1: Subdomain Enumeration

#### Phase 1: Passive Enumeration
```bash
# OWASP Amass - Most comprehensive
amass enum -passive -df domains.txt -o amass_passive.txt

# Subfinder - Fast and reliable
subfinder -dL domains.txt -all -recursive -silent

# Findomain - Lightning fast
findomain -f domains.txt -q
```

#### Phase 2: Certificate Transparency
```bash
# Query crt.sh for each domain
for domain in $(cat domains.txt); do
    curl -s "https://crt.sh/?q=%.$domain&output=json" | jq -r '.[].name_value'
done
```

#### Phase 3: Verification (Google 8.8.8.8)
```bash
# Combine all sources
cat *.txt | sort -uf > all_subdomains.txt

# Verify with dnsx against 8.8.8.8
dnsx -l all_subdomains.txt -a -cname -mx -txt \
     -r <(echo -e "8.8.8.8\n8.8.4.4") \
     -o verified.txt

# Final output
cat verified.txt | awk '{print $1}' | sort -u > subdomains.txt
```

**Why this approach?**
- **amass**: Discovers from 100+ passive sources (Shodan, Crt.sh, PassiveTotal, etc.)
- **subfinder**: Fast brute force with recursive enumeration
- **findomain**: Additional coverage with different algorithms
- **dnsx**: Reliable verification against Google's resolver
- **deduplication**: Ensures no duplicates in final output

### Part 2: Cybersteps Target Analysis

#### Phase 1: Target Identification
```bash
# Find subdomain containing "scan"
for word in scan scanner scanning scanme scanthis; do
    host -t A "${word}.cybersteps.de" 8.8.8.8 && echo "Found: ${word}.cybersteps.de"
done

# Alternative with subfinder
subfinder -d cybersteps.de | grep -i scan
```

#### Phase 2: Stealth Port Scanning
```bash
# SYN scan with stealth timing
nmap -sS -Pn -n -T2 \
     --max-retries 2 \
     --max-rtt-timeout 3s \
     --initial-rtt-timeout 1s \
     --open \
     -oX portscan.xml \
     <target_ip>
```

**Why this configuration?**
- `-sS`: SYN scan (stealth, doesn't complete handshake)
- `-T2`: Slow timing (avoids IDS detection)
- `-Pn`: Skip host discovery (assume up)
- `--max-retries 2`: Minimal retries (stealth)
- `--max-rtt-timeout 3s`: Don't wait too long

#### Phase 3: Service Version Detection
```bash
# Deep service detection
nmap -sV -Pn -n -T3 --version-intensity 5 \
     -p <open_ports> \
     -oX services.xml \
     <target_ip>
```

#### Phase 4: HTTP Analysis (if web services found)
```bash
# HTTP probing with technology detection
echo "target.domain.com" | httpx -tech-detect -silent
```

### Alternative: Fast Complete Scan

```bash
# Naabu for fast port discovery
cat target.txt | naabu -p - -silent

# Combine with nmap for service detection
```

## Deliverables

### Part 1
- **subdomains.txt**: One verified subdomain per line (A, CNAME, MX, or TXT records verified against 8.8.8.8)
- **PDF Write-up**:
  - Tools used (amass, subfinder, findomain, dnsx)
  - Verification methodology (Google DNS, record types)
  - Interesting discovery

### Part 2
- **PDF Report** with:
  - Target identification method
  - All open TCP/UDP ports
  - Service enumeration (name, version, banner, purpose)
  - Security issues and recommendations

## Methodology Comparison

### Approach A: Professional Tools (Recommended)
| Aspect | Quality |
|--------|---------|
| Coverage | ⭐⭐⭐⭐⭐ (100+ sources via amass) |
| Speed | ⭐⭐⭐⭐⭐ (optimized binaries) |
| Accuracy | ⭐⭐⭐⭐⭐ (battle-tested, community-verified) |
| Stealth | ⭐⭐⭐⭐⭐ (optimized scan timing) |
| Maintenance | ⭐⭐⭐⭐⭐ (actively maintained by experts) |

### Approach B: Custom Scripts (Educational)
| Aspect | Quality |
|--------|---------|
| Coverage | ⭐⭐⭐ (limited sources) |
| Speed | ⭐⭐ (Python overhead) |
| Accuracy | ⭐⭐⭐ (limited testing) |
| Stealth | ⭐⭐ (basic implementation) |
| Maintenance | ⭐ (manual updates required) |

## Installation Details

### Automatic Installation (Windows)

```powershell
# Run the installer
.\install_tools.ps1

# This will download:
# - subfinder.exe (ProjectDiscovery)
# - dnsx.exe (ProjectDiscovery)
# - naabu.exe (ProjectDiscovery)
# - httpx.exe (ProjectDiscovery)
# - findomain.exe (Findomain)
# - assetfinder.exe (Tom Nomnom)
# - shuffledns.exe (ProjectDiscovery)
```

### Manual Installation (Any Platform)

```bash
# Go-based tools (most common)
go install -v github.com/owasp-amass/amass/v4/...@master
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest

# Binary downloads (releases)
# https://github.com/Findomain/Findomain/releases
```

### Nmap Installation

```bash
# Ubuntu/Debian
sudo apt-get install nmap

# macOS
brew install nmap

# Windows
# Download from https://nmap.org/download.html
# Or: choco install nmap
```

## Troubleshooting

### Tools not found after installation

```powershell
# Windows: Refresh PATH or restart terminal
$env:PATH = "$env:USERPROFILE\recon-tools\bin;$env:PATH"

# Or run the wrapper
& "$env:USERPROFILE\recon-tools\recon-env.ps1"
```

### DNS Resolution Issues

```bash
# Test DNS connectivity
dig @8.8.8.8 google.com

# Alternative resolvers
echo -e "1.1.1.1\n9.9.9.9" > resolvers.txt
dnsx -l domains.txt -a -r resolvers.txt
```

### Rate Limiting

```bash
# Slow down requests
subfinder -dL domains.txt -rate-limit 10

# Use multiple resolvers
dnsx -l domains.txt -a -r resolvers.txt -retry 3
```

## Tool Authors & Attribution

| Tool | Author/Organization | GitHub |
|------|---------------------|--------|
| amass | OWASP, Jeff Foley | @OWASP, @caffix |
| subfinder | ProjectDiscovery | @projectdiscovery |
| dnsx | ProjectDiscovery | @projectdiscovery |
| naabu | ProjectDiscovery | @projectdiscovery |
| httpx | ProjectDiscovery | @projectdiscovery |
| nuclei | ProjectDiscovery | @projectdiscovery |
| findomain | Eduard Tolosa | @Findomain |
| assetfinder | Tom Hudson | @tomnomnom |
| nmap | Gordon Lyon | @nmap |

## License & Legal Notice

These tools are open-source and free to use for authorized security assessments. Always ensure you have:
1. **Written authorization** before scanning any target
2. **Clear scope definition** (what is in/out of bounds)
3. **Responsible disclosure** process for any findings

**This project is for educational and authorized testing purposes only.**

## Additional Resources

- [OWASP Amass Documentation](https://github.com/owasp-amass/amass/blob/master/doc/user_guide.md)
- [ProjectDiscovery Docs](https://docs.projectdiscovery.io/)
- [Nmap Reference Guide](https://nmap.org/book/)
- [Bug Bounty Hunter Methodology](https://github.com/jhaddix/tbhm)

## Summary

**Why use professional tools?**

1. **Coverage**: amass alone queries 100+ data sources
2. **Speed**: Written in Go, optimized for performance
3. **Accuracy**: Battle-tested by thousands of security professionals
4. **Stealth**: Optimized scan timing to avoid detection
5. **Updates**: Actively maintained with latest techniques

**Result**: Better findings, faster execution, professional quality.

---

*"The best tools are built by the community, for the community."*
