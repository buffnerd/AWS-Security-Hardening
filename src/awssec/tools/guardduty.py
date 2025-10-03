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

import logging
from typing import Dict, List, Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from ..sessions import get_session
from ..utils import retry_on_throttle, get_all_regions, print_status

logger = logging.getLogger(__name__)
CFG = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})


@retry_on_throttle(max_retries=3)
def enable_guardduty(
    session: boto3.Session,
    regions: Optional[List[str]] = None,
    dry_run: bool = False
) -> Dict[str, bool]:
    """
    Enable GuardDuty in specified regions.
    
    Args:
        session: Boto3 session
        regions: List of regions to enable GuardDuty in (None for all)
        dry_run: If True, only check status without making changes
        
    Returns:
        Dict mapping regions to success status
    """
    if regions is None:
        regions = get_all_regions(session)
    
    results = {}
    
    for region in regions:
        try:
            guardduty = session.client("guardduty", region_name=region, config=CFG)
            
            # Check existing detectors
            detectors = guardduty.list_detectors()["DetectorIds"]
            
            if detectors:
                # GuardDuty already enabled, ensure it's active
                detector_id = detectors[0]
                detector_info = guardduty.get_detector(DetectorId=detector_id)
                
                if detector_info['Status'] == 'ENABLED':
                    print_status(f"GuardDuty already enabled in {region}", 'SUCCESS', dry_run)
                    results[region] = True
                else:
                    if not dry_run:
                        guardduty.update_detector(DetectorId=detector_id, Enable=True)
                        print_status(f"Enabled existing GuardDuty detector in {region}", 'SUCCESS')
                    else:
                        print_status(f"Would enable existing GuardDuty detector in {region}", 'INFO', dry_run)
                    results[region] = True
            else:
                # Create new detector
                if not dry_run:
                    response = guardduty.create_detector(Enable=True)
                    detector_id = response["DetectorId"]
                    print_status(f"Created GuardDuty detector {detector_id} in {region}", 'SUCCESS')
                else:
                    print_status(f"Would create GuardDuty detector in {region}", 'INFO', dry_run)
                results[region] = True
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UnauthorizedOperation':
                print_status(f"Insufficient permissions for {region}", 'ERROR')
            else:
                print_status(f"Failed to enable GuardDuty in {region}: {e}", 'ERROR')
            results[region] = False
        except Exception as e:
            print_status(f"Unexpected error in {region}: {e}", 'ERROR')
            results[region] = False
    
    return results


@retry_on_throttle(max_retries=3)
def check_guardduty_status(
    session: boto3.Session,
    regions: Optional[List[str]] = None
) -> Dict[str, Dict[str, str]]:
    """
    Check GuardDuty status across regions.
    
    Args:
        session: Boto3 session
        regions: List of regions to check (None for all)
        
    Returns:
        Dict mapping regions to status information
    """
    if regions is None:
        regions = get_all_regions(session)
    
    statuses = {}
    
    for region in regions:
        try:
            guardduty = session.client("guardduty", region_name=region, config=CFG)
            detectors = guardduty.list_detectors()["DetectorIds"]
            
            if detectors:
                detector_id = detectors[0]
                detector_info = guardduty.get_detector(DetectorId=detector_id)
                statuses[region] = {
                    'status': detector_info['Status'],
                    'detector_id': detector_id,
                    'created': detector_info.get('CreatedAt', 'Unknown'),
                    'service_role': detector_info.get('ServiceRole', 'Default')
                }
            else:
                statuses[region] = {
                    'status': 'DISABLED',
                    'detector_id': None,
                    'created': None,
                    'service_role': None
                }
                
        except ClientError as e:
            statuses[region] = {
                'status': 'ERROR',
                'error': str(e),
                'detector_id': None,
                'created': None,
                'service_role': None
            }
        except Exception as e:
            statuses[region] = {
                'status': 'ERROR',
                'error': str(e),
                'detector_id': None,
                'created': None,
                'service_role': None
            }
    
    return statuses


def disable_guardduty(
    session: boto3.Session,
    regions: Optional[List[str]] = None,
    dry_run: bool = False
) -> Dict[str, bool]:
    """
    Disable GuardDuty in specified regions.
    
    Args:
        session: Boto3 session
        regions: List of regions to disable GuardDuty in (None for all)
        dry_run: If True, only show what would be disabled
        
    Returns:
        Dict mapping regions to success status
    """
    if regions is None:
        regions = get_all_regions(session)
    
    results = {}
    
    for region in regions:
        try:
            guardduty = session.client("guardduty", region_name=region, config=CFG)
            detectors = guardduty.list_detectors()["DetectorIds"]
            
            if detectors:
                detector_id = detectors[0]
                if not dry_run:
                    guardduty.delete_detector(DetectorId=detector_id)
                    print_status(f"Disabled GuardDuty detector {detector_id} in {region}", 'SUCCESS')
                else:
                    print_status(f"Would disable GuardDuty detector {detector_id} in {region}", 'WARNING', dry_run)
                results[region] = True
            else:
                print_status(f"GuardDuty already disabled in {region}", 'INFO', dry_run)
                results[region] = True
                
        except ClientError as e:
            print_status(f"Failed to disable GuardDuty in {region}: {e}", 'ERROR')
            results[region] = False
        except Exception as e:
            print_status(f"Unexpected error in {region}: {e}", 'ERROR')
            results[region] = False
    
    return results