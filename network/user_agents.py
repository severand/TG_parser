"""User-Agent strings collection for anti-detection.

Provides a collection of realistic User-Agent strings from various browsers
and operating systems to rotate during requests.
"""

import random
from typing import List


class UserAgents:
    """Collection of User-Agent strings for request rotation.

    Provides methods to get random or specific User-Agent strings
    for anti-detection purposes.

    Example:
        >>> ua = UserAgents()
        >>> random_ua = ua.get_random()
        >>> chrome_ua = ua.get_by_browser('chrome')
    """

    # Chrome User-Agents (Windows, macOS, Linux)
    CHROME_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    # Firefox User-Agents
    FIREFOX_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]

    # Safari User-Agents
    SAFARI_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    ]

    # Edge User-Agents
    EDGE_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    ]

    # All agents combined
    ALL_AGENTS = CHROME_AGENTS + FIREFOX_AGENTS + SAFARI_AGENTS + EDGE_AGENTS

    # Browser mapping
    BROWSER_MAP = {
        'chrome': CHROME_AGENTS,
        'firefox': FIREFOX_AGENTS,
        'safari': SAFARI_AGENTS,
        'edge': EDGE_AGENTS,
    }

    @staticmethod
    def get_random() -> str:
        """Get random User-Agent string.

        Returns:
            Random User-Agent string from all available agents

        Example:
            >>> ua = UserAgents()
            >>> agent = ua.get_random()
            >>> len(agent) > 0
            True
        """
        return random.choice(UserAgents.ALL_AGENTS)

    @staticmethod
    def get_by_browser(browser: str) -> str:
        """Get User-Agent for specific browser.

        Args:
            browser: Browser name ('chrome', 'firefox', 'safari', 'edge')

        Returns:
            Random User-Agent for specified browser

        Raises:
            ValueError: If browser is not supported

        Example:
            >>> ua = UserAgents()
            >>> chrome_ua = ua.get_by_browser('chrome')
            >>> 'Chrome' in chrome_ua
            True
        """
        browser_lower = browser.lower().strip()
        if browser_lower not in UserAgents.BROWSER_MAP:
            raise ValueError(
                f"Unsupported browser: {browser}. "
                f"Supported: {list(UserAgents.BROWSER_MAP.keys())}"
            )
        return random.choice(UserAgents.BROWSER_MAP[browser_lower])

    @staticmethod
    def get_all() -> List[str]:
        """Get all available User-Agent strings.

        Returns:
            List of all User-Agent strings
        """
        return UserAgents.ALL_AGENTS.copy()

    @staticmethod
    def get_count() -> int:
        """Get total number of available User-Agent strings.

        Returns:
            Count of User-Agent strings
        """
        return len(UserAgents.ALL_AGENTS)
