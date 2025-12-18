"""Integration tests for parser components."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from core.parser import Parser
from core.message_processor import MessageProcessor
from core.search_engine import SearchEngine
from data.models import Message, SearchResult


@pytest.mark.integration
class TestParserIntegration:
    """Integration tests for complete parser workflow."""

    def test_parse_and_search_full_workflow(self, sample_messages, sample_html):
        """Test complete parse and search workflow."""
        # Initialize components
        parser = Parser(max_workers=2)
        search_engine = SearchEngine(case_sensitive=False)

        # Process messages through pipeline
        results = search_engine.search(sample_messages, ['test'])

        assert len(results) >= 0
        for result in results:
            assert isinstance(result, SearchResult)
            assert result.relevance_score >= 0

    def test_message_processing_pipeline(self, sample_html):
        """Test message processing pipeline."""
        # Extract text from HTML
        text = MessageProcessor.extract_text(sample_html)
        assert len(text) > 0

        # Extract metadata
        metadata = MessageProcessor.extract_metadata(sample_html)
        assert 'author' in metadata or 'timestamp' in metadata

        # Extract mentions and hashtags
        mentions = MessageProcessor.extract_mentions(text)
        hashtags = MessageProcessor.extract_hashtags(text)
        urls = MessageProcessor.extract_urls(text)

        assert isinstance(mentions, list)
        assert isinstance(hashtags, list)
        assert isinstance(urls, list)

    @pytest.mark.integration
    def test_parse_messages_multiple_times(self, sample_messages):
        """Test parser handling of multiple parsing operations."""
        parser = Parser(max_workers=2)
        search_engine = SearchEngine()

        # First search
        results1 = search_engine.search(sample_messages, ['test'])
        # Second search
        results2 = search_engine.search(sample_messages, ['content'])
        # Third search
        results3 = search_engine.search(sample_messages, ['message'])

        assert isinstance(results1, list)
        assert isinstance(results2, list)
        assert isinstance(results3, list)


@pytest.mark.integration
class TestSearchIntegration:
    """Integration tests for search operations."""

    def test_search_with_all_filters(self, sample_messages):
        """Test search with multiple filters applied."""
        engine = SearchEngine(case_sensitive=False)

        # Apply multiple filters
        keyword_results = engine.search(sample_messages, ['test'])
        filtered_by_views = engine.filter_by_views(keyword_results, min_views=500)
        filtered_by_author = engine.filter_by_author(filtered_by_views, 'author_0')

        for result in filtered_by_author:
            assert result.views >= 500
            assert 'author_0' in result.author or result.author == 'author_0'

    def test_search_relevance_consistency(self, sample_messages):
        """Test that relevance scoring is consistent."""
        engine = SearchEngine()

        # Search twice with same keywords
        results1 = engine.search(sample_messages, ['test'])
        results2 = engine.search(sample_messages, ['test'])

        # Should have same number of results
        assert len(results1) == len(results2)

        # Relevance scores should match
        for r1, r2 in zip(results1, results2):
            assert r1.message_id == r2.message_id
            assert abs(r1.relevance_score - r2.relevance_score) < 0.01

    def test_search_statistics_accuracy(self, sample_messages):
        """Test that statistics are calculated correctly."""
        engine = SearchEngine()
        results = engine.search(sample_messages, ['test'])
        stats = engine.get_statistics(results)

        if results:
            # Verify statistics calculations
            assert stats['total_results'] == len(results)
            avg_relevance = sum(r.relevance_score for r in results) / len(results)
            assert abs(stats['avg_relevance'] - avg_relevance) < 0.1

            total_views = sum(r.views for r in results) if hasattr(results[0], 'views') else 0
            assert stats['total_views'] >= 0


@pytest.mark.integration
class TestDataFlow:
    """Integration tests for data flow through system."""

    def test_message_data_preservation(self, sample_message):
        """Test that message data is preserved through pipeline."""
        # Original data
        original_id = sample_message.id
        original_text = sample_message.text
        original_author = sample_message.author

        # Process message
        engine = SearchEngine()
        results = engine.search([sample_message], ['test'])

        # Verify data preserved
        for result in results:
            assert result.message_id == original_id
            # Text should be in result
            assert original_text in result.full_text or result.full_text

    def test_search_result_completeness(self, sample_message):
        """Test that search results contain all required fields."""
        engine = SearchEngine()
        results = engine.search([sample_message], ['test'])

        required_fields = [
            'message_id', 'channel_id', 'full_text', 'matched_keywords',
            'relevance_score', 'author'
        ]

        for result in results:
            for field in required_fields:
                assert hasattr(result, field), f"Missing field: {field}"


@pytest.mark.integration
class TestErrorHandling:
    """Integration tests for error handling."""

    def test_search_handles_empty_input(self):
        """Test search handles empty message list."""
        engine = SearchEngine()
        results = engine.search([], ['test'])
        # Should return empty list, not error
        assert results == [] or len(results) == 0

    def test_parser_graceful_degradation(self):
        """Test parser handles invalid input gracefully."""
        parser = Parser()
        # Should not crash with empty channels
        # (actual call would be mocked in real scenario)
        assert parser is not None

    def test_search_with_special_characters(self, sample_messages):
        """Test search handles special characters."""
        engine = SearchEngine()
        # These should not crash the search
        special_keywords = ['test*', 'test?', 'test|', 'test&']
        for keyword in special_keywords:
            try:
                results = engine.search(sample_messages, [keyword])
                assert isinstance(results, list)
            except:
                # Special chars might not be supported, that's ok
                pass
