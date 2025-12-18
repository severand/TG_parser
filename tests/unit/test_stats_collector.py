"""Unit tests for stats collector module."""

import pytest
from datetime import datetime

from stats.collector import StatsCollector, ParseError
from data.models import Message


class TestStatsCollectorInitialization:
    """Test StatsCollector initialization."""

    def test_collector_init(self):
        """Test collector initializes with empty state."""
        collector = StatsCollector()
        assert collector.total_messages == 0
        assert len(collector.parsed_channels) == 0
        assert len(collector.failed_channels) == 0
        assert len(collector.errors) == 0


class TestStatsCollectorChannelTracking:
    """Test channel tracking."""

    def test_add_parsed_channel(self, stats_collector):
        """Test adding parsed channel."""
        stats_collector.add_parsed_channel('@channel1', 100)
        assert len(stats_collector.parsed_channels) == 1
        assert stats_collector.channel_message_counts['@channel1'] == 100

    def test_add_failed_channel(self, stats_collector):
        """Test adding failed channel."""
        stats_collector.add_failed_channel('@channel1', 'Connection error')
        assert len(stats_collector.failed_channels) == 1
        assert len(stats_collector.errors) == 1

    def test_add_multiple_channels(self, stats_collector):
        """Test adding multiple channels."""
        stats_collector.add_parsed_channel('@channel1', 100)
        stats_collector.add_parsed_channel('@channel2', 50)
        stats_collector.add_failed_channel('@channel3', 'Error')
        assert len(stats_collector.parsed_channels) == 2
        assert len(stats_collector.failed_channels) == 1


class TestStatsCollectorMessageTracking:
    """Test message tracking."""

    def test_add_single_message(self, stats_collector, sample_message):
        """Test adding single message."""
        stats_collector.add_message(sample_message)
        assert stats_collector.total_messages == 1

    def test_add_duplicate_message(self, stats_collector, sample_message):
        """Test that duplicate messages aren't counted twice."""
        stats_collector.add_message(sample_message)
        stats_collector.add_message(sample_message)  # Same ID
        assert stats_collector.total_messages == 1

    def test_add_multiple_messages(self, stats_collector, sample_messages):
        """Test adding multiple messages."""
        for msg in sample_messages:
            stats_collector.add_message(msg)
        assert stats_collector.total_messages == len(sample_messages)

    def test_message_tracking_aggregates_views(self, stats_collector, sample_messages):
        """Test that views are aggregated."""
        total_views = sum(m.views for m in sample_messages)
        for msg in sample_messages:
            stats_collector.add_message(msg)
        assert stats_collector.total_views == total_views

    def test_message_tracking_aggregates_reactions(self, stats_collector, sample_messages):
        """Test that reactions are aggregated."""
        total_reactions = sum(m.reactions for m in sample_messages)
        for msg in sample_messages:
            stats_collector.add_message(msg)
        assert stats_collector.total_reactions == total_reactions

    def test_message_tracking_extracts_metadata(self, stats_collector, sample_messages):
        """Test that metadata is extracted from messages."""
        for msg in sample_messages:
            stats_collector.add_message(msg)
        # Authors should be tracked
        assert len(stats_collector.authors) > 0
        # Hashtags should be tracked
        assert len(stats_collector.hashtags) > 0


class TestStatsCollectorStatistics:
    """Test statistics generation."""

    def test_get_statistics_empty(self, stats_collector):
        """Test getting statistics from empty collector."""
        stats = stats_collector.get_statistics()
        assert stats['total_messages'] == 0
        assert stats['total_channels_parsed'] == 0
        assert stats['total_channels_failed'] == 0

    def test_get_statistics_structure(self, stats_collector, sample_messages):
        """Test statistics have all required fields."""
        for msg in sample_messages:
            stats_collector.add_message(msg)
        stats_collector.add_parsed_channel('@channel1', len(sample_messages))

        stats = stats_collector.get_statistics()
        required_fields = [
            'total_channels_parsed',
            'total_channels_failed',
            'total_messages',
            'total_views',
            'total_reactions',
            'avg_views_per_message',
            'avg_reactions_per_message',
            'success_rate',
        ]
        for field in required_fields:
            assert field in stats

    def test_statistics_success_rate(self, stats_collector):
        """Test success rate calculation."""
        stats_collector.add_parsed_channel('@channel1', 10)
        stats_collector.add_parsed_channel('@channel2', 20)
        stats_collector.add_failed_channel('@channel3', 'Error')

        stats = stats_collector.get_statistics()
        # 2 successful, 1 failed = 66.67% success rate
        expected_rate = (2 / 3) * 100
        assert abs(stats['success_rate'] - expected_rate) < 1


class TestStatsCollectorErrorTracking:
    """Test error tracking."""

    def test_get_errors(self, stats_collector):
        """Test getting list of errors."""
        stats_collector.add_failed_channel('@channel1', 'Connection error')
        stats_collector.add_failed_channel('@channel2', 'Timeout')

        errors = stats_collector.get_errors()
        assert len(errors) == 2
        assert any('Connection error' in e['error'] for e in errors)

    def test_error_structure(self, stats_collector):
        """Test error object structure."""
        stats_collector.add_failed_channel('@channel1', 'Test error')
        errors = stats_collector.get_errors()
        assert len(errors) > 0
        error = errors[0]
        assert 'channel' in error
        assert 'error' in error
        assert 'timestamp' in error


class TestStatsCollectorChannelSummary:
    """Test channel summary."""

    def test_get_channel_summary(self, stats_collector):
        """Test getting channel summary."""
        stats_collector.add_parsed_channel('@channel1', 100)
        stats_collector.add_failed_channel('@channel2', 'Error')

        summary = stats_collector.get_channel_summary()
        assert '@channel1' in summary
        assert '@channel2' in summary
        assert summary['@channel1']['status'] == 'parsed'
        assert summary['@channel2']['status'] == 'failed'

    def test_get_top_channels(self, stats_collector):
        """Test getting top channels by message count."""
        stats_collector.add_parsed_channel('@channel1', 50)
        stats_collector.add_parsed_channel('@channel2', 100)
        stats_collector.add_parsed_channel('@channel3', 75)

        top = stats_collector.get_top_channels_by_messages(limit=2)
        assert len(top) == 2
        # Should be sorted by message count
        assert top[0][1] >= top[1][1]


class TestStatsCollectorReset:
    """Test reset functionality."""

    def test_reset_clears_state(self, stats_collector, sample_messages):
        """Test that reset clears all data."""
        for msg in sample_messages:
            stats_collector.add_message(msg)
        stats_collector.add_parsed_channel('@channel1', 10)

        stats_collector.reset()
        assert stats_collector.total_messages == 0
        assert len(stats_collector.parsed_channels) == 0
        assert len(stats_collector.failed_channels) == 0
        assert len(stats_collector.errors) == 0
