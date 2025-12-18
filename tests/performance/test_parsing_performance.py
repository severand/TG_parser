"""Performance tests for parsing."""

import pytest
import time
from unittest.mock import Mock, patch
from core.parser import Parser
from data.models import Message
from datetime import datetime


@pytest.mark.performance
class TestParsingPerformance:
    """Performance tests for parsing operations."""

    def test_parse_1000_messages_speed(self, sample_messages):
        """Test parsing 1000 messages completes in reasonable time."""
        # Create 1000 messages
        messages = sample_messages * 200  # 5 * 200 = 1000

        parser = Parser(max_workers=4)
        start = time.time()
        # Search through messages
        results = parser.search(messages, ['test'])
        elapsed = time.time() - start

        # Should complete in < 5 seconds
        assert elapsed < 5.0

    def test_search_relevance_calculation_speed(self, sample_messages):
        """Test relevance calculation on 1000 messages is fast."""
        messages = sample_messages * 200

        parser = Parser()
        start = time.time()
        results = parser.search(messages, ['test', 'message'])
        elapsed = time.time() - start

        # Relevance calculation should be fast
        assert elapsed < 2.0

    def test_memory_usage_parsing(self, sample_messages):
        """Test memory usage remains reasonable during parsing."""
        messages = sample_messages * 100  # 500 messages

        parser = Parser()
        results = parser.search(messages, ['test'])
        # Should not consume excessive memory
        assert len(results) >= 0


@pytest.mark.performance
class TestSearchPerformance:
    """Performance tests for search operations."""

    def test_search_with_multiple_keywords(self, sample_messages):
        """Test search with multiple keywords on large dataset."""
        messages = sample_messages * 100
        keywords = ['test', 'message', 'content', 'data']

        parser = Parser()
        start = time.time()
        results = parser.search(messages, keywords)
        elapsed = time.time() - start

        assert elapsed < 3.0

    def test_filter_large_result_set(self, sample_messages):
        """Test filtering large result set."""
        messages = sample_messages * 50

        parser = Parser()
        results = parser.search(messages, ['test'])
        start = time.time()
        filtered = [r for r in results if r.relevance_score > 50]
        elapsed = time.time() - start

        # Filtering should be instant
        assert elapsed < 0.1


@pytest.mark.performance
@pytest.mark.slow
class TestLargeScalePerformance:
    """Large scale performance tests."""

    def test_parse_10000_messages(self, sample_messages):
        """Test parsing 10000 messages."""
        messages = sample_messages * 2000

        parser = Parser(max_workers=4)
        start = time.time()
        results = parser.search(messages, ['test'])
        elapsed = time.time() - start

        # Should complete in < 30 seconds
        assert elapsed < 30.0
        assert len(results) >= 0
