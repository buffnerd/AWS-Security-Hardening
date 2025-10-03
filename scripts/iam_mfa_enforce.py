#!/usr/bin/env python3
"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Report/enforce MFA; optionally disable access keys lacking MFA.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from awssec.sessions import get_session
from awssec.tools.iam_mfa import generate_mfa_report, enforce_mfa_policy, disable_access_keys_without_mfa
from awssec.utils import setup_logger, format_output, print_status


def main():
    parser = argparse.ArgumentParser(description='Enforce IAM MFA requirements')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    parser.add_argument('--report-only', action='store_true', help='Only generate MFA compliance report')
    parser.add_argument('--disable-keys', action='store_true', help='Disable access keys for users without MFA')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--output', choices=['table', 'json', 'csv'], default='table')
    
    args = parser.parse_args()
    logger = setup_logger('iam_mfa_enforce', 'INFO')
    
    try:
        session = get_session(profile=args.profile)
        
        if args.report_only:
            result = generate_mfa_report(session=session, output_format=args.output)
            print(result)
        else:
            result = enforce_mfa_policy(
                session=session,
                disable_keys=args.disable_keys,
                dry_run=not args.apply
            )
            print(format_output(result, args.output))
        
    except Exception as e:
        print_status(f"Error: {e}", 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()