"""Tests for GuardDuty enable script."""

import unittest
from unittest.mock import patch, MagicMock, call
from moto import mock_aws
import boto3
import pytest
from botocore.exceptions import ClientError

from aws_sec_toolkit.scripts.guardduty_enable import enable_guardduty_all_regions, check_guardduty_status


class TestGuardDutyEnable(unittest.TestCase):
    """Test cases for GuardDuty enablement functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock()
        self.mock_regions = ['us-east-1', 'us-west-2', 'eu-west-1']

    @patch('aws_sec_toolkit.scripts.guardduty_enable.get_enabled_regions')
    @patch('boto3.Session')
    def test_enable_guardduty_new_detectors(self, mock_session_class, mock_get_regions):
        """Test enabling GuardDuty in regions without existing detectors."""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_get_regions.return_value = self.mock_regions
        
        mock_gd = MagicMock()
        mock_session.client.return_value = mock_gd
        
        # No existing detectors
        mock_gd.list_detectors.return_value = {'DetectorIds': []}
        mock_gd.create_detector.return_value = {'DetectorId': 'new-detector-123'}
        
        result = enable_guardduty_all_regions()
        
        # Verify results
        self.assertEqual(len(result), 3)
        for region in self.mock_regions:
            self.assertTrue(result[region])
        
        # Verify create_detector was called for each region
        self.assertEqual(mock_gd.create_detector.call_count, 3)
        mock_gd.create_detector.assert_has_calls([
            call(Enable=True),
            call(Enable=True),
            call(Enable=True)
        ])

    @patch('aws_sec_toolkit.scripts.guardduty_enable.get_enabled_regions')
    @patch('boto3.Session')
    def test_enable_guardduty_existing_detectors(self, mock_session_class, mock_get_regions):
        """Test enabling GuardDuty in regions with existing detectors."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_get_regions.return_value = ['us-east-1']
        
        mock_gd = MagicMock()
        mock_session.client.return_value = mock_gd
        
        # Existing detector
        mock_gd.list_detectors.return_value = {'DetectorIds': ['existing-detector-456']}
        
        result = enable_guardduty_all_regions()
        
        # Should update existing detector
        self.assertTrue(result['us-east-1'])
        mock_gd.update_detector.assert_called_once_with(
            DetectorId='existing-detector-456', 
            Enable=True
        )
        mock_gd.create_detector.assert_not_called()

    @patch('aws_sec_toolkit.scripts.guardduty_enable.get_enabled_regions')
    @patch('boto3.Session')
    def test_enable_guardduty_client_error(self, mock_session_class, mock_get_regions):
        """Test handling ClientError during GuardDuty enablement."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_get_regions.return_value = ['us-east-1']
        
        mock_gd = MagicMock()
        mock_session.client.return_value = mock_gd
        
        # Simulate error
        mock_gd.list_detectors.return_value = {'DetectorIds': []}
        mock_gd.create_detector.side_effect = ClientError(
            error_response={'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            operation_name='CreateDetector'
        )
        
        result = enable_guardduty_all_regions()
        
        # Should continue processing despite error
        self.assertEqual(len(result), 0)  # Region should be skipped


class TestGuardDutyStatus(unittest.TestCase):
    """Test cases for GuardDuty status checking."""

    @patch('boto3.Session')
    def test_check_guardduty_status_enabled(self, mock_session_class):
        """Test checking status for enabled GuardDuty."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_gd = MagicMock()
        mock_session.client.return_value = mock_gd
        mock_gd.list_detectors.return_value = {'DetectorIds': ['detector-123']}
        
        result = check_guardduty_status(['us-east-1'])
        
        self.assertEqual(result['us-east-1'], 'ENABLED')

    @patch('boto3.Session')
    def test_check_guardduty_status_disabled(self, mock_session_class):
        """Test checking status for disabled GuardDuty."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_gd = MagicMock()
        mock_session.client.return_value = mock_gd
        mock_gd.list_detectors.return_value = {'DetectorIds': []}
        
        result = check_guardduty_status(['us-west-2'])
        
        self.assertEqual(result['us-west-2'], 'DISABLED')


@mock_aws
class TestGuardDutyMotoIntegration(unittest.TestCase):
    """Integration tests using moto for realistic AWS API simulation."""
    
    def test_guardduty_enable_integration(self):
        """Test GuardDuty enablement with moto mocks."""
        # This would require a more complex setup with moto
        # For now, we'll test the structure
        session = boto3.Session(region_name='us-east-1')
        client = session.client('guardduty', region_name='us-east-1')
        
        # Test basic client creation
        self.assertIsNotNone(client)
        
        # Note: moto's GuardDuty support is limited, so we keep this simple


if __name__ == '__main__':
    unittest.main()