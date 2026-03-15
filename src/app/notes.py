from dataclasses import dataclass, field

from app.book import Book, BookItem
from app.types import NoteEditFields


@dataclass()
class Note(BookItem):
    """Represents a text note with optional tags.

    Notes support text content and categorization via tags. Tags are
    automatically cleaned (stripped, lowercased, deduplicated) on creation.
    Notes can be sorted by tags for organized display.

    Attributes:
        text: Note text content (required).
        tags: List of tag strings for categorization (optional, defaults to empty list).
    """

    text: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Clean tags after dataclass initialization."""
        self.tags = self._clean_tags(self.tags)

    def _sort_key(self) -> str:
        """Generate sort key for comparing notes by tags.

        Notes are sorted alphabetically by their concatenated tags.
        Notes without tags are sorted last (use "zzz_no_tags" as key).

        Returns:
            Sort key string for tag-based ordering.
        """
        if not self.tags:
            return "zzz_no_tags"
        return self.tags_str

    # Only __lt__ is required for sorting; other comparison operators unnecessary
    def __lt__(self, other: "Note", /) -> bool:
        """Compare notes for sorting based on tags.

        Notes are sorted alphabetically by their concatenated tags.
        Notes without tags are placed at the end of sorted list.

        Args:
            other: Another Note instance to compare against.

        Returns:
            True if this note should come before the other note in sorted order.
        """
        return self._sort_key() < other._sort_key()

    @property
    def title(self) -> str:
        """Generate short title from note text.

        Takes the first line of text and truncates to 30 characters.
        Used for compact display in tables and lists.

        Returns:
            Short title string for display purposes.
        """
        return self.text.split("\n")[0][:30].strip()

    @property
    def tags_str(self) -> str:
        """Format tags as comma-separated string.

        Provides human-readable representation of tags for display.

        Returns:
            Comma-separated string of tags, or empty string if no tags.
        """
        return ", ".join(sorted(tag for tag in self.tags))

    @staticmethod
    def _clean_tags(tags: list[str] | None = None) -> list[str]:
        """Normalize tags by cleaning and deduplicating.

        Strips whitespace, converts to lowercase, removes empty strings,
        and eliminates duplicates while preserving insertion order.
        Ensures consistent tag format across all notes.

        Args:
            tags: List of tag strings to clean, or None.

        Returns:
            List of cleaned, normalized tag strings.
        """
        if not tags:
            return []
        return list(
            dict.fromkeys(tag.strip().casefold() for tag in tags if tag.strip())
        )

    @staticmethod
    def validate_text(text: str) -> bool:
        """Validate that note text is not empty.

        Args:
            text: Note text to validate.

        Returns:
            True if text contains non-whitespace characters, False otherwise.
        """
        return len(text.strip()) > 0


class NotesBook(Book[Note]):
    """Manages note collection with search, edit, and tag-based sorting.

    Extends Book to provide list-like access while adding domain-specific
    operations for note management including text search and tag filtering.
    """

    item_type = Note

    def find(self, search: str) -> list[Note]:
        """Search notes by text content or tags.

        Performs case-insensitive substring search in note text
        and tag names. Returns all notes that match the search term.

        Args:
            search: Search term to match against note text and tags.

        Returns:
            List of Note instances with matching text or tags.
        """
        keywords = search.casefold().strip()
        found: list[Note] = []
        for note in self.data:
            if keywords in note.text.casefold():
                found.append(note)
            elif any(keywords in tag.casefold() for tag in note.tags):
                found.append(note)
        return found

    def find_by_tag(self, tags: list[str]) -> list[Note]:
        """Find notes that have any of the specified tags.

        Performs exact tag matching (case-insensitive) against note tags.
        Returns all notes containing at least one matching tag.

        Args:
            tags: List of tag names to search for.

        Returns:
            List of Note instances with matching tags.
        """
        found: list[Note] = []
        cleaned_tags = [tag.casefold().strip() for tag in tags if tag.strip()]
        for note in self.data:
            if any(tag in note.tags for tag in cleaned_tags):
                found.append(note)
        return found

    def edit(self, index: int | str, fields: NoteEditFields) -> bool:
        """Update note fields with validated values.

        Only updates fields that are present and non-empty in the dictionary.
        This partial update pattern allows editing specific note attributes
        without requiring full note data.

        Args:
            index: 1-based index of note to edit.
            fields: Dictionary containing fields to update. Valid keys:
                    'text', 'tags'.

        Returns:
            True if note was found and updated, False otherwise.
        """
        note = self.get(index)
        if not note:
            return False

        if "text" in fields and fields["text"]:
            note.text = fields["text"].strip()

        if "tags" in fields and fields["tags"]:
            note.tags = fields["tags"]

        return True
