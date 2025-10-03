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

import logging
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError
import csv
import io

from ..sessions import get_session
from ..utils import retry_on_throttle, print_status

logger = logging.getLogger(__name__)


@retry_on_throttle(max_retries=3)
def get_users_without_mfa(session: boto3.Session) -> List[Dict]:
    """Get list of IAM users without MFA enabled."""
    iam = session.client("iam")
    users_without_mfa = []
    
    try:
        paginator = iam.get_paginator('list_users')
        
        for page in paginator.paginate():
            for user in page['Users']:
                username = user['UserName']
                
                # Check MFA devices
                mfa_devices = iam.list_mfa_devices(UserName=username)
                virtual_mfa = iam.list_virtual_mfa_devices()
                
                has_mfa = (
                    len(mfa_devices['MFADevices']) > 0 or
                    any(device.get('User', {}).get('UserName') == username 
                        for device in virtual_mfa['VirtualMFADevices'])
                )
                
                if not has_mfa:
                    # Get access keys
                    access_keys = iam.list_access_keys(UserName=username)
                    
                    users_without_mfa.append({
                        'username': username,
                        'created': user['CreateDate'].isoformat(),
                        'last_used': user.get('PasswordLastUsed', 'Never').isoformat() if user.get('PasswordLastUsed') else 'Never',
                        'access_keys': len(access_keys['AccessKeyMetadata']),
                        'console_access': 'PasswordLastUsed' in user
                    })
    
    except ClientError as e:
        print_status(f"Failed to list IAM users: {e}", 'ERROR')
    except Exception as e:
        print_status(f"Unexpected error: {e}", 'ERROR')
    
    return users_without_mfa


@retry_on_throttle(max_retries=3)
def generate_mfa_report(session: boto3.Session, output_format: str = 'table') -> str:
    """Generate MFA compliance report."""
    users_without_mfa = get_users_without_mfa(session)
    
    if not users_without_mfa:
        return "All users have MFA enabled!"
    
    if output_format == 'csv':
        output = io.StringIO()
        fieldnames = ['username', 'created', 'last_used', 'access_keys', 'console_access']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users_without_mfa)
        return output.getvalue()
    
    elif output_format == 'json':
        import json
        return json.dumps(users_without_mfa, indent=2)
    
    else:  # table format
        if not users_without_mfa:
            return "No users without MFA found."
        
        # Simple table formatting
        lines = []
        lines.append("Users without MFA:")
        lines.append("-" * 80)
        lines.append(f"{'Username':<20} {'Created':<12} {'Last Used':<12} {'Keys':<5} {'Console':<8}")
        lines.append("-" * 80)
        
        for user in users_without_mfa:
            lines.append(
                f"{user['username']:<20} "
                f"{user['created'][:10]:<12} "
                f"{user['last_used'][:10]:<12} "
                f"{user['access_keys']:<5} "
                f"{str(user['console_access']):<8}"
            )
        
        return "\n".join(lines)


@retry_on_throttle(max_retries=3)
def disable_access_keys_without_mfa(
    session: boto3.Session,
    dry_run: bool = False
) -> Dict[str, bool]:
    """Disable access keys for users without MFA."""
    iam = session.client("iam")
    results = {}
    
    users_without_mfa = get_users_without_mfa(session)
    
    for user_info in users_without_mfa:
        username = user_info['username']
        
        if user_info['access_keys'] == 0:
            continue  # No access keys to disable
        
        try:
            access_keys = iam.list_access_keys(UserName=username)
            
            for key_metadata in access_keys['AccessKeyMetadata']:
                access_key_id = key_metadata['AccessKeyId']
                status = key_metadata['Status']
                
                if status == 'Active':
                    if not dry_run:
                        iam.update_access_key(
                            UserName=username,
                            AccessKeyId=access_key_id,
                            Status='Inactive'
                        )
                        print_status(f"Disabled access key {access_key_id} for user {username}", 'SUCCESS')
                    else:
                        print_status(f"Would disable access key {access_key_id} for user {username}", 'WARNING', dry_run)
                    
                    results[f"{username}:{access_key_id}"] = True
                else:
                    print_status(f"Access key {access_key_id} for user {username} already inactive", 'INFO')
        
        except ClientError as e:
            print_status(f"Failed to disable access keys for user {username}: {e}", 'ERROR')
            results[username] = False
        except Exception as e:
            print_status(f"Unexpected error for user {username}: {e}", 'ERROR')
            results[username] = False
    
    return results


def enforce_mfa_policy(
    session: boto3.Session,
    disable_keys: bool = False,
    dry_run: bool = False
) -> Dict[str, any]:
    """Comprehensive MFA enforcement."""
    results = {}
    
    # Generate report
    users_without_mfa = get_users_without_mfa(session)
    results['users_without_mfa'] = len(users_without_mfa)
    results['users_list'] = users_without_mfa
    
    # Optionally disable access keys
    if disable_keys:
        results['disabled_keys'] = disable_access_keys_without_mfa(session, dry_run)
    
    return results