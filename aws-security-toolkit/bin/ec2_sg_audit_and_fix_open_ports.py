#!/usr/bin/env python3
"""Audit and fix EC2 security groups with open ports."""

import sys
import os
import json
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aws_sec_toolkit.scripts.sg_audit_fix import audit_security_groups, fix_open_security_groups
from colorama import init, Fore, Style

init()  # Initialize colorama


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Audit and fix EC2 security groups with open ports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --audit-only                    # Audit only, no changes
  %(prog)s --apply                         # Fix open security groups
  %(prog)s --ports 22,3389                 # Focus on specific ports
  %(prog)s --apply --dry-run               # Show what would be fixed
        """
    )
    
    parser.add_argument(
        "--apply", 
        action="store_true", 
        help="Apply fixes to open security groups (default is audit-only)"
    )
    
    parser.add_argument(
        "--audit-only", 
        action="store_true", 
        help="Only audit security groups, no fixes"
    )
    
    parser.add_argument(
        "--ports", 
        type=str, 
        help="Comma-separated list of ports to focus on (e.g., 22,3389,80)"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be changed without applying fixes"
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
        # Parse ports if provided
        focus_ports = None
        if args.ports:
            focus_ports = [int(p.strip()) for p in args.ports.split(',')]
        
        # Always run audit first
        print(f"{Fore.BLUE}🔍 Auditing security groups for open ports...{Style.RESET_ALL}")
        audit_result = audit_security_groups()
        
        if args.json and args.audit_only:
            print(json.dumps(audit_result, indent=2))
            return 0
        
        if not args.json:
            print(f"{Fore.GREEN}📊 Security Group Audit Results:{Style.RESET_ALL}")
            total_issues = sum(len(issues) for issues in audit_result.values())
            
            if total_issues == 0:
                print("  ✅ No open security group issues found!")
            else:
                print(f"  ⚠️  Found {total_issues} security group issues across {len(audit_result)} regions")
                for region, issues in audit_result.items():
                    if issues:
                        print(f"    📍 {region}: {len(issues)} issues")
                        for issue in issues[:3]:  # Show first 3
                            sg_id = issue.get('GroupId', 'Unknown')
                            port = issue.get('Port', 'Unknown')
                            print(f"      • {sg_id}: Port {port} open to 0.0.0.0/0")
                        if len(issues) > 3:
                            print(f"      • ... and {len(issues) - 3} more")
        
        # Early exit if audit-only
        if args.audit_only:
            return 0
        
        # Apply fixes if requested
        if args.apply:
            if not audit_result or sum(len(issues) for issues in audit_result.values()) == 0:
                print(f"{Fore.GREEN}✅ No fixes needed{Style.RESET_ALL}")
                return 0
            
            dry_run = args.dry_run
            if dry_run:
                print(f"{Fore.YELLOW}🔍 DRY-RUN MODE: Showing what would be fixed{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️  Applying security group fixes...{Style.RESET_ALL}")
            
            fix_result = fix_open_security_groups(dry_run=dry_run)
            
            if args.json:
                print(json.dumps({"audit": audit_result, "fixes": fix_result}, indent=2))
            else:
                print(f"{Fore.GREEN}🔧 Security Group Fix Results:{Style.RESET_ALL}")
                for sg_id, fixed in fix_result.items():
                    status_icon = "✅" if fixed else "❌"
                    action = "WOULD FIX" if dry_run else ("FIXED" if fixed else "FAILED")
                    print(f"  {status_icon} {sg_id}: {action}")
            
            return 0 if all(fix_result.values()) else 1
        else:
            print(f"{Fore.YELLOW}🔍 Use --apply to fix security group issues{Style.RESET_ALL}")
            return 0
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error with security group operation: {e}{Style.RESET_ALL}", file=sys.stderr)
        if args.json:
            print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())