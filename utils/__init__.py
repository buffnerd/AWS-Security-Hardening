"""
Common utility functions for AWS Security Hardening scripts.

This module provides shared functionality used across multiple scripts:
- AWS session management
- Region handling
- Logging configuration
- Error handling
"""

import boto3
import logging
from typing import List, Optional
from botocore.exceptions import ClientError, BotoCoreError


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure logging for security scripts.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, level.upper())
    )
    return logging.getLogger(__name__)


def get_aws_session(profile: Optional[str] = None, region: Optional[str] = None) -> boto3.Session:
    """
    Create an AWS session with optional profile and region.
    
    Args:
        profile: AWS CLI profile name
        region: AWS region name
    
    Returns:
        boto3.Session instance
    """
    return boto3.Session(profile_name=profile, region_name=region)


def get_all_regions(session: boto3.Session, service: str = 'ec2') -> List[str]:
    """
    Get all available AWS regions for a service.
    
    Args:
        session: boto3.Session instance
        service: AWS service name (default: ec2)
    
    Returns:
        List of region names
    """
    ec2_client = session.client('ec2')
    try:
        response = ec2_client.describe_regions()
        return [region['RegionName'] for region in response['Regions']]
    except ClientError as e:
        logging.error(f"Error fetching regions: {e}")
        return []


def get_enabled_regions(session: boto3.Session) -> List[str]:
    """
    Get all enabled AWS regions for the account.
    
    Args:
        session: boto3.Session instance
    
    Returns:
        List of enabled region names
    """
    ec2_client = session.client('ec2')
    try:
        response = ec2_client.describe_regions(AllRegions=False)
        return [region['RegionName'] for region in response['Regions']]
    except ClientError as e:
        logging.error(f"Error fetching enabled regions: {e}")
        return []


def get_account_id(session: boto3.Session) -> Optional[str]:
    """
    Get the AWS account ID for the current session.
    
    Args:
        session: boto3.Session instance
    
    Returns:
        AWS account ID or None if error
    """
    sts_client = session.client('sts')
    try:
        response = sts_client.get_caller_identity()
        return response['Account']
    except ClientError as e:
        logging.error(f"Error getting account ID: {e}")
        return None


def handle_aws_error(error: Exception, context: str = "") -> None:
    """
    Handle AWS API errors with appropriate logging.
    
    Args:
        error: Exception that occurred
        context: Additional context about where the error occurred
    """
    if isinstance(error, ClientError):
        error_code = error.response['Error']['Code']
        error_message = error.response['Error']['Message']
        logging.error(f"{context} - AWS Error [{error_code}]: {error_message}")
    elif isinstance(error, BotoCoreError):
        logging.error(f"{context} - BotoCore Error: {str(error)}")
    else:
        logging.error(f"{context} - Unexpected Error: {str(error)}")


def confirm_action(message: str) -> bool:
    """
    Ask user for confirmation before proceeding with an action.
    
    Args:
        message: Confirmation message to display
    
    Returns:
        True if user confirms, False otherwise
    """
    response = input(f"{message} (yes/no): ").lower().strip()
    return response in ['yes', 'y']
