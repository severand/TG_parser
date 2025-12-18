# Core Layer - Parser Engine

Main parsing logic for Telegram channels.

## Modules

- **parser.py** - Main TelegramParser orchestrator
- **channel_handler.py** - Single channel parsing logic
- **search_engine.py** - Search and filtering
- **message_processor.py** - Message extraction and processing

## Usage

```python
from core import TelegramParser

parser = TelegramParser(config)
messages = parser.parse_channels(["channel1", "channel2"])
results = parser.search(["keyword1", "keyword2"])
stats = parser.get_statistics()
```
