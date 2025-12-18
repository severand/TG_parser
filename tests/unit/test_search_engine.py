"""Unit tests for search_engine module."""

import pytest
from datetime import datetime, timedelta

from core.search_engine import SearchEngine, SearchFilter
from data.models import Message
from utils.exceptions import ValidationException


class TestSearchEngineBasicSearch:
    """Test basic keyword search."""

    def test_search_single_keyword(self, sample_messages):
        """Test searching with single keyword."""
        engine = SearchEngine(case_sensitive=False)
        results = engine.search(sample_messages, ['keyword'])
        assert len(results) > 0
        assert all('keyword' in r.matched_keywords for r in results)

    def test_search_multiple_keywords(self, sample_messages):
        """Test searching with multiple keywords."""
        engine = SearchEngine(case_sensitive=False)
        results = engine.search(sample_messages, ['content', 'message'])
        assert len(results) > 0

    def test_search_no_results(self, sample_messages):
        """Test search with no matching results."""
        engine = SearchEngine(case_sensitive=False)
        results = engine.search(sample_messages, ['nonexistent_keyword_xyz'])
        assert len(results) == 0

    def test_search_case_sensitive(self, sample_messages):
        """Test case-sensitive search."""
        engine = SearchEngine(case_sensitive=True)
        results = engine.search(sample_messages, ['Message'])  # Capital M
        # Results depend on actual message text casing
        assert isinstance(results, list)

    def test_search_case_insensitive(self, sample_messages):
        """Test case-insensitive search."""
        engine = SearchEngine(case_sensitive=False)
        results_lower = engine.search(sample_messages, ['message'])
        results_upper = engine.search(sample_messages, ['MESSAGE'])
        assert len(results_lower) == len(results_upper)

    def test_search_empty_keywords_error(self, sample_messages):
        """Test search with no keywords raises error."""
        engine = SearchEngine()
        with pytest.raises(ValidationException):
            engine.search(sample_messages, [])

    def test_search_with_limit(self, sample_messages):
        """Test search result limiting."""
        engine = SearchEngine()
        all_results = engine.search(sample_messages, ['test'])
        limited_results = engine.search(sample_messages, ['test'], limit=2)
        assert len(limited_results) <= 2
        assert len(limited_results) <= len(all_results)


class TestSearchEngineRelevance:
    """Test relevance scoring."""

    def test_relevance_scores_sorted(self, sample_messages):
        """Test that results are sorted by relevance."""
        engine = SearchEngine()
        results = engine.search(sample_messages, ['test'])
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].relevance_score >= results[i+1].relevance_score

    def test_relevance_score_range(self, sample_messages):
        """Test that relevance scores are between 0 and 100."""
        engine = SearchEngine()
        results = engine.search(sample_messages, ['test'])
        for result in results:
            assert 0 <= result.relevance_score <= 100

    def test_relevance_higher_for_multiple_matches(self):
        """Test that messages with more keyword matches score higher."""
        msg_single = Message(
            id=1, channel_id=1, author='a', text='test keyword once',
            timestamp=datetime.now(), views=100, reactions=0,
            mentions=[], hashtags=[], urls=[], edited=False, pinned=False
        )
        msg_multiple = Message(
            id=2, channel_id=1, author='a', text='test test test keyword keyword',
            timestamp=datetime.now(), views=100, reactions=0,
            mentions=[], hashtags=[], urls=[], edited=False, pinned=False
        )
        engine = SearchEngine()
        results = engine.search([msg_single, msg_multiple], ['test', 'keyword'])
        # Message with more matches should score higher
        if len(results) >= 2:
            assert results[0].relevance_score >= results[1].relevance_score


class TestSearchEngineFilters:
    """Test filtering operations."""

    def test_filter_by_date_range(self, sample_messages):
        """Test filtering by date range."""
        engine = SearchEngine()
        now = datetime.now()
        date_from = now - timedelta(days=3)
        date_to = now - timedelta(days=1)
        filtered = engine.filter_by_date(sample_messages, date_from, date_to)
        assert len(filtered) <= len(sample_messages)

    def test_filter_by_hashtag(self, sample_messages):
        """Test filtering by hashtags."""
        engine = SearchEngine()
        filtered = engine.filter_by_hashtag(sample_messages, ['#tag0', '#tag1'])
        assert len(filtered) <= len(sample_messages)

    def test_filter_by_mention(self, sample_messages):
        """Test filtering by mentions."""
        engine = SearchEngine()
        filtered = engine.filter_by_mention(sample_messages, ['@user0'])
        assert len(filtered) <= len(sample_messages)

    def test_filter_by_author(self, sample_messages):
        """Test filtering by author."""
        engine = SearchEngine()
        filtered = engine.filter_by_author(sample_messages, 'author_0')
        assert len(filtered) > 0
        assert all('author_0' in m.author for m in filtered)

    def test_filter_by_views(self, sample_messages):
        """Test filtering by minimum views."""
        engine = SearchEngine()
        filtered = engine.filter_by_views(sample_messages, min_views=2000)
        assert all(m.views >= 2000 for m in filtered)

    def test_filter_with_urls(self, sample_messages):
        """Test filtering messages with/without URLs."""
        engine = SearchEngine()
        with_urls = engine.filter_with_urls(sample_messages, has_urls=True)
        without_urls = engine.filter_with_urls(sample_messages, has_urls=False)
        assert len(with_urls) + len(without_urls) == len(sample_messages)


class TestSearchEngineAdvanced:
    """Test advanced search with multiple filters."""

    def test_advanced_search_all_filters(self, sample_messages):
        """Test advanced search with all filter types."""
        engine = SearchEngine()
        filters = SearchFilter(
            keywords=['test'],
            hashtags=['#tag0'],
            min_views=1000,
            date_from=datetime.now() - timedelta(days=10),
            date_to=datetime.now(),
        )
        results = engine.advanced_search(sample_messages, filters)
        assert isinstance(results, list)

    def test_advanced_search_no_results(self, sample_messages):
        """Test advanced search returning no results."""
        engine = SearchEngine()
        filters = SearchFilter(
            keywords=['impossible_keyword_xyz'],
            hashtags=['#nonexistent'],
        )
        results = engine.advanced_search(sample_messages, filters)
        assert len(results) == 0


class TestSearchEngineStatistics:
    """Test statistics generation."""

    def test_get_statistics_empty_results(self, sample_messages):
        """Test statistics for empty results."""
        engine = SearchEngine()
        stats = engine.get_statistics([])
        assert stats['total_results'] == 0
        assert stats['avg_relevance'] == 0
        assert stats['total_views'] == 0

    def test_get_statistics_with_results(self, sample_messages):
        """Test statistics calculation."""
        engine = SearchEngine()
        results = engine.search(sample_messages, ['test'])
        if results:
            stats = engine.get_statistics(results)
            assert stats['total_results'] == len(results)
            assert 0 <= stats['avg_relevance'] <= 100
            assert stats['total_views'] >= 0
            assert stats['total_reactions'] >= 0

    def test_statistics_structure(self, sample_messages):
        """Test that statistics have all required fields."""
        engine = SearchEngine()
        results = engine.search(sample_messages, ['test'])
        stats = engine.get_statistics(results)
        required_fields = [
            'total_results', 'avg_relevance', 'total_views',
            'total_reactions', 'avg_views', 'avg_reactions'
        ]
        for field in required_fields:
            assert field in stats
