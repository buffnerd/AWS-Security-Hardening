"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Enforce and verify S3 Block Public Access at account & bucket level.
"""

import logging
from typing import Dict, List, Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from ..sessions import get_session
from ..utils import retry_on_throttle, print_status

logger = logging.getLogger(__name__)
CFG = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})

BLOCK_PUBLIC_ACCESS_CONFIG = {
    "BlockPublicAcls": True,
    "IgnorePublicAcls": True,
    "BlockPublicPolicy": True,
    "RestrictPublicBuckets": True
}


@retry_on_throttle(max_retries=3)
def enforce_account_block_public_access(
    session: boto3.Session,
    dry_run: bool = False
) -> bool:
    """
    Enable S3 Block Public Access at the account level.
    
    Args:
        session: Boto3 session
        dry_run: If True, only check status without making changes
        
    Returns:
        True if successful, False otherwise
    """
    try:
        s3control = session.client("s3control", config=CFG)
        sts = session.client("sts")
        account_id = sts.get_caller_identity()["Account"]
        
        if not dry_run:
            s3control.put_public_access_block(
                AccountId=account_id,
                PublicAccessBlockConfiguration=BLOCK_PUBLIC_ACCESS_CONFIG
            )
            print_status(f"Enabled account-level S3 Block Public Access for account {account_id}", 'SUCCESS')
        else:
            print_status(f"Would enable account-level S3 Block Public Access for account {account_id}", 'INFO', dry_run)
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print_status("Insufficient permissions for account-level S3 Block Public Access", 'ERROR')
        else:
            print_status(f"Failed to set account-level S3 Block Public Access: {e}", 'ERROR')
        return False
    except Exception as e:
        print_status(f"Unexpected error setting account-level S3 Block Public Access: {e}", 'ERROR')
        return False


@retry_on_throttle(max_retries=3)
def enforce_bucket_block_public_access(
    session: boto3.Session,
    bucket_names: Optional[List[str]] = None,
    dry_run: bool = False
) -> Dict[str, bool]:
    """
    Enable S3 Block Public Access for specific buckets or all buckets.
    
    Args:
        session: Boto3 session
        bucket_names: List of bucket names (None for all buckets)
        dry_run: If True, only check status without making changes
        
    Returns:
        Dict mapping bucket names to success status
    """
    s3 = session.client("s3", config=CFG)
    results = {}
    
    try:
        # Get bucket list if not provided
        if bucket_names is None:
            buckets_response = s3.list_buckets()
            bucket_names = [bucket['Name'] for bucket in buckets_response['Buckets']]
        
        if not bucket_names:
            print_status("No S3 buckets found", 'INFO')
            return results
        
        for bucket_name in bucket_names:
            try:
                if not dry_run:
                    s3.put_public_access_block(
                        Bucket=bucket_name,
                        PublicAccessBlockConfiguration=BLOCK_PUBLIC_ACCESS_CONFIG
                    )
                    print_status(f"Enabled Block Public Access for bucket: {bucket_name}", 'SUCCESS')
                else:
                    print_status(f"Would enable Block Public Access for bucket: {bucket_name}", 'INFO', dry_run)
                
                results[bucket_name] = True
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchBucket':
                    print_status(f"Bucket {bucket_name} does not exist", 'WARNING')
                elif error_code == 'AccessDenied':
                    print_status(f"Access denied for bucket {bucket_name}", 'ERROR')
                else:
                    print_status(f"Failed to set Block Public Access for {bucket_name}: {e}", 'ERROR')
                results[bucket_name] = False
            except Exception as e:
                print_status(f"Unexpected error for bucket {bucket_name}: {e}", 'ERROR')
                results[bucket_name] = False
        
    except ClientError as e:
        print_status(f"Failed to list S3 buckets: {e}", 'ERROR')
    except Exception as e:
        print_status(f"Unexpected error listing buckets: {e}", 'ERROR')
    
    return results


@retry_on_throttle(max_retries=3)
def check_account_block_public_access_status(session: boto3.Session) -> Dict[str, any]:
    """
    Check account-level S3 Block Public Access status.
    
    Args:
        session: Boto3 session
        
    Returns:
        Dict with status information
    """
    try:
        s3control = session.client("s3control", config=CFG)
        sts = session.client("sts")
        account_id = sts.get_caller_identity()["Account"]
        
        response = s3control.get_public_access_block(AccountId=account_id)
        config = response['PublicAccessBlockConfiguration']
        
        return {
            'account_id': account_id,
            'block_public_acls': config.get('BlockPublicAcls', False),
            'ignore_public_acls': config.get('IgnorePublicAcls', False),
            'block_public_policy': config.get('BlockPublicPolicy', False),
            'restrict_public_buckets': config.get('RestrictPublicBuckets', False),
            'fully_configured': all([
                config.get('BlockPublicAcls', False),
                config.get('IgnorePublicAcls', False),
                config.get('BlockPublicPolicy', False),
                config.get('RestrictPublicBuckets', False)
            ])
        }
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
            return {
                'account_id': account_id,
                'block_public_acls': False,
                'ignore_public_acls': False,
                'block_public_policy': False,
                'restrict_public_buckets': False,
                'fully_configured': False,
                'error': 'No configuration set'
            }
        else:
            return {'error': str(e)}
    except Exception as e:
        return {'error': str(e)}


@retry_on_throttle(max_retries=3)
def check_bucket_block_public_access_status(
    session: boto3.Session,
    bucket_names: Optional[List[str]] = None
) -> Dict[str, Dict]:
    """
    Check bucket-level S3 Block Public Access status.
    
    Args:
        session: Boto3 session
        bucket_names: List of bucket names (None for all buckets)
        
    Returns:
        Dict mapping bucket names to status information
    """
    s3 = session.client("s3", config=CFG)
    results = {}
    
    try:
        # Get bucket list if not provided
        if bucket_names is None:
            buckets_response = s3.list_buckets()
            bucket_names = [bucket['Name'] for bucket in buckets_response['Buckets']]
        
        for bucket_name in bucket_names:
            try:
                response = s3.get_public_access_block(Bucket=bucket_name)
                config = response['PublicAccessBlockConfiguration']
                
                results[bucket_name] = {
                    'block_public_acls': config.get('BlockPublicAcls', False),
                    'ignore_public_acls': config.get('IgnorePublicAcls', False),
                    'block_public_policy': config.get('BlockPublicPolicy', False),
                    'restrict_public_buckets': config.get('RestrictPublicBuckets', False),
                    'fully_configured': all([
                        config.get('BlockPublicAcls', False),
                        config.get('IgnorePublicAcls', False),
                        config.get('BlockPublicPolicy', False),
                        config.get('RestrictPublicBuckets', False)
                    ])
                }
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                    results[bucket_name] = {
                        'block_public_acls': False,
                        'ignore_public_acls': False,
                        'block_public_policy': False,
                        'restrict_public_buckets': False,
                        'fully_configured': False,
                        'error': 'No configuration set'
                    }
                else:
                    results[bucket_name] = {'error': str(e)}
            except Exception as e:
                results[bucket_name] = {'error': str(e)}
        
    except ClientError as e:
        print_status(f"Failed to list S3 buckets: {e}", 'ERROR')
    except Exception as e:
        print_status(f"Unexpected error listing buckets: {e}", 'ERROR')
    
    return results


def enforce_s3_block_public_access(
    session: boto3.Session,
    bucket_names: Optional[List[str]] = None,
    account_level: bool = True,
    bucket_level: bool = True,
    dry_run: bool = False
) -> Dict[str, any]:
    """
    Comprehensive S3 Block Public Access enforcement.
    
    Args:
        session: Boto3 session
        bucket_names: List of bucket names (None for all buckets)
        account_level: Whether to enforce at account level
        bucket_level: Whether to enforce at bucket level
        dry_run: If True, only check status without making changes
        
    Returns:
        Dict with results for account and bucket operations
    """
    results = {}
    
    if account_level:
        results['account'] = enforce_account_block_public_access(session, dry_run)
    
    if bucket_level:
        results['buckets'] = enforce_bucket_block_public_access(session, bucket_names, dry_run)
    
    return results