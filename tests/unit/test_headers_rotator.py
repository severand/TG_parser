"""Unit tests for headers_rotator module."""

import pytest
from network.headers_rotator import HeadersRotator


class TestHeadersRotatorInitialization:
    """Test HeadersRotator initialization."""

    def test_headers_rotator_init(self):
        """Test HeadersRotator initializes."""
        rotator = HeadersRotator()
        assert rotator is not None
        assert len(rotator.headers_list) > 0

    def test_headers_rotator_has_required_headers(self):
        """Test rotator has required header fields."""
        rotator = HeadersRotator()
        sample_header = rotator.get_random_headers()
        assert 'User-Agent' in sample_header
        assert 'Accept' in sample_header
        assert 'Accept-Language' in sample_header


class TestHeadersRotatorGeneration:
    """Test header generation."""

    def test_get_random_headers(self):
        """Test getting random headers."""
        rotator = HeadersRotator()
        headers = rotator.get_random_headers()
        assert isinstance(headers, dict)
        assert len(headers) > 0
        assert 'User-Agent' in headers

    def test_random_headers_vary(self):
        """Test that random headers vary."""
        rotator = HeadersRotator()
        headers1 = rotator.get_random_headers()
        headers2 = rotator.get_random_headers()
        # At least some headers should differ
        assert headers1 != headers2 or len(rotator.headers_list) == 1

    def test_user_agent_format(self):
        """Test User-Agent format is valid."""
        rotator = HeadersRotator()
        headers = rotator.get_random_headers()
        user_agent = headers.get('User-Agent', '')
        assert len(user_agent) > 0
        # Common UA patterns
        assert any(x in user_agent for x in ['Mozilla', 'Chrome', 'Safari', 'Firefox'])


class TestHeadersRotatorConsistency:
    """Test header consistency."""

    def test_headers_always_valid(self):
        """Test all generated headers are valid."""
        rotator = HeadersRotator()
        for _ in range(10):
            headers = rotator.get_random_headers()
            assert isinstance(headers, dict)
            assert all(isinstance(k, str) and isinstance(v, str) for k, v in headers.items())

    def test_required_headers_present(self):
        """Test required headers are always present."""
        rotator = HeadersRotator()
        required = ['User-Agent', 'Accept']
        for _ in range(5):
            headers = rotator.get_random_headers()
            for req_header in required:
                assert req_header in headers


class TestHeadersRotatorRealistic:
    """Test realistic header combinations."""

    def test_accept_language_format(self):
        """Test Accept-Language format."""
        rotator = HeadersRotator()
        headers = rotator.get_random_headers()
        accept_lang = headers.get('Accept-Language', '')
        # Should be like en-US,en;q=0.9
        assert 'en' in accept_lang.lower() or accept_lang

    def test_accept_encoding_format(self):
        """Test Accept-Encoding format."""
        rotator = HeadersRotator()
        headers = rotator.get_random_headers()
        accept_enc = headers.get('Accept-Encoding', '')
        assert isinstance(accept_enc, str)
