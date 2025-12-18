"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "parser": {
            "max_threads": 2,
            "timeout": 10,
            "max_retries": 1,
            "delay_min": 0,
            "delay_max": 1,
        },
        "logging": {
            "level": "DEBUG",
        },
    }


@pytest.fixture
def sample_channel():
    """Sample channel data."""
    return {
        "id": "test_channel_1",
        "username": "testchannel",
        "title": "Test Channel",
        "description": "A test channel",
        "url": "https://t.me/testchannel",
    }


@pytest.fixture
def sample_message():
    """Sample message data."""
    return {
        "id": "msg_1",
        "channel_id": "test_channel_1",
        "text": "Test message content",
        "timestamp": "2025-12-18T10:00:00Z",
        "author_id": "user_1",
    }
