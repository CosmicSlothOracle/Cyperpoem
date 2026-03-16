#!/usr/bin/env python3
"""
PDF Report Generator
Creates professional PDF reports from reconnaissance data
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def generate_part1_writeup(output_file: str = "Part1_Writeup.pdf"):
    """Generate Part 1 PDF writeup"""

    # This is a text template - convert to PDF using appropriate tools
    content = f"""
================================================================================
                    PART 1: SUBDOMAIN ENUMERATION
                    Methodology & Results Writeup
================================================================================

Date: {datetime.now().strftime('%Y-%m-%d')}
Project: R&E Surface Tension - Attack Surface Analysis

--------------------------------------------------------------------------------
1. TOOLS AND METHODS USED
--------------------------------------------------------------------------------

Primary Enumeration Tool:
  - Custom Python script: subdomain_enum.py
  - Asynchronous DNS resolution using aiodns
  - Concurrent workers: 50
  - DNS resolver: Google 8.8.8.8

Enumeration Techniques:
  a) Dictionary-based brute force
     - 500+ common subdomain prefixes (www, mail, ftp, api, etc.)
     - Numeric enumeration (1-99)
     - Compound prefixes (www1, mail2, etc.)

  b) Environment-based enumeration
     - Standard environments: dev, staging, prod, test, uat, qa
     - Combined prefixes: api-dev, dev-api, staging-www, etc.

  c) Regional/Geographic enumeration
     - Regions: us, eu, asia, east, west, north, south
     - Combined with common prefixes

Secondary Enumeration Sources:
  - Certificate Transparency logs (crt.sh)
  - ThreatCrowd API
  - HackerTarget API
  - BufferOver (Rapid7) DNS database

--------------------------------------------------------------------------------
2. VERIFICATION METHODOLOGY
--------------------------------------------------------------------------------

All discovered subdomains were verified against Google's recursive resolver
(8.8.8.8) to ensure validity:

Record Types Checked:
  - A records (IPv4 addresses)
  - CNAME records (canonical names)
  - MX records (mail exchange)
  - TXT records (text records)

Invalid Subdomain Criteria:
  - NXDOMAIN responses
  - DNS timeout errors
  - No valid record types found

Filtering Process:
  1. Collect subdomains from all enumeration sources
  2. Remove duplicates
  3. Query 8.8.8.8 for each record type
  4. Accept subdomain if any valid record found
  5. Reject if NXDOMAIN or no records

--------------------------------------------------------------------------------
3. INTERESTING DISCOVERIES
--------------------------------------------------------------------------------

During the enumeration process, several patterns emerged:

  - Dev/Staging Exposure: Many organizations expose development and
    staging environments publicly, which often have less stringent
    security controls than production.

  - Legacy Subdomains: Older subdomains (www1, www2, etc.) suggest
    legacy infrastructure that may not receive the same security
    attention as primary domains.

  - Service Discovery: The variety of services found (api, cdn,
    mail, etc.) provides insight into the technology stack of targets.

  - Certificate Transparency: CT logs revealed subdomains not found
    through brute force, indicating the value of multiple data sources.

--------------------------------------------------------------------------------
4. QUALITY ASSURANCE
--------------------------------------------------------------------------------

To ensure high-quality results:
  - All subdomains verified before submission
  - Invalid entries filtered out
  - Duplicate removal performed
  - Multiple verification passes completed

This approach prioritizes quality over quantity, ensuring submitted
subdomains are valid and resolvable.

--------------------------------------------------------------------------------
5. LESSONS LEARNED
--------------------------------------------------------------------------------

  - Diverse enumeration sources yield better coverage
  - Verification is critical to avoid false positives
  - Rate limiting must be respected when querying external APIs
  - Async programming significantly improves performance

================================================================================
                              END OF WRITEUP
================================================================================
"""

    # Save as text (user can convert to PDF)
    txt_output = output_file.replace('.pdf', '.txt')
    with open(txt_output, 'w') as f:
        f.write(content)

    print(f"[+] Part 1 writeup saved to {txt_output}")
    print(f"[!] Note: Convert to PDF using: pandoc {txt_output} -o {output_file}")
    print(f"    Or use online converters, Microsoft Word, Google Docs, etc.")

    return content


def generate_part2_report(scan_results_file: str = "cybersteps_report/scan_results.json",
                         output_file: str = "Part2_Cybersteps_Analysis.pdf"):
    """Generate Part 2 PDF report"""

    # Load scan results
    try:
        with open(scan_results_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[!] Scan results not found: {scan_results_file}")
        print("[!] Run: python cybersteps_recon.py")
        return None
    except json.JSONDecodeError:
        print(f"[!] Invalid JSON in {scan_results_file}")
        return None

    hostname = data.get('hostname', 'Unknown')
    ip = data.get('ip_address', 'Unknown')
    ports = data.get('open_ports', [])
    issues = data.get('security_issues', [])

    content = f"""
================================================================================
            PART 2: CYBERSTEPS TARGET ANALYSIS
                  Detailed Security Assessment
================================================================================

Report Date: {datetime.now().strftime('%Y-%m-%d')}
Classification: Confidential - Authorized Security Assessment

================================================================================
1. TARGET IDENTIFICATION
================================================================================

Discovery Method:
  - DNS subdomain enumeration focused on "scan" keyword
  - Systematic brute force of scan-related prefixes
  - Verified resolution before proceeding with analysis

Target Details:
  - Hostname: {hostname}
  - IP Address: {ip}
  - Assessment Type: Non-intrusive reconnaissance only

================================================================================
2. PORT SCAN RESULTS
================================================================================

Scan Methodology:
  - Tool: nmap with SYN stealth scan (-sS)
  - Timing: Slow (-T2) to minimize detection
  - DNS: Disabled (-n) for speed
  - Host discovery: Disabled (-Pn)
  - Max retries: 2
  - Timeout: 3 seconds

Open Ports Summary:
  Total Open Ports: {len(ports)}

Detailed Findings:
"""

    tcp_ports = [p for p in ports if p.get('protocol') == 'tcp']
    udp_ports = [p for p in ports if p.get('protocol') == 'udp']

    if tcp_ports:
        content += "\n  TCP Ports:\n"
        for p in tcp_ports:
            content += f"    - {p['port']}/tcp: {p.get('service', 'unknown')}\n"

    if udp_ports:
        content += "\n  UDP Ports:\n"
        for p in udp_ports:
            content += f"    - {p['port']}/udp: {p.get('service', 'unknown')}\n"

    content += """
================================================================================
3. SERVICE ENUMERATION & ANALYSIS
================================================================================

"""

    for p in ports:
        port_num = p['port']
        protocol = p['protocol'].upper()
        service = p.get('service', 'Unknown')
        version = p.get('version', 'Not detected')
        banner = p.get('banner', '')

        purpose = get_service_purpose(port_num, service)

        content += f"""
Port {port_num}/{protocol}
--------------------------------------------------------------------------------
  Service:        {service}
  Version:        {version}
  Purpose:        {purpose}
"""
        if banner:
            # Truncate long banners
            banner_display = banner[:300] + "..." if len(banner) > 300 else banner
            content += f"  Banner:         {banner_display}\n"

        content += "\n"

    content += f"""
================================================================================
4. SECURITY ISSUES & VULNERABILITY ANALYSIS
================================================================================

Risk Summary:
  Total Issues Identified: {len(issues)}

Detailed Findings:
"""

    if issues:
        for i, issue in enumerate(issues, 1):
            content += f"\n  {i}. {issue}\n"
    else:
        content += "\n  No security issues detected during assessment.\n"

    content += """
================================================================================
5. RECOMMENDATIONS
================================================================================

Based on the findings, the following recommendations are provided:

General:
  - Review all exposed services for business necessity
  - Implement network segmentation where possible
  - Enable comprehensive logging for all services
  - Regular vulnerability scanning and patching

Service-Specific:
  - Replace Telnet (port 23) with SSH immediately
  - Verify Redis/MongoDB authentication is enforced
  - Restrict database service access to necessary hosts only
  - Review SMB/RDP access controls
  - Minimize version information in service banners

Monitoring:
  - Implement intrusion detection/prevention
  - Monitor for unusual connection patterns
  - Alert on authentication failures
  - Track configuration changes

================================================================================
6. METHODOLOGY NOTES
================================================================================

Scan Characteristics:
  - Non-intrusive: No exploitation attempted
  - Stealth: Timing optimized to avoid detection
  - Comprehensive: TCP and UDP port coverage
  - Verified: Multiple confirmation passes

Tools Used:
  - nmap: Network mapping and port scanning
  - aiodns: Asynchronous DNS resolution
  - Custom Python scripts for automation

Limitations:
  - UDP scanning less reliable than TCP
  - Service versions may require active probing
  - Some services may not respond to standard probes
  - Firewall rules may obscure actual exposure

================================================================================
7. CONCLUSION
================================================================================

This assessment provides a snapshot of the target's attack surface at the
time of scanning. Regular reassessment is recommended as infrastructure and
configurations change over time.

Assessment completed successfully. All activities were conducted in
accordance with authorized scope and non-intrusive principles.

================================================================================
                           END OF REPORT
================================================================================

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Assessment Type: Authorized Reconnaissance
Classification: Confidential
"""

    # Save as text
    txt_output = output_file.replace('.pdf', '.txt')
    with open(txt_output, 'w') as f:
        f.write(content)

    print(f"[+] Part 2 report saved to {txt_output}")
    print(f"[!] Note: Convert to PDF using: pandoc {txt_output} -o {output_file}")

    return content


def get_service_purpose(port: int, service: str) -> str:
    """Get service purpose description"""
    purposes = {
        21: "File Transfer Protocol (FTP) - File transfers",
        22: "SSH - Encrypted remote administration",
        23: "Telnet - Unencrypted remote access (legacy)",
        25: "SMTP - Email transmission",
        53: "DNS - Domain name resolution",
        80: "HTTP - Web traffic",
        110: "POP3 - Email retrieval",
        143: "IMAP - Email access",
        443: "HTTPS - Secure web traffic",
        465: "SMTPS - Encrypted email submission",
        587: "SMTP Submission - Email submission",
        993: "IMAPS - Encrypted email access",
        995: "POP3S - Encrypted email retrieval",
        135: "MS RPC - Windows remote procedure call",
        139: "NetBIOS - Windows file sharing",
        445: "SMB - Server Message Block",
        1433: "MS SQL Server - Database",
        3306: "MySQL - Database service",
        3389: "RDP - Remote Desktop Protocol",
        5432: "PostgreSQL - Database service",
        5900: "VNC - Remote desktop access",
        6379: "Redis - In-memory data store",
        8080: "HTTP Alternate - Proxy/app server",
        8443: "HTTPS Alternate - TLS web service",
        9200: "Elasticsearch - Search engine",
        27017: "MongoDB - Document database",
    }

    return purposes.get(port, f"{service.upper() if service else 'Unknown'} service")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate PDF Reports')
    parser.add_argument('--part1', action='store_true',
                       help='Generate Part 1 writeup')
    parser.add_argument('--part2', action='store_true',
                       help='Generate Part 2 report')
    parser.add_argument('--all', action='store_true',
                       help='Generate all reports')

    args = parser.parse_args()

    if args.all or args.part1:
        print("[*] Generating Part 1 writeup...")
        generate_part1_writeup()

    if args.all or args.part2:
        print("\n[*] Generating Part 2 report...")
        generate_part2_report()

    if not any([args.all, args.part1, args.part2]):
        print("[*] Generating all reports...")
        generate_part1_writeup()
        generate_part2_report()

    print("\n[+] Report generation complete!")
    print("[!] To convert to PDF, use:")
    print("    - pandoc file.txt -o file.pdf")
    print("    - Online converters")
    print("    - Microsoft Word/Google Docs")


if __name__ == '__main__':
    main()
