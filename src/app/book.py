from collections import UserList
from dataclasses import asdict
from typing import Dict, List, TypeVar

T = TypeVar("T")


class Book(UserList[T]):
    """Generic book for storing indexed collections.

    Extends UserList to provide 1-based indexing (instead of 0-based),
    making it more intuitive for CLI users. Handles conversion between
    indices and internal list positions automatically.

    Type Parameters:
        T: The type of items stored in the book.
    """

    item_type: T = None

    def get(self, index: int | str) -> T | None:
        """Retrieve item by 1-based index.

        Handles both string and integer indices, converting them to
        internal 0-based position automatically. Returns None for invalid
        indices instead of raising exceptions.

        Args:
            index: 1-based index of item to retrieve.

        Returns:
            Item instance if found, None otherwise.
        """
        try:
            index = int(index)
        except ValueError:
            return None

        if index < 1 or index > len(self.data):
            return None
        return self.data[index - 1]

    def delete(self, index: int | str) -> bool:
        """Remove item from book by index.

        Converts string index to integer and removes the item at that position.
        Uses 1-based indexing to match CLI user expectations.

        Args:
            index: Item index to remove (1-based).

        Returns:
            True if item was deleted, False if index is invalid.

        Raises:
            IndexError: If index is out of range after conversion.
        """
        try:
            index = int(index)
        except ValueError:
            return False
        self.data.pop(index - 1)
        return True

    def to_list(self) -> list[dict]:
        """Convert all items to list of dictionaries for serialization.

        Enables easy JSON export and persistence of item data.

        Returns:
            List of item dictionaries with all field values.
        """
        return [item.to_dict() for item in self.data]

    def validate_index(self, index: int | str) -> bool:
        """Validate that index is within valid range.

        Checks that index can be converted to integer and falls within
        the 1-based range [1, len(data)] inclusive.

        Args:
            index: Index to validate.

        Returns:
            True if index is valid, False otherwise.
        """
        return index.isdigit() and int(index) > 0 and int(index) <= len(self.data)

    def load_from_list(self, data: List[Dict]) -> None:
        """Load items from list of dictionaries, handling errors gracefully.

        Replaces existing data with loaded items. Skips corrupted or invalid
        items rather than failing entirely, allowing partial data recovery.
        This fail-safe approach ensures data durability even when some items
        are malformed.

        Args:
            data: List of dictionaries to deserialize into items.

        Note:
            Requires item_type class variable to be set by subclass.
        """
        loaded_items = []
        for item in data:
            try:
                loaded_items.append(self.item_type.from_dict(item))
            except Exception:
                continue
        self.data = loaded_items


class Item:
    """Base class for serializable items stored in Book collections."""

    def to_dict(self) -> dict:
        """Convert item to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        """Create Item instance from dictionary data.

        Only loads fields that exist in class annotations, gracefully ignoring
        unknown fields. This allows schema evolution where old data may contain
        fields not present in newer class versions.

        Args:
            data: Dictionary containing field-value pairs for initialization.

        Returns:
            New Item instance with loaded fields.
        """
        fields = {}

        for field, value in data.items():
            if field in cls.__annotations__:
                fields[field] = value

        return cls(**fields)
