"""Core layer - Main parser logic and orchestration."""

from core.parser import Parser
from core.channel_handler import ChannelHandler
from core.search_engine import SearchEngine
from core.message_processor import MessageProcessor

# Alias for backward compatibility
TelegramParser = Parser

__all__ = [
    "Parser",
    "TelegramParser",
    "ChannelHandler",
    "SearchEngine",
    "MessageProcessor",
]
