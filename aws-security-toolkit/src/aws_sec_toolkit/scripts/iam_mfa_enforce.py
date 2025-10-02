"""IAM MFA enforcement and reporting."""

from typing import List, Dict
import boto3
from botocore.config import Config

CFG = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})

def generate_no_mfa_report() -> List[Dict]:
    """Generate report of users without MFA."""
    session = boto3.Session()
    iam = session.client("iam", config=CFG)
    report = []
    for user in iam.list_users()["Users"]:
        uname = user["UserName"]
        mfa = iam.list_mfa_devices(UserName=uname)["MFADevices"]
        if not mfa:
            report.append({"User": uname, "HasMFA": False})
    return report

def disable_access_keys_no_mfa() -> Dict[str, bool]:
    """Disable access keys for users without MFA."""
    session = boto3.Session()
    iam = session.client("iam", config=CFG)
    report = generate_no_mfa_report()
    for entry in report:
        uname = entry["User"]
        keys = iam.list_access_keys(UserName=uname)["AccessKeyMetadata"]
        for k in keys:
            if k["Status"] == "Active":
                iam.update_access_key(UserName=uname, AccessKeyId=k["AccessKeyId"], Status="Inactive")
    return {"keys_disabled": True}

def enforce_mfa_requirement() -> Dict[str, bool]:
    """Enforce MFA requirement by disabling keys for users without MFA."""
    disable_access_keys_no_mfa()
    return {"mfa_enforced": True}
