"""Cookie management for HTTP sessions.

Provides CookieManager for saving, loading, and persisting cookies
across requests.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from utils.logger import Logger
from utils.exceptions import StorageException

logger = Logger()


class CookieManager:
    """Manage HTTP cookies with persistence.

    Provides methods to save, load, and persist cookies
    between sessions.

    Example:
        >>> manager = CookieManager()
        >>> manager.save('session_id', 'abc123')
        >>> value = manager.load('session_id')
        >>> manager.persist()
    """

    def __init__(self, storage_path: str = "data/cookies.json") -> None:
        """Initialize CookieManager.

        Args:
            storage_path: Path to cookies storage file (default: data/cookies.json)
        """
        self.storage_path = Path(storage_path)
        self._cookies: Dict[str, Any] = {}
        self._load_from_file()

    def save(self, key: str, value: Any) -> None:
        """Save cookie value.

        Args:
            key: Cookie name
            value: Cookie value

        Example:
            >>> manager = CookieManager()
            >>> manager.save('session', 'xyz789')
        """
        self._cookies[key] = value
        logger.debug(f"Saved cookie: {key}")

    def load(self, key: str) -> Optional[Any]:
        """Load cookie value.

        Args:
            key: Cookie name

        Returns:
            Cookie value or None if not found

        Example:
            >>> manager = CookieManager()
            >>> value = manager.load('session')
        """
        return self._cookies.get(key)

    def delete(self, key: str) -> None:
        """Delete cookie.

        Args:
            key: Cookie name to delete
        """
        if key in self._cookies:
            del self._cookies[key]
            logger.debug(f"Deleted cookie: {key}")

    def exists(self, key: str) -> bool:
        """Check if cookie exists.

        Args:
            key: Cookie name

        Returns:
            True if cookie exists, False otherwise
        """
        return key in self._cookies

    def persist(self) -> None:
        """Save cookies to file.

        Persists cookies dictionary to JSON file for later retrieval.
        """
        try:
            # Create directory if needed
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to file
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self._cookies, f, indent=2, default=str)

            logger.debug(f"Persisted cookies to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to persist cookies: {e}")
            raise StorageException(f"Failed to persist cookies: {str(e)}") from e

    def clear(self) -> None:
        """Clear all cookies."""
        self._cookies.clear()
        logger.debug("Cleared all cookies")

    def get_all(self) -> Dict[str, Any]:
        """Get all cookies.

        Returns:
            Dictionary of all cookies
        """
        return self._cookies.copy()

    def _load_from_file(self) -> None:
        """Load cookies from file.

        Internal method to load cookies from storage file if it exists.
        """
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                self._cookies = json.load(f)
            logger.debug(f"Loaded {len(self._cookies)} cookies from {self.storage_path}")
        except Exception as e:
            logger.warning(f"Failed to load cookies: {e}")
            self._cookies = {}
