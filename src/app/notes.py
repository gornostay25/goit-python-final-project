from dataclasses import asdict, dataclass, field

from app.book import Book


@dataclass()
class Note:
    text: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.tags = self._clean_tags(self.tags)

    def _sort_key(self) -> str:
        """Generate sort key for comparing notes by tags.

        Notes are sorted alphabetically by their concatenated tags.
        Notes without tags are sorted last (use "zzz" as key).

        Returns:
            Sort key string for tag-based ordering.
        """
        if not self.tags:
            return "zzz_no_tags"
        return ", ".join(sorted(tag for tag in self.tags))

    # No need to implement __le__, __gt__, __ge__ because sort
    def __lt__(self, other: "Note") -> bool:
        """Compare notes for less-than based on tags."""
        return self._sort_key() < other._sort_key()

    @property
    def title(self) -> str:
        return self.text.split("\n")[0][:10].strip()

    @property
    def tags_str(self) -> str:
        return ", ".join(self.tags)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(data.get("text", ""), data.get("tags", []))

    @staticmethod
    def _clean_tags(tags: list[str] | None = None) -> list[str]:
        if not tags:
            return []
        # Strip, lowercase, filter empty, and remove duplicates while preserving order
        return list(
            dict.fromkeys(tag.strip().casefold() for tag in tags if tag.strip())
        )

    @staticmethod
    def validate_text(text: str) -> bool:
        return len(text.strip()) > 0


class NotesBook(Book[Note]):
    def get(self, index: int | str) -> Note | None:
        """Get contact by index.

        Args:
            index: Contact index to get.

        Returns:
            Contact instance if found, None otherwise.
        """
        if isinstance(index, str) and index.isdigit():
            index = int(index)
        elif not isinstance(index, int):
            return None

        if index < 1 or index > len(self.data):
            return None
        return self.data[index - 1]

    def find(self, search: str) -> list[Note]:
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

    def edit(self, index: int | str, fields: dict) -> bool:
        note = self.get(index)
        if not note:
            return False

        if "text" in fields and fields["text"]:
            note.text = fields["text"].strip()

        if "tags" in fields and fields["tags"]:
            note.tags = fields["tags"]

        return True

    def load_from_list(self, data):
        """
        Завантажує нотатки зі списку словників.
        """
        self.notes = [Note.from_dict(item) for item in data]
