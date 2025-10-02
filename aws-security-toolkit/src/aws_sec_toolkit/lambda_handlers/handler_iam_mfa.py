"""Lambda handler for IAM MFA operations."""

import json
import logging
from typing import Any, Dict

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for IAM MFA enforcement."""
    try:
        # Import here to avoid cold start issues
        from aws_sec_toolkit.scripts.iam_mfa_enforce import generate_no_mfa_report, disable_access_keys_no_mfa
        
        logger.info("Starting IAM MFA enforcement")
        
        # Generate report first
        report = generate_no_mfa_report()
        logger.info(f"Found {len(report)} users without MFA")
        
        # Disable access keys for non-MFA users if any found
        disable_result = {}
        if report:
            disable_result = disable_access_keys_no_mfa()
            logger.info(f"Access key disable results: {disable_result}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'IAM MFA enforcement completed successfully',
                'no_mfa_users': report,
                'users_without_mfa_count': len(report),
                'access_keys_disabled': disable_result,
                'successful_disables': sum(1 for success in disable_result.values() if success),
                'failed_disables': sum(1 for success in disable_result.values() if not success)
            })
        }
        
    except Exception as e:
        logger.error(f"Error in IAM MFA enforcement: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to enforce IAM MFA'
            })
        }