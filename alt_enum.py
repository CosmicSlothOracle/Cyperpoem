#!/usr/bin/env python3
"""
Alternative Subdomain Enumeration Methods
Additional techniques using certificate transparency, DNS zone transfers, etc.
"""

import asyncio
import aiohttp
import json
from typing import Set, List, Optional
from dataclasses import dataclass


@dataclass
class SubdomainSource:
    name: str
    subdomains: Set[str]


class AlternativeEnumerator:
    """Additional enumeration techniques"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.discovered: Set[str] = set()

    async def init_session(self):
        """Initialize HTTP session"""
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=50)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector
        )

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    async def crt_sh_lookup(self, domain: str) -> Set[str]:
        """Query crt.sh for certificate transparency logs"""
        subdomains = set()
        url = f"https://crt.sh/?q=%.{domain}&output=json"

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for entry in data:
                        name = entry.get('name_value', '').strip()
                        if name and '*' not in name:
                            # Handle multiple names in one entry
                            for sub in name.split('\n'):
                                sub = sub.strip().lower()
                                if sub.endswith(domain) and sub != domain:
                                    subdomains.add(sub)
        except Exception as e:
            print(f"  [!] crt.sh error for {domain}: {e}")

        return subdomains

    async def threatcrowd_lookup(self, domain: str) -> Set[str]:
        """Query ThreatCrowd API"""
        subdomains = set()
        url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}"

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for sub in data.get('subdomains', []):
                        sub = sub.strip().lower()
                        if sub.endswith(domain):
                            subdomains.add(sub)
        except Exception as e:
            print(f"  [!] ThreatCrowd error for {domain}: {e}")

        return subdomains

    async def hackertarget_lookup(self, domain: str) -> Set[str]:
        """Query HackerTarget API"""
        subdomains = set()
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    for line in text.split('\n'):
                        if ',' in line:
                            subdomain = line.split(',')[0].strip().lower()
                            if subdomain and subdomain != domain:
                                subdomains.add(subdomain)
        except Exception as e:
            print(f"  [!] HackerTarget error for {domain}: {e}")

        return subdomains

    async def bufferover_lookup(self, domain: str) -> Set[str]:
        """Query BufferOver (Rapid7) DNS data"""
        subdomains = set()
        url = f"https://dns.bufferover.run/dns?q=.{domain}"

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for record in data.get('FDNS_A', []):
                        if ',' in record:
                            subdomain = record.split(',')[1].strip().lower()
                            if subdomain.endswith(domain) and subdomain != domain:
                                subdomains.add(subdomain)
        except Exception as e:
            print(f"  [!] BufferOver error for {domain}: {e}")

        return subdomains

    async def enumerate_domain(self, domain: str) -> SubdomainSource:
        """Run all enumeration methods on a domain"""
        print(f"[*] Running alternative enumeration for {domain}...")

        # Run all lookups concurrently
        tasks = [
            self.crt_sh_lookup(domain),
            self.threatcrowd_lookup(domain),
            self.hackertarget_lookup(domain),
            self.bufferover_lookup(domain),
        ]

        results = await asyncio.gather(*tasks)

        all_subdomains = set()
        source_names = ['crt.sh', 'ThreatCrowd', 'HackerTarget', 'BufferOver']

        for source, subs in zip(source_names, results):
            if subs:
                print(f"  [+] {source}: {len(subs)} subdomains")
                all_subdomains.update(subs)

        return SubdomainSource(name='alternative', subdomains=all_subdomains)

    async def run_enumeration(self, domains: List[str]) -> Set[str]:
        """Run alternative enumeration on all domains"""
        await self.init_session()

        all_discovered = set()

        for domain in domains:
            source = await self.enumerate_domain(domain)
            all_discovered.update(source.subdomains)

        await self.close()

        return all_discovered


def load_domains(filepath: str) -> List[str]:
    """Load domains from file"""
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]


async def main():
    import argparse

    parser = argparse.ArgumentParser(description='Alternative Subdomain Enumeration')
    parser.add_argument('-d', '--domains', default='domains.txt',
                       help='File containing root domains')
    parser.add_argument('-o', '--output', default='subdomains_alt.txt',
                       help='Output file')

    args = parser.parse_args()

    domains = load_domains(args.domains)
    print(f"[*] Loaded {len(domains)} domains")

    enumerator = AlternativeEnumerator()
    discovered = await enumerator.run_enumeration(domains)

    # Save results
    with open(args.output, 'w') as f:
        for sub in sorted(discovered):
            f.write(f"{sub}\n")

    print(f"\n[+] Discovered {len(discovered)} unique subdomains")
    print(f"[+] Results saved to {args.output}")


if __name__ == '__main__':
    asyncio.run(main())
