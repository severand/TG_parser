# Usage Examples

## Basic Usage

```python
from core import TelegramParser
from utils import Logger

# Initialize logger
logger = Logger()

# Load configuration
config = {
    "parser": {"max_threads": 5},
    "logging": {"level": "INFO"}
}

# Create parser
parser = TelegramParser(config)

# Parse channels
messages = parser.parse_channels(["channel1", "channel2"])
logger.info(f"Parsed {len(messages)} messages")
```

## Search and Filter

```python
# Search for keywords
results = parser.search(["keyword1", "keyword2"])
logger.info(f"Found {len(results)} matches")

# Print results
for result in results:
    print(f"{result.channel}: {result.context}")
```

## Export Results

```python
from output import JSONExporter, CSVExporter

# Export to JSON
json_exporter = JSONExporter()
json_exporter.export(results, "results.json")

# Export to CSV
csv_exporter = CSVExporter()
csv_exporter.export(results, "results.csv")
```

## Statistics

```python
stats = parser.get_statistics()
print(f"Channels parsed: {stats.total_channels}")
print(f"Messages found: {stats.total_messages}")
print(f"Matches: {stats.matches}")
```
