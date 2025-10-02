#!/usr/bin/env python3
"""Enable Security Hub in all regions."""

import sys
import os
import json
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aws_sec_toolkit.scripts.securityhub_enable import enable_securityhub_all_regions
from colorama import init, Fore, Style

init()  # Initialize colorama


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Enable Security Hub across all AWS regions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dry-run    # Check what would be done
  %(prog)s --apply      # Actually enable Security Hub
        """
    )
    
    parser.add_argument(
        "--apply", 
        action="store_true", 
        help="Apply changes (default is dry-run mode)"
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
    
    if not args.apply:
        print(f"{Fore.YELLOW}🔍 DRY-RUN MODE: No changes will be made{Style.RESET_ALL}")
        print("Use --apply to actually enable Security Hub")
        return
    
    try:
        print(f"{Fore.BLUE}🚀 Enabling Security Hub across all regions...{Style.RESET_ALL}")
        
        result = enable_securityhub_all_regions()
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{Fore.GREEN}✅ Security Hub enablement completed!{Style.RESET_ALL}")
            for region, status in result.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {region}: {'ENABLED' if status else 'FAILED'}")
                
        return 0 if all(result.values()) else 1
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error enabling Security Hub: {e}{Style.RESET_ALL}", file=sys.stderr)
        if args.json:
            print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())