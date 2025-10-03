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

import logging
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError

from ..sessions import get_session
from ..utils import retry_on_throttle, get_all_regions, print_status

logger = logging.getLogger(__name__)


@retry_on_throttle(max_retries=3)
def enable_security_hub(
    session: boto3.Session,
    regions: Optional[List[str]] = None,
    dry_run: bool = False
) -> Dict[str, bool]:
    """Enable Security Hub in specified regions."""
    if regions is None:
        regions = get_all_regions(session)
    
    results = {}
    
    for region in regions:
        try:
            securityhub = session.client("securityhub", region_name=region)
            
            # Check if Security Hub is already enabled
            try:
                securityhub.describe_hub()
                print_status(f"Security Hub already enabled in {region}", 'SUCCESS', dry_run)
                results[region] = True
            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidAccessException':
                    # Security Hub not enabled, enable it
                    if not dry_run:
                        securityhub.enable_security_hub()
                        print_status(f"Enabled Security Hub in {region}", 'SUCCESS')
                    else:
                        print_status(f"Would enable Security Hub in {region}", 'INFO', dry_run)
                    results[region] = True
                else:
                    raise
            
        except ClientError as e:
            print_status(f"Failed to enable Security Hub in {region}: {e}", 'ERROR')
            results[region] = False
        except Exception as e:
            print_status(f"Unexpected error in {region}: {e}", 'ERROR')
            results[region] = False
    
    return results


@retry_on_throttle(max_retries=3)
def check_security_hub_status(
    session: boto3.Session,
    regions: Optional[List[str]] = None
) -> Dict[str, Dict]:
    """Check Security Hub status across regions."""
    if regions is None:
        regions = get_all_regions(session)
    
    statuses = {}
    
    for region in regions:
        try:
            securityhub = session.client("securityhub", region_name=region)
            
            try:
                hub_info = securityhub.describe_hub()
                standards = securityhub.get_enabled_standards()
                
                statuses[region] = {
                    'status': 'ENABLED',
                    'hub_arn': hub_info.get('HubArn'),
                    'auto_enable_controls': hub_info.get('AutoEnableControls', False),
                    'standards_count': len(standards.get('StandardsSubscriptions', []))
                }
            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidAccessException':
                    statuses[region] = {'status': 'DISABLED'}
                else:
                    statuses[region] = {'status': 'ERROR', 'error': str(e)}
                    
        except Exception as e:
            statuses[region] = {'status': 'ERROR', 'error': str(e)}
    
    return statuses