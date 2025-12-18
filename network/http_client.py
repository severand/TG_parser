"""HTTP client for making requests with anti-detection features.

Provides HTTPClient class that wraps requests library with:
- Automatic retry logic with exponential backoff
- Request timeouts
- User-Agent rotation
- Header randomization
- Cookie management
- Proper error handling and logging
"""

import time
from typing import Optional, Dict, Any
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as UrlRetry

from utils.logger import Logger
from utils.exceptions import NetworkException
from network.user_agents import UserAgents
from network.headers_rotator import HeadersRotator

logger = Logger()


class HTTPClient:
    """HTTP client with anti-detection and retry mechanisms.

    Makes HTTP requests with automatic retries, timeouts, and rotating
    User-Agents and headers to avoid detection.

    Example:
        >>> client = HTTPClient(timeout=30)
        >>> response = client.get("https://example.com")
        >>> response.status_code
        200
    """

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize HTTPClient.

        Args:
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries (default: 3)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self.headers_rotator = HeadersRotator()
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy.

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = UrlRetry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """Make GET request.

        Args:
            url: URL to request
            params: Query parameters
            **kwargs: Additional arguments for requests.get()

        Returns:
            Response object

        Raises:
            NetworkException: If request fails

        Example:
            >>> client = HTTPClient()
            >>> response = client.get("https://example.com", params={"q": "test"})
        """
        return self._request(
            method="GET",
            url=url,
            params=params,
            **kwargs,
        )

    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """Make POST request.

        Args:
            url: URL to request
            data: Form data
            json: JSON body
            **kwargs: Additional arguments

        Returns:
            Response object

        Raises:
            NetworkException: If request fails
        """
        return self._request(
            method="POST",
            url=url,
            data=data,
            json=json,
            **kwargs,
        )

    def head(
        self,
        url: str,
        **kwargs,
    ) -> requests.Response:
        """Make HEAD request.

        Args:
            url: URL to request
            **kwargs: Additional arguments

        Returns:
            Response object

        Raises:
            NetworkException: If request fails
        """
        return self._request(
            method="HEAD",
            url=url,
            **kwargs,
        )

    def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> requests.Response:
        """Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, HEAD)
            url: URL to request
            **kwargs: Additional arguments

        Returns:
            Response object

        Raises:
            NetworkException: If request fails
        """
        # Set timeout
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        # Set SSL verification
        if "verify" not in kwargs:
            kwargs["verify"] = self.verify_ssl

        # Merge headers
        headers = self.headers_rotator.get_random_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        try:
            logger.debug(
                f"Making {method} request to {url}",
            )

            response = self.session.request(method, url, **kwargs)

            # Log response
            logger.debug(
                f"Received response: {response.status_code}",
            )

            # Raise for HTTP errors (4xx, 5xx)
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error(
                    f"HTTP error {response.status_code}: {url}",
                )
                raise NetworkException(f"HTTP {response.status_code}: {str(e)}") from e

            return response

        except requests.Timeout as e:
            logger.error(f"Request timeout ({self.timeout}s): {url}")
            raise NetworkException(f"Request timeout after {self.timeout}s") from e

        except requests.ConnectionError as e:
            logger.error(f"Connection error: {url}")
            raise NetworkException(f"Connection error: {str(e)}") from e

        except requests.RequestException as e:
            logger.error(f"Request failed: {url}")
            raise NetworkException(f"Request failed: {str(e)}") from e

    def set_timeout(self, seconds: int) -> None:
        """Change request timeout.

        Args:
            seconds: Timeout in seconds
        """
        self.timeout = seconds
        logger.debug(f"Set request timeout to {seconds}s")

    def enable_cookies(self) -> None:
        """Enable cookie persistence.

        Cookies are automatically handled by requests.Session.
        """
        logger.debug("Cookies enabled (handled by session)")

    def close(self) -> None:
        """Close session and cleanup."""
        self.session.close()
        logger.debug("HTTPClient session closed")

    def __enter__(self) -> 'HTTPClient':
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
