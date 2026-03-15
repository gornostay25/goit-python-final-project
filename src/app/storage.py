import json
import os
from typing import TypeVar

from app.book import Book

T = TypeVar("T")


class Storage:
    """Handles file I/O for Book objects, separating persistence from data management.

    Storage pattern delegates JSON serialization to Book's to_list()/load_from_list()
    methods, keeping Book focused on data operations while Storage handles file
    system concerns. This separation allows easy switching of storage backends
    (e.g., database, cloud storage) without changing Book logic.

    Attributes:
        book: Book instance containing data to persist.
        filename: Path to JSON file for persistence.
    """

    def __init__(self, book: Book[T], filename: str):
        self.book = book
        self.filename = filename

    def save(self):
        """Persist book data to JSON file."""
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(
                self.book.to_list(), file, ensure_ascii=False, indent=4, default=str
            )

    def load(self) -> None:
        """Restore book data from JSON file.

        If file doesn't exist or contains invalid JSON, initializes book with
        empty data. Handles malformed items gracefully via Book.load_from_list().
        """
        if not os.path.exists(self.filename):
            return
        with open(self.filename, "r", encoding="utf-8") as file:
            try:
                self.book.load_from_list(json.load(file))
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"Error loading data from {self.filename}: {e}")
