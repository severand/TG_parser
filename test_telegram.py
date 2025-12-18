"""Test Telegram API finder."""

import asyncio
from core.telegram_finder import TelegramFinder
from telegram_config import API_ID, API_HASH, PHONE_NUMBER  # FIXED IMPORT


async def main():
    if not API_ID or not API_HASH or not PHONE_NUMBER:
        print("❌ Error: заполни telegram_config.py с API_ID, API_HASH и PHONE_NUMBER")
        return

    finder = TelegramFinder(API_ID, API_HASH, PHONE_NUMBER)

    try:
        print("🔄 Подключаюсь к Telegram...")
        await finder.connect()
        print("✅ Подключен к Telegram!\n")

        # Search channels
        print("🔍 Ищу каналы по слову 'крипто'...")
        channels = await finder.search_channels("крипто", limit=5)
        print(f"\n✅ Найдено {len(channels)} каналов:")
        for ch in channels:
            print(f"  - {ch.title} (@{ch.username})")

        # Search chats
        print("\n🔍 Ищу чаты по слову 'крипто'...")
        chats = await finder.search_chats("крипто", limit=5)
        print(f"\n✅ Найдено {len(chats)} чатов:")
        for ch in chats:
            print(f"  - {ch.title}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await finder.disconnect()
        print("\n👋 Отключен от Telegram")


if __name__ == "__main__":
    asyncio.run(main())
