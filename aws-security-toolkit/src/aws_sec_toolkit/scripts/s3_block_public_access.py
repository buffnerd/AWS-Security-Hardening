"""S3 block public access enforcement."""

from typing import Dict
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

CFG = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})
ACCOUNT_BPA = {
    "BlockPublicAcls": True,
    "IgnorePublicAcls": True,
    "BlockPublicPolicy": True,
    "RestrictPublicBuckets": True
}

def block_public_access_all_buckets() -> Dict[str, bool]:
    """Block public access for all S3 buckets."""
    session = boto3.Session()
    s3 = session.client("s3", config=CFG)
    s3control = session.client("s3control", config=CFG)
    account_id = session.client("sts").get_caller_identity()["Account"]
    s3control.put_public_access_block(AccountId=account_id, PublicAccessBlockConfiguration=ACCOUNT_BPA)
    for b in s3.list_buckets()["Buckets"]:
        try:
            s3.put_public_access_block(Bucket=b["Name"], PublicAccessBlockConfiguration=ACCOUNT_BPA)
        except ClientError:
            continue
    return {"account": True, "buckets": True}

def check_public_access_status() -> Dict[str, Dict]:
    """Check public access status for all S3 buckets."""
    session = boto3.Session()
    s3 = session.client("s3", config=CFG)
    status = {}
    for b in s3.list_buckets()["Buckets"]:
        try:
            cfg = s3.get_public_access_block(Bucket=b["Name"])["PublicAccessBlockConfiguration"]
            status[b["Name"]] = cfg
        except ClientError:
            status[b["Name"]] = {"error": "No config"}
    return status
