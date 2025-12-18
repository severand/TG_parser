# Statistics Layer - Metrics and Monitoring

Statistics collection and reporting.

## Modules

- **collector.py** - Statistics collector
- **reporter.py** - Statistics reporting
- **metrics.py** - Metrics dataclasses

## Usage

```python
from stats import StatisticsCollector

collector = StatisticsCollector()
collector.add_parsed_channel()
collector.add_message()
collector.add_match()

stats = collector.get_statistics()
```
