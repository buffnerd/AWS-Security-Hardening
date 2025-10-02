#!/usr/bin/env python3
"""Enable GuardDuty in all regions."""

import sys
import os
import json
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aws_sec_toolkit.scripts.guardduty_enable import enable_guardduty_all_regions, check_guardduty_status
from colorama import init, Fore, Style

init()  # Initialize colorama


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Enable GuardDuty threat detection across all AWS regions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dry-run       # Check current status without changes
  %(prog)s --apply         # Actually enable GuardDuty
  %(prog)s --status-only   # Just check current status
        """
    )
    
    parser.add_argument(
        "--apply", 
        action="store_true", 
        help="Apply changes (default is dry-run mode)"
    )
    
    parser.add_argument(
        "--status-only", 
        action="store_true", 
        help="Only check current GuardDuty status"
    )
    
    parser.add_argument(
        "--json", 
        action="store_true", 
        help="Output results in JSON format"
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()
    
    try:
        if args.status_only:
            print(f"{Fore.BLUE}🔍 Checking GuardDuty status...{Style.RESET_ALL}")
            # We need to get regions first
            import boto3
            session = boto3.Session()
            ec2 = session.client("ec2", region_name="us-east-1")
            regions = ec2.describe_regions()["Regions"]
            region_names = [r["RegionName"] for r in regions]
            
            result = check_guardduty_status(region_names)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"{Fore.GREEN}📊 GuardDuty Status:{Style.RESET_ALL}")
                for region, status in result.items():
                    status_icon = "✅" if status == "ENABLED" else "❌"
                    print(f"  {status_icon} {region}: {status}")
            return 0
        
        if not args.apply:
            print(f"{Fore.YELLOW}🔍 DRY-RUN MODE: No changes will be made{Style.RESET_ALL}")
            print("Use --apply to actually enable GuardDuty")
            return
        
        print(f"{Fore.BLUE}🚀 Enabling GuardDuty across all regions...{Style.RESET_ALL}")
        
        result = enable_guardduty_all_regions()
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{Fore.GREEN}✅ GuardDuty enablement completed!{Style.RESET_ALL}")
            for region, status in result.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {region}: {'ENABLED' if status else 'FAILED'}")
                
        return 0 if all(result.values()) else 1
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error with GuardDuty operation: {e}{Style.RESET_ALL}", file=sys.stderr)
        if args.json:
            print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())