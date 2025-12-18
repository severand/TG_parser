"""Statistics collector for tracking parsing metrics."""

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

    def end(self):
        """Mark end of parsing."""
        self.end_time = datetime.now()

    def add_parsed_channel(self, channel_url: str, message_count: int):
        """Record successfully parsed channel."""
        self.parsed_channels.append(channel_url)
        self.channel_message_counts[channel_url] = message_count

    def add_failed_channel(self, channel_url: str, error_message: str):
        """Record failed channel."""
        self.failed_channels.append(channel_url)
        error = ParseError(
            channel_url=channel_url,
            error_message=error_message
        )
        self.errors.append(error)

    def add_message(self, message: Message):
        """Record parsed message."""
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
        """Get current statistics."""
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
            'total_messages': self.total_messages,
            'total_views': self.total_views,
            'total_reactions': self.total_reactions,
            'avg_views_per_message': self.total_views / self.total_messages if self.total_messages > 0 else 0,
            'duration_seconds': duration_seconds,
            'messages_per_second': messages_per_second,
            'success_rate': (len(self.parsed_channels) / (len(self.parsed_channels) + len(self.failed_channels)) * 100) if (len(self.parsed_channels) + len(self.failed_channels)) > 0 else 0,
        }

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


# Alias for backward compatibility
StatisticsCollector = StatsCollector
