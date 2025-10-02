"""GuardDuty enablement across all regions."""

from typing import List, Dict
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

CFG = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})

def get_enabled_regions(session) -> List[str]:
    ec2 = session.client("ec2", region_name="us-east-1", config=CFG)
    regions = ec2.describe_regions(AllRegions=True)["Regions"]
    return [r["RegionName"] for r in regions if r.get("OptInStatus") in (None, "opt-in-not-required", "opted-in")]

def enable_guardduty_all_regions() -> Dict[str, bool]:
    """Enable GuardDuty in all enabled regions."""
    session = boto3.Session()
    results = {}
    for region in get_enabled_regions(session):
        gd = session.client("guardduty", region_name=region, config=CFG)
        dets = gd.list_detectors()["DetectorIds"]
        det_id = dets[0] if dets else None
        if not det_id:
            try:
                det_id = gd.create_detector(Enable=True)["DetectorId"]
            except ClientError:
                continue
        else:
            gd.update_detector(DetectorId=det_id, Enable=True)
        results[region] = True
    return results

def check_guardduty_status(regions: List[str]) -> Dict[str, str]:
    """Check GuardDuty status across regions."""
    session = boto3.Session()
    statuses = {}
    for r in regions:
        gd = session.client("guardduty", region_name=r, config=CFG)
        dets = gd.list_detectors()["DetectorIds"]
        statuses[r] = "ENABLED" if dets else "DISABLED"
    return statuses
