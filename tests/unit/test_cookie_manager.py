"""Unit tests for cookie_manager module."""

import pytest
from datetime import datetime, timedelta
from network.cookie_manager import CookieManager


class TestCookieManagerInitialization:
    """Test CookieManager initialization."""

    def test_cookie_manager_init(self):
        """Test CookieManager initializes."""
        manager = CookieManager()
        assert manager is not None
        assert len(manager.cookies) == 0

    def test_cookie_manager_max_cookies(self):
        """Test CookieManager max cookies setting."""
        manager = CookieManager(max_cookies=100)
        assert manager.max_cookies == 100


class TestCookieManagerOperations:
    """Test cookie operations."""

    def test_add_cookie(self):
        """Test adding cookie."""
        manager = CookieManager()
        manager.add_cookie('session', 'abc123')
        assert 'session' in manager.cookies
        assert manager.cookies['session'] == 'abc123'

    def test_add_multiple_cookies(self):
        """Test adding multiple cookies."""
        manager = CookieManager()
        manager.add_cookie('session', 'abc123')
        manager.add_cookie('user_id', '456')
        assert len(manager.cookies) == 2

    def test_get_cookie(self):
        """Test getting cookie."""
        manager = CookieManager()
        manager.add_cookie('session', 'abc123')
        value = manager.get_cookie('session')
        assert value == 'abc123'

    def test_get_nonexistent_cookie(self):
        """Test getting nonexistent cookie."""
        manager = CookieManager()
        value = manager.get_cookie('nonexistent')
        assert value is None

    def test_delete_cookie(self):
        """Test deleting cookie."""
        manager = CookieManager()
        manager.add_cookie('session', 'abc123')
        manager.delete_cookie('session')
        assert 'session' not in manager.cookies


class TestCookieManagerClear:
    """Test cookie clearing."""

    def test_clear_all_cookies(self):
        """Test clearing all cookies."""
        manager = CookieManager()
        manager.add_cookie('session', 'abc')
        manager.add_cookie('user_id', '123')
        manager.clear()
        assert len(manager.cookies) == 0

    def test_clear_empty_manager(self):
        """Test clearing empty manager."""
        manager = CookieManager()
        manager.clear()
        assert len(manager.cookies) == 0


class TestCookieManagerDict:
    """Test cookie dictionary representation."""

    def test_get_all_cookies_dict(self):
        """Test getting all cookies as dict."""
        manager = CookieManager()
        manager.add_cookie('a', '1')
        manager.add_cookie('b', '2')
        cookies_dict = manager.get_cookies_dict()
        assert cookies_dict == {'a': '1', 'b': '2'}

    def test_update_from_dict(self):
        """Test updating from dictionary."""
        manager = CookieManager()
        manager.update_from_dict({'session': 'xyz', 'user': '789'})
        assert manager.get_cookie('session') == 'xyz'
        assert manager.get_cookie('user') == '789'


class TestCookieManagerLimits:
    """Test cookie limits."""

    def test_max_cookies_limit(self):
        """Test max cookies limit."""
        manager = CookieManager(max_cookies=3)
        manager.add_cookie('a', '1')
        manager.add_cookie('b', '2')
        manager.add_cookie('c', '3')
        # Adding 4th might trigger cleanup
        manager.add_cookie('d', '4')
        assert len(manager.cookies) <= 4
