"""Local file-based storage for parsed messages and data.

Provides LocalStorage class for saving, loading, and exporting data
to JSON and CSV formats.
"""

import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.logger import Logger
from utils.exceptions import StorageException
from data.models import Message, SearchResult

logger = Logger()


class LocalStorage:
    """Local file-based storage for parser data.

    Manages saving, loading, and exporting messages and results
    to local files.

    Example:
        >>> storage = LocalStorage()
        >>> storage.save("messages", message_data)
        >>> loaded = storage.load("messages")
        >>> storage.export_json("messages", "results.json")
    """

    def __init__(self, base_path: str = "data/storage") -> None:
        """Initialize LocalStorage.

        Args:
            base_path: Base directory for storage (default: data/storage)
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Initialized LocalStorage at {self.base_path}")

    def save(self, key: str, value: Any) -> None:
        """Save data to local storage.

        Args:
            key: Storage key (used as filename)
            value: Data to save (will be serialized to JSON)

        Raises:
            StorageException: If save fails

        Example:
            >>> storage = LocalStorage()
            >>> storage.save("channel_data", {"id": "123", "name": "test"})
        """
        try:
            file_path = self.base_path / f"{key}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(value, f, indent=2, default=str)
            logger.debug(f"Saved data to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save {key}: {e}")
            raise StorageException(f"Failed to save {key}: {str(e)}") from e

    def load(self, key: str) -> Optional[Any]:
        """Load data from local storage.

        Args:
            key: Storage key (filename without extension)

        Returns:
            Loaded data or None if not found

        Raises:
            StorageException: If load fails

        Example:
            >>> storage = LocalStorage()
            >>> data = storage.load("channel_data")
        """
        try:
            file_path = self.base_path / f"{key}.json"
            if not file_path.exists():
                logger.debug(f"File not found: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Loaded data from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load {key}: {e}")
            raise StorageException(f"Failed to load {key}: {str(e)}") from e

    def delete(self, key: str) -> None:
        """Delete data from storage.

        Args:
            key: Storage key to delete
        """
        try:
            file_path = self.base_path / f"{key}.json"
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            raise StorageException(f"Failed to delete {key}: {str(e)}") from e

    def list_keys(self) -> List[str]:
        """List all storage keys.

        Returns:
            List of keys (filenames without .json extension)
        """
        keys = [f.stem for f in self.base_path.glob("*.json")]
        return sorted(keys)

    def export_json(self, key: str, output_file: str) -> None:
        """Export data to JSON file.

        Args:
            key: Storage key to export
            output_file: Output file path

        Raises:
            StorageException: If export fails
        """
        try:
            data = self.load(key)
            if data is None:
                raise StorageException(f"Data not found for key: {key}")

            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Exported data to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export {key} to JSON: {e}")
            raise StorageException(f"Failed to export to JSON: {str(e)}") from e

    def export_csv(self, key: str, output_file: str) -> None:
        """Export data to CSV file.

        Args:
            key: Storage key to export
            output_file: Output file path

        Raises:
            StorageException: If export fails
        """
        try:
            data = self.load(key)
            if data is None:
                raise StorageException(f"Data not found for key: {key}")

            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Handle different data types
            if isinstance(data, list) and len(data) > 0:
                # List of dictionaries
                if isinstance(data[0], dict):
                    keys = set()
                    for item in data:
                        keys.update(item.keys())

                    with open(output_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=sorted(keys))
                        writer.writeheader()
                        for item in data:
                            writer.writerow(item)
                else:
                    # List of non-dict items
                    with open(output_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['value'])
                        for item in data:
                            writer.writerow([item])
            elif isinstance(data, dict):
                # Single dictionary
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data.keys())
                    writer.writeheader()
                    writer.writerow(data)
            else:
                raise StorageException(f"Cannot export data type: {type(data)}")

            logger.info(f"Exported data to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export {key} to CSV: {e}")
            raise StorageException(f"Failed to export to CSV: {str(e)}") from e

    def clear(self) -> None:
        """Clear all storage."""
        try:
            for file_path in self.base_path.glob("*.json"):
                file_path.unlink()
            logger.debug(f"Cleared all storage in {self.base_path}")
        except Exception as e:
            logger.error(f"Failed to clear storage: {e}")
            raise StorageException(f"Failed to clear storage: {str(e)}") from e
