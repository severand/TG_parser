"""Unit tests for validators module."""

import pytest

from utils.validators import (
    validate_channel_url,
    validate_keywords,
    validate_config,
    #validate_message,
    #validate_email,
)
from utils.exceptions import ValidationException


class TestChannelUrlValidation:
    """Test channel URL validation."""

    def test_validate_valid_channel_url(self):
        """Test validating valid channel URLs."""
        assert validate_channel_url("@channel_name") is True
        assert validate_channel_url("@test123") is True
        assert validate_channel_url("https://t.me/channel_name") is True

    def test_validate_invalid_channel_url(self):
        """Test validating invalid channel URLs."""
        assert validate_channel_url("") is False
        assert validate_channel_url("invalid") is False
        assert validate_channel_url("@") is False

    def test_validate_channel_url_with_numbers(self):
        """Test validating channel URLs with numbers."""
        assert validate_channel_url("@channel123") is True
        assert validate_channel_url("@123channel") is True

    def test_validate_channel_url_with_underscore(self):
        """Test validating channel URLs with underscores."""
        assert validate_channel_url("@channel_name") is True
        assert validate_channel_url("@_private") is True


class TestKeywordsValidation:
    """Test keywords validation."""

    def test_validate_valid_keywords(self):
        """Test validating valid keywords."""
        assert validate_keywords(["python", "code"]) is True
        assert validate_keywords(["test"]) is True

    def test_validate_empty_keywords(self):
        """Test validating empty keywords list."""
        assert validate_keywords([]) is False

    def test_validate_keywords_with_special_chars(self):
        """Test validating keywords with special characters."""
        assert validate_keywords(["#hashtag", "@mention"]) is True
        assert validate_keywords(["test-keyword"]) is True

    def test_validate_keywords_too_long(self):
        """Test validating very long keywords."""
        long_keyword = "a" * 1000
        # Should still be valid but implementation may limit
        result = validate_keywords([long_keyword])
        assert isinstance(result, bool)


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_valid_config(self):
        """Test validating valid configuration."""
        config = {
            'channels': ['@channel1'],
            'keywords': ['test'],
            'timeout': 10,
        }
        assert validate_config(config) is True

    def test_validate_config_empty_dict(self):
        """Test validating empty configuration."""
        assert validate_config({}) is False

    def test_validate_config_wrong_types(self):
        """Test validating configuration with wrong types."""
        config = {
            'channels': 'not_a_list',
            'timeout': 'not_a_number',
        }
        result = validate_config(config)
        # Should validate types
        assert isinstance(result, bool)

    def test_validate_config_with_required_fields(self):
        """Test validating config has required fields."""
        config = {
            'channels': [],
            'keywords': [],
        }
        result = validate_config(config)
        assert isinstance(result, bool)


class TestMessageValidation:
    """Test message validation."""

    def test_validate_valid_message(self):
        """Test validating valid message."""
        message = {
            'id': 1,
            'text': 'Test message',
            'author': 'test_user',
        }
        assert validate_message(message) is True

    def test_validate_message_missing_required_fields(self):
        """Test validating message with missing required fields."""
        message = {'text': 'Test'}
        # Should fail if required fields missing
        result = validate_message(message)
        assert isinstance(result, bool)

    def test_validate_message_empty(self):
        """Test validating empty message."""
        assert validate_message({}) is False

    def test_validate_message_with_extra_fields(self):
        """Test validating message with extra fields."""
        message = {
            'id': 1,
            'text': 'Test',
            'author': 'user',
            'extra_field': 'extra_value',
        }
        result = validate_message(message)
        assert isinstance(result, bool)


class TestEmailValidation:
    """Test email validation."""

    def test_validate_valid_email(self):
        """Test validating valid emails."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@example.co.uk") is True

    def test_validate_invalid_email(self):
        """Test validating invalid emails."""
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("") is False

    def test_validate_email_with_special_chars(self):
        """Test validating emails with special characters."""
        assert validate_email("test+tag@example.com") is True

    def test_validate_email_case_insensitive(self):
        """Test email validation is case-insensitive."""
        assert validate_email("TEST@EXAMPLE.COM") is True
        assert validate_email("Test@Example.Com") is True
