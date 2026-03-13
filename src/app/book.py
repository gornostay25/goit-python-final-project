from collections import UserList
from typing import TypeVar

T = TypeVar("T")


class Book(UserList[T]):
    """Generic book for storing indexed collections.

    Extends UserList to provide 1-based indexing (instead of 0-based),
    making it more intuitive for CLI users. Handles conversion between
    indices and internal list positions automatically.

    Type Parameters:
        T: The type of items stored in the book.
    """

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
