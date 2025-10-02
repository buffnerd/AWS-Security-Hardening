#!/usr/bin/env python3
"""Block public access for all S3 buckets."""

import sys
import os
import json
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aws_sec_toolkit.scripts.s3_block_public_access import block_public_access_all_buckets
from colorama import init, Fore, Style

init()  # Initialize colorama


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Block public access for all S3 buckets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dry-run    # Check what would be changed
  %(prog)s --apply      # Actually block public access
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
        print("Use --apply to actually block S3 public access")
        return
    
    try:
        print(f"{Fore.BLUE}🚀 Blocking public access for all S3 buckets...{Style.RESET_ALL}")
        
        result = block_public_access_all_buckets()
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{Fore.GREEN}✅ S3 public access blocking completed!{Style.RESET_ALL}")
            for bucket, status in result.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {bucket}: {'BLOCKED' if status else 'FAILED'}")
                
        return 0 if all(result.values()) else 1
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error blocking S3 public access: {e}{Style.RESET_ALL}", file=sys.stderr)
        if args.json:
            print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())