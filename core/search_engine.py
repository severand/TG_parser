"""Search engine module for finding messages by keywords.

This module provides:
- Full-text search across messages
- Date range filtering
- Hashtag and mention filtering
- Relevance scoring
- Context extraction
"""

import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from utils.logger import Logger
from utils.exceptions import ParserException, ValidationException
from data.models import Message, SearchResult
from core.message_processor import MessageProcessor


logger = Logger.get_instance()


@dataclass
class SearchFilter:
    """Search filter parameters."""
    keywords: List[str]
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_views: Optional[int] = None
    has_url: Optional[bool] = None
    author: Optional[str] = None


class SearchEngine:
    """Search engine for finding messages."""

    def __init__(self, case_sensitive: bool = False):
        """Initialize SearchEngine.

        Args:
            case_sensitive: Whether search is case-sensitive
        """
        self.case_sensitive = case_sensitive
        self.results_cache = {}

    def _normalize_text(self, text: str) -> str:
        """Normalize text for search.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        if self.case_sensitive:
            return text
        return text.lower()

    def _contains_keyword(self, text: str, keyword: str) -> bool:
        """Check if text contains keyword (case-sensitive or not).

        Args:
            text: Text to search in
            keyword: Keyword to find

        Returns:
            True if keyword found
        """
        normalized_text = self._normalize_text(text)
        normalized_keyword = self._normalize_text(keyword)
        return normalized_keyword in normalized_text

    def _count_keyword_occurrences(self, text: str, keyword: str) -> int:
        """Count keyword occurrences in text.

        Args:
            text: Text to search in
            keyword: Keyword to count

        Returns:
            Number of occurrences
        """
        normalized_text = self._normalize_text(text)
        normalized_keyword = self._normalize_text(keyword)
        return normalized_text.count(normalized_keyword)

    def _calculate_relevance(
        self,
        message: Message,
        keywords: List[str]
    ) -> float:
        """Calculate relevance score for message.

        Factors:
        - Keyword occurrence count
        - Position of first keyword
        - Match in title vs body
        - Views and reactions

        Args:
            message: Message to score
            keywords: Keywords being searched for

        Returns:
            Relevance score (0-100)
        """
        score = 0.0
        text = message.text.lower() if not self.case_sensitive else message.text

        # Count keyword occurrences
        keyword_count = 0
        for keyword in keywords:
            keyword_count += self._count_keyword_occurrences(text, keyword)

        # Base score: keyword frequency
        score += min(keyword_count * 10, 40)

        # Position score: keywords at beginning count more
        for keyword in keywords:
            pos = self._normalize_text(text).find(
                self._normalize_text(keyword)
            )
            if pos != -1:
                # Earlier position = higher score
                position_score = max(0, 20 - (pos / len(text)) * 10)
                score += position_score

        # Engagement score: views and reactions
        view_score = min(message.views / 1000, 20)
        reaction_score = min(message.reactions * 2, 20)
        score += view_score + reaction_score

        return min(score, 100.0)

    def search(
        self,
        messages: List[Message],
        keywords: List[str],
        limit: Optional[int] = None
    ) -> List[SearchResult]:
        """Search messages by keywords.

        Args:
            messages: List of messages to search
            keywords: Keywords to search for
            limit: Maximum number of results

        Returns:
            List of SearchResult objects sorted by relevance

        Raises:
            ValidationException: If keywords invalid
        """
        if not keywords:
            raise ValidationException("At least one keyword required")

        results = []

        for message in messages:
            # Check if any keyword matches
            matches = []
            for keyword in keywords:
                if self._contains_keyword(message.text, keyword):
                    matches.append(keyword)

            if matches:
                # Calculate relevance
                relevance = self._calculate_relevance(message, keywords)

                # Get context
                context = MessageProcessor.extract_context(
                    message.text,
                    matches[0],
                    context_words=5
                )

                # Create SearchResult
                result = SearchResult(
                    message_id=message.id,
                    channel_id=message.channel_id,
                    text_snippet=message.text[:150],
                    full_text=message.text,
                    context=context or '',
                    matched_keywords=matches,
                    relevance_score=relevance,
                    timestamp=message.timestamp,
                    author=message.author,
                    views=message.views,
                    reactions=message.reactions
                )

                results.append(result)

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Apply limit
        if limit:
            results = results[:limit]

        logger.info(f"Search found {len(results)} results for: {keywords}")
        return results

    def filter_by_date(
        self,
        messages: List[Message],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Message]:
        """Filter messages by date range.

        Args:
            messages: Messages to filter
            date_from: Start date (inclusive)
            date_to: End date (inclusive)

        Returns:
            Filtered messages
        """
        filtered = messages

        if date_from:
            filtered = [m for m in filtered if m.timestamp and m.timestamp >= date_from]

        if date_to:
            filtered = [m for m in filtered if m.timestamp and m.timestamp <= date_to]

        logger.debug(f"Date filter: {len(messages)} -> {len(filtered)} messages")
        return filtered

    def filter_by_hashtag(
        self,
        messages: List[Message],
        hashtags: List[str]
    ) -> List[Message]:
        """Filter messages by hashtags.

        Args:
            messages: Messages to filter
            hashtags: Hashtags to search for

        Returns:
            Messages containing any of the hashtags
        """
        filtered = []

        for message in messages:
            msg_hashtags = MessageProcessor.extract_hashtags(message.text)
            for hashtag in hashtags:
                if hashtag.lower() in [h.lower() for h in msg_hashtags]:
                    filtered.append(message)
                    break

        logger.debug(f"Hashtag filter: {len(messages)} -> {len(filtered)} messages")
        return filtered

    def filter_by_mention(
        self,
        messages: List[Message],
        mentions: List[str]
    ) -> List[Message]:
        """Filter messages by mentions.

        Args:
            messages: Messages to filter
            mentions: Usernames to search for

        Returns:
            Messages containing any of the mentions
        """
        filtered = []

        for message in messages:
            msg_mentions = MessageProcessor.extract_mentions(message.text)
            for mention in mentions:
                # Normalize for comparison
                mention_clean = mention.lstrip('@').lower()
                if mention_clean in [m.lstrip('@').lower() for m in msg_mentions]:
                    filtered.append(message)
                    break

        logger.debug(f"Mention filter: {len(messages)} -> {len(filtered)} messages")
        return filtered

    def filter_by_author(
        self,
        messages: List[Message],
        author: str
    ) -> List[Message]:
        """Filter messages by author.

        Args:
            messages: Messages to filter
            author: Author name or username

        Returns:
            Messages from specified author
        """
        filtered = [
            m for m in messages
            if m.author and author.lower() in m.author.lower()
        ]
        logger.debug(f"Author filter: {len(messages)} -> {len(filtered)} messages")
        return filtered

    def filter_by_views(
        self,
        messages: List[Message],
        min_views: int
    ) -> List[Message]:
        """Filter messages by minimum views.

        Args:
            messages: Messages to filter
            min_views: Minimum number of views

        Returns:
            Messages with at least min_views views
        """
        filtered = [m for m in messages if m.views >= min_views]
        logger.debug(f"Views filter (>={min_views}): {len(messages)} -> {len(filtered)} messages")
        return filtered

    def filter_with_urls(
        self,
        messages: List[Message],
        has_urls: bool = True
    ) -> List[Message]:
        """Filter messages by URL presence.

        Args:
            messages: Messages to filter
            has_urls: If True, return only messages with URLs

        Returns:
            Filtered messages
        """
        if has_urls:
            filtered = [m for m in messages if m.urls]
        else:
            filtered = [m for m in messages if not m.urls]

        logger.debug(f"URL filter: {len(messages)} -> {len(filtered)} messages")
        return filtered

    def advanced_search(
        self,
        messages: List[Message],
        filter_params: SearchFilter
    ) -> List[SearchResult]:
        """Perform advanced search with multiple filters.

        Args:
            messages: Messages to search
            filter_params: Search filter parameters

        Returns:
            Filtered and ranked search results
        """
        try:
            # Apply filters
            filtered = messages

            if filter_params.date_from or filter_params.date_to:
                filtered = self.filter_by_date(
                    filtered,
                    filter_params.date_from,
                    filter_params.date_to
                )

            if filter_params.hashtags:
                filtered = self.filter_by_hashtag(filtered, filter_params.hashtags)

            if filter_params.mentions:
                filtered = self.filter_by_mention(filtered, filter_params.mentions)

            if filter_params.author:
                filtered = self.filter_by_author(filtered, filter_params.author)

            if filter_params.min_views:
                filtered = self.filter_by_views(filtered, filter_params.min_views)

            if filter_params.has_url is not None:
                filtered = self.filter_with_urls(filtered, filter_params.has_url)

            # Perform keyword search on filtered results
            results = self.search(
                filtered,
                filter_params.keywords
            )

            logger.info(
                f"Advanced search complete: "
                f"{len(messages)} -> {len(filtered)} -> {len(results)} results"
            )
            return results

        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            raise ParserException(f"Advanced search failed: {e}")

    def get_statistics(
        self,
        results: List[SearchResult]
    ) -> Dict[str, Any]:
        """Get statistics for search results.

        Args:
            results: Search results

        Returns:
            Dictionary with statistics
        """
        if not results:
            return {
                'total_results': 0,
                'avg_relevance': 0,
                'total_views': 0,
                'total_reactions': 0,
                'avg_views': 0,
                'avg_reactions': 0,
            }

        avg_relevance = sum(r.relevance_score for r in results) / len(results)
        total_views = sum(r.views for r in results)
        total_reactions = sum(r.reactions for r in results)
        avg_views = total_views / len(results) if results else 0
        avg_reactions = total_reactions / len(results) if results else 0

        return {
            'total_results': len(results),
            'avg_relevance': round(avg_relevance, 2),
            'total_views': total_views,
            'total_reactions': total_reactions,
            'avg_views': round(avg_views, 1),
            'avg_reactions': round(avg_reactions, 2),
        }
