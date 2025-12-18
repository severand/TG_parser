"""Session management for request handling.

Provides SessionHandler for managing requests.Session instances
with automatic cleanup and cookie persistence.
"""

import logging
from typing import Optional

import requests

from utils.logger import Logger
from utils.exceptions import NetworkException

logger = Logger()


class SessionHandler:
    """Manage HTTP sessions with automatic cleanup.

    Provides methods to create, maintain, and close requests sessions
    with proper resource management.

    Example:
        >>> with SessionHandler.create_context() as handler:
        ...     session = handler.get_session()
        ...     response = session.get("https://example.com")
    """

    _active_session: Optional[requests.Session] = None

    @staticmethod
    def create_session() -> requests.Session:
        """Create new HTTP session.

        Returns:
            New requests.Session with default configuration

        Example:
            >>> session = SessionHandler.create_session()
            >>> response = session.get("https://example.com")
        """
        session = requests.Session()
        SessionHandler._active_session = session
        logger.debug("Created new HTTP session")
        return session

    @staticmethod
    def close_session() -> None:
        """Close active session.

        Closes the currently active session and cleans up resources.
        """
        if SessionHandler._active_session:
            SessionHandler._active_session.close()
            SessionHandler._active_session = None
            logger.debug("Closed HTTP session")

    @staticmethod
    def get_active_session() -> requests.Session:
        """Get currently active session.

        Returns:
            Active session or creates new one if none exists

        Example:
            >>> session = SessionHandler.get_active_session()
            >>> session
            <requests.Session object at 0x...>
        """
        if SessionHandler._active_session is None:
            SessionHandler.create_session()
        return SessionHandler._active_session

    @staticmethod
    def maintain_session() -> None:
        """Ensure session is active and healthy.

        Verifies session exists and is usable.
        """
        try:
            session = SessionHandler.get_active_session()
            logger.debug(f"Session is active with {len(session.cookies)} cookies")
        except Exception as e:
            logger.error(f"Session maintenance failed: {e}")
            SessionHandler._active_session = None

    @staticmethod
    def create_context():
        """Create context manager for session.

        Returns:
            Context manager for automatic session cleanup

        Example:
            >>> with SessionHandler.create_context() as handler:
            ...     session = handler.get_session()
        """
        return _SessionContext()

    @staticmethod
    def get_session_cookies() -> dict:
        """Get cookies from active session.

        Returns:
            Dictionary of session cookies
        """
        session = SessionHandler.get_active_session()
        return dict(session.cookies)


class _SessionContext:
    """Context manager for session handling."""

    def __enter__(self):
        """Enter context."""
        SessionHandler.create_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and cleanup."""
        SessionHandler.close_session()

    def get_session(self) -> requests.Session:
        """Get active session.

        Returns:
            Active requests.Session
        """
        return SessionHandler.get_active_session()
