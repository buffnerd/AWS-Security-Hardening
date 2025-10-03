"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
AWS session management with profile switching and role assumption.
"""

import boto3
from typing import Optional
import logging
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

logger = logging.getLogger(__name__)


def get_session(
    profile: Optional[str] = None,
    region: Optional[str] = None,
    assume_role_arn: Optional[str] = None
) -> boto3.Session:
    """
    Create a boto3 session with optional profile, region, and role assumption.
    
    Args:
        profile: AWS profile name to use
        region: AWS region to target
        assume_role_arn: IAM role ARN to assume
        
    Returns:
        Configured boto3.Session
        
    Raises:
        ProfileNotFound: If the specified profile doesn't exist
        NoCredentialsError: If no valid credentials are found
        ClientError: If role assumption fails
    """
    try:
        # Create base session with profile and region
        session = boto3.Session(profile_name=profile, region_name=region)
        
        # If no role assumption needed, return session as-is
        if not assume_role_arn:
            return session
            
        # Assume role if ARN provided
        logger.info(f"Assuming role: {assume_role_arn}")
        sts_client = session.client('sts')
        
        assumed_role = sts_client.assume_role(
            RoleArn=assume_role_arn,
            RoleSessionName=f"awssec-{session.profile_name or 'default'}"
        )
        
        credentials = assumed_role['Credentials']
        
        # Create new session with assumed role credentials
        return boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=region
        )
        
    except ProfileNotFound as e:
        logger.error(f"AWS profile '{profile}' not found")
        raise
    except NoCredentialsError as e:
        logger.error("No AWS credentials found. Please configure credentials.")
        raise
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            logger.error(f"Access denied when assuming role {assume_role_arn}")
        else:
            logger.error(f"Error assuming role: {e}")
        raise


def get_current_identity(session: boto3.Session) -> dict:
    """Get current AWS identity information."""
    try:
        sts = session.client('sts')
        return sts.get_caller_identity()
    except Exception as e:
        logger.error(f"Failed to get caller identity: {e}")
        raise


def get_available_regions(session: boto3.Session, service: str = 'ec2') -> list:
    """Get list of available regions for a service."""
    try:
        client = session.client(service)
        response = client.describe_regions()
        return [region['RegionName'] for region in response['Regions']]
    except Exception as e:
        logger.error(f"Failed to get regions: {e}")
        return []