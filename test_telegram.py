"""Test Telegram API finder."""

import asyncio
from core.telegram_finder import TelegramFinder
from config import API_ID, API_HASH, PHONE_NUMBER


async def main():
    if not API_ID or not API_HASH or not PHONE_NUMBER:
        print("❌ Error: заполни config.py с API_ID, API_HASH и PHONE_NUMBER")
        return

    finder = TelegramFinder(API_ID, API_HASH, PHONE_NUMBER)

    try:
        await finder.connect()

        # Search channels
        channels = await finder.search_channels("крипто", limit=5)
        print(f"\n✅ Найдено {len(channels)} каналов:")
        for ch in channels:
            print(f"  - {ch.title} (@{ch.username})")

        # Search chats
        chats = await finder.search_chats("крипто", limit=5)
        print(f"\n✅ Найдено {len(chats)} чатов:")
        for ch in chats:
            print(f"  - {ch.title} (@{ch.username})")

    finally:
        await finder.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
