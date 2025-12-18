"""Pytest configuration and fixtures for all tests.

Provides:
- Temporary directories
- Mock data
- Sample objects
- Logging configuration
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from data.models import Message, Channel, SearchResult
from stats.collector import StatsCollector
from core.parser import Parser


@pytest.fixture
def tmp_dir():
    """Create temporary directory for tests."""
    tmp_path = Path(tempfile.mkdtemp())
    yield tmp_path
    # Cleanup
    shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
def sample_message():
    """Create sample Message object."""
    return Message(
        id=1,
        channel_id=100,
        author='test_author',
        text='This is a test message about Python programming',
        timestamp=datetime.now() - timedelta(days=1),
        views=1500,
        reactions=25,
        mentions=['@user1', '@user2'],
        hashtags=['#python', '#code'],
        urls=['https://example.com'],
        edited=False,
        pinned=False,
    )


@pytest.fixture
def sample_messages():
    """Create sample list of Message objects."""
    messages = []
    for i in range(5):
        msg = Message(
            id=i+1,
            channel_id=100+i,
            author=f'author_{i}',
            text=f'Test message {i} with keywords and content',
            timestamp=datetime.now() - timedelta(days=i),
            views=1000 * (i+1),
            reactions=10 * (i+1),
            mentions=[f'@user{i}'],
            hashtags=[f'#tag{i}'],
            urls=['https://example.com'],
            edited=i % 2 == 0,
            pinned=i == 0,
        )
        messages.append(msg)
    return messages


@pytest.fixture
def sample_channel():
    """Create sample Channel object."""
    return {
        'username': 'test_channel',
        'title': 'Test Channel',
        'description': 'This is a test channel',
        'followers': 50000,
        'photo_url': 'https://example.com/photo.jpg',
        'url': 'https://t.me/test_channel',
    }


@pytest.fixture
def sample_search_result():
    """Create sample SearchResult object."""
    return SearchResult(
        message_id=1,
        channel_id=100,
        text_snippet='This is a test message about Python programming',
        full_text='This is a test message about Python programming and more details',
        context='...about Python programming...',
        matched_keywords=['Python', 'programming'],
        relevance_score=85.5,
        timestamp=datetime.now() - timedelta(days=1),
        author='test_author',
        views=1500,
        reactions=25,
    )


@pytest.fixture
def sample_html():
    """Create sample HTML for parsing."""
    return '''
    <html>
        <body>
            <div class="tgme_widget_message" id="message-12345">
                <a class="user">TestAuthor</a>
                <time datetime="2025-12-18T10:30:45">Dec 18, 2025, 10:30 AM</time>
                <div class="text">Test message with keywords</div>
                <span class="views">1500 views</span>
                <div class="reactions">
                    <span class="reaction" data-emoji="👍">25</span>
                </div>
            </div>
        </body>
    </html>
    '''


@pytest.fixture
def mock_http_client():
    """Create mock HTTP client."""
    mock = MagicMock()
    mock.get.return_value.status_code = 200
    mock.get.return_value.text = '<html><body>Test</body></html>'
    return mock


@pytest.fixture
def stats_collector():
    """Create StatsCollector instance."""
    return StatsCollector()


@pytest.fixture
def parser_instance():
    """Create Parser instance."""
    return Parser(max_workers=2)


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    logger = MagicMock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset modules between tests to avoid state leakage."""
    yield
    # Cleanup code can go here if needed


# Configuration
pytest_plugins = ['pytest_cov']


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        'markers',
        'unit: mark test as unit test'
    )
    config.addinivalue_line(
        'markers',
        'integration: mark test as integration test'
    )
    config.addinivalue_line(
        'markers',
        'performance: mark test as performance test'
    )
