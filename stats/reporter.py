"""Statistics reporter module."""

from typing import Dict, Any


class StatsReporter:
    """Generate statistics reports."""
    
    def __init__(self):
        pass
    
    def generate_report(self, stats: Dict[str, Any]) -> str:
        """Generate text report from statistics."""
        report = []
        report.append("=" * 50)
        report.append("STATISTICS REPORT")
        report.append("=" * 50)
        
        for key, value in stats.items():
            if isinstance(value, float):
                report.append(f"{key}: {value:.2f}")
            else:
                report.append(f"{key}: {value}")
        
        report.append("=" * 50)
        return "\n".join(report)


# Alias for backward compatibility
StatisticsReporter = StatsReporter
