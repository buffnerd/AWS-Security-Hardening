#!/usr/bin/env python3
"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Find inbound 0.0.0.0/0 risks and offer safe remediations.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from awssec.sessions import get_session
from awssec.tools.sg_audit import audit_and_fix_security_groups
from awssec.utils import setup_logger, format_output, print_status


def main():
    parser = argparse.ArgumentParser(description='Audit and fix security group rules')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    parser.add_argument('--audit-only', action='store_true', help='Only audit, do not fix')
    parser.add_argument('--regions', help='Comma-separated list of regions')
    parser.add_argument('--ports', help='Comma-separated list of risky ports to check')
    parser.add_argument('--replacement-cidrs', help='Comma-separated list of replacement CIDRs')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--output', choices=['table', 'json', 'csv'], default='table')
    
    args = parser.parse_args()
    logger = setup_logger('security_group_audit', 'INFO')
    
    try:
        session = get_session(profile=args.profile)
        regions = [r.strip() for r in args.regions.split(',')] if args.regions else None
        ports = [int(p.strip()) for p in args.ports.split(',')] if args.ports else None
        replacement_cidrs = [c.strip() for c in args.replacement_cidrs.split(',')] if args.replacement_cidrs else None
        
        result = audit_and_fix_security_groups(
            session=session,
            regions=regions,
            risky_ports=ports,
            fix_rules=not args.audit_only,
            replacement_cidrs=replacement_cidrs,
            dry_run=not args.apply
        )
        
        print(format_output(result, args.output))
        
    except Exception as e:
        print_status(f"Error: {e}", 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()