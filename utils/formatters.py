"""Output formatters for displaying results and statistics.

Provides formatting utilities for consistent output presentation.
"""

from typing import List, Dict, Any
from data.models import SearchResult, ParsingStatistics


class OutputFormatter:
    """Format output for display and export.

    Provides methods to format results, statistics, and other data
    for console or file output.
    """

    @staticmethod
    def format_result(result: SearchResult) -> str:
        """Format single search result.

        Args:
            result: SearchResult object

        Returns:
            Formatted result string
        """
        lines = [
            f"Channel: {result.channel.title} (@{result.channel.username})",
            f"Author: {result.author.username}",
            f"Message: {result.message.text[:100]}...",
            f"Context: {result.context}",
            f"Relevance: {result.relevance:.2%}",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_results(results: List[SearchResult]) -> str:
        """Format multiple search results.

        Args:
            results: List of SearchResult objects

        Returns:
            Formatted results string
        """
        if not results:
            return "No results found"

        lines = [f"Found {len(results)} results:\n"]
        for i, result in enumerate(results, 1):
            lines.append(f"\n--- Result #{i} ---")
            lines.append(OutputFormatter.format_result(result))

        return "\n".join(lines)

    @staticmethod
    def format_statistics(stats: ParsingStatistics) -> str:
        """Format parsing statistics.

        Args:
            stats: ParsingStatistics object

        Returns:
            Formatted statistics string
        """
        lines = [
            "═" * 50,
            "PARSING STATISTICS",
            "═" * 50,
            f"Total channels: {stats.total_channels}",
            f"Successfully parsed: {stats.successfully_parsed} ({stats.success_rate:.1f}%)",
            f"Failed channels: {stats.failed_channels}",
            f"Total messages: {stats.total_messages}",
            f"Matches found: {stats.matches_found}",
            f"Errors: {stats.errors_count}",
            f"Rate limits hit: {stats.rate_limits_hit}",
            f"Captcha challenges: {stats.captcha_count}",
            f"Duration: {stats.duration_seconds:.2f}s",
            f"Avg messages/channel: {stats.average_messages_per_channel:.1f}",
            "═" * 50,
        ]
        return "\n".join(lines)
