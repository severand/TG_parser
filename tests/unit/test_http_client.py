"""Unit tests for http_client module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from requests.exceptions import Timeout, ConnectionError

from network.http_client import HTTPClient
from utils.exceptions import ParserException


class TestHTTPClientInitialization:
    """Test HTTPClient initialization."""

    def test_http_client_init_default(self):
        """Test HTTPClient initializes with defaults."""
        client = HTTPClient()
        assert client.timeout == 10
        assert client.max_retries == 3
        assert client.retry_delay == 1

    def test_http_client_init_custom(self):
        """Test HTTPClient initializes with custom parameters."""
        client = HTTPClient(timeout=20, max_retries=5, retry_delay=2)
        assert client.timeout == 20
        assert client.max_retries == 5
        assert client.retry_delay == 2


class TestHTTPClientRequests:
    """Test HTTP requests."""

    @patch('network.http_client.requests.get')
    def test_get_success(self, mock_get):
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html>content</html>'
        mock_get.return_value = mock_response

        client = HTTPClient()
        response = client.get('https://example.com')
        assert response.status_code == 200
        assert response.text == '<html>content</html>'

    @patch('network.http_client.requests.get')
    def test_get_timeout_retry(self, mock_get):
        """Test GET request with timeout and retry."""
        mock_get.side_effect = [Timeout(), Mock(status_code=200, text='ok')]
        client = HTTPClient(max_retries=2)
        response = client.get('https://example.com')
        assert response.status_code == 200

    @patch('network.http_client.requests.get')
    def test_get_connection_error(self, mock_get):
        """Test GET request with connection error."""
        mock_get.side_effect = ConnectionError()
        client = HTTPClient(max_retries=1)
        with pytest.raises(ParserException):
            client.get('https://example.com')

    def test_get_invalid_url(self):
        """Test GET with invalid URL."""
        client = HTTPClient()
        with pytest.raises((ParserException, Exception)):
            client.get('invalid-url')


class TestHTTPClientHeaders:
    """Test header handling."""

    @patch('network.http_client.requests.get')
    def test_get_with_custom_headers(self, mock_get):
        """Test GET request with custom headers."""
        mock_response = Mock(status_code=200, text='ok')
        mock_get.return_value = mock_response

        client = HTTPClient()
        headers = {'User-Agent': 'CustomAgent/1.0'}
        client.get('https://example.com', headers=headers)
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert 'headers' in call_kwargs

    @patch('network.http_client.requests.get')
    def test_get_default_headers(self, mock_get):
        """Test GET request includes default headers."""
        mock_response = Mock(status_code=200, text='ok')
        mock_get.return_value = mock_response

        client = HTTPClient()
        client.get('https://example.com')
        call_kwargs = mock_get.call_args[1]
        assert 'headers' in call_kwargs


class TestHTTPClientCookies:
    """Test cookie handling."""

    @patch('network.http_client.requests.get')
    def test_get_with_cookies(self, mock_get):
        """Test GET request with cookies."""
        mock_response = Mock(status_code=200, text='ok')
        mock_get.return_value = mock_response

        client = HTTPClient()
        cookies = {'session': 'abc123'}
        client.get('https://example.com', cookies=cookies)
        call_kwargs = mock_get.call_args[1]
        assert 'cookies' in call_kwargs


class TestHTTPClientRetry:
    """Test retry logic."""

    @patch('network.http_client.requests.get')
    def test_retry_on_timeout(self, mock_get):
        """Test retry on timeout."""
        responses = [Timeout(), Timeout(), Mock(status_code=200, text='ok')]
        mock_get.side_effect = responses

        client = HTTPClient(max_retries=3)
        response = client.get('https://example.com')
        assert response.status_code == 200
        assert mock_get.call_count == 3

    @patch('network.http_client.requests.get')
    def test_max_retries_exceeded(self, mock_get):
        """Test max retries exceeded."""
        mock_get.side_effect = Timeout()

        client = HTTPClient(max_retries=2)
        with pytest.raises(ParserException):
            client.get('https://example.com')
        assert mock_get.call_count == 2


class TestHTTPClientStatus:
    """Test status code handling."""

    @patch('network.http_client.requests.get')
    def test_status_404(self, mock_get):
        """Test handling 404 status."""
        mock_response = Mock(status_code=404, text='Not found')
        mock_get.return_value = mock_response

        client = HTTPClient()
        response = client.get('https://example.com')
        assert response.status_code == 404

    @patch('network.http_client.requests.get')
    def test_status_500(self, mock_get):
        """Test handling 500 status."""
        mock_response = Mock(status_code=500, text='Server error')
        mock_get.return_value = mock_response

        client = HTTPClient()
        response = client.get('https://example.com')
        assert response.status_code == 500
