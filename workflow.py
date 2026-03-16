#!/usr/bin/env python3
"""
Complete Workflow Script
Orchestrates the entire reconnaissance process
"""

import subprocess
import sys
from pathlib import Path
import argparse


class WorkflowRunner:
    """Run the complete reconnaissance workflow"""

    def __init__(self, skip_verification: bool = False):
        self.skip_verification = skip_verification
        self.steps_completed = []

    def run_command(self, cmd: list, description: str) -> bool:
        """Run a command and report status"""
        print(f"\n{'='*60}")
        print(f"STEP: {description}")
        print('='*60)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            self.steps_completed.append(description)
            return True
        except subprocess.CalledProcessError as e:
            print(f"[!] Error: {e}")
            print(f"[!] STDERR: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"[!] Command not found: {cmd[0]}")
            print(f"[!] Please ensure '{cmd[0]}' is installed and in PATH")
            return False

    def run_part1(self) -> bool:
        """Run Part 1: Subdomain Enumeration"""
        print("\n" + "="*60)
        print("PART 1: SUBDOMAIN ENUMERATION")
        print("="*60)

        # Step 1: Primary enumeration
        if not self.run_command(
            [sys.executable, 'subdomain_enum.py', '-d', 'domains.txt', '-o', 'subdomains_primary.txt'],
            "Primary DNS enumeration"
        ):
            return False

        # Step 2: Alternative enumeration
        if not self.run_command(
            [sys.executable, 'alt_enum.py', '-d', 'domains.txt', '-o', 'subdomains_alt.txt'],
            "Alternative enumeration (CT logs, APIs)"
        ):
            print("[!] Alternative enumeration failed or skipped")

        # Step 3: Combine results
        print("\n[*] Combining results...")
        try:
            primary = Path('subdomains_primary.txt')
            alt = Path('subdomains_alt.txt')

            combined = set()
            if primary.exists():
                with open(primary) as f:
                    combined.update(line.strip() for line in f if line.strip())
            if alt.exists():
                with open(alt) as f:
                    combined.update(line.strip() for line in f if line.strip())

            with open('subdomains_combined.txt', 'w') as f:
                for sub in sorted(combined):
                    f.write(f"{sub}\n")

            print(f"[+] Combined {len(combined)} unique subdomains")
        except Exception as e:
            print(f"[!] Error combining: {e}")
            return False

        # Step 4: Verification (unless skipped)
        if not self.skip_verification:
            if not self.run_command(
                [sys.executable, 'verify_subdomains.py',
                 '-i', 'subdomains_combined.txt',
                 '-o', 'subdomains.txt'],
                "DNS verification against 8.8.8.8"
            ):
                return False
        else:
            # Just copy combined to final
            import shutil
            shutil.copy('subdomains_combined.txt', 'subdomains.txt')
            print("[+] Skipped verification, using combined results")

        # Report
        final_path = Path('subdomains.txt')
        if final_path.exists():
            count = len(final_path.read_text().strip().split('\n'))
            print(f"\n[+] Part 1 Complete: {count} subdomains ready")
        else:
            print("[!] Final file not created")
            return False

        return True

    def run_part2(self) -> bool:
        """Run Part 2: Target Analysis"""
        print("\n" + "="*60)
        print("PART 2: CYBERSTEPS TARGET ANALYSIS")
        print("="*60)

        # Check for nmap
        try:
            subprocess.run(['nmap', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[!] nmap not found. Please install nmap to run Part 2.")
            print("[!] Ubuntu/Debian: sudo apt-get install nmap")
            print("[!] macOS: brew install nmap")
            print("[!] Windows: https://nmap.org/download.html")
            return False

        if not self.run_command(
            [sys.executable, 'cybersteps_recon.py', '-o', 'cybersteps_report'],
            "Full target reconnaissance"
        ):
            return False

        # Report
        report_dir = Path('cybersteps_report')
        if report_dir.exists():
            print(f"\n[+] Part 2 Complete: Reports in {report_dir}/")
            for f in report_dir.iterdir():
                print(f"    - {f.name}")
        else:
            print("[!] Report directory not created")
            return False

        return True

    def print_summary(self):
        """Print workflow summary"""
        print("\n" + "="*60)
        print("WORKFLOW SUMMARY")
        print("="*60)
        print(f"Completed steps: {len(self.steps_completed)}")
        for i, step in enumerate(self.steps_completed, 1):
            print(f"  {i}. {step}")

        # Deliverables
        print("\nDeliverables:")

        subdomains = Path('subdomains.txt')
        if subdomains.exists():
            count = len([l for l in subdomains.read_text().split('\n') if l.strip()])
            print(f"  [OK] subdomains.txt - {count} entries")

        report_dir = Path('cybersteps_report')
        if report_dir.exists():
            if (report_dir / 'scan_results.json').exists():
                print(f"  [OK] cybersteps_report/scan_results.json")
            if (report_dir / 'recon_report.txt').exists():
                print(f"  [OK] cybersteps_report/recon_report.txt")

        print("\nNext Steps:")
        print("  1. Review subdomains.txt for quality")
        print("  2. Create PDF write-up for Part 1")
        print("  3. Convert recon_report.txt to PDF for Part 2")
        print("  4. Submit deliverables")


def main():
    parser = argparse.ArgumentParser(description='Complete Reconnaissance Workflow')
    parser.add_argument('--skip-part1', action='store_true',
                       help='Skip Part 1 (subdomain enumeration)')
    parser.add_argument('--skip-part2', action='store_true',
                       help='Skip Part 2 (target analysis)')
    parser.add_argument('--skip-verify', action='store_true',
                       help='Skip DNS verification (faster)')

    args = parser.parse_args()

    runner = WorkflowRunner(skip_verification=args.skip_verify)

    success = True

    if not args.skip_part1:
        if not runner.run_part1():
            print("\n[!] Part 1 failed")
            success = False
    else:
        print("[*] Skipping Part 1")

    if not args.skip_part2:
        if not runner.run_part2():
            print("\n[!] Part 2 failed")
            success = False
    else:
        print("[*] Skipping Part 2")

    runner.print_summary()

    if success:
        print("\n[+] Workflow completed successfully!")
        return 0
    else:
        print("\n[!] Workflow completed with errors")
        return 1


if __name__ == '__main__':
    sys.exit(main())
