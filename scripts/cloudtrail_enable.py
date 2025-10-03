#!/usr/bin/env python3
"""
██████╗░██╡░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Enable & validate multi-region CloudTrail with S3/KMS best practices.
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from awssec.sessions import get_session
from awssec.tools.cloudtrail import enable_cloudtrail, check_cloudtrail_status
from awssec.utils import setup_logger, format_output, print_status


def main():
    parser = argparse.ArgumentParser(
        description='Enable and manage CloudTrail across AWS regions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cloudtrail_enable.py --dry-run
  cloudtrail_enable.py --apply --trail-name my-trail
  cloudtrail_enable.py --status-only --output json
        """
    )
    
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    parser.add_argument('--status-only', action='store_true', help='Only check CloudTrail status')
    parser.add_argument('--trail-name', default='aws-security-toolkit-trail', help='CloudTrail name')
    parser.add_argument('--regions', help='Comma-separated list of regions')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--region', help='AWS region')
    parser.add_argument('--assume-role-arn', help='IAM role ARN to assume')
    parser.add_argument('--output', choices=['table', 'json', 'csv'], default='table', help='Output format')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger('cloudtrail_enable', args.log_level)
    
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
            result = check_cloudtrail_status(session=session, regions=regions)
            print(format_output(result, args.output))
        else:
            dry_run = not args.apply
            result = enable_cloudtrail(
                session=session,
                trail_name=args.trail_name,
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