"""Telegram API finder for searching channels and chats."""

from typing import List, Optional
from config import API_ID, API_HASH, PHONE_NUMBER
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from data.models import Channel

from utils.logger import Logger

logger = Logger.get_instance()


class TelegramFinder:
    """Search channels and chats using Telegram API."""

    def __init__(self, api_id: int, api_hash: str, phone: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = None
        self.session_name = 'tg_parser_session'

        logger.info("TelegramFinder initialized")

    async def connect(self):
        """Connect to Telegram."""
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.start(phone=self.phone)
        logger.info("Connected to Telegram")

    async def disconnect(self):
        """Disconnect from Telegram."""
        if self.client:
            await self.client.disconnect()
            logger.info("Disconnected from Telegram")

    async def search_channels(self, query: str, limit: int = 50) -> List[Channel]:
        """Search for channels by keyword."""
        if not self.client:
            await self.connect()

        results = []

        try:
            # Search using Telegram's search
            async for dialog in self.client.iter_dialogs():
                if dialog.is_channel and limit > 0:
                    # Check if query in channel name
                    if query.lower() in dialog.name.lower():
                        entity = dialog.entity
                        channel = Channel(
                            id=str(entity.id),
                            username=entity.username or dialog.name,
                            title=dialog.name,
                            description=entity.about or "",
                            followers=getattr(entity, 'participants_count', 0),
                        )
                        results.append(channel)
                        limit -= 1

            logger.info(f"Found {len(results)} channels for '{query}'")

        except Exception as e:
            logger.error(f"Search error: {e}")

        return results

    async def search_chats(self, query: str, limit: int = 50) -> List[Channel]:
        """Search for chats/groups by keyword."""
        if not self.client:
            await self.connect()

        results = []

        try:
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group and limit > 0:
                    if query.lower() in dialog.name.lower():
                        entity = dialog.entity
                        channel = Channel(
                            id=str(entity.id),
                            username=dialog.name,
                            title=dialog.name,
                            description=entity.about or "",
                            followers=getattr(entity, 'participants_count', 0),
                        )
                        results.append(channel)
                        limit -= 1

            logger.info(f"Found {len(results)} chats for '{query}'")

        except Exception as e:
            logger.error(f"Search error: {e}")

        return results
