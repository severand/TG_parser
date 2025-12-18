"""Data models for Telegram Parser using dataclasses.

Defines all core data structures used throughout the parser:
- Channel: Telegram channel metadata
- User: User/author information
- Message: Message data
- SearchResult: Search result with context
- ParsingStatistics: Parsing statistics and metrics
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass(frozen=True)
class Channel:
    """Telegram channel metadata.

    Represents a Telegram channel with its properties.

    Attributes:
        id: Unique channel identifier
        username: Channel username (handle)
        title: Channel display title
        description: Channel description
        url: Full channel URL
        followers: Number of followers/subscribers
        created_at: Channel creation timestamp
    """

    id: str
    username: str
    title: str
    description: str = ""
    url: str = ""
    followers: int = 0
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert Channel to dictionary.

        Returns:
            Dictionary representation of Channel

        Example:
            >>> channel = Channel(
            ...     id="123", username="test", title="Test Channel"
            ... )
            >>> channel.to_dict()
            {'id': '123', 'username': 'test', ...}
        """
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Channel':
        """Create Channel from dictionary.

        Args:
            data: Dictionary with channel data

        Returns:
            Channel instance

        Raises:
            KeyError: If required fields missing
            TypeError: If field types are invalid

        Example:
            >>> data = {'id': '123', 'username': 'test', 'title': 'Test'}
            >>> channel = Channel.from_dict(data)
        """
        required_fields = {'id', 'username', 'title'}
        if not required_fields.issubset(data.keys()):
            raise KeyError(f"Missing required fields: {required_fields - set(data.keys())}")

        return Channel(
            id=str(data['id']),
            username=str(data['username']),
            title=str(data['title']),
            description=str(data.get('description', '')),
            url=str(data.get('url', '')),
            followers=int(data.get('followers', 0)),
            created_at=str(data.get('created_at', '')),
        )


@dataclass(frozen=True)
class User:
    """User/author information.

    Represents a Telegram user or channel author.

    Attributes:
        id: Unique user identifier
        username: User handle/username
        first_name: User first name
        last_name: User last name
        verified: Whether user is verified
    """

    id: str
    username: str
    first_name: str = ""
    last_name: str = ""
    verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert User to dictionary.

        Returns:
            Dictionary representation of User
        """
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'User':
        """Create User from dictionary.

        Args:
            data: Dictionary with user data

        Returns:
            User instance

        Raises:
            KeyError: If required fields missing
        """
        required_fields = {'id', 'username'}
        if not required_fields.issubset(data.keys()):
            raise KeyError(f"Missing required fields: {required_fields - set(data.keys())}")

        return User(
            id=str(data['id']),
            username=str(data['username']),
            first_name=str(data.get('first_name', '')),
            last_name=str(data.get('last_name', '')),
            verified=bool(data.get('verified', False)),
        )


@dataclass(frozen=True)
class Message:
    """Telegram message data.

    Represents a single message from a Telegram channel.

    Attributes:
        id: Unique message identifier
        channel_id: Channel where message was posted
        author: Message author/user
        text: Message text content
        timestamp: Message posting timestamp
        views: Number of views (if available)
        reactions: Number/dict of reactions (if available)
    """

    id: str
    channel_id: str
    author: User
    text: str
    timestamp: str
    views: int = 0
    reactions: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert Message to dictionary.

        Returns:
            Dictionary representation of Message (author as dict)
        """
        data = asdict(self)
        data['author'] = self.author.to_dict()
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Message':
        """Create Message from dictionary.

        Args:
            data: Dictionary with message data

        Returns:
            Message instance

        Raises:
            KeyError: If required fields missing
        """
        required_fields = {'id', 'channel_id', 'author', 'text', 'timestamp'}
        if not required_fields.issubset(data.keys()):
            raise KeyError(f"Missing required fields: {required_fields - set(data.keys())}")

        # Parse author if it's a dict
        author = data['author']
        if isinstance(author, dict):
            author = User.from_dict(author)
        elif not isinstance(author, User):
            raise TypeError(f"author must be User or dict, got {type(author)}")

        return Message(
            id=str(data['id']),
            channel_id=str(data['channel_id']),
            author=author,
            text=str(data['text']),
            timestamp=str(data['timestamp']),
            views=int(data.get('views', 0)),
            reactions=int(data.get('reactions', 0)),
        )


@dataclass(frozen=True)
class SearchResult:
    """Search result with context.

    Represents a message that matched search criteria, with surrounding context.

    Attributes:
        channel: Channel where match was found
        author: Message author
        message: The matched message
        context: Extracted context around the match (surrounding text)
        match_position: Position of match in text (character index)
        relevance: Relevance score (0.0 to 1.0)
    """

    channel: Channel
    author: User
    message: Message
    context: str
    match_position: int = 0
    relevance: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert SearchResult to dictionary.

        Returns:
            Dictionary representation with nested objects as dicts
        """
        return {
            'channel': self.channel.to_dict(),
            'author': self.author.to_dict(),
            'message': self.message.to_dict(),
            'context': self.context,
            'match_position': self.match_position,
            'relevance': self.relevance,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SearchResult':
        """Create SearchResult from dictionary.

        Args:
            data: Dictionary with search result data

        Returns:
            SearchResult instance

        Raises:
            KeyError: If required fields missing
        """
        required_fields = {'channel', 'author', 'message', 'context'}
        if not required_fields.issubset(data.keys()):
            raise KeyError(f"Missing required fields: {required_fields - set(data.keys())}")

        # Parse nested objects
        channel = Channel.from_dict(data['channel']) if isinstance(data['channel'], dict) else data['channel']
        author = User.from_dict(data['author']) if isinstance(data['author'], dict) else data['author']
        message = Message.from_dict(data['message']) if isinstance(data['message'], dict) else data['message']

        return SearchResult(
            channel=channel,
            author=author,
            message=message,
            context=str(data['context']),
            match_position=int(data.get('match_position', 0)),
            relevance=float(data.get('relevance', 0.0)),
        )


@dataclass(frozen=True)
class ParsingStatistics:
    """Parsing statistics and metrics.

    Accumulates statistics about a parsing session.

    Attributes:
        total_channels: Total channels attempted to parse
        successfully_parsed: Channels successfully parsed
        failed_channels: Channels that failed to parse
        total_messages: Total messages extracted
        matches_found: Total matches found during search
        errors_count: Total errors encountered
        duration_seconds: Total parsing duration in seconds
        rate_limits_hit: Number of rate limit events
        captcha_count: Number of captcha challenges
    """

    total_channels: int = 0
    successfully_parsed: int = 0
    failed_channels: int = 0
    total_messages: int = 0
    matches_found: int = 0
    errors_count: int = 0
    duration_seconds: float = 0.0
    rate_limits_hit: int = 0
    captcha_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert ParsingStatistics to dictionary.

        Returns:
            Dictionary representation of statistics
        """
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ParsingStatistics':
        """Create ParsingStatistics from dictionary.

        Args:
            data: Dictionary with statistics data

        Returns:
            ParsingStatistics instance
        """
        return ParsingStatistics(
            total_channels=int(data.get('total_channels', 0)),
            successfully_parsed=int(data.get('successfully_parsed', 0)),
            failed_channels=int(data.get('failed_channels', 0)),
            total_messages=int(data.get('total_messages', 0)),
            matches_found=int(data.get('matches_found', 0)),
            errors_count=int(data.get('errors_count', 0)),
            duration_seconds=float(data.get('duration_seconds', 0.0)),
            rate_limits_hit=int(data.get('rate_limits_hit', 0)),
            captcha_count=int(data.get('captcha_count', 0)),
        )

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage.

        Returns:
            Success rate as percentage (0-100)
        """
        if self.total_channels == 0:
            return 0.0
        return (self.successfully_parsed / self.total_channels) * 100

    @property
    def average_messages_per_channel(self) -> float:
        """Calculate average messages per successfully parsed channel.

        Returns:
            Average messages per channel (0.0 if no channels parsed)
        """
        if self.successfully_parsed == 0:
            return 0.0
        return self.total_messages / self.successfully_parsed
