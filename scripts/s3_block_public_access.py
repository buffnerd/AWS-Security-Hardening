#!/usr/bin/env python3
"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Enforce account & bucket-level S3 Block Public Access; print exceptions.
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from awssec.sessions import get_session
from awssec.tools.s3_bpa import (
    enforce_s3_block_public_access,
    check_account_block_public_access_status,
    check_bucket_block_public_access_status
)
from awssec.utils import setup_logger, format_output, print_status


def main():
    parser = argparse.ArgumentParser(
        description='Block public access for all S3 buckets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  s3_block_public_access.py --dry-run
  s3_block_public_access.py --apply
  s3_block_public_access.py --status-only --output json
        """
    )
    
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    parser.add_argument('--status-only', action='store_true', help='Only check S3 Block Public Access status')
    parser.add_argument('--buckets', help='Comma-separated list of bucket names (default: all)')
    parser.add_argument('--account-level-only', action='store_true', help='Only apply at account level')
    parser.add_argument('--bucket-level-only', action='store_true', help='Only apply at bucket level')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--region', help='AWS region')
    parser.add_argument('--assume-role-arn', help='IAM role ARN to assume')
    parser.add_argument('--output', choices=['table', 'json', 'csv'], default='table', help='Output format')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger('s3_block_public_access', args.log_level)
    
    try:
        # Get session
        session = get_session(
            profile=args.profile,
            region=args.region,
            assume_role_arn=args.assume_role_arn
        )
        
        # Parse buckets
        bucket_names = None
        if args.buckets:
            bucket_names = [b.strip() for b in args.buckets.split(',')]
        
        # Execute action
        if args.status_only:
            account_status = check_account_block_public_access_status(session)
            bucket_status = check_bucket_block_public_access_status(session, bucket_names)
            result = {'account': account_status, 'buckets': bucket_status}
            print(format_output(result, args.output))
        else:
            dry_run = not args.apply
            account_level = not args.bucket_level_only
            bucket_level = not args.account_level_only
            
            result = enforce_s3_block_public_access(
                session=session,
                bucket_names=bucket_names,
                account_level=account_level,
                bucket_level=bucket_level,
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