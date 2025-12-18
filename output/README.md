# Output Layer - Results Export

Formatting and exporting results.

## Modules

- **console_output.py** - Console output formatting
- **json_exporter.py** - JSON export
- **csv_exporter.py** - CSV export
- **table_formatter.py** - Table formatting

## Usage

```python
from output import ConsoleOutput, JSONExporter

console = ConsoleOutput()
console.print_results(results)
console.print_statistics(stats)

json_exporter = JSONExporter()
json_exporter.export(results, "output.json")
```
