"""Lambda handler for Security Hub operations."""

import json
import logging
from typing import Any, Dict

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for Security Hub enablement."""
    try:
        # Import here to avoid cold start issues
        from aws_sec_toolkit.scripts.securityhub_enable import enable_securityhub_all_regions
        
        logger.info("Starting Security Hub enablement across all regions")
        
        result = enable_securityhub_all_regions()
        
        logger.info(f"Security Hub enablement completed. Results: {result}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Security Hub enablement completed successfully',
                'results': result,
                'total_regions': len(result),
                'successful_regions': sum(1 for success in result.values() if success),
                'failed_regions': sum(1 for success in result.values() if not success)
            })
        }
        
    except Exception as e:
        logger.error(f"Error in Security Hub enablement: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to enable Security Hub'
            })
        }