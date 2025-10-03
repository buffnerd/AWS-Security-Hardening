"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Unified CLI for AWS security hardening toolkit.
"""

import argparse
import sys
import logging
from typing import Optional

from .sessions import get_session
from .utils import setup_logger, format_output, print_status
from .tools import (
    cloudtrail, guardduty, securityhub, s3_bpa, iam_mfa, sg_audit
)


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog='awssec',
        description='AWS Security Hardening Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  awssec guardduty enable --dry-run
  awssec s3-bpa enforce --profile prod
  awssec iam-mfa report --output json
  awssec sg audit --regions us-east-1,us-west-2
        """
    )
    
    # Global arguments
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--region', help='AWS region to target')
    parser.add_argument('--assume-role-arn', help='IAM role ARN to assume')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--output', choices=['table', 'json', 'csv'], default='table', help='Output format')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='Log level')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='service', help='Security service to manage')
    
    # CloudTrail subcommand
    ct_parser = subparsers.add_parser('cloudtrail', help='CloudTrail management')
    ct_subparsers = ct_parser.add_subparsers(dest='action', help='CloudTrail actions')
    
    ct_enable = ct_subparsers.add_parser('enable', help='Enable CloudTrail')
    ct_enable.add_argument('--trail-name', default='aws-security-toolkit-trail', help='Trail name')
    ct_enable.add_argument('--regions', help='Comma-separated list of regions')
    
    ct_status = ct_subparsers.add_parser('status', help='Check CloudTrail status')
    ct_status.add_argument('--regions', help='Comma-separated list of regions')
    
    # GuardDuty subcommand
    gd_parser = subparsers.add_parser('guardduty', help='GuardDuty management')
    gd_subparsers = gd_parser.add_subparsers(dest='action', help='GuardDuty actions')
    
    gd_enable = gd_subparsers.add_parser('enable', help='Enable GuardDuty')
    gd_enable.add_argument('--regions', help='Comma-separated list of regions')
    
    gd_status = gd_subparsers.add_parser('status', help='Check GuardDuty status')
    gd_status.add_argument('--regions', help='Comma-separated list of regions')
    
    # Security Hub subcommand
    sh_parser = subparsers.add_parser('securityhub', help='Security Hub management')
    sh_subparsers = sh_parser.add_subparsers(dest='action', help='Security Hub actions')
    
    sh_enable = sh_subparsers.add_parser('enable', help='Enable Security Hub')
    sh_enable.add_argument('--regions', help='Comma-separated list of regions')
    
    sh_status = sh_subparsers.add_parser('status', help='Check Security Hub status')
    sh_status.add_argument('--regions', help='Comma-separated list of regions')
    
    # S3 Block Public Access subcommand
    s3_parser = subparsers.add_parser('s3-bpa', help='S3 Block Public Access management')
    s3_subparsers = s3_parser.add_subparsers(dest='action', help='S3 BPA actions')
    
    s3_enforce = s3_subparsers.add_parser('enforce', help='Enforce S3 Block Public Access')
    s3_enforce.add_argument('--buckets', help='Comma-separated list of bucket names (default: all)')
    s3_enforce.add_argument('--account-level', action='store_true', default=True, help='Apply at account level')
    s3_enforce.add_argument('--bucket-level', action='store_true', default=True, help='Apply at bucket level')
    
    s3_status = s3_subparsers.add_parser('status', help='Check S3 Block Public Access status')
    s3_status.add_argument('--buckets', help='Comma-separated list of bucket names (default: all)')
    
    # IAM MFA subcommand
    iam_parser = subparsers.add_parser('iam-mfa', help='IAM MFA management')
    iam_subparsers = iam_parser.add_subparsers(dest='action', help='IAM MFA actions')
    
    iam_report = iam_subparsers.add_parser('report', help='Generate MFA compliance report')
    
    iam_enforce = iam_subparsers.add_parser('enforce', help='Enforce MFA requirements')
    iam_enforce.add_argument('--disable-keys', action='store_true', help='Disable access keys for users without MFA')
    
    iam_disable_keys = iam_subparsers.add_parser('disable-keys', help='Disable access keys for users without MFA')
    
    # Security Group audit subcommand
    sg_parser = subparsers.add_parser('sg', help='Security Group management')
    sg_subparsers = sg_parser.add_subparsers(dest='action', help='Security Group actions')
    
    sg_audit = sg_subparsers.add_parser('audit', help='Audit security groups for risky rules')
    sg_audit.add_argument('--regions', help='Comma-separated list of regions')
    sg_audit.add_argument('--ports', help='Comma-separated list of risky ports to check')
    
    sg_fix = sg_subparsers.add_parser('fix', help='Fix risky security group rules')
    sg_fix.add_argument('--regions', help='Comma-separated list of regions')
    sg_fix.add_argument('--ports', help='Comma-separated list of risky ports to check')
    sg_fix.add_argument('--replacement-cidrs', help='Comma-separated list of replacement CIDRs')
    
    return parser


def parse_regions(regions_str: Optional[str]) -> Optional[list]:
    """Parse comma-separated regions string."""
    if regions_str:
        return [r.strip() for r in regions_str.split(',')]
    return None


def parse_ports(ports_str: Optional[str]) -> Optional[list]:
    """Parse comma-separated ports string."""
    if ports_str:
        return [int(p.strip()) for p in ports_str.split(',')]
    return None


def parse_buckets(buckets_str: Optional[str]) -> Optional[list]:
    """Parse comma-separated buckets string."""
    if buckets_str:
        return [b.strip() for b in buckets_str.split(',')]
    return None


def handle_cloudtrail(args, session):
    """Handle CloudTrail subcommands."""
    regions = parse_regions(args.regions)
    
    if args.action == 'enable':
        result = cloudtrail.enable_cloudtrail(
            session=session,
            trail_name=args.trail_name,
            regions=regions,
            dry_run=args.dry_run
        )
    elif args.action == 'status':
        result = cloudtrail.check_cloudtrail_status(session=session, regions=regions)
    else:
        print_status("Invalid CloudTrail action", 'ERROR')
        return False
    
    print(format_output(result, args.output))
    return True


def handle_guardduty(args, session):
    """Handle GuardDuty subcommands."""
    regions = parse_regions(args.regions)
    
    if args.action == 'enable':
        result = guardduty.enable_guardduty(
            session=session,
            regions=regions,
            dry_run=args.dry_run
        )
    elif args.action == 'status':
        result = guardduty.check_guardduty_status(session=session, regions=regions)
    else:
        print_status("Invalid GuardDuty action", 'ERROR')
        return False
    
    print(format_output(result, args.output))
    return True


def handle_securityhub(args, session):
    """Handle Security Hub subcommands."""
    regions = parse_regions(args.regions)
    
    if args.action == 'enable':
        result = securityhub.enable_security_hub(
            session=session,
            regions=regions,
            dry_run=args.dry_run
        )
    elif args.action == 'status':
        result = securityhub.check_security_hub_status(session=session, regions=regions)
    else:
        print_status("Invalid Security Hub action", 'ERROR')
        return False
    
    print(format_output(result, args.output))
    return True


def handle_s3_bpa(args, session):
    """Handle S3 Block Public Access subcommands."""
    buckets = parse_buckets(args.buckets) if hasattr(args, 'buckets') else None
    
    if args.action == 'enforce':
        result = s3_bpa.enforce_s3_block_public_access(
            session=session,
            bucket_names=buckets,
            account_level=getattr(args, 'account_level', True),
            bucket_level=getattr(args, 'bucket_level', True),
            dry_run=args.dry_run
        )
    elif args.action == 'status':
        account_status = s3_bpa.check_account_block_public_access_status(session)
        bucket_status = s3_bpa.check_bucket_block_public_access_status(session, buckets)
        result = {'account': account_status, 'buckets': bucket_status}
    else:
        print_status("Invalid S3 BPA action", 'ERROR')
        return False
    
    print(format_output(result, args.output))
    return True


def handle_iam_mfa(args, session):
    """Handle IAM MFA subcommands."""
    if args.action == 'report':
        result = iam_mfa.generate_mfa_report(session=session, output_format=args.output)
        print(result)
    elif args.action == 'enforce':
        result = iam_mfa.enforce_mfa_policy(
            session=session,
            disable_keys=getattr(args, 'disable_keys', False),
            dry_run=args.dry_run
        )
        print(format_output(result, args.output))
    elif args.action == 'disable-keys':
        result = iam_mfa.disable_access_keys_without_mfa(session=session, dry_run=args.dry_run)
        print(format_output(result, args.output))
    else:
        print_status("Invalid IAM MFA action", 'ERROR')
        return False
    
    return True


def handle_sg(args, session):
    """Handle Security Group subcommands."""
    regions = parse_regions(args.regions)
    ports = parse_ports(getattr(args, 'ports', None))
    
    if args.action == 'audit':
        result = sg_audit.audit_security_groups(
            session=session,
            regions=regions,
            risky_ports=ports
        )
    elif args.action == 'fix':
        replacement_cidrs = None
        if hasattr(args, 'replacement_cidrs') and args.replacement_cidrs:
            replacement_cidrs = [c.strip() for c in args.replacement_cidrs.split(',')]
        
        result = sg_audit.audit_and_fix_security_groups(
            session=session,
            regions=regions,
            risky_ports=ports,
            fix_rules=True,
            replacement_cidrs=replacement_cidrs,
            dry_run=args.dry_run
        )
    else:
        print_status("Invalid Security Group action", 'ERROR')
        return False
    
    print(format_output(result, args.output))
    return True


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger('awssec', args.log_level)
    
    # Check if service was provided
    if not args.service:
        parser.print_help()
        sys.exit(1)
    
    # Check if action was provided for services that require it
    if hasattr(args, 'action') and not args.action:
        print_status(f"Action required for {args.service}", 'ERROR')
        sys.exit(1)
    
    try:
        # Get AWS session
        session = get_session(
            profile=args.profile,
            region=args.region,
            assume_role_arn=args.assume_role_arn
        )
        
        # Route to appropriate handler
        handlers = {
            'cloudtrail': handle_cloudtrail,
            'guardduty': handle_guardduty,
            'securityhub': handle_securityhub,
            's3-bpa': handle_s3_bpa,
            'iam-mfa': handle_iam_mfa,
            'sg': handle_sg
        }
        
        handler = handlers.get(args.service)
        if not handler:
            print_status(f"Unknown service: {args.service}", 'ERROR')
            sys.exit(1)
        
        success = handler(args, session)
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print_status("Operation cancelled by user", 'WARNING')
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print_status(f"Unexpected error: {e}", 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()