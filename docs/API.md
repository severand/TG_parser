# API Documentation

## Main Entry Point

### TelegramParser

```python
class TelegramParser:
    def __init__(self, config: dict) -> None:
        """Initialize parser with configuration."""
        pass

    def parse_channels(self, channels: List[str]) -> List[Message]:
        """Parse list of channels.
        
        Args:
            channels: List of channel names/URLs
            
        Returns:
            List of Message objects
        """
        pass

    def search(self, keywords: List[str]) -> List[SearchResult]:
        """Search for keywords in parsed messages.
        
        Args:
            keywords: List of keywords to search
            
        Returns:
            List of SearchResult objects
        """
        pass

    def get_statistics(self) -> ParsingStatistics:
        """Get parsing statistics.
        
        Returns:
            ParsingStatistics object
        """
        pass
```

## Configuration

See `config/config.example.json` for full configuration options.

## Data Models

See `data/README.md` for model documentation.
