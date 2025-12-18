# TG Parser Usage Examples

## Installation

```bash
git clone https://github.com/severand/TG_parser.git
cd TG_parser
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## CLI Examples

### Basic Search

```bash
python main.py search \
  --channels "@python" "@code" \
  --keywords "tutorial" "guide"
```

### Search with Filters

```bash
python main.py search \
  --channels "@python" \
  --keywords "async" \
  --min-views 100 \
  --date-from 2025-01-01 \
  --date-to 2025-12-31
```

### Export to JSON

```bash
python main.py search \
  --channels "@python" \
  --keywords "django" \
  --output-format json \
  --output-file results.json
```

### Export to CSV

```bash
python main.py search \
  --channels "@python" \
  --keywords "flask" \
  --output-format csv \
  --output-file results.csv
```

### Parse Without Searching

```bash
python main.py parse \
  --channels "@python" "@code" \
  --output-dir results
```

### With Report

```bash
python main.py search \
  --channels "@python" \
  --keywords "test" \
  --report
```

---

## Python API Examples

### Example 1: Basic Search

```python
from core.parser import Parser

parser = Parser(max_workers=4)
result = parser.parse_and_search(
    channels=['@python'],
    keywords=['tutorial', 'guide']
)

if result['success']:
    print(f"Found {len(result['search_results'])} results")
    for msg in result['search_results'][:5]:
        print(f"\n{msg.author}: {msg.text_snippet}")
        print(f"Relevance: {msg.relevance_score}%")
        print(f"Views: {msg.views}")
else:
    print(f"Error: {result['error']}")
```

### Example 2: Advanced Search with Filters

```python
from core.parser import Parser
from datetime import datetime, timedelta

parser = Parser(max_workers=4)
result = parser.parse_and_search(
    channels=['@python', '@code'],
    keywords=['python', 'programming'],
    max_messages=500,
    min_views=100,
    date_from=datetime.now() - timedelta(days=30),
    date_to=datetime.now()
)

print(f"Total messages parsed: {result['statistics']['total_messages']}")
print(f"Search results: {len(result['search_results'])}")
```

### Example 3: Export Results

```python
from core.parser import Parser
from output.json_exporter import JSONExporter
from output.csv_exporter import CSVExporter

parser = Parser()
result = parser.parse_and_search(
    channels=['@python'],
    keywords=['async']
)

# Export to JSON
json_exp = JSONExporter(output_dir='results')
json_file = json_exp.export_search_results(
    result['search_results'],
    filename='python_async.json'
)
print(f"JSON exported: {json_file}")

# Export to CSV
csv_exp = CSVExporter(output_dir='results')
csv_file = csv_exp.export_search_results(
    result['search_results'],
    filename='python_async.csv'
)
print(f"CSV exported: {csv_file}")
```

### Example 4: Parse Only (No Search)

```python
from core.parser import Parser

parser = Parser(max_workers=4)
messages = parser.parse_channels(['@python', '@code'])

print(f"Parsed {len(messages)} messages")
print(f"Channels: {parser.get_statistics()['total_channels_parsed']}")
```

### Example 5: Manual Search

```python
from core.parser import Parser
from core.search_engine import SearchEngine, SearchFilter

parser = Parser()
messages = parser.parse_channels(['@python'])

engine = SearchEngine(case_sensitive=False)
results = engine.search(messages, ['tutorial'])

print(f"Found {len(results)} results")
for r in results[:3]:
    print(f"Score: {r.relevance_score}% - {r.text_snippet[:50]}")
```

### Example 6: Advanced Filtering

```python
from core.parser import Parser
from core.search_engine import SearchEngine, SearchFilter
from datetime import datetime

parser = Parser()
messages = parser.parse_channels(['@python'])

engine = SearchEngine()
filters = SearchFilter(
    keywords=['python'],
    hashtags=['#code', '#programming'],
    min_views=500,
    date_from=datetime(2025, 1, 1),
    date_to=datetime(2025, 12, 31)
)

results = engine.advanced_search(messages, filters)
print(f"Advanced search: {len(results)} results")
```

### Example 7: Statistics

```python
from core.parser import Parser

parser = Parser(max_workers=4)
result = parser.parse_and_search(
    channels=['@python', '@code'],
    keywords=['test']
)

stats = result['statistics']
print(f"Total messages: {stats['total_messages']}")
print(f"Total views: {stats['total_views']}")
print(f"Average views: {stats['avg_views_per_message']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
```

### Example 8: Error Handling

```python
from core.parser import Parser
from utils.exceptions import ValidationException, ParserException

parser = Parser()

try:
    result = parser.parse_and_search(
        channels=['@python'],
        keywords=['valid']
    )
    
    if not result['success']:
        print(f"Parse error: {result['error']}")
    else:
        print(f"Success: {len(result['search_results'])} results")
        
except ValidationException as e:
    print(f"Validation error: {e}")
except ParserException as e:
    print(f"Parser error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Example 9: Custom Configuration

```python
from core.parser import Parser
from config.config_loader import ConfigLoader

# Load custom config
config = ConfigLoader().load('config/config.json')

parser = Parser(
    max_workers=config.get('max_workers', 4),
    timeout=config.get('timeout', 10),
    max_retries=config.get('max_retries', 3)
)

result = parser.parse_and_search(
    channels=config.get('channels', []),
    keywords=config.get('keywords', [])
)
```

### Example 10: Batch Processing

```python
from core.parser import Parser

channels_list = [
    ['@python', '@code'],
    ['@webdev', '@javascript'],
    ['@datascience', '@ml']
]

parser = Parser(max_workers=4)

for channels in channels_list:
    result = parser.parse_and_search(
        channels=channels,
        keywords=['tutorial']
    )
    print(f"Channels {channels}: {len(result['search_results'])} results")
    parser.reset()  # Clear state for next batch
```

---

## Configuration Example

```json
{
  "channels": ["@python", "@code"],
  "keywords": ["tutorial", "guide"],
  "max_workers": 4,
  "timeout": 10,
  "max_retries": 3,
  "retry_delay": 1,
  "output_format": "json",
  "output_dir": "results",
  "min_views": 0,
  "with_urls": false
}
```

---

**Last Updated:** 2025-12-18
