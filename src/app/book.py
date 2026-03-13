from collections import UserList
from typing import TypeVar

T = TypeVar("T")


class Book(UserList[T]):
    def get(self, index: int | str) -> T | None:
        """Get item by index.

        Args:
            index: Item index to get.

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
        """Validate index format.

        Args:
            index: Index to validate.

        Returns:
            True if index is a number greater than 0, False otherwise.
        """
        return index.isdigit() and int(index) > 0 and int(index) <= len(self.data)
