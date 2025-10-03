#!/usr/bin/env python3
"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Enable GuardDuty across all regions and verify coverage.
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from awssec.sessions import get_session
from awssec.tools.guardduty import enable_guardduty, check_guardduty_status
from awssec.utils import setup_logger, format_output, print_status


def main():
    parser = argparse.ArgumentParser(
        description='Enable GuardDuty threat detection across all AWS regions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  guardduty_enable.py --dry-run
  guardduty_enable.py --apply
  guardduty_enable.py --status-only --output json
        """
    )
    
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    parser.add_argument('--status-only', action='store_true', help='Only check GuardDuty status')
    parser.add_argument('--regions', help='Comma-separated list of regions')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--region', help='AWS region')
    parser.add_argument('--assume-role-arn', help='IAM role ARN to assume')
    parser.add_argument('--output', choices=['table', 'json', 'csv'], default='table', help='Output format')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger('guardduty_enable', args.log_level)
    
    try:
        # Get session
        session = get_session(
            profile=args.profile,
            region=args.region,
            assume_role_arn=args.assume_role_arn
        )
        
        # Parse regions
        regions = None
        if args.regions:
            regions = [r.strip() for r in args.regions.split(',')]
        
        # Execute action
        if args.status_only:
            result = check_guardduty_status(session=session, regions=regions)
            print(format_output(result, args.output))
        else:
            dry_run = not args.apply
            result = enable_guardduty(
                session=session,
                regions=regions,
                dry_run=dry_run
            )
            print(format_output(result, args.output))
        
    except KeyboardInterrupt:
        print_status("Operation cancelled by user", 'WARNING')
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        print_status(f"Error: {e}", 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()