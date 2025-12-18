# Data Layer - Models and Storage

Data models and persistence.

## Modules

- **models.py** - Dataclasses for Channel, User, Message, etc.
- **storage.py** - Local file-based storage
- **cache.py** - In-memory caching
- **deduplicator.py** - Duplicate detection and removal

## Models

- `Channel` - Telegram channel metadata
- `User` - User/author information
- `Message` - Message data
- `SearchResult` - Search result with context
- `ParsingStatistics` - Parsing statistics

## Usage

```python
from data import Message, LocalStorage

message = Message(
    id="123",
    channel_id="channel1",
    text="Hello world",
    timestamp="2025-12-18T10:00:00Z"
)

storage = LocalStorage()
storage.save("messages", message)
```
