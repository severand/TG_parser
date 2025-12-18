# TG Parser API Reference

## Overview

TG Parser provides a comprehensive API for parsing Telegram channels and searching messages.

---

## Parser Module

### `Parser(max_workers=4, timeout=10, max_retries=3)`

Main orchestrator for parsing and searching operations.

```python
from core.parser import Parser

parser = Parser(max_workers=4)
```

#### Methods

##### `parse_and_search(channels, keywords, max_messages=None, **filters)`

Parse channels and search for keywords.

```python
result = parser.parse_and_search(
    channels=['@channel1', '@channel2'],
    keywords=['python', 'code'],
    max_messages=100,
    min_views=50,
    date_from=datetime(2025, 1, 1)
)
```

**Returns:**
```python
{
    'success': True,
    'messages': [...],
    'search_results': [...],
    'statistics': {...},
    'error': None
}
```

##### `parse_channels(channels, show_progress=True)`

Parse channels without searching.

```python
messages = parser.parse_channels(['@channel1', '@channel2'])
```

##### `search(messages, keywords, limit=None)`

Search through messages.

```python
results = parser.search(messages, ['keyword'])
```

##### `get_statistics()`

Get parsing statistics.

```python
stats = parser.get_statistics()
print(stats['total_messages'])
```

---

## Search Engine Module

### `SearchEngine(case_sensitive=False)`

Search and filter messages.

```python
from core.search_engine import SearchEngine

engine = SearchEngine(case_sensitive=False)
```

#### Methods

##### `search(messages, keywords, limit=None)`

```python
results = engine.search(messages, ['python', 'code'])
```

##### `filter_by_date(messages, date_from, date_to)`

```python
from datetime import datetime

filtered = engine.filter_by_date(
    messages,
    datetime(2025, 1, 1),
    datetime(2025, 12, 31)
)
```

##### `filter_by_hashtag(messages, hashtags)`

```python
filtered = engine.filter_by_hashtag(messages, ['#python', '#code'])
```

##### `filter_by_views(messages, min_views)`

```python
filtered = engine.filter_by_views(messages, min_views=100)
```

##### `advanced_search(messages, filters)`

```python
from core.search_engine import SearchFilter

filters = SearchFilter(
    keywords=['test'],
    hashtags=['#tag'],
    min_views=50,
    date_from=datetime(2025, 1, 1)
)

results = engine.advanced_search(messages, filters)
```

---

## Data Models

### `Message`

```python
from data.models import Message
from datetime import datetime

message = Message(
    id=1,
    channel_id=100,
    author='author_name',
    text='Message text',
    timestamp=datetime.now(),
    views=1000,
    reactions=25,
    mentions=['@user'],
    hashtags=['#tag'],
    urls=['https://example.com'],
    edited=False,
    pinned=False
)
```

### `SearchResult`

```python
from data.models import SearchResult

result = SearchResult(
    message_id=1,
    channel_id=100,
    text_snippet='...',
    full_text='...',
    context='...',
    matched_keywords=['python'],
    relevance_score=85.5,
    timestamp=datetime.now(),
    author='author',
    views=1000,
    reactions=25
)
```

---

## Output Exporters

### JSON Export

```python
from output.json_exporter import JSONExporter

exporter = JSONExporter(output_dir='results')
filepath = exporter.export_search_results(results)
```

### CSV Export

```python
from output.csv_exporter import CSVExporter

exporter = CSVExporter(output_dir='results')
filepath = exporter.export_search_results(results)
```

### Console Output

```python
from output.console_output import ConsoleOutput

output = ConsoleOutput(use_colors=True)
output.print_results(results, show_top=10)
output.print_statistics(stats)
```

---

## Validators

```python
from utils.validators import (
    validate_channel_url,
    validate_keywords,
    validate_config
)

if validate_channel_url('@channel'):
    print('Valid channel')

if validate_keywords(['python', 'code']):
    print('Valid keywords')
```

---

## Statistics Collector

```python
from stats.collector import StatsCollector

collector = StatsCollector()
collector.add_message(message)
collector.add_parsed_channel('@channel', 100)

stats = collector.get_statistics()
print(stats['total_messages'])
```

---

## Examples

### Basic Search

```python
from core.parser import Parser

parser = Parser(max_workers=4)
result = parser.parse_and_search(
    channels=['@python', '@code'],
    keywords=['tutorial', 'guide']
)

if result['success']:
    for msg in result['search_results']:
        print(f"{msg.author}: {msg.text_snippet}")
        print(f"Relevance: {msg.relevance_score}%")
```

### Advanced Search with Filters

```python
from datetime import datetime, timedelta

result = parser.parse_and_search(
    channels=['@channel1'],
    keywords=['python'],
    date_from=datetime.now() - timedelta(days=30),
    date_to=datetime.now(),
    min_views=100,
    with_urls=True
)
```

### Export Results

```python
from output.json_exporter import JSONExporter
from output.csv_exporter import CSVExporter

json_exp = JSONExporter()
json_file = json_exp.export_search_results(result['search_results'])

csv_exp = CSVExporter()
csv_file = csv_exp.export_search_results(result['search_results'])
```

---

**Last Updated:** 2025-12-18
