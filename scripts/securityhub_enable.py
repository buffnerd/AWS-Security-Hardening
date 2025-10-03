#!/usr/bin/env python3
"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Enable Security Hub + FSBP/CIS standards and check control status.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from awssec.sessions import get_session
from awssec.tools.securityhub import enable_security_hub, check_security_hub_status
from awssec.utils import setup_logger, format_output, print_status


def main():
    parser = argparse.ArgumentParser(description='Enable Security Hub across AWS regions')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    parser.add_argument('--status-only', action='store_true', help='Only check Security Hub status')
    parser.add_argument('--regions', help='Comma-separated list of regions')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--output', choices=['table', 'json', 'csv'], default='table')
    
    args = parser.parse_args()
    logger = setup_logger('securityhub_enable', 'INFO')
    
    try:
        session = get_session(profile=args.profile)
        regions = [r.strip() for r in args.regions.split(',')] if args.regions else None
        
        if args.status_only:
            result = check_security_hub_status(session=session, regions=regions)
        else:
            result = enable_security_hub(session=session, regions=regions, dry_run=not args.apply)
        
        print(format_output(result, args.output))
        
    except Exception as e:
        print_status(f"Error: {e}", 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()