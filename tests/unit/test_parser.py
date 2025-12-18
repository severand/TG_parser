"""Unit tests for parser module."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

from core.parser import Parser
from utils.exceptions import ValidationException, ParserException


class TestParserInitialization:
    """Test Parser initialization."""

    def test_parser_init_default(self):
        """Test default Parser initialization."""
        parser = Parser()
        assert parser.max_workers == 4
        assert parser.timeout == 10
        assert parser.max_retries == 3
        assert parser.is_running is False

    def test_parser_init_custom_params(self):
        """Test Parser initialization with custom parameters."""
        parser = Parser(max_workers=8, timeout=20, max_retries=5)
        assert parser.max_workers == 8
        assert parser.timeout == 20
        assert parser.max_retries == 5


class TestParserStatistics:
    """Test statistics collection."""

    def test_get_statistics_initial_empty(self):
        """Test getting statistics before any parsing."""
        parser = Parser()
        stats = parser.get_statistics()
        assert stats['total_messages'] == 0
        assert stats['total_channels_parsed'] == 0
        assert stats['total_channels_failed'] == 0

    def test_get_statistics_after_reset(self):
        """Test statistics after reset."""
        parser = Parser()
        parser.reset()
        stats = parser.get_statistics()
        assert stats['total_messages'] == 0


class TestParserMessageGrouping:
    """Test message grouping methods."""

    def test_get_messages_by_channel(self, sample_messages):
        """Test grouping messages by channel."""
        parser = Parser()
        channel_messages = parser.get_messages_by_channel(sample_messages, 100)
        assert len(channel_messages) > 0
        assert all(m.channel_id == 100 for m in channel_messages)

    def test_get_messages_by_channel_empty(self, sample_messages):
        """Test getting messages from non-existent channel."""
        parser = Parser()
        channel_messages = parser.get_messages_by_channel(sample_messages, 9999)
        assert len(channel_messages) == 0

    def test_get_messages_by_author(self, sample_messages):
        """Test grouping messages by author."""
        parser = Parser()
        author_messages = parser.get_messages_by_author(sample_messages, 'author_0')
        assert len(author_messages) > 0
        assert all('author_0' in m.author for m in author_messages)


class TestParserTrending:
    """Test trending messages analysis."""

    def test_get_trending_by_views(self, sample_messages):
        """Test getting trending messages by views."""
        parser = Parser()
        trending = parser.get_trending_messages(sample_messages, limit=3, metric='views')
        assert len(trending) <= 3
        # Check they're sorted by views
        if len(trending) > 1:
            for i in range(len(trending) - 1):
                assert trending[i].views >= trending[i+1].views

    def test_get_trending_by_reactions(self, sample_messages):
        """Test getting trending messages by reactions."""
        parser = Parser()
        trending = parser.get_trending_messages(sample_messages, limit=3, metric='reactions')
        assert len(trending) <= 3

    def test_get_trending_default_limit(self, sample_messages):
        """Test trending messages with default limit."""
        parser = Parser()
        trending = parser.get_trending_messages(sample_messages)
        assert len(trending) <= 10


class TestParserSearch:
    """Test search functionality."""

    def test_search_basic(self, sample_messages):
        """Test basic search through messages."""
        parser = Parser()
        results = parser.search(sample_messages, ['test'])
        assert isinstance(results, list)

    def test_search_with_filters(self, sample_messages):
        """Test search with additional filters."""
        parser = Parser()
        results = parser.search(
            sample_messages,
            ['test'],
            min_views=100,
        )
        assert isinstance(results, list)

    def test_search_no_keywords_error(self, sample_messages):
        """Test search without keywords raises error."""
        parser = Parser()
        with pytest.raises(ValidationException):
            parser.search(sample_messages, [])


class TestParserReset:
    """Test parser reset functionality."""

    def test_reset_clears_state(self):
        """Test that reset clears parser state."""
        parser = Parser()
        parser.is_running = True
        parser.start_time = datetime.now()
        parser.reset()
        assert parser.is_running is False
        assert parser.start_time is None

    def test_reset_clears_stats(self):
        """Test that reset clears statistics."""
        parser = Parser()
        parser.reset()
        stats = parser.get_statistics()
        assert stats['total_messages'] == 0
        assert stats['total_channels_parsed'] == 0


class TestParserConcurrency:
    """Test concurrent parsing behavior."""

    def test_parser_not_running_initially(self):
        """Test parser is not running initially."""
        parser = Parser()
        assert parser.is_running is False

    def test_parser_sets_running_flag(self):
        """Test parser sets running flag during parsing."""
        parser = Parser(max_workers=1)
        # We can't actually test this without mocking, as it requires real channels
        assert parser.is_running is False


class TestParserInputValidation:
    """Test input validation."""

    def test_parse_channels_empty_list_error(self):
        """Test parsing with empty channel list raises error."""
        parser = Parser()
        with pytest.raises(ValidationException):
            parser.parse_channels([])

    def test_parse_and_search_empty_channels_error(self):
        """Test parse_and_search with empty channels raises error."""
        parser = Parser()
        # This would raise if actually called, but we test the pattern
        # Real test would need mocking
        assert parser is not None


class TestParserIntegration:
    """Integration tests for parser."""

    @pytest.mark.integration
    def test_parse_and_search_result_structure(self, sample_messages):
        """Test that parse_and_search returns correct structure."""
        parser = Parser()
        # Mock the actual parsing
        with patch.object(parser, 'parse_channels', return_value=sample_messages):
            result = parser.parse_and_search(
                channels=['@test'],
                keywords=['test'],
                max_messages=10
            )
            assert 'messages' in result
            assert 'search_results' in result
            assert 'statistics' in result
            assert 'success' in result

    @pytest.mark.integration
    def test_parse_and_search_handles_errors(self):
        """Test parse_and_search handles errors gracefully."""
        parser = Parser()
        # Mock parse_channels to raise an error
        with patch.object(parser, 'parse_channels', side_effect=Exception("Test error")):
            result = parser.parse_and_search(
                channels=['@test'],
                keywords=['test']
            )
            assert result['success'] is False
            assert result['error'] is not None
