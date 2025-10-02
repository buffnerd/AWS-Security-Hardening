"""Lambda handler for S3 Block Public Access operations."""

import json
import logging
from typing import Any, Dict

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for S3 BPA enforcement."""
    try:
        # Import here to avoid cold start issues
        from aws_sec_toolkit.scripts.s3_block_public_access import block_public_access_all_buckets
        
        logger.info("Starting S3 Block Public Access enforcement")
        
        result = block_public_access_all_buckets()
        
        logger.info(f"S3 BPA enforcement completed. Results: {result}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'S3 Block Public Access enforcement completed successfully',
                'results': result,
                'total_buckets': len(result),
                'successful_buckets': sum(1 for success in result.values() if success),
                'failed_buckets': sum(1 for success in result.values() if not success)
            })
        }
        
    except Exception as e:
        logger.error(f"Error in S3 BPA enforcement: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to enforce S3 Block Public Access'
            })
        }