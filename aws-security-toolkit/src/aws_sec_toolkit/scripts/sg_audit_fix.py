"""Security Group audit and remediation."""

from typing import List, Dict
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

CFG = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})
DEFAULT_PORTS = {22, 3389, 3306, 5432, 6379, 9200, 27017, 25}

def get_enabled_regions(session) -> List[str]:
    ec2 = session.client("ec2", region_name="us-east-1", config=CFG)
    regions = ec2.describe_regions(AllRegions=True)["Regions"]
    return [r["RegionName"] for r in regions if r.get("OptInStatus") in (None, "opt-in-not-required", "opted-in")]

def audit_security_groups() -> Dict[str, List]:
    """Audit security groups for open ports."""
    session = boto3.Session()
    results = {}
    for r in get_enabled_regions(session):
        ec2 = session.client("ec2", region_name=r, config=CFG)
        sgs = ec2.describe_security_groups()["SecurityGroups"]
        risky = []
        for sg in sgs:
            for perm in sg.get("IpPermissions", []):
                if perm.get("IpProtocol") in ("tcp", "udp"):
                    from_p, to_p = perm.get("FromPort"), perm.get("ToPort")
                    if isinstance(from_p, int) and any(from_p <= p <= to_p for p in DEFAULT_PORTS):
                        for rng in perm.get("IpRanges", []):
                            if rng.get("CidrIp") in ("0.0.0.0/0",):
                                risky.append(sg["GroupId"])
        results[r] = risky
    return results

def fix_open_security_groups(dry_run: bool = True) -> Dict[str, bool]:
    """Fix security groups with open ports."""
    session = boto3.Session()
    for r in get_enabled_regions(session):
        ec2 = session.client("ec2", region_name=r, config=CFG)
        sgs = ec2.describe_security_groups()["SecurityGroups"]
        for sg in sgs:
            risky_perms = []
            for perm in sg.get("IpPermissions", []):
                if perm.get("IpProtocol") in ("tcp", "udp"):
                    from_p, to_p = perm.get("FromPort"), perm.get("ToPort")
                    if isinstance(from_p, int) and any(from_p <= p <= to_p for p in DEFAULT_PORTS):
                        for rng in perm.get("IpRanges", []):
                            if rng.get("CidrIp") == "0.0.0.0/0":
                                risky_perms.append(perm)
            if risky_perms and not dry_run:
                try:
                    ec2.revoke_security_group_ingress(GroupId=sg["GroupId"], IpPermissions=risky_perms)
                except ClientError:
                    continue
    return {"remediation_run": True}
