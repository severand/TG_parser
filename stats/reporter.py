"""Reporter module for generating summary reports.

Generates:
- Text summaries
- Formatted reports
- Statistics tables
"""

from typing import Dict, Any, List
from datetime import datetime

from utils.logger import Logger
from stats.collector import StatsCollector


logger = Logger.get_instance()


class Reporter:
    """Generates parsing reports from statistics."""

    def __init__(self, stats_collector: StatsCollector):
        """Initialize Reporter.

        Args:
            stats_collector: StatsCollector instance
        """
        self.collector = stats_collector

    def generate_report(self) -> str:
        """Generate complete text report.

        Returns:
            Formatted report string
        """
        stats = self.collector.get_statistics()
        errors = self.collector.get_errors()
        top_channels = self.collector.get_top_channels_by_messages(5)

        report_lines = []
        report_lines.append("\n" + "="*60)
        report_lines.append("PARSING REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("="*60 + "\n")

        # Summary section
        report_lines.append("SUMMARY")
        report_lines.append("-" * 60)
        report_lines.append(f"Total Channels Attempted: {stats['total_channels_attempted']}")
        report_lines.append(f"  - Successfully Parsed: {stats['total_channels_parsed']}")
        report_lines.append(f"  - Failed: {stats['total_channels_failed']}")
        report_lines.append(f"  - Success Rate: {stats['success_rate']:.1f}%")
        report_lines.append()

        # Messages section
        report_lines.append("MESSAGES")
        report_lines.append("-" * 60)
        report_lines.append(f"Total Messages Found: {stats['total_messages']}")
        report_lines.append(f"Unique Messages: {stats['total_unique_messages']}")
        report_lines.append(f"Total Views: {stats['total_views']:,}")
        report_lines.append(f"Total Reactions: {stats['total_reactions']:,}")
        report_lines.append(f"Avg Views per Message: {stats['avg_views_per_message']:.2f}")
        report_lines.append(f"Avg Reactions per Message: {stats['avg_reactions_per_message']:.2f}")
        report_lines.append()

        # Content analysis section
        report_lines.append("CONTENT ANALYSIS")
        report_lines.append("-" * 60)
        report_lines.append(f"Unique Authors: {stats['total_authors']}")
        report_lines.append(f"Unique Hashtags: {stats['total_unique_hashtags']}")
        report_lines.append(f"Unique Mentions: {stats['total_unique_mentions']}")
        report_lines.append()

        # Performance section
        report_lines.append("PERFORMANCE")
        report_lines.append("-" * 60)
        report_lines.append(f"Total Duration: {stats['duration_seconds']:.2f} seconds")
        report_lines.append(f"Processing Rate: {stats['messages_per_second']:.2f} messages/sec")
        report_lines.append()

        # Top channels section
        if top_channels:
            report_lines.append("TOP CHANNELS BY MESSAGE COUNT")
            report_lines.append("-" * 60)
            for idx, (channel, count) in enumerate(top_channels, 1):
                report_lines.append(f"{idx}. {channel}: {count} messages")
            report_lines.append()

        # Errors section
        if errors:
            report_lines.append("ERRORS ENCOUNTERED")
            report_lines.append("-" * 60)
            for error in errors[:10]:  # Show first 10 errors
                report_lines.append(f"Channel: {error['channel']}")
                report_lines.append(f"  Error: {error['error']}")
                report_lines.append(f"  Time: {error['timestamp']}")
            if len(errors) > 10:
                report_lines.append(f"... and {len(errors) - 10} more errors")
            report_lines.append()
        else:
            report_lines.append("No errors encountered\n")

        report_lines.append("="*60 + "\n")

        return "\n".join(report_lines)

    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary as dictionary.

        Returns:
            Dictionary with summary data
        """
        stats = self.collector.get_statistics()

        return {
            'timestamp': datetime.now().isoformat(),
            'channels': {
                'total_attempted': stats['total_channels_attempted'],
                'successful': stats['total_channels_parsed'],
                'failed': stats['total_channels_failed'],
                'success_rate_percent': round(stats['success_rate'], 2),
            },
            'messages': {
                'total': stats['total_messages'],
                'unique': stats['total_unique_messages'],
                'total_views': stats['total_views'],
                'total_reactions': stats['total_reactions'],
                'avg_views': round(stats['avg_views_per_message'], 2),
                'avg_reactions': round(stats['avg_reactions_per_message'], 2),
            },
            'content': {
                'unique_authors': stats['total_authors'],
                'unique_hashtags': stats['total_unique_hashtags'],
                'unique_mentions': stats['total_unique_mentions'],
            },
            'performance': {
                'duration_seconds': round(stats['duration_seconds'], 2),
                'messages_per_second': round(stats['messages_per_second'], 2),
            },
        }

    def export_report_to_file(self, filepath: str):
        """Export report to text file.

        Args:
            filepath: Path to save report
        """
        try:
            report = self.generate_report()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report exported to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")

    def print_quick_summary(self):
        """Print quick summary to console."""
        stats = self.collector.get_statistics()
        print(f"\n✓ Parsed {stats['total_channels_parsed']} channels")
        print(f"✓ Found {stats['total_messages']} messages")
        print(f"✓ Total views: {stats['total_views']:,}")
        print(f"✓ Success rate: {stats['success_rate']:.1f}%")
        print(f"✓ Duration: {stats['duration_seconds']:.2f}s\n")
