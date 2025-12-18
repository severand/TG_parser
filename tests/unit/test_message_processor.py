"""Unit tests for message_processor module."""

import pytest
from datetime import datetime

from core.message_processor import MessageProcessor
from utils.exceptions import ParserException, ValidationException


class TestMessageProcessorTextExtraction:
    """Test text extraction from HTML."""

    def test_extract_text_simple(self):
        """Test extracting plain text from simple HTML."""
        html = "<p>Hello World</p>"
        text = MessageProcessor.extract_text(html)
        assert text == "Hello World"

    def test_extract_text_with_multiple_elements(self):
        """Test extracting text from multiple elements."""
        html = "<div><p>Hello</p><p>World</p></div>"
        text = MessageProcessor.extract_text(html)
        assert "Hello" in text and "World" in text

    def test_extract_text_removes_scripts(self):
        """Test that script tags are removed."""
        html = "<p>Text</p><script>alert('bad')</script>"
        text = MessageProcessor.extract_text(html)
        assert "alert" not in text
        assert "Text" in text

    def test_extract_text_empty_html(self):
        """Test extracting text from empty HTML."""
        text = MessageProcessor.extract_text("<div></div>")
        assert text == ""

    def test_extract_text_whitespace_normalization(self):
        """Test that whitespace is normalized."""
        html = "<p>Text   with    multiple     spaces</p>"
        text = MessageProcessor.extract_text(html)
        assert "   " not in text
        assert text == "Text with multiple spaces"


class TestMessageProcessorMetadata:
    """Test metadata extraction."""

    def test_extract_metadata_with_timestamp(self, sample_html):
        """Test extracting timestamp from metadata."""
        metadata = MessageProcessor.extract_metadata(sample_html)
        assert "timestamp" in metadata
        assert metadata["timestamp"] is not None

    def test_extract_metadata_structure(self, sample_html):
        """Test metadata has all required fields."""
        metadata = MessageProcessor.extract_metadata(sample_html)
        required_fields = [
            'timestamp', 'author', 'message_id', 'views',
            'reactions', 'edited', 'pinned'
        ]
        for field in required_fields:
            assert field in metadata

    def test_extract_metadata_reactions_parsing(self, sample_html):
        """Test parsing reactions count."""
        metadata = MessageProcessor.extract_metadata(sample_html)
        assert "reactions" in metadata
        assert isinstance(metadata["reactions"], list)


class TestMessageProcessorTimestampParsing:
    """Test timestamp parsing."""

    def test_parse_iso_timestamp(self):
        """Test parsing ISO 8601 timestamp."""
        ts = MessageProcessor.parse_timestamp("2025-12-18T10:30:45")
        assert ts is not None
        assert ts.year == 2025
        assert ts.month == 12
        assert ts.day == 18

    def test_parse_timestamp_none_input(self):
        """Test parsing None returns None."""
        ts = MessageProcessor.parse_timestamp(None)
        assert ts is None

    def test_parse_timestamp_empty_string(self):
        """Test parsing empty string returns None."""
        ts = MessageProcessor.parse_timestamp("")
        assert ts is None

    def test_parse_invalid_timestamp(self):
        """Test parsing invalid timestamp."""
        ts = MessageProcessor.parse_timestamp("invalid-date")
        assert ts is None


class TestMessageProcessorExtractors:
    """Test extracting mentions, hashtags, URLs."""

    def test_extract_mentions(self):
        """Test extracting mentions from text."""
        text = "Hello @user1 and @user2, check this @user1 again"
        mentions = MessageProcessor.extract_mentions(text)
        assert set(mentions) == {'user1', 'user2'}

    def test_extract_mentions_empty(self):
        """Test extracting mentions from text without mentions."""
        mentions = MessageProcessor.extract_mentions("No mentions here")
        assert mentions == []

    def test_extract_hashtags(self):
        """Test extracting hashtags from text."""
        text = "#python #code #programming #python again"
        hashtags = MessageProcessor.extract_hashtags(text)
        assert set(hashtags) == {'python', 'code', 'programming'}

    def test_extract_hashtags_empty(self):
        """Test extracting hashtags from text without hashtags."""
        hashtags = MessageProcessor.extract_hashtags("No hashtags")
        assert hashtags == []

    def test_extract_urls(self):
        """Test extracting URLs from text."""
        text = "Check https://example.com and http://test.org for more"
        urls = MessageProcessor.extract_urls(text)
        assert "https://example.com" in urls
        assert "http://test.org" in urls

    def test_extract_urls_empty(self):
        """Test extracting URLs from text without URLs."""
        urls = MessageProcessor.extract_urls("No URLs here")
        assert urls == []


class TestMessageProcessorContext:
    """Test context extraction."""

    def test_extract_context_found(self):
        """Test extracting context when keyword found."""
        text = "The quick brown fox jumps over lazy dog"
        context = MessageProcessor.extract_context(text, "brown", context_words=2)
        assert context is not None
        assert "brown" in context
        assert "quick" in context or "fox" in context

    def test_extract_context_not_found(self):
        """Test extracting context when keyword not found."""
        context = MessageProcessor.extract_context(
            "Some text here",
            "missing_keyword",
            context_words=2
        )
        assert context is None

    def test_extract_context_case_insensitive(self):
        """Test context extraction is case-insensitive."""
        text = "The Quick Brown Fox"
        context = MessageProcessor.extract_context(text, "BROWN", context_words=2)
        assert context is not None


class TestMessageProcessorParsing:
    """Test full message parsing."""

    def test_parse_message_basic(self, sample_html):
        """Test parsing basic message."""
        message = MessageProcessor.parse_message(sample_html, channel_id=100, message_id=1)
        assert message.id == 1
        assert message.channel_id == 100
        assert message.text
        assert len(message.text) > 0

    def test_parse_message_with_auto_id(self, sample_html):
        """Test parsing message with auto-extracted ID."""
        message = MessageProcessor.parse_message(sample_html, channel_id=100)
        assert message.id is not None
        assert message.channel_id == 100

    def test_parse_message_invalid_no_id(self, sample_html):
        """Test parsing message without ID raises error."""
        with pytest.raises(ValidationException):
            MessageProcessor.parse_message(sample_html, channel_id=100, message_id=None)

    def test_parse_message_extracts_all_fields(self, sample_html):
        """Test that all message fields are extracted."""
        message = MessageProcessor.parse_message(sample_html, channel_id=100, message_id=1)
        assert message.timestamp is not None
        assert isinstance(message.views, int)
        assert isinstance(message.reactions, int)
        assert isinstance(message.mentions, list)
        assert isinstance(message.hashtags, list)
        assert isinstance(message.urls, list)


class TestMessageProcessorErrors:
    """Test error handling."""

    def test_extract_text_malformed_html(self):
        """Test extracting text from malformed HTML still works."""
        html = "<p>Unclosed paragraph<div>nested"
        text = MessageProcessor.extract_text(html)
        # Should not raise, should extract what it can
        assert isinstance(text, str)

    def test_parse_message_with_invalid_html(self):
        """Test parsing message with invalid HTML."""
        message = MessageProcessor.parse_message(
            "Invalid HTML",
            channel_id=100,
            message_id=1
        )
        # Should create message even with bad HTML
        assert message.id == 1
        assert message.channel_id == 100
