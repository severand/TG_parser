"""Channel handler module for parsing Telegram channels.

This module handles:
- Fetching channel content
- Parsing multiple messages from a channel
- Extracting channel metadata (title, description, followers)
- Handling errors and blocked channels
- Rate limit detection
"""

import time
from typing import Optional, List
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from network.http_client import HTTPClient
from network.headers_rotator import HeadersRotator
from network.delay_generator import DelayGenerator
from utils.logger import Logger
from utils.exceptions import (
    ParserException,
    NetworkException,
    ValidationException,
)
from utils.validators import validate_channel_url
from data.models import Channel, Message
from core.message_processor import MessageProcessor


logger = Logger.get_instance()


class ChannelHandler:
    """Handles parsing of individual Telegram channels."""

    BASE_URL = "https://t.me"
    MESSAGES_SELECTOR = "div.tgme_widget_message"
    CHANNEL_INFO_SELECTOR = "div.tgme_channel_info"

    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 3,
        use_delay: bool = True
    ):
        """Initialize ChannelHandler.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            use_delay: Whether to use random delays between requests
        """
        self.http_client = HTTPClient(
            timeout=timeout,
            max_retries=max_retries
        )
        self.headers_rotator = HeadersRotator()
        self.delay_generator = DelayGenerator()
        self.use_delay = use_delay
        self.channel_url = None
        self.channel_data = None

    def validate(self, channel_url: str) -> bool:
        """Validate channel URL format.

        Args:
            channel_url: URL to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not validate_channel_url(channel_url):
                logger.error(f"Invalid channel URL: {channel_url}")
                return False

            # Normalize URL
            if not channel_url.startswith('http'):
                channel_url = f"{self.BASE_URL}/{channel_url}"

            self.channel_url = channel_url
            logger.debug(f"Channel URL validated: {channel_url}")
            return True

        except Exception as e:
            logger.error(f"Error validating channel URL: {e}")
            return False

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch channel page HTML.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if fetch fails

        Raises:
            NetworkException: If network error occurs
        """
        try:
            headers = self.headers_rotator.get_random_headers()

            if self.use_delay:
                delay = self.delay_generator.get_delay(1, 3)
                logger.debug(f"Applying delay: {delay:.2f}s")
                time.sleep(delay)

            logger.info(f"Fetching: {url}")
            response = self.http_client.get(url, headers=headers)

            if response.status_code == 404:
                raise NetworkException(f"Channel not found (404): {url}")
            elif response.status_code == 403:
                raise NetworkException(f"Access forbidden (403): {url}")
            elif response.status_code == 429:
                raise NetworkException(f"Rate limited (429): {url}")
            elif response.status_code >= 400:
                raise NetworkException(
                    f"HTTP error {response.status_code}: {url}"
                )

            logger.debug(f"Page fetched successfully, size: {len(response.text)} bytes")
            return response.text

        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            raise NetworkException(f"Failed to fetch channel page: {e}")

    def extract_channel_metadata(self, html: str) -> Optional[Channel]:
        """Extract channel metadata from HTML.

        Args:
            html: Channel page HTML

        Returns:
            Channel object with metadata

        Raises:
            ParserException: If metadata extraction fails
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Extract channel info
            title = soup.find('h1', {'class': 'tgme_channel_title'})
            description = soup.find('div', {'class': 'tgme_channel_description'})
            followers = soup.find('span', {'class': 'tgme_channel_subscribers'})
            image = soup.find('img', {'class': 'tgme_channel_photo_image'})

            channel_data = {
                'username': None,
                'title': title.get_text(strip=True) if title else 'Unknown',
                'description': description.get_text(strip=True) if description else '',
                'followers': 0,
                'photo_url': None,
                'url': self.channel_url,
            }

            # Extract followers count
            if followers:
                followers_text = followers.get_text()
                # Extract number from text like "10.5K subscribers"
                import re
                match = re.search(r'([\d.]+)([KMB]?)', followers_text)
                if match:
                    num_str = match.group(1)
                    multiplier = match.group(2)
                    try:
                        num = float(num_str)
                        if multiplier == 'K':
                            num *= 1000
                        elif multiplier == 'M':
                            num *= 1_000_000
                        elif multiplier == 'B':
                            num *= 1_000_000_000
                        channel_data['followers'] = int(num)
                    except ValueError:
                        logger.warning(f"Could not parse followers: {followers_text}")

            # Extract photo URL
            if image:
                photo_url = image.get('src')
                if photo_url:
                    channel_data['photo_url'] = photo_url

            # Extract username from URL
            if self.channel_url:
                username = self.channel_url.rstrip('/').split('/')[-1]
                channel_data['username'] = username

            logger.debug(f"Extracted channel metadata: {channel_data}")
            self.channel_data = channel_data
            return channel_data

        except Exception as e:
            logger.error(f"Error extracting channel metadata: {e}")
            raise ParserException(f"Failed to extract channel metadata: {e}")

    def parse_messages(self, html: str, max_messages: Optional[int] = None) -> List[Message]:
        """Parse messages from channel HTML.

        Args:
            html: Channel page HTML
            max_messages: Maximum number of messages to extract

        Returns:
            List of Message objects

        Raises:
            ParserException: If message parsing fails
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            messages = []

            # Get channel ID from metadata if available
            channel_id = getattr(self, 'channel_id', 0)

            # Find all message elements
            message_elements = soup.select(self.MESSAGES_SELECTOR)
            logger.info(f"Found {len(message_elements)} messages on page")

            for idx, msg_elem in enumerate(message_elements):
                if max_messages and idx >= max_messages:
                    break

                try:
                    # Get message HTML
                    msg_html = str(msg_elem)

                    # Try to extract message ID from element
                    msg_id = msg_elem.get('data-post-id')
                    if not msg_id:
                        # Generate ID based on index if not found
                        msg_id = idx
                    else:
                        msg_id = int(msg_id)

                    # Parse message
                    message = MessageProcessor.parse_message(
                        html=msg_html,
                        channel_id=channel_id,
                        message_id=msg_id
                    )

                    messages.append(message)
                    logger.debug(f"Parsed message {msg_id}")

                except Exception as e:
                    logger.warning(f"Error parsing individual message: {e}")
                    continue

            logger.info(f"Successfully parsed {len(messages)} messages")
            return messages

        except Exception as e:
            logger.error(f"Error parsing messages from HTML: {e}")
            raise ParserException(f"Failed to parse messages: {e}")

    def parse(
        self,
        channel_url: str,
        max_messages: Optional[int] = None
    ) -> dict:
        """Parse complete channel.

        Args:
            channel_url: Channel URL or username
            max_messages: Maximum number of messages to parse

        Returns:
            Dictionary with channel data and messages:
            {
                'channel': Channel object,
                'messages': List[Message],
                'success': bool,
                'error': Optional[str]
            }
        """
        try:
            # Validate URL
            if not self.validate(channel_url):
                return {
                    'channel': None,
                    'messages': [],
                    'success': False,
                    'error': f"Invalid channel URL: {channel_url}"
                }

            # Fetch page
            html = self._fetch_page(self.channel_url)
            if not html:
                return {
                    'channel': None,
                    'messages': [],
                    'success': False,
                    'error': f"Failed to fetch channel: {channel_url}"
                }

            # Extract channel metadata
            channel_metadata = self.extract_channel_metadata(html)

            # Parse messages
            messages = self.parse_messages(html, max_messages=max_messages)

            result = {
                'channel': channel_metadata,
                'messages': messages,
                'success': True,
                'error': None,
                'message_count': len(messages)
            }

            logger.info(
                f"Channel parsing complete: {len(messages)} messages from "
                f"{channel_metadata.get('title', 'Unknown')}"
            )

            return result

        except NetworkException as e:
            logger.error(f"Network error parsing channel: {e}")
            return {
                'channel': None,
                'messages': [],
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except ParserException as e:
            logger.error(f"Parser error: {e}")
            return {
                'channel': None,
                'messages': [],
                'success': False,
                'error': f"Parser error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error parsing channel: {e}")
            return {
                'channel': None,
                'messages': [],
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }

    def parse_multiple_pages(
        self,
        channel_url: str,
        page_numbers: List[int]
    ) -> List[Message]:
        """Parse multiple pages of a channel.

        Args:
            channel_url: Channel URL
            page_numbers: List of page numbers to parse

        Returns:
            Combined list of messages from all pages
        """
        all_messages = []

        for page_num in page_numbers:
            try:
                # Construct paginated URL
                page_url = f"{channel_url}?p={page_num}"

                # Parse page
                result = self.parse(page_url)

                if result['success']:
                    all_messages.extend(result['messages'])
                    logger.info(f"Page {page_num}: {len(result['messages'])} messages")
                else:
                    logger.warning(f"Failed to parse page {page_num}: {result['error']}")

            except Exception as e:
                logger.error(f"Error parsing page {page_num}: {e}")
                continue

        logger.info(f"Total messages from {len(page_numbers)} pages: {len(all_messages)}")
        return all_messages
