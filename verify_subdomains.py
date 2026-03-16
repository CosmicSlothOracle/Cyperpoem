#!/usr/bin/env python3
"""
Subdomain Verification Tool
Validates subdomains against Google's 8.8.8.8 resolver
Only accepts A, CNAME, MX, TXT records
Removes NXDOMAIN and invalid entries
"""

import asyncio
import aiodns
import argparse
from pathlib import Path
from typing import Set, List, Tuple
from dataclasses import dataclass


@dataclass
class VerificationResult:
    subdomain: str
    record_type: str
    target: str
    is_valid: bool


class SubdomainVerifier:
    """Verify subdomains against Google DNS"""

    DNS_SERVER = '8.8.8.8'
    VALID_RECORDS = {'A', 'CNAME', 'MX', 'TXT'}

    def __init__(self, input_file: str, output_file: str, invalid_file: str = None,
                 domains_file: str = None, quiet: bool = False):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.invalid_file = Path(invalid_file) if invalid_file else None
        self.domains_file = Path(domains_file) if domains_file else None
        self.quiet = quiet
        self.resolver = None
        self.valid_subdomains: Set[str] = set()
        self.invalid_subdomains: Set[str] = set()
        self.results: List[VerificationResult] = []

    async def init_resolver(self):
        """Initialize DNS resolver with Google's DNS"""
        self.resolver = aiodns.DNSResolver(
            nameservers=[self.DNS_SERVER],
            timeout=10,
            tries=3
        )

    def load_root_domains(self) -> Set[str]:
        """Load allowed root domains for in-scope filtering"""
        if not self.domains_file or not self.domains_file.exists():
            return set()
        with open(self.domains_file, 'r') as f:
            return set(line.strip().lower() for line in f if line.strip())

    def is_in_scope(self, subdomain: str, roots: Set[str]) -> bool:
        """Check if subdomain belongs to one of the allowed root domains"""
        subdomain = subdomain.lower().strip()
        for root in roots:
            if subdomain == root or subdomain.endswith('.' + root):
                return True
        return False

    def load_subdomains(self) -> List[str]:
        """Load subdomains from file; filter to in-scope if domains_file set"""
        with open(self.input_file, 'r') as f:
            raw = list(set(line.strip().lower() for line in f if line.strip()))
        roots = self.load_root_domains()
        if not roots:
            return raw
        in_scope = [s for s in raw if self.is_in_scope(s, roots)]
        if not self.quiet and len(in_scope) != len(raw):
            print(f"[*] Filtered to {len(in_scope)} in-scope subdomains (from {len(raw)} total)")
        return in_scope

    async def verify_record(self, subdomain: str, record_type: str) -> Tuple[bool, str]:
        """Verify a specific DNS record type"""
        try:
            if record_type == 'A':
                result = await self.resolver.query(subdomain, 'A')
                if result:
                    target = result[0].host if hasattr(result[0], 'host') else str(result[0])
                    return True, target

            elif record_type == 'CNAME':
                result = await self.resolver.query(subdomain, 'CNAME')
                if result:
                    target = result.cname if hasattr(result, 'cname') else str(result)
                    return True, target

            elif record_type == 'MX':
                result = await self.resolver.query(subdomain, 'MX')
                if result:
                    target = result[0].host if hasattr(result[0], 'host') else str(result[0])
                    return True, target

            elif record_type == 'TXT':
                result = await self.resolver.query(subdomain, 'TXT')
                if result:
                    target = str(result[0]) if result else ""
                    return True, target

        except aiodns.error.DNSError as e:
            error_code = e.args[0]
            if error_code == aiodns.error.ARES_ENOTFOUND:
                return False, "NXDOMAIN"
            elif error_code == aiodns.error.ARES_ETIMEOUT:
                return False, "TIMEOUT"
            else:
                return False, f"DNS_ERROR_{error_code}"
        except Exception as e:
            return False, f"ERROR: {str(e)}"

        return False, "NO_RECORD"

    async def verify_subdomain(self, subdomain: str) -> VerificationResult:
        """Verify a subdomain by checking all valid record types"""
        if not self.quiet:
            print(f"[*] Verifying: {subdomain}")

        for record_type in self.VALID_RECORDS:
            is_valid, target = await self.verify_record(subdomain, record_type)
            if is_valid:
                if not self.quiet:
                    print(f"  [+] {record_type}: {target}")
                return VerificationResult(
                    subdomain=subdomain,
                    record_type=record_type,
                    target=target,
                    is_valid=True
                )

        if not self.quiet:
            print(f"  [-] No valid records found")
        return VerificationResult(
            subdomain=subdomain,
            record_type='NONE',
            target=target if 'target' in dir() else "",
            is_valid=False
        )

    async def run_verification(self):
        """Run verification on all subdomains"""
        await self.init_resolver()
        subdomains = self.load_subdomains()

        print(f"[*] Loaded {len(subdomains)} subdomains for verification")
        print(f"[*] Using DNS resolver: {self.DNS_SERVER}")
        print(f"[*] Valid record types: {', '.join(self.VALID_RECORDS)}\n")

        # Process all subdomains
        semaphore = asyncio.Semaphore(300)

        async def bounded_verify(subdomain: str):
            async with semaphore:
                return await self.verify_subdomain(subdomain)

        tasks = [bounded_verify(s) for s in subdomains]
        self.results = await asyncio.gather(*tasks)

        # Categorize results
        for result in self.results:
            if result.is_valid:
                self.valid_subdomains.add(result.subdomain)
            else:
                self.invalid_subdomains.add(result.subdomain)

        # Save results
        self.save_results()
        self.print_summary()

    def save_results(self):
        """Save verified and invalid subdomains"""
        # Save valid subdomains
        valid_sorted = sorted(self.valid_subdomains)
        with open(self.output_file, 'w') as f:
            for subdomain in valid_sorted:
                f.write(f"{subdomain}\n")
        print(f"\n[+] Saved {len(valid_sorted)} valid subdomains to {self.output_file}")

        # Save invalid subdomains if requested
        if self.invalid_file:
            invalid_sorted = sorted(self.invalid_subdomains)
            with open(self.invalid_file, 'w') as f:
                for subdomain in invalid_sorted:
                    f.write(f"{subdomain}\n")
            print(f"[+] Saved {len(invalid_sorted)} invalid subdomains to {self.invalid_file}")

    def print_summary(self):
        """Print verification summary"""
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        print(f"Total subdomains checked: {len(self.results)}")
        print(f"Valid subdomains: {len(self.valid_subdomains)}")
        print(f"Invalid subdomains: {len(self.invalid_subdomains)}")
        print(f"Success rate: {len(self.valid_subdomains)/len(self.results)*100:.1f}%")
        print("="*60)

        # Show record type distribution
        print("\nRecord Type Distribution:")
        record_counts = {}
        for result in self.results:
            if result.is_valid:
                record_counts[result.record_type] = record_counts.get(result.record_type, 0) + 1

        for record_type, count in sorted(record_counts.items()):
            print(f"  {record_type}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description='Verify subdomains against Google DNS (8.8.8.8)'
    )
    parser.add_argument('-i', '--input', required=True,
                       help='Input file with subdomains to verify')
    parser.add_argument('-o', '--output', default='subdomains_verified.txt',
                       help='Output file for valid subdomains')
    parser.add_argument('--invalid', default='subdomains_invalid.txt',
                       help='Output file for invalid subdomains')
    parser.add_argument('-d', '--domains', default=None,
                       help='Domains file: only verify subdomains under these roots')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet mode (less output)')

    args = parser.parse_args()

    verifier = SubdomainVerifier(
        input_file=args.input,
        output_file=args.output,
        invalid_file=args.invalid,
        domains_file=args.domains,
        quiet=args.quiet
    )

    try:
        asyncio.run(verifier.run_verification())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        verifier.save_results()


if __name__ == '__main__':
    main()
