"""Deduplicator for removing duplicate messages.

Provides Deduplicator class for tracking and removing duplicate
messages during parsing.
"""

from typing import Any, List, Set

from utils.logger import Logger

logger = Logger()


class Deduplicator:
    """Track and remove duplicate items.

    Provides efficient O(1) duplicate detection using sets.

    Example:
        >>> dup = Deduplicator()
        >>> dup.add("msg_1")
        >>> dup.is_duplicate("msg_1")
        True
        >>> dup.is_duplicate("msg_2")
        False
    """

    def __init__(self) -> None:
        """Initialize Deduplicator."""
        self._seen: Set[str] = set()
        logger.debug("Initialized Deduplicator")

    def add(self, item: Any) -> None:
        """Add item to deduplication set.

        Args:
            item: Item to track (will be converted to string)

        Example:
            >>> dup = Deduplicator()
            >>> dup.add("message_id_1")
        """
        item_str = str(item)
        self._seen.add(item_str)
        logger.debug(f"Added item to deduplicator: {item_str}")

    def is_duplicate(self, item: Any) -> bool:
        """Check if item is duplicate.

        Args:
            item: Item to check (will be converted to string)

        Returns:
            True if item was seen before, False otherwise

        Example:
            >>> dup = Deduplicator()
            >>> dup.add("message_id")
            >>> dup.is_duplicate("message_id")
            True
        """
        item_str = str(item)
        return item_str in self._seen

    def deduplicate(self, items: List[Any]) -> List[Any]:
        """Deduplicate list of items.

        Removes items that have been seen before. Updates internal set
        with new items.

        Args:
            items: List of items to deduplicate

        Returns:
            List of new (not seen before) items

        Example:
            >>> dup = Deduplicator()
            >>> dup.add("msg_1")
            >>> new_items = dup.deduplicate(["msg_1", "msg_2", "msg_3"])
            >>> new_items
            ['msg_2', 'msg_3']
        """
        new_items = []
        for item in items:
            item_str = str(item)
            if item_str not in self._seen:
                new_items.append(item)
                self._seen.add(item_str)

        logger.debug(
            f"Deduplicated {len(items)} items, kept {len(new_items)} new items"
        )
        return new_items

    def clear(self) -> None:
        """Clear deduplication set.

        Resets the tracker to start fresh.
        """
        count = len(self._seen)
        self._seen.clear()
        logger.debug(f"Cleared deduplicator ({count} items removed)")

    def get_count(self) -> int:
        """Get number of tracked items.

        Returns:
            Count of unique items tracked
        """
        return len(self._seen)

    def __repr__(self) -> str:
        """String representation."""
        return f"Deduplicator(tracked={len(self._seen)} items)"
