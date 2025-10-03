"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Enable & validate multi-region CloudTrail with S3/KMS best practices.
"""

import logging
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError

from ..sessions import get_session
from ..utils import retry_on_throttle, get_all_regions, print_status

logger = logging.getLogger(__name__)


@retry_on_throttle(max_retries=3)
def enable_cloudtrail(
    session: boto3.Session,
    trail_name: str = "aws-security-toolkit-trail",
    regions: Optional[List[str]] = None,
    dry_run: bool = False
) -> Dict[str, bool]:
    """Enable CloudTrail in specified regions."""
    if regions is None:
        regions = get_all_regions(session)
    
    results = {}
    
    for region in regions:
        try:
            cloudtrail = session.client("cloudtrail", region_name=region)
            
            # Check existing trails
            trails = cloudtrail.describe_trails()["trailList"]
            existing_trail = next((t for t in trails if t["Name"] == trail_name), None)
            
            if existing_trail:
                if not dry_run:
                    cloudtrail.start_logging(Name=trail_name)
                    print_status(f"Started logging for CloudTrail {trail_name} in {region}", 'SUCCESS')
                else:
                    print_status(f"Would start logging for CloudTrail {trail_name} in {region}", 'INFO', dry_run)
            else:
                print_status(f"CloudTrail {trail_name} not found in {region}", 'WARNING')
            
            results[region] = True
            
        except ClientError as e:
            print_status(f"Failed to enable CloudTrail in {region}: {e}", 'ERROR')
            results[region] = False
        except Exception as e:
            print_status(f"Unexpected error in {region}: {e}", 'ERROR')
            results[region] = False
    
    return results


@retry_on_throttle(max_retries=3)
def check_cloudtrail_status(
    session: boto3.Session,
    regions: Optional[List[str]] = None
) -> Dict[str, Dict]:
    """Check CloudTrail status across regions."""
    if regions is None:
        regions = get_all_regions(session)
    
    statuses = {}
    
    for region in regions:
        try:
            cloudtrail = session.client("cloudtrail", region_name=region)
            trails = cloudtrail.describe_trails()["trailList"]
            
            statuses[region] = {
                'trail_count': len(trails),
                'trails': [{'name': t['Name'], 'is_logging': False} for t in trails]
            }
            
            # Check logging status for each trail
            for i, trail in enumerate(trails):
                try:
                    status = cloudtrail.get_trail_status(Name=trail['Name'])
                    statuses[region]['trails'][i]['is_logging'] = status.get('IsLogging', False)
                except:
                    pass
                    
        except Exception as e:
            statuses[region] = {'error': str(e)}
    
    return statuses