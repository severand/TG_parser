"""Header rotation for anti-detection purposes.

Provides methods to generate and rotate realistic HTTP headers
with proper User-Agents.
"""

from typing import Dict

from network.user_agents import UserAgents


class HeadersRotator:
    """Rotate and generate realistic HTTP headers.

    Provides methods to get random HTTP headers with rotating User-Agents
    to avoid detection.

    Example:
        >>> rotator = HeadersRotator()
        >>> headers = rotator.get_random_headers()
        >>> 'User-Agent' in headers
        True
    """

    @staticmethod
    def get_random_headers() -> Dict[str, str]:
        """Get random HTTP headers with rotating User-Agent.

        Returns:
            Dictionary of HTTP headers

        Example:
            >>> rotator = HeadersRotator()
            >>> headers = rotator.get_random_headers()
            >>> headers['Accept']
            'text/html,application/xhtml+xml,...'
        """
        return {
            'User-Agent': UserAgents.get_random(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }

    @staticmethod
    def rotate() -> Dict[str, str]:
        """Alias for get_random_headers().

        Returns:
            Dictionary of HTTP headers
        """
        return HeadersRotator.get_random_headers()
