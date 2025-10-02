"""CloudTrail enablement and configuration."""

from typing import Dict
import boto3, json, uuid
from botocore.config import Config
from botocore.exceptions import ClientError

CFG = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})
TRAIL_NAME = "org-secure-trail"

def ensure_bucket(session, bucket_name: str) -> str:
    """Ensure secure S3 bucket for CloudTrail logs (private, encrypted, policy applied)."""
    s3 = session.client("s3", region_name="us-east-1", config=CFG)

    if not bucket_name:
        account_id = session.client("sts", config=CFG).get_caller_identity()["Account"]
        bucket_name = f"cloudtrail-logs-{account_id}-{uuid.uuid4().hex[:8]}"
        s3.create_bucket(Bucket=bucket_name)

    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        }
    )

    s3.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
        }
    )

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AWSCloudTrailAclCheck20150319",
                "Effect": "Allow",
                "Principal": {"Service": "cloudtrail.amazonaws.com"},
                "Action": "s3:GetBucketAcl",
                "Resource": f"arn:aws:s3:::{bucket_name}"
            },
            {
                "Sid": "AWSCloudTrailWrite20150319",
                "Effect": "Allow",
                "Principal": {"Service": "cloudtrail.amazonaws.com"},
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/AWSLogs/*",
                "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
            }
        ]
    }
    s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
    return bucket_name

def enable_cloudtrail_multiregion(bucket: str = None) -> Dict[str, bool]:
    """Enable CloudTrail across all regions with validation and global events."""
    session = boto3.Session()
    ct = session.client("cloudtrail", region_name="us-east-1", config=CFG)
    bucket_name = ensure_bucket(session, bucket)

    trails = ct.describe_trails(includeShadowTrails=False)["trailList"]
    trail = next((t for t in trails if t["Name"] == TRAIL_NAME), None)

    if not trail:
        ct.create_trail(
            Name=TRAIL_NAME,
            S3BucketName=bucket_name,
            IsMultiRegionTrail=True,
            EnableLogFileValidation=True,
            IncludeGlobalServiceEvents=True
        )
    else:
        ct.update_trail(
            Name=TRAIL_NAME,
            S3BucketName=bucket_name,
            IsMultiRegionTrail=True,
            EnableLogFileValidation=True,
            IncludeGlobalServiceEvents=True
        )
    ct.start_logging(Name=TRAIL_NAME)
    return {"trail_enabled": True, "bucket": bucket_name}

def check_cloudtrail_status() -> Dict[str, str]:
    """Check CloudTrail status across regions."""
    session = boto3.Session()
    ct = session.client("cloudtrail", region_name="us-east-1", config=CFG)
    status = ct.get_trail_status(Name=TRAIL_NAME)
    return {"IsLogging": str(status.get("IsLogging", False))}
