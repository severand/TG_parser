"""Message processor module for parsing Telegram HTML content.

This module extracts text, metadata, and structured information from
Telegram message HTML. It handles:
- Text content extraction (with proper encoding)
- Metadata extraction (author, timestamp, reactions)
- Message ID and channel ID parsing
- Context and related information
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

from utils.logger import Logger
from utils.exceptions import (
    ParserException,
    ValidationException,
)
from data.models import Message, User


logger = Logger.get_instance()


class MessageProcessor:
    """Processes and parses Telegram message HTML content."""

    # Regex patterns
    TIMESTAMP_PATTERN = r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})'
    MESSAGE_ID_PATTERN = r'message-(\d+)'
    USER_MENTION_PATTERN = r'@([a-zA-Z0-9_]+)'
    HASHTAG_PATTERN = r'#([a-zA-Z0-9_]+)'
    URL_PATTERN = r'https?://[^\s]+'

    @staticmethod
    def extract_text(html: str) -> str:
        """Extract plain text from HTML message.

        Args:
            html: HTML string containing message content

        Returns:
            Plain text extracted from HTML

        Raises:
            ParserException: If HTML parsing fails
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script and style elements
            for element in soup(['script', 'style']):
                element.decompose()

            # Get text
            text = soup.get_text(separator=' ', strip=True)

            # Clean up extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()

            logger.debug(f"Extracted text length: {len(text)} chars")
            return text

        except Exception as e:
            logger.error(f"Error extracting text from HTML: {e}")
            raise ParserException(f"Failed to extract text from HTML: {e}")

    @staticmethod
    def extract_metadata(html: str) -> Dict[str, Any]:
        """Extract metadata from message HTML.

        Extracts: timestamp, author, message ID, reactions, views, etc.

        Args:
            html: HTML string containing message

        Returns:
            Dictionary with metadata

        Raises:
            ParserException: If metadata extraction fails
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            metadata = {
                'timestamp': None,
                'author': None,
                'message_id': None,
                'views': None,
                'reactions': [],
                'reply_to': None,
                'pinned': False,
                'edited': False,
            }

            # Extract timestamp from data attribute
            time_element = soup.find('time')
            if time_element:
                datetime_str = time_element.get('datetime')
                if datetime_str:
                    metadata['timestamp'] = MessageProcessor.parse_timestamp(
                        datetime_str
                    )

            # Extract message ID from div id
            message_div = soup.find('div', {'class': 'message'})
            if message_div:
                div_id = message_div.get('id', '')
                match = re.search(MessageProcessor.MESSAGE_ID_PATTERN, div_id)
                if match:
                    metadata['message_id'] = int(match.group(1))

            # Extract author name
            author_elem = soup.find('a', {'class': 'user'})
            if author_elem:
                metadata['author'] = author_elem.get_text(strip=True)
            else:
                # Try to find author in data attribute
                author_elem = soup.find('div', {'class': 'from'})
                if author_elem:
                    metadata['author'] = author_elem.get_text(strip=True)

            # Extract view count
            views_elem = soup.find('span', {'class': 'views'})
            if views_elem:
                views_text = views_elem.get_text()
                try:
                    metadata['views'] = int(
                        re.search(r'\d+', views_text).group()
                    )
                except (ValueError, AttributeError):
                    pass

            # Extract reactions
            reactions_elem = soup.find('div', {'class': 'reactions'})
            if reactions_elem:
                for reaction in reactions_elem.find_all('span', {'class': 'reaction'}):
                    emoji = reaction.get('data-emoji')
                    count = reaction.get_text()
                    try:
                        count = int(count)
                        metadata['reactions'].append({
                            'emoji': emoji,
                            'count': count
                        })
                    except (ValueError, TypeError):
                        pass

            # Check for edited indicator
            if 'edited' in html.lower() or soup.find('span', {'class': 'edited'}):
                metadata['edited'] = True

            # Check for pinned indicator
            if 'pinned' in html.lower() or soup.find('span', {'class': 'pinned'}):
                metadata['pinned'] = True

            logger.debug(f"Extracted metadata: {metadata}")
            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            raise ParserException(f"Failed to extract metadata: {e}")

    @staticmethod
    def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object.

        Supports formats:
        - ISO 8601: 2025-12-18T10:30:45
        - Unix timestamp: 1703079045
        - RFC 2822: Thu, 18 Dec 2025 10:30:45

        Args:
            timestamp_str: Timestamp string

        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not timestamp_str:
            return None

        try:
            # Try ISO 8601
            match = re.match(MessageProcessor.TIMESTAMP_PATTERN, timestamp_str)
            if match:
                year, month, day, hour, minute, second = map(int, match.groups())
                return datetime(year, month, day, hour, minute, second)

            # Try Unix timestamp
            try:
                unix_ts = float(timestamp_str)
                return datetime.fromtimestamp(unix_ts)
            except (ValueError, OSError):
                pass

            # Try parsing with common formats
            formats = [
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%d %b %Y %H:%M:%S',
                '%a, %d %b %Y %H:%M:%S',
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue

            logger.warning(f"Could not parse timestamp: {timestamp_str}")
            return None

        except Exception as e:
            logger.error(f"Error parsing timestamp '{timestamp_str}': {e}")
            return None

    @staticmethod
    def extract_mentions(text: str) -> list[str]:
        """Extract user mentions from text.

        Args:
            text: Message text

        Returns:
            List of mentioned usernames
        """
        matches = re.findall(MessageProcessor.USER_MENTION_PATTERN, text)
        return list(set(matches))  # Remove duplicates

    @staticmethod
    def extract_hashtags(text: str) -> list[str]:
        """Extract hashtags from text.

        Args:
            text: Message text

        Returns:
            List of hashtags
        """
        matches = re.findall(MessageProcessor.HASHTAG_PATTERN, text)
        return list(set(matches))  # Remove duplicates

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """Extract URLs from text.

        Args:
            text: Message text

        Returns:
            List of URLs
        """
        matches = re.findall(MessageProcessor.URL_PATTERN, text)
        return list(set(matches))  # Remove duplicates

    @staticmethod
    def extract_context(
        text: str,
        keyword: str,
        context_words: int = 5
    ) -> Optional[str]:
        """Extract context around keyword in text.

        Args:
            text: Full message text
            keyword: Keyword to find
            context_words: Number of words before and after keyword

        Returns:
            Context string or None if keyword not found
        """
        try:
            # Case-insensitive search
            text_lower = text.lower()
            keyword_lower = keyword.lower()

            index = text_lower.find(keyword_lower)
            if index == -1:
                return None

            # Split into words
            words = text.split()
            keyword_word_index = len(text[:index].split()) - 1

            # Get context
            start_idx = max(0, keyword_word_index - context_words)
            end_idx = min(len(words), keyword_word_index + context_words + 1)

            context_words_list = words[start_idx:end_idx]
            context = ' '.join(context_words_list)

            return f"...{context}..."

        except Exception as e:
            logger.error(f"Error extracting context: {e}")
            return None

    @staticmethod
    def parse_message(
        html: str,
        channel_id: int,
        message_id: Optional[int] = None
    ) -> Message:
        """Parse complete message from HTML to Message object.

        Args:
            html: Message HTML content
            channel_id: ID of the channel containing this message
            message_id: Optional message ID (extracted if not provided)

        Returns:
            Message object

        Raises:
            ParserException: If message parsing fails
        """
        try:
            text = MessageProcessor.extract_text(html)
            metadata = MessageProcessor.extract_metadata(html)

            # Use provided message_id or extract from metadata
            msg_id = message_id or metadata.get('message_id')
            if not msg_id:
                raise ValidationException("Message ID is required")

            # Create author User object
            author_name = metadata.get('author') or 'Unknown'
            author = User(
                id=str(channel_id),
                username=author_name,
                first_name=author_name
            )

            # Create Message object
            message = Message(
                id=str(msg_id),
                channel_id=str(channel_id),
                author=author,
                text=text,
                timestamp=str(metadata.get('timestamp') or ''),
                views=metadata.get('views') or 0,
                reactions=len(metadata.get('reactions', [])),
                mentions=tuple(MessageProcessor.extract_mentions(text)),
                hashtags=tuple(MessageProcessor.extract_hashtags(text)),
                urls=tuple(MessageProcessor.extract_urls(text)),
                edited=metadata.get('edited', False),
                pinned=metadata.get('pinned', False),
            )

            logger.debug(f"Parsed message {msg_id}: {len(text)} chars")
            return message

        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            raise ParserException(f"Failed to parse message: {e}")
