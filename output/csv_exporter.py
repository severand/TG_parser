"""CSV exporter for saving results to CSV files.

Supports:
- Message export
- Search results export
- Statistics export
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from utils.logger import Logger
from utils.exceptions import ParserException
from data.models import Message, SearchResult


logger = Logger.get_instance()


class CSVExporter:
    """Exports data to CSV format."""

    def __init__(self, output_dir: str = "results"):
        """Initialize CSVExporter.

        Args:
            output_dir: Directory to save CSV files
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Ensure output directory exists."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directory: {self.output_dir}")

    def export_messages(
        self,
        messages: List[Message],
        filename: Optional[str] = None
    ) -> str:
        """Export messages to CSV.

        Args:
            messages: Messages to export
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"messages_{timestamp}.csv"

            filepath = os.path.join(self.output_dir, filename)

            # Define CSV fields
            fieldnames = [
                'id',
                'channel_id',
                'author',
                'text',
                'timestamp',
                'views',
                'reactions',
                'mentions',
                'hashtags',
                'urls',
                'edited',
                'pinned',
            ]

            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for msg in messages:
                    writer.writerow({
                        'id': msg.id,
                        'channel_id': msg.channel_id,
                        'author': msg.author or '',
                        'text': msg.text[:1000],  # Truncate long text
                        'timestamp': msg.timestamp.isoformat() if msg.timestamp else '',
                        'views': msg.views,
                        'reactions': msg.reactions,
                        'mentions': '; '.join(msg.mentions) if msg.mentions else '',
                        'hashtags': '; '.join(msg.hashtags) if msg.hashtags else '',
                        'urls': '; '.join(msg.urls) if msg.urls else '',
                        'edited': 'Yes' if msg.edited else 'No',
                        'pinned': 'Yes' if msg.pinned else 'No',
                    })

            logger.info(f"Exported {len(messages)} messages to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting messages to CSV: {e}")
            raise ParserException(f"Failed to export messages to CSV: {e}")

    def export_search_results(
        self,
        results: List[SearchResult],
        filename: Optional[str] = None
    ) -> str:
        """Export search results to CSV.

        Args:
            results: Search results to export
            filename: Output filename

        Returns:
            Path to saved file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"search_results_{timestamp}.csv"

            filepath = os.path.join(self.output_dir, filename)

            # Define CSV fields
            fieldnames = [
                'message_id',
                'channel_id',
                'author',
                'relevance_score',
                'matched_keywords',
                'text_snippet',
                'context',
                'timestamp',
                'views',
                'reactions',
            ]

            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for result in results:
                    writer.writerow({
                        'message_id': result.message_id,
                        'channel_id': result.channel_id,
                        'author': result.author or '',
                        'relevance_score': f"{result.relevance_score:.2f}%",
                        'matched_keywords': ', '.join(result.matched_keywords),
                        'text_snippet': result.text_snippet[:500],  # Truncate
                        'context': result.context or '',
                        'timestamp': result.timestamp.isoformat() if result.timestamp else '',
                        'views': result.views,
                        'reactions': result.reactions,
                    })

            logger.info(f"Exported {len(results)} search results to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting search results to CSV: {e}")
            raise ParserException(f"Failed to export search results to CSV: {e}")

    def export_statistics(
        self,
        stats: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """Export statistics to CSV.

        Args:
            stats: Statistics dictionary
            filename: Output filename

        Returns:
            Path to saved file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"statistics_{timestamp}.csv"

            filepath = os.path.join(self.output_dir, filename)

            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(['Metric', 'Value'])

                # Data
                for key, value in stats.items():
                    formatted_key = str(key).replace('_', ' ').title()
                    if isinstance(value, float):
                        formatted_value = f"{value:.2f}"
                    else:
                        formatted_value = str(value)
                    writer.writerow([formatted_key, formatted_value])

            logger.info(f"Exported statistics to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting statistics to CSV: {e}")
            raise ParserException(f"Failed to export statistics to CSV: {e}")
