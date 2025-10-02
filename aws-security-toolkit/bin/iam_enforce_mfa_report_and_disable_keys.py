#!/usr/bin/env python3
"""Enforce IAM MFA and disable access keys for non-MFA users."""

import sys
import os
import json
import argparse
import csv
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aws_sec_toolkit.scripts.iam_mfa_enforce import generate_no_mfa_report, disable_access_keys_no_mfa
from colorama import init, Fore, Style

init()  # Initialize colorama


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate MFA report and optionally disable access keys for non-MFA users",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --report-only                    # Generate report only
  %(prog)s --csv report.csv                 # Save report to CSV
  %(prog)s --apply                          # Disable access keys for non-MFA users
  %(prog)s --apply --csv report.csv         # Both actions
        """
    )
    
    parser.add_argument(
        "--apply", 
        action="store_true", 
        help="Disable access keys for users without MFA (default is report-only)"
    )
    
    parser.add_argument(
        "--report-only", 
        action="store_true", 
        help="Only generate the MFA compliance report"
    )
    
    parser.add_argument(
        "--csv", 
        type=str, 
        help="Save report to CSV file"
    )
    
    parser.add_argument(
        "--json", 
        action="store_true", 
        help="Output results in JSON format"
    )
    
    return parser.parse_args()


def save_csv_report(report_data, csv_file):
    """Save report to CSV file."""
    if not report_data:
        return
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if isinstance(report_data[0], dict):
            fieldnames = report_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(report_data)
        else:
            writer = csv.writer(f)
            writer.writerows(report_data)


def main():
    """Main execution function."""
    args = parse_args()
    
    try:
        # Generate MFA report
        print(f"{Fore.BLUE}📊 Generating MFA compliance report...{Style.RESET_ALL}")
        report = generate_no_mfa_report()
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"{Fore.GREEN}📋 MFA Compliance Report:{Style.RESET_ALL}")
            if report:
                for user in report:
                    print(f"  ❌ {user.get('UserName', 'Unknown')}: No MFA configured")
                print(f"\n📈 Total users without MFA: {len(report)}")
            else:
                print("  ✅ All users have MFA configured!")
        
        # Save CSV if requested
        if args.csv:
            save_csv_report(report, args.csv)
            print(f"{Fore.GREEN}💾 Report saved to: {args.csv}{Style.RESET_ALL}")
        
        # Early exit if report-only
        if args.report_only:
            return 0
        
        # Disable access keys if apply flag is set
        if args.apply:
            if not report:
                print(f"{Fore.GREEN}✅ No action needed - all users have MFA{Style.RESET_ALL}")
                return 0
                
            print(f"{Fore.YELLOW}⚠️  Disabling access keys for {len(report)} users without MFA...{Style.RESET_ALL}")
            result = disable_access_keys_no_mfa()
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                for user, disabled in result.items():
                    status_icon = "✅" if disabled else "❌"
                    print(f"  {status_icon} {user}: {'DISABLED' if disabled else 'FAILED'}")
            
            return 0 if all(result.values()) else 1
        else:
            print(f"{Fore.YELLOW}🔍 DRY-RUN MODE: Use --apply to disable access keys{Style.RESET_ALL}")
            return 0
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error with IAM MFA operation: {e}{Style.RESET_ALL}", file=sys.stderr)
        if args.json:
            print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())