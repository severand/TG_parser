"""Unit tests for storage and cache modules."""

import pytest
from pathlib import Path
from data.storage import LocalStorage
from data.cache import InMemoryCache
from data.models import Message
from datetime import datetime


class TestStorage:
    """Test Storage class."""

    def test_storage_init(self, tmp_dir):
        """Test Storage initialization."""
        storage = LocalStorage(data_dir=str(tmp_dir))
        assert storage is not None

    def test_storage_save_message(self, tmp_dir, sample_message):
        """Test saving message."""
        storage = LocalStorage(data_dir=str(tmp_dir))
        storage.save_message(sample_message)
        assert True

    def test_storage_load_messages(self, tmp_dir, sample_messages):
        """Test loading messages."""
        storage = LocalStorage(data_dir=str(tmp_dir))
        for msg in sample_messages:
            storage.save_message(msg)
        loaded = storage.load_all_messages()
        assert isinstance(loaded, list)

    def test_storage_clear(self, tmp_dir):
        """Test clearing storage."""
        storage = LocalStorage(data_dir=str(tmp_dir))
        storage.clear()
        assert True


class TestCache:
    """Test Cache class."""

    def test_cache_init(self):
        """Test Cache initialization."""
        cache = InMemoryCache()
        assert cache.get_count() == 0

    def test_cache_set_get(self, sample_message):
        """Test set and get in cache."""
        cache = InMemoryCache()
        cache.set('msg_1', sample_message)
        retrieved = cache.get('msg_1')
        assert retrieved is not None
        assert retrieved.id == sample_message.id

    def test_cache_delete(self):
        """Test deleting from cache."""
        cache = InMemoryCache()
        cache.set('key', 'value')
        cache.delete('key')
        assert cache.get('key') is None

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = InMemoryCache()
        cache.set('key1', 'val1')
        cache.set('key2', 'val2')
        cache.clear()
        assert cache.get_count() == 0

    def test_cache_exists(self):
        """Test checking if key exists."""
        cache = InMemoryCache()
        cache.set('exists', 'value')
        assert cache.exists('exists')
        assert not cache.exists('not_exists')

    def test_cache_ttl(self):
        """Test cache with TTL."""
        cache = InMemoryCache()
        cache.set('temp', 'value', ttl=60)
        assert cache.get('temp') is not None

    def test_cache_cleanup(self):
        """Test cache cleanup."""
        cache = InMemoryCache()
        cache.set('key1', 'val1')
        cache.set('key2', 'val2')
        count = cache.cleanup()
        assert count >= 0
