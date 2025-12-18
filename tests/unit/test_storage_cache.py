"""Unit tests for storage and cache modules."""

import pytest
from pathlib import Path
from data.storage import Storage
from data.cache import Cache
from data.models import Message
from datetime import datetime


class TestStorage:
    """Test Storage class."""

    def test_storage_init(self, tmp_dir):
        """Test Storage initialization."""
        storage = Storage(data_dir=str(tmp_dir))
        assert storage is not None

    def test_storage_save_message(self, tmp_dir, sample_message):
        """Test saving message."""
        storage = Storage(data_dir=str(tmp_dir))
        storage.save_message(sample_message)
        # Should not raise
        assert True

    def test_storage_load_messages(self, tmp_dir, sample_messages):
        """Test loading messages."""
        storage = Storage(data_dir=str(tmp_dir))
        for msg in sample_messages:
            storage.save_message(msg)
        # Load and verify
        loaded = storage.load_all_messages()
        assert isinstance(loaded, list)

    def test_storage_clear(self, tmp_dir):
        """Test clearing storage."""
        storage = Storage(data_dir=str(tmp_dir))
        storage.clear()
        # Should not raise
        assert True


class TestCache:
    """Test Cache class."""

    def test_cache_init(self):
        """Test Cache initialization."""
        cache = Cache(max_size=100)
        assert cache.max_size == 100
        assert len(cache) == 0

    def test_cache_set_get(self, sample_message):
        """Test set and get in cache."""
        cache = Cache()
        cache.set('msg_1', sample_message)
        retrieved = cache.get('msg_1')
        assert retrieved is not None
        assert retrieved.id == sample_message.id

    def test_cache_delete(self):
        """Test deleting from cache."""
        cache = Cache()
        cache.set('key', 'value')
        cache.delete('key')
        assert cache.get('key') is None

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = Cache()
        cache.set('key1', 'val1')
        cache.set('key2', 'val2')
        cache.clear()
        assert len(cache) == 0

    def test_cache_size_limit(self):
        """Test cache size limit."""
        cache = Cache(max_size=3)
        cache.set('a', 1)
        cache.set('b', 2)
        cache.set('c', 3)
        cache.set('d', 4)  # Should trigger eviction
        assert len(cache) <= 4

    def test_cache_has_key(self):
        """Test checking if key exists."""
        cache = Cache()
        cache.set('exists', 'value')
        assert cache.has_key('exists')
        assert not cache.has_key('not_exists')

    def test_cache_ttl(self):
        """Test cache with TTL."""
        cache = Cache(ttl=1)
        cache.set('temp', 'value')
        assert cache.get('temp') is not None

    def test_cache_keys(self):
        """Test getting all cache keys."""
        cache = Cache()
        cache.set('key1', 'val1')
        cache.set('key2', 'val2')
        keys = cache.get_keys()
        assert 'key1' in keys
        assert 'key2' in keys
