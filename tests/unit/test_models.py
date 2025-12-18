"""Unit tests for data models."""

import pytest
from datetime import datetime
from data.models import Message, Channel, SearchResult


class TestMessageModel:
    """Test Message model."""

    def test_message_creation(self, sample_message):
        """Test creating Message."""
        assert sample_message.id == 1
        assert sample_message.text
        assert sample_message.author

    def test_message_fields(self, sample_message):
        """Test Message has all required fields."""
        assert sample_message.id
        assert sample_message.channel_id
        assert sample_message.text
        assert sample_message.author
        assert sample_message.timestamp
        assert sample_message.views >= 0
        assert sample_message.reactions >= 0

    def test_message_mentions(self, sample_message):
        """Test Message mentions list."""
        assert isinstance(sample_message.mentions, list)

    def test_message_hashtags(self, sample_message):
        """Test Message hashtags list."""
        assert isinstance(sample_message.hashtags, list)

    def test_message_urls(self, sample_message):
        """Test Message URLs list."""
        assert isinstance(sample_message.urls, list)

    def test_message_equality(self, sample_message):
        """Test Message equality."""
        msg1 = sample_message
        msg2 = Message(
            id=msg1.id,
            channel_id=msg1.channel_id,
            author=msg1.author,
            text=msg1.text,
            timestamp=msg1.timestamp,
            views=msg1.views,
            reactions=msg1.reactions,
            mentions=msg1.mentions,
            hashtags=msg1.hashtags,
            urls=msg1.urls,
            edited=msg1.edited,
            pinned=msg1.pinned,
        )
        assert msg1.id == msg2.id


class TestSearchResultModel:
    """Test SearchResult model."""

    def test_search_result_creation(self, sample_search_result):
        """Test creating SearchResult."""
        assert sample_search_result.message_id
        assert sample_search_result.matched_keywords
        assert sample_search_result.relevance_score >= 0

    def test_search_result_fields(self, sample_search_result):
        """Test SearchResult has all required fields."""
        assert sample_search_result.message_id
        assert sample_search_result.channel_id
        assert sample_search_result.text_snippet
        assert sample_search_result.full_text
        assert sample_search_result.matched_keywords
        assert sample_search_result.relevance_score

    def test_search_result_relevance_range(self, sample_search_result):
        """Test SearchResult relevance score is 0-100."""
        assert 0 <= sample_search_result.relevance_score <= 100

    def test_search_result_keywords_list(self, sample_search_result):
        """Test SearchResult keywords are list."""
        assert isinstance(sample_search_result.matched_keywords, list)
        assert len(sample_search_result.matched_keywords) > 0
