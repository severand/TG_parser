"""JSON exporter for saving results to JSON files.

Supports:
- Pretty-printed JSON
- Compact JSON
- Custom serialization
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from utils.logger import Logger
from utils.exceptions import ParserException
from data.models import Message, SearchResult, ParsingStatistics


logger = Logger.get_instance()


class JSONExporter:
    """Exports data to JSON format."""

    def __init__(self, output_dir: str = "results"):
        """Initialize JSONExporter.

        Args:
            output_dir: Directory to save JSON files
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Ensure output directory exists."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directory: {self.output_dir}")

    def _json_encoder(self, obj: Any) -> Any:
        """Custom JSON encoder for special types.

        Args:
            obj: Object to encode

        Returns:
            JSON-serializable object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return str(obj)

    def export_messages(
        self,
        messages: List[Message],
        filename: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """Export messages to JSON.

        Args:
            messages: Messages to export
            filename: Output filename (auto-generated if None)
            pretty: Pretty-print JSON

        Returns:
            Path to saved file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"messages_{timestamp}.json"

            filepath = os.path.join(self.output_dir, filename)

            # Convert messages to dictionaries
            data = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'total_messages': len(messages),
                    'file_version': '1.0',
                },
                'messages': [
                    {
                        'id': msg.id,
                        'channel_id': msg.channel_id,
                        'author': msg.author,
                        'text': msg.text,
                        'timestamp': msg.timestamp.isoformat() if msg.timestamp else None,
                        'views': msg.views,
                        'reactions': msg.reactions,
                        'mentions': msg.mentions,
                        'hashtags': msg.hashtags,
                        'urls': msg.urls,
                        'edited': msg.edited,
                        'pinned': msg.pinned,
                    }
                    for msg in messages
                ]
            }

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_encoder)
                else:
                    json.dump(data, f, ensure_ascii=False, default=self._json_encoder)

            logger.info(f"Exported {len(messages)} messages to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting messages: {e}")
            raise ParserException(f"Failed to export messages: {e}")

    def export_search_results(
        self,
        results: List[SearchResult],
        filename: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """Export search results to JSON.

        Args:
            results: Search results to export
            filename: Output filename
            pretty: Pretty-print JSON

        Returns:
            Path to saved file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"search_results_{timestamp}.json"

            filepath = os.path.join(self.output_dir, filename)

            # Convert to dictionaries
            data = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'total_results': len(results),
                    'file_version': '1.0',
                },
                'results': [
                    {
                        'message_id': r.message_id,
                        'channel_id': r.channel_id,
                        'text_snippet': r.text_snippet,
                        'full_text': r.full_text,
                        'context': r.context,
                        'matched_keywords': r.matched_keywords,
                        'relevance_score': r.relevance_score,
                        'timestamp': r.timestamp.isoformat() if r.timestamp else None,
                        'author': r.author,
                        'views': r.views,
                        'reactions': r.reactions,
                    }
                    for r in results
                ]
            }

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_encoder)
                else:
                    json.dump(data, f, ensure_ascii=False, default=self._json_encoder)

            logger.info(f"Exported {len(results)} search results to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting search results: {e}")
            raise ParserException(f"Failed to export search results: {e}")

    def export_statistics(
        self,
        stats: Dict[str, Any],
        filename: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """Export statistics to JSON.

        Args:
            stats: Statistics dictionary
            filename: Output filename
            pretty: Pretty-print JSON

        Returns:
            Path to saved file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"statistics_{timestamp}.json"

            filepath = os.path.join(self.output_dir, filename)

            data = {
                'export_date': datetime.now().isoformat(),
                'statistics': stats,
            }

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_encoder)
                else:
                    json.dump(data, f, ensure_ascii=False, default=self._json_encoder)

            logger.info(f"Exported statistics to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting statistics: {e}")
            raise ParserException(f"Failed to export statistics: {e}")

    def export_combined(
        self,
        messages: List[Message],
        search_results: List[SearchResult],
        statistics: Dict[str, Any],
        filename: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """Export messages, results, and statistics in one file.

        Args:
            messages: All messages
            search_results: Search results
            statistics: Statistics
            filename: Output filename
            pretty: Pretty-print JSON

        Returns:
            Path to saved file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_{timestamp}.json"

            filepath = os.path.join(self.output_dir, filename)

            data = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'total_messages': len(messages),
                    'total_results': len(search_results),
                    'file_version': '1.0',
                },
                'messages': [
                    {
                        'id': msg.id,
                        'channel_id': msg.channel_id,
                        'author': msg.author,
                        'text': msg.text,
                        'timestamp': msg.timestamp.isoformat() if msg.timestamp else None,
                        'views': msg.views,
                        'reactions': msg.reactions,
                        'mentions': msg.mentions,
                        'hashtags': msg.hashtags,
                        'urls': msg.urls,
                    }
                    for msg in messages
                ],
                'search_results': [
                    {
                        'message_id': r.message_id,
                        'relevance_score': r.relevance_score,
                        'matched_keywords': r.matched_keywords,
                        'context': r.context,
                    }
                    for r in search_results
                ],
                'statistics': statistics,
            }

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_encoder)
                else:
                    json.dump(data, f, ensure_ascii=False, default=self._json_encoder)

            logger.info(f"Exported combined data to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting combined data: {e}")
            raise ParserException(f"Failed to export combined data: {e}")
