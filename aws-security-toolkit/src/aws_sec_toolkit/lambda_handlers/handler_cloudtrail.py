"""Lambda handler for CloudTrail operations."""

import json
import logging
from typing import Any, Dict

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for CloudTrail enablement."""
    try:
        # Import here to avoid cold start issues
        from aws_sec_toolkit.scripts.cloudtrail_enable import enable_cloudtrail_multiregion
        
        logger.info("Starting CloudTrail enablement across all regions")
        
        # Extract bucket name from event if provided
        bucket_name = event.get('bucket_name')
        
        result = enable_cloudtrail_multiregion(bucket_name=bucket_name)
        
        logger.info(f"CloudTrail enablement completed. Results: {result}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'CloudTrail enablement completed successfully',
                'results': result,
                'total_regions': len(result),
                'successful_regions': sum(1 for success in result.values() if success),
                'failed_regions': sum(1 for success in result.values() if not success)
            })
        }
        
    except Exception as e:
        logger.error(f"Error in CloudTrail enablement: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to enable CloudTrail'
            })
        }