#!/usr/bin/env python3
"""
Cybersteps Target Reconnaissance
Part 2: Find scan subdomain and perform in-depth analysis
"""

import asyncio
import aiodns
import argparse
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict, field
import subprocess
import socket


@dataclass
class PortScanResult:
    port: int
    protocol: str  # tcp or udp
    state: str  # open, closed, filtered
    service: str = ""
    version: str = ""
    banner: str = ""
    notes: str = ""


@dataclass
class TargetInfo:
    hostname: str
    ip_address: str = ""
    open_ports: List[PortScanResult] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)


class CyberstepsRecon:
    """Reconnaissance for Cybersteps target"""

    ROOT_DOMAIN = "cybersteps.de"
    DNS_SERVER = '8.8.8.8'

    # Common TCP ports to check
    TCP_PORTS = [
        21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995,
        135, 139, 445, 3389, 5900, 5901, 8080, 8443, 8888, 9000, 9200,
        3000, 3306, 5432, 6379, 27017, 5000, 8000, 8081, 8444, 10000
    ]

    # UDP ports to check
    UDP_PORTS = [53, 67, 68, 69, 123, 137, 138, 161, 162, 500, 514, 520]

    def __init__(self, output_dir: str = "cybersteps_report"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.resolver = None
        self.target_info: Optional[TargetInfo] = None

    async def init_resolver(self):
        """Initialize DNS resolver"""
        self.resolver = aiodns.DNSResolver(
            nameservers=[self.DNS_SERVER],
            timeout=5,
            tries=2
        )

    async def find_scan_subdomain(self) -> Optional[str]:
        """Find subdomain containing 'scan'"""
        print(f"[*] Searching for scan subdomain in {self.ROOT_DOMAIN}...")

        # Generate scan-related subdomains
        scan_prefixes = [
            'scan', 'scanner', 'scanning', 'scans', 'scanme',
            'scan-test', 'test-scan', 'scan-dev', 'dev-scan',
            'scan-prod', 'prod-scan', 'scan-api', 'api-scan',
            'scanthis', 'scan-this', 'this-scan', 'scanthat',
            'secure-scan', 'vuln-scan', 'vulnscan', 'port-scan',
            'portscan', 'network-scan', 'net-scan', 'scanmepls',
            'scanmeplease', 'canscan', 'scanme', 'scanmebaby',
            'scan-01', 'scan-02', 'scan1', 'scan2', 'scan3',
            'webscan', 'urlscan', 'hostscan', 'ipscan', 'domain-scan'
        ]

        for prefix in scan_prefixes:
            subdomain = f"{prefix}.{self.ROOT_DOMAIN}"
            try:
                result = await self.resolver.query(subdomain, 'A')
                if result:
                    ip = result[0].host if hasattr(result[0], 'host') else str(result[0])
                    print(f"[+] Found scan subdomain: {subdomain} -> {ip}")
                    return subdomain
            except Exception:
                pass

            # Also check CNAME
            try:
                result = await self.resolver.query(subdomain, 'CNAME')
                if result:
                    cname = result.cname if hasattr(result, 'cname') else str(result)
                    print(f"[+] Found scan subdomain: {subdomain} -> CNAME: {cname}")
                    return subdomain
            except Exception:
                pass

        print("[-] No scan subdomain found")
        return None

    def resolve_ip(self, hostname: str) -> str:
        """Resolve hostname to IP"""
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return ""

    async def _tcp_connect_scan_fallback(self, target: str, ports: List[int]) -> List[PortScanResult]:
        """Fallback: TCP connect scan when nmap is not available (quiet, non-intrusive)."""
        results = []
        sem = asyncio.Semaphore(50)

        async def check_port(port: int) -> Optional[PortScanResult]:
            async with sem:
                try:
                    _ = await asyncio.wait_for(
                        asyncio.open_connection(target, port),
                        timeout=2.0
                    )
                    _[1].close()
                    await _[1].wait_closed()
                    return PortScanResult(port=port, protocol='tcp', state='open', service='')
                except (OSError, asyncio.TimeoutError):
                    return None

        tasks = [check_port(p) for p in ports]
        done = await asyncio.gather(*tasks)
        for r in done:
            if r is not None:
                results.append(r)
                print(f"  [+] TCP/{r.port} - open")
        return results

    async def stealth_port_scan(self, target: str, ports: List[int],
                               protocol: str = 'tcp') -> List[PortScanResult]:
        """Perform stealthy port scan using nmap, or TCP connect fallback if nmap missing."""
        print(f"[*] Performing stealth {protocol.upper()} port scan on {target}...")

        results = []

        # Use nmap with stealth options
        port_str = ','.join(map(str, ports))

        if protocol == 'tcp':
            cmd = [
                'nmap', '-sS',  # SYN scan
                '-Pn',  # No ping
                '-n',   # No DNS resolution
                '-T2',  # Slow timing for stealth
                '--max-retries', '2',
                '--max-rtt-timeout', '3s',
                '--initial-rtt-timeout', '1s',
                '-p', port_str,
                '-oX', '-',  # XML output to stdout
                target
            ]
        else:
            cmd = [
                'nmap', '-sU',  # UDP scan
                '-Pn',
                '-n',
                '-T2',
                '--max-retries', '1',
                '-p', port_str,
                '-oX', '-',
                target
            ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            # Parse nmap XML output
            if result.returncode == 0 and result.stdout:
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(result.stdout)
                    for host in root.findall('.//host'):
                        for port_elem in host.findall('.//port'):
                            port_num = int(port_elem.get('portid'))
                            state_elem = port_elem.find('state')
                            state = state_elem.get('state') if state_elem is not None else 'unknown'

                            service_elem = port_elem.find('service')
                            service = ''
                            version = ''
                            if service_elem is not None:
                                service = service_elem.get('name', '')
                                version = service_elem.get('version', '')
                                if service_elem.get('product'):
                                    version = f"{service_elem.get('product')} {version}".strip()

                            if state == 'open':
                                results.append(PortScanResult(
                                    port=port_num,
                                    protocol=protocol,
                                    state=state,
                                    service=service,
                                    version=version
                                ))
                                print(f"  [+] {protocol.upper()}/{port_num} - {service} {version}")
                except ET.ParseError:
                    pass

        except FileNotFoundError:
            # nmap not installed: use TCP connect fallback for TCP only
            if protocol == 'tcp':
                print("  [*] nmap not found; using TCP connect scan fallback")
                results = await self._tcp_connect_scan_fallback(target, ports)
            # UDP without nmap is not reliable; skip
        except subprocess.TimeoutExpired:
            print(f"  [!] Scan timed out")
        except Exception as e:
            print(f"  [!] Scan error: {e}")

        return results

    async def grab_banner(self, target: str, port: int,
                          protocol: str = 'tcp') -> Optional[str]:
        """Grab service banner"""
        try:
            if protocol == 'tcp':
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(target, port),
                    timeout=5
                )

                # Send common probes
                probes = [
                    b'',  # Empty probe
                    b'HEAD / HTTP/1.0\r\n\r\n',  # HTTP
                    b'GET / HTTP/1.0\r\n\r\n',   # HTTP
                    b'\r\n',  # Generic
                    b'HELP\r\n',  # Generic
                    b'EHLO test\r\n',  # SMTP
                    b'USER anonymous\r\n',  # FTP
                    b'\x00\x00\x00\x22\x00\x00\x00\x03',  # Binary (SSH)
                ]

                banner = b''
                for probe in probes:
                    try:
                        if probe:
                            writer.write(probe)
                            await writer.drain()

                        data = await asyncio.wait_for(reader.read(1024), timeout=3)
                        if data:
                            banner = data
                            break
                    except:
                        continue

                writer.close()
                await writer.wait_closed()

                if banner:
                    # Clean and decode banner
                    try:
                        return banner.decode('utf-8', errors='replace').strip()
                    except:
                        return repr(banner)

        except Exception:
            pass

        return None

    async def service_version_detection(self, target: str,
                                        port_results: List[PortScanResult]):
        """Enhanced service version detection using nmap -sV, or banner grab fallback."""
        print(f"[*] Running service version detection...")

        if not port_results:
            return

        ports = [r.port for r in port_results]
        port_str = ','.join(map(str, ports))

        cmd = [
            'nmap', '-sV',
            '-Pn', '-n',
            '-T3',
            '--version-intensity', '5',
            '-p', port_str,
            '-oX', '-',
            target
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and result.stdout:
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(result.stdout)
                    for host in root.findall('.//host'):
                        for port_elem in host.findall('.//port'):
                            port_num = int(port_elem.get('portid'))
                            service_elem = port_elem.find('service')

                            if service_elem is not None:
                                for pr in port_results:
                                    if pr.port == port_num:
                                        pr.service = service_elem.get('name', pr.service)
                                        product = service_elem.get('product', '')
                                        version = service_elem.get('version', '')
                                        extrainfo = service_elem.get('extrainfo', '')

                                        version_str = f"{product} {version} {extrainfo}".strip()
                                        if version_str:
                                            pr.version = version_str

                                        # Try to grab banner for additional info
                                        banner = await self.grab_banner(target, port_num)
                                        if banner:
                                            pr.banner = banner[:500]  # Truncate long banners

                except ET.ParseError:
                    pass

        except FileNotFoundError:
            # nmap not available: use banner grab only
            print("  [*] nmap not found; using banner grab for service info")
            for pr in port_results:
                banner = await self.grab_banner(target, pr.port)
                if banner:
                    pr.banner = banner[:500]
                    # Infer service from banner or port
                    if not pr.service:
                        pr.service = self._infer_service(pr.port, banner)
        except Exception as e:
            print(f"  [!] Version detection error: {e}")

    def analyze_security_issues(self, target_info: TargetInfo) -> List[str]:
        """Analyze findings for security issues"""
        issues = []

        for port in target_info.open_ports:
            # Check for common security issues
            if port.port == 21:
                issues.append("FTP service detected (port 21) - Consider using SFTP instead")

            elif port.port == 22:
                if 'OpenSSH' in port.version:
                    # Check version for known vulnerabilities
                    issues.append("SSH service detected (port 22) - Verify latest patches applied")

            elif port.port == 23:
                issues.append("TELNET detected (port 23) - CRITICAL: Unencrypted protocol, replace with SSH")

            elif port.port == 25 and 'ESMTP' not in port.version.upper():
                issues.append("SMTP without ESMTPS may allow unencrypted communication")

            elif port.port == 53:
                issues.append("DNS service (port 53) - Verify recursion not open to public")

            elif port.port in [135, 139, 445]:
                issues.append(f"Windows SMB/NetBIOS on port {port.port} - Ensure restricted access, check for EternalBlue")

            elif port.port == 3389:
                issues.append("RDP service (port 3389) - Verify NLA enabled, restrict source IPs")

            elif port.port in [5900, 5901]:
                issues.append(f"VNC service (port {port.port}) - Check for authentication and encryption")

            elif port.port == 3306:
                issues.append("MySQL (port 3306) exposed - Verify bind-address and authentication")

            elif port.port == 5432:
                issues.append("PostgreSQL (port 5432) exposed - Verify pg_hba.conf restrictions")

            elif port.port == 6379:
                issues.append("Redis (port 6379) - CRITICAL: Check for AUTH and protected-mode")

            elif port.port == 27017:
                issues.append("MongoDB (port 27017) - Verify authentication enabled and bind IP restricted")

            elif port.port == 8080:
                if 'http' in port.service.lower() or not port.service:
                    issues.append("HTTP on non-standard port 8080 - May indicate proxy or alternate web server")

            elif port.port == 9200:
                issues.append("Elasticsearch (port 9200) - Verify no sensitive data exposed without authentication")

            # Check for version disclosure in banner
            if port.banner and any(x in port.banner.lower() for x in ['server:', 'version:', 'welcome']):
                if len(port.banner) > 50:
                    issues.append(f"Port {port.port} reveals detailed banner information - Consider minimizing version disclosure")

            # Check for outdated services
            outdated_keywords = ['apache/2.2', 'nginx/1.10', 'openssl/1.0', 'openssh/6',
                                'php/5.', 'tomcat/7.', 'iis/6.', 'iis/7.']
            version_lower = (port.version + ' ' + port.banner).lower()
            for keyword in outdated_keywords:
                if keyword in version_lower:
                    issues.append(f"Port {port.port} may run outdated software ({keyword}) - Verify latest security patches")

        return issues

    async def run_full_recon(self):
        """Run complete reconnaissance"""
        await self.init_resolver()

        # Step 1: Find scan subdomain
        scan_subdomain = await self.find_scan_subdomain()
        if not scan_subdomain:
            print("[-] Could not find scan subdomain. Exiting.")
            return

        # Step 2: Resolve IP
        ip = self.resolve_ip(scan_subdomain)
        print(f"[*] Resolved {scan_subdomain} to {ip}")

        self.target_info = TargetInfo(
            hostname=scan_subdomain,
            ip_address=ip
        )

        # Step 3: Port scanning
        print("\n[*] Starting port scan phase...")

        # TCP scan
        tcp_results = await self.stealth_port_scan(ip or scan_subdomain, self.TCP_PORTS, 'tcp')
        self.target_info.open_ports.extend(tcp_results)

        # UDP scan (subset)
        udp_results = await self.stealth_port_scan(ip or scan_subdomain, self.UDP_PORTS, 'udp')
        self.target_info.open_ports.extend(udp_results)

        # Step 4: Service version detection
        if self.target_info.open_ports:
            await self.service_version_detection(ip or scan_subdomain, self.target_info.open_ports)

        # Step 5: Security analysis
        print("\n[*] Analyzing security issues...")
        self.target_info.security_issues = self.analyze_security_issues(self.target_info)

        # Step 6: Save results
        self.save_results()
        self.generate_report()

    def save_results(self):
        """Save results to JSON"""
        results_file = self.output_dir / 'scan_results.json'

        data = {
            'hostname': self.target_info.hostname,
            'ip_address': self.target_info.ip_address,
            'open_ports': [
                {
                    'port': p.port,
                    'protocol': p.protocol,
                    'state': p.state,
                    'service': p.service,
                    'version': p.version,
                    'banner': p.banner
                }
                for p in self.target_info.open_ports
            ],
            'security_issues': self.target_info.security_issues
        }

        with open(results_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n[+] Results saved to {results_file}")

    def generate_report(self):
        """Generate text report"""
        report_file = self.output_dir / 'recon_report.txt'

        with open(report_file, 'w', encoding='utf-8', errors='replace') as f:
            f.write("="*70 + "\n")
            f.write("CYBERSTEPS TARGET RECONNAISSANCE REPORT\n")
            f.write("="*70 + "\n\n")

            # Target Identification
            f.write("TARGET IDENTIFICATION\n")
            f.write("-"*40 + "\n")
            f.write(f"Method: DNS enumeration for subdomains containing 'scan'\n")
            f.write(f"Target Hostname: {self.target_info.hostname}\n")
            f.write(f"IP Address: {self.target_info.ip_address}\n\n")

            # Port Scan Results
            f.write("PORT SCAN RESULTS\n")
            f.write("-"*40 + "\n")
            f.write(f"Open Ports Found: {len(self.target_info.open_ports)}\n\n")

            tcp_ports = [p for p in self.target_info.open_ports if p.protocol == 'tcp']
            udp_ports = [p for p in self.target_info.open_ports if p.protocol == 'udp']

            if tcp_ports:
                f.write("TCP Ports:\n")
                for p in tcp_ports:
                    f.write(f"  {p.port}/tcp - {p.service}\n")
                f.write("\n")

            if udp_ports:
                f.write("UDP Ports:\n")
                for p in udp_ports:
                    f.write(f"  {p.port}/udp - {p.service}\n")
                f.write("\n")

            # Service Enumeration
            f.write("SERVICE ENUMERATION & ANALYSIS\n")
            f.write("-"*40 + "\n\n")

            for p in self.target_info.open_ports:
                f.write(f"Port {p.port}/{p.protocol.upper()}\n")
                f.write(f"  Service: {p.service}\n")
                f.write(f"  Version: {p.version}\n")
                if p.banner:
                    safe_banner = p.banner[:200].encode('utf-8', errors='replace').decode('utf-8')
                    f.write(f"  Banner: {safe_banner}\n")

                # Purpose description
                purpose = self.get_service_purpose(p.port, p.service)
                f.write(f"  Purpose: {purpose}\n\n")

            # Security Issues
            f.write("\nSECURITY ISSUES & VULNERABILITY ANALYSIS\n")
            f.write("-"*40 + "\n\n")

            if self.target_info.security_issues:
                for i, issue in enumerate(self.target_info.security_issues, 1):
                    f.write(f"{i}. {issue}\n\n")
            else:
                f.write("No obvious security issues detected.\n")

            f.write("\n" + "="*70 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*70 + "\n")

        print(f"[+] Report saved to {report_file}")

    def _infer_service(self, port: int, banner: str) -> str:
        """Infer service name from port and banner."""
        banner_lower = banner.lower()
        if 'ssh' in banner_lower or port == 22:
            return 'ssh'
        if 'http' in banner_lower or port in (80, 443, 8080, 8443):
            return 'http'
        if 'smtp' in banner_lower or port == 25:
            return 'smtp'
        if 'ftp' in banner_lower or port == 21:
            return 'ftp'
        if port == 22:
            return 'ssh'
        if port in (80, 8080):
            return 'http'
        if port in (443, 8443):
            return 'https'
        return 'unknown'

    def get_service_purpose(self, port: int, service: str) -> str:
        """Get description of service purpose"""
        purposes = {
            21: "File Transfer Protocol (FTP) - Unencrypted file transfers",
            22: "SSH (Secure Shell) - Encrypted remote administration",
            23: "Telnet - Unencrypted remote access (deprecated)",
            25: "SMTP - Email transmission",
            53: "DNS - Domain name resolution",
            80: "HTTP - Web traffic (unencrypted)",
            110: "POP3 - Email retrieval",
            143: "IMAP - Email access and management",
            443: "HTTPS - Secure web traffic",
            465: "SMTPS - Encrypted email submission",
            587: "Submission - Email submission with STARTTLS",
            993: "IMAPS - Encrypted email access",
            995: "POP3S - Encrypted email retrieval",
            135: "MS RPC - Microsoft Remote Procedure Call",
            139: "NetBIOS - Windows file sharing",
            445: "SMB - Server Message Block (file sharing)",
            1433: "MS SQL Server - Database service",
            3306: "MySQL - Database service",
            3389: "RDP - Remote Desktop Protocol",
            5432: "PostgreSQL - Database service",
            5900: "VNC - Virtual Network Computing remote desktop",
            6379: "Redis - In-memory data store",
            8080: "HTTP Alternate - Common for proxies and apps",
            8443: "HTTPS Alternate - TLS-secured web service",
            9200: "Elasticsearch - Search and analytics engine",
            27017: "MongoDB - Document database"
        }

        if port in purposes:
            return purposes[port]

        if service:
            return f"{service.upper()} service detected"

        return "Unknown service"


def main():
    parser = argparse.ArgumentParser(
        description='Cybersteps Target Reconnaissance'
    )
    parser.add_argument('-o', '--output', default='cybersteps_report',
                       help='Output directory for reports')

    args = parser.parse_args()

    recon = CyberstepsRecon(output_dir=args.output)

    try:
        asyncio.run(recon.run_full_recon())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")


if __name__ == '__main__':
    main()
