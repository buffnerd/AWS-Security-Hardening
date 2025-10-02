"""Security Hub enablement across all regions."""

from typing import List, Dict
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

CFG = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})

def get_enabled_regions(session) -> List[str]:
    ec2 = session.client("ec2", region_name="us-east-1", config=CFG)
    regions = ec2.describe_regions(AllRegions=True)["Regions"]
    return [r["RegionName"] for r in regions if r.get("OptInStatus") in (None, "opt-in-not-required", "opted-in")]

def enable_securityhub_all_regions() -> Dict[str, bool]:
    """Enable Security Hub in all enabled regions."""
    session = boto3.Session()
    results = {}
    for r in get_enabled_regions(session):
        sh = session.client("securityhub", region_name=r, config=CFG)
        try:
            sh.enable_security_hub()
            results[r] = True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceConflictException":
                results[r] = True
            else:
                results[r] = False
    return results

def check_securityhub_status(regions: List[str]) -> Dict[str, str]:
    """Check Security Hub status across regions."""
    session = boto3.Session()
    statuses = {}
    for r in regions:
        sh = session.client("securityhub", region_name=r, config=CFG)
        try:
            resp = sh.describe_hub()
            statuses[r] = "ENABLED" if resp.get("HubArn") else "DISABLED"
        except ClientError:
            statuses[r] = "DISABLED"
    return statuses
