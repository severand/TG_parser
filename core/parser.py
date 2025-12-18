"""Main parser orchestrator module.

This module provides:
- Multi-threaded channel parsing
- Task queue management
- Statistics collection
- Error handling and retry logic
- Progress tracking
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any
from queue import Queue
from datetime import datetime

from utils.logger import Logger
from utils.exceptions import ParserException, ValidationException
from core.channel_handler import ChannelHandler
from core.search_engine import SearchEngine, SearchFilter
from data.models import Message, ParsingStatistics
from stats.collector import StatsCollector


logger = Logger.get_instance()


class Parser:
    """Main parser orchestrator for multi-threaded parsing."""

    def __init__(
        self,
        max_workers: int = 4,
        timeout: int = 10,
        max_retries: int = 3,
    ):
        """Initialize Parser.

        Args:
            max_workers: Maximum number of concurrent threads
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries per channel
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.max_retries = max_retries
        self.stats_collector = StatsCollector()
        self.search_engine = SearchEngine(case_sensitive=False)
        self.is_running = False
        self.start_time = None
        self.lock = threading.Lock()

    def _parse_single_channel(
        self,
        channel_url: str,
        max_messages: Optional[int] = None
    ) -> Dict[str, Any]:
        """Parse single channel (worker function).

        Args:
            channel_url: Channel URL to parse
            max_messages: Maximum messages to extract

        Returns:
            Parse result dictionary
        """
        channel_handler = ChannelHandler(
            timeout=self.timeout,
            max_retries=self.max_retries,
            use_delay=True
        )

        try:
            logger.info(f"Starting parse of channel: {channel_url}")

            result = channel_handler.parse(
                channel_url,
                max_messages=max_messages
            )

            if result['success']:
                with self.lock:
                    self.stats_collector.add_parsed_channel(
                        channel_url,
                        len(result['messages'])
                    )
                    for msg in result['messages']:
                        self.stats_collector.add_message(msg)
                logger.info(
                    f"✓ Channel '{channel_url}': "
                    f"{len(result['messages'])} messages"
                )
            else:
                with self.lock:
                    self.stats_collector.add_failed_channel(
                        channel_url,
                        result['error']
                    )
                logger.error(
                    f"✗ Channel '{channel_url}' failed: {result['error']}"
                )

            return result

        except Exception as e:
            logger.error(f"Error parsing channel {channel_url}: {e}")
            with self.lock:
                self.stats_collector.add_failed_channel(
                    channel_url,
                    str(e)
                )
            return {
                'channel': None,
                'messages': [],
                'success': False,
                'error': str(e)
            }

    def parse_channels(
        self,
        channels: List[str],
        max_messages: Optional[int] = None,
        show_progress: bool = True
    ) -> List[Message]:
        """Parse multiple channels concurrently.

        Args:
            channels: List of channel URLs
            max_messages: Maximum messages per channel
            show_progress: Whether to show progress

        Returns:
            Combined list of all parsed messages
        """
        if not channels:
            raise ValidationException("No channels provided")

        logger.info(f"Starting parse of {len(channels)} channels")
        self.is_running = True
        self.start_time = datetime.now()
        all_messages = []
        results = []

        try:
            with ThreadPoolExecutor(
                max_workers=min(self.max_workers, len(channels))
            ) as executor:
                # Submit all tasks
                futures = {
                    executor.submit(
                        self._parse_single_channel,
                        channel,
                        max_messages
                    ): channel
                    for channel in channels
                }

                # Process completed tasks
                completed = 0
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=self.timeout + 10)
                        results.append(result)
                        if result['success']:
                            all_messages.extend(result['messages'])

                        completed += 1
                        if show_progress:
                            progress = (completed / len(channels)) * 100
                            logger.info(
                                f"Progress: {completed}/{len(channels)} "
                                f"({progress:.1f}%) | "
                                f"Total messages: {len(all_messages)}"
                            )

                    except Exception as e:
                        logger.error(f"Error processing future: {e}")
                        completed += 1

            logger.info(f"Parse complete: {len(all_messages)} total messages")
            return all_messages

        except Exception as e:
            logger.error(f"Critical error during parsing: {e}")
            raise ParserException(f"Failed to parse channels: {e}")
        finally:
            self.is_running = False

    def search(
        self,
        messages: List[Message],
        keywords: List[str],
        limit: Optional[int] = None,
        **filter_kwargs
    ):
        """Search through messages.

        Args:
            messages: Messages to search
            keywords: Search keywords
            limit: Maximum results
            **filter_kwargs: Additional filter parameters
                - hashtags: List[str]
                - mentions: List[str]
                - date_from: datetime
                - date_to: datetime
                - min_views: int
                - author: str
                - has_url: bool

        Returns:
            Search results list
        """
        try:
            # Create filter from kwargs
            filter_params = SearchFilter(
                keywords=keywords,
                hashtags=filter_kwargs.get('hashtags'),
                mentions=filter_kwargs.get('mentions'),
                date_from=filter_kwargs.get('date_from'),
                date_to=filter_kwargs.get('date_to'),
                min_views=filter_kwargs.get('min_views'),
                has_url=filter_kwargs.get('has_url'),
                author=filter_kwargs.get('author'),
            )

            # Perform search
            results = self.search_engine.advanced_search(
                messages,
                filter_params
            )

            # Apply limit if specified
            if limit:
                results = results[:limit]

            logger.info(
                f"Search complete: {len(results)} results for {keywords}"
            )
            return results

        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            raise ParserException(f"Search failed: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get current parsing statistics.

        Returns:
            Dictionary with statistics
        """
        stats = self.stats_collector.get_statistics()

        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            stats['duration_seconds'] = duration
            if duration > 0:
                stats['messages_per_second'] = stats['total_messages'] / duration

        return stats

    def parse_and_search(
        self,
        channels: List[str],
        keywords: List[str],
        max_messages: Optional[int] = None,
        limit: Optional[int] = None,
        **filter_kwargs
    ) -> Dict[str, Any]:
        """Parse channels and search in one operation.

        Args:
            channels: Channels to parse
            keywords: Keywords to search for
            max_messages: Max messages per channel
            limit: Max results to return
            **filter_kwargs: Additional filters

        Returns:
            Dictionary with messages, search_results, and statistics
        """
        try:
            logger.info(
                f"Starting parse & search: {len(channels)} channels, "
                f"keywords: {keywords}"
            )

            # Parse channels
            messages = self.parse_channels(
                channels,
                max_messages=max_messages,
                show_progress=True
            )

            if not messages:
                logger.warning("No messages parsed")
                return {
                    'messages': [],
                    'search_results': [],
                    'statistics': self.get_statistics(),
                    'success': True,
                    'warning': 'No messages found'
                }

            # Search in parsed messages
            search_results = self.search(
                messages,
                keywords,
                limit=limit,
                **filter_kwargs
            )

            return {
                'messages': messages,
                'search_results': search_results,
                'statistics': self.get_statistics(),
                'success': True,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error in parse_and_search: {e}")
            return {
                'messages': [],
                'search_results': [],
                'statistics': self.get_statistics(),
                'success': False,
                'error': str(e)
            }

    def get_messages_by_channel(
        self,
        messages: List[Message],
        channel_id: int
    ) -> List[Message]:
        """Get all messages from specific channel.

        Args:
            messages: All messages
            channel_id: Channel ID to filter

        Returns:
            Messages from that channel
        """
        return [m for m in messages if m.channel_id == channel_id]

    def get_messages_by_author(
        self,
        messages: List[Message],
        author: str
    ) -> List[Message]:
        """Get all messages from specific author.

        Args:
            messages: All messages
            author: Author name

        Returns:
            Messages from that author
        """
        return [
            m for m in messages
            if m.author and author.lower() in m.author.lower()
        ]

    def get_trending_messages(
        self,
        messages: List[Message],
        limit: int = 10,
        metric: str = 'views'
    ) -> List[Message]:
        """Get trending messages by metric.

        Args:
            messages: Messages to analyze
            limit: Number of top messages to return
            metric: Metric to rank by ('views' or 'reactions')

        Returns:
            Top messages sorted by metric
        """
        if metric == 'views':
            sorted_messages = sorted(
                messages,
                key=lambda m: m.views,
                reverse=True
            )
        elif metric == 'reactions':
            sorted_messages = sorted(
                messages,
                key=lambda m: m.reactions,
                reverse=True
            )
        else:
            logger.warning(f"Unknown metric: {metric}, using views")
            sorted_messages = sorted(
                messages,
                key=lambda m: m.views,
                reverse=True
            )

        return sorted_messages[:limit]

    def reset(self):
        """Reset parser state."""
        self.stats_collector = StatsCollector()
        self.is_running = False
        self.start_time = None
        logger.info("Parser reset")
