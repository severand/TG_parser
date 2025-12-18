"""Statistics collector for tracking parsing metrics.

Collects:
- Parsing statistics (channels, messages, errors)
- Performance metrics
- Error tracking
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict

from utils.logger import Logger
from data.models import Message


logger = Logger.get_instance()


@dataclass
class ParseError:
    """Represents a parse error."""
    channel_url: str
    error_message: str
    timestamp: datetime = field(default_factory=datetime.now)
    error_type: str = "unknown"


class StatsCollector:
    """Collects parsing statistics."""

    def __init__(self):
        """Initialize StatsCollector."""
        self.parsed_channels: List[str] = []
        self.failed_channels: List[str] = []
        self.total_messages = 0
        self.message_ids: set = set()
        self.errors: List[ParseError] = []
        self.channel_message_counts: Dict[str, int] = defaultdict(int)
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.total_views = 0
        self.total_reactions = 0
        self.authors: set = set()
        self.hashtags: set = set()
        self.mentions: set = set()

    def start(self):
        """Mark start of parsing."""
        self.start_time = datetime.now()
        logger.debug("Statistics collection started")

    def end(self):
        """Mark end of parsing."""
        self.end_time = datetime.now()
        logger.debug("Statistics collection ended")

    def add_parsed_channel(self, channel_url: str, message_count: int):
        """Record successfully parsed channel.

        Args:
            channel_url: Channel URL
            message_count: Number of messages parsed
        """
        self.parsed_channels.append(channel_url)
        self.channel_message_counts[channel_url] = message_count
        logger.debug(f"Added parsed channel: {channel_url} ({message_count} messages)")

    def add_failed_channel(self, channel_url: str, error_message: str):
        """Record failed channel.

        Args:
            channel_url: Channel URL
            error_message: Error description
        """
        self.failed_channels.append(channel_url)
        error = ParseError(
            channel_url=channel_url,
            error_message=error_message
        )
        self.errors.append(error)
        logger.debug(f"Added failed channel: {channel_url} ({error_message})")

    def add_message(self, message: Message):
        """Record parsed message.

        Args:
            message: Message object
        """
        if message.id not in self.message_ids:
            self.message_ids.add(message.id)
            self.total_messages += 1
            self.total_views += message.views
            self.total_reactions += message.reactions

            if message.author:
                self.authors.add(message.author)
            if message.hashtags:
                self.hashtags.update(message.hashtags)
            if message.mentions:
                self.mentions.update(message.mentions)

    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics.

        Returns:
            Dictionary with statistics
        """
        duration_seconds = 0
        if self.start_time and self.end_time:
            duration_seconds = (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            duration_seconds = (datetime.now() - self.start_time).total_seconds()

        messages_per_second = 0
        if duration_seconds > 0:
            messages_per_second = self.total_messages / duration_seconds

        return {
            'total_channels_parsed': len(self.parsed_channels),
            'total_channels_failed': len(self.failed_channels),
            'total_channels_attempted': len(self.parsed_channels) + len(self.failed_channels),
            'total_messages': self.total_messages,
            'total_unique_messages': len(self.message_ids),
            'total_views': self.total_views,
            'total_reactions': self.total_reactions,
            'avg_views_per_message': self.total_views / self.total_messages if self.total_messages > 0 else 0,
            'avg_reactions_per_message': self.total_reactions / self.total_messages if self.total_messages > 0 else 0,
            'total_authors': len(self.authors),
            'total_unique_hashtags': len(self.hashtags),
            'total_unique_mentions': len(self.mentions),
            'duration_seconds': duration_seconds,
            'messages_per_second': messages_per_second,
            'success_rate': (len(self.parsed_channels) / (len(self.parsed_channels) + len(self.failed_channels)) * 100) if (len(self.parsed_channels) + len(self.failed_channels)) > 0 else 0,
        }

    def get_errors(self) -> List[Dict[str, Any]]:
        """Get list of errors.

        Returns:
            List of error dictionaries
        """
        return [
            {
                'channel': e.channel_url,
                'error': e.error_message,
                'timestamp': e.timestamp.isoformat(),
                'type': e.error_type,
            }
            for e in self.errors
        ]

    def get_channel_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary by channel.

        Returns:
            Dictionary with channel summaries
        """
        summary = {}

        for channel in self.parsed_channels:
            summary[channel] = {
                'status': 'parsed',
                'message_count': self.channel_message_counts.get(channel, 0),
            }

        for channel in self.failed_channels:
            # Find error for this channel
            error_msg = "Unknown error"
            for error in self.errors:
                if error.channel_url == channel:
                    error_msg = error.error_message
                    break
            summary[channel] = {
                'status': 'failed',
                'error': error_msg,
            }

        return summary

    def get_top_channels_by_messages(
        self,
        limit: int = 10
    ) -> List[tuple]:
        """Get top channels by message count.

        Args:
            limit: Maximum results

        Returns:
            List of (channel_url, message_count) tuples
        """
        sorted_channels = sorted(
            self.channel_message_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_channels[:limit]

    def reset(self):
        """Reset all statistics."""
        self.parsed_channels.clear()
        self.failed_channels.clear()
        self.total_messages = 0
        self.message_ids.clear()
        self.errors.clear()
        self.channel_message_counts.clear()
        self.start_time = None
        self.end_time = None
        self.total_views = 0
        self.total_reactions = 0
        self.authors.clear()
        self.hashtags.clear()
        self.mentions.clear()
        logger.debug("Statistics collector reset")

    def print_summary(self):
        """Print statistics summary to logger."""
        stats = self.get_statistics()
        logger.info("="*50)
        logger.info("PARSING STATISTICS")
        logger.info("="*50)
        for key, value in stats.items():
            if isinstance(value, float):
                logger.info(f"{key}: {value:.2f}")
            else:
                logger.info(f"{key}: {value}")
        logger.info("="*50)
