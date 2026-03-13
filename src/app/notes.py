from collections import UserList
from dataclasses import asdict, dataclass, field


@dataclass
class Note:
    text: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.tags = self._clean_tags(self.tags)

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


class NotesBook(UserList[Note]):
    def find(self, search: str) -> list[Note]:
        keywords = search.casefold().strip()
        found: list[Note] = []
        for note in self.data:
            if keywords in note.text.casefold():
                found.append(note)
            elif any(keywords in tag.casefold() for tag in note.tags):
                found.append(note)
        return found

    def edit(
        self, index: int, new_text: str, new_tags: list[str] | None = None
    ) -> bool:
        if index < 0 or index >= len(self.data):
            return False
        self.data[index].text = new_text
        self.data[index].tags = self._clean_tags(new_tags)
        return True

    def delete(self, index: int) -> bool:
        if index < 0 or index >= len(self.data):
            return False
        self.data.pop(index)
        return True

    # TODO REMOVE OLD METHODS
    def old_find_notes(self, keyword):
        """
        Шукає нотатки за текстом.
        """
        keyword = keyword.lower().strip()
        found = []

        for index, note in enumerate(self.notes, start=1):
            if keyword in note.text.lower():
                found.append(f"{index}. {note}")

        if not found:
            return "Нотатки не знайдено"

        return "\n".join(found)

    def old_find_by_tag(self, tag):
        """
        Шукає нотатки за тегом.
        """
        tag = tag.lower().strip()
        found = []

        for index, note in enumerate(self.notes, start=1):
            lower_tags = [item.lower() for item in note.tags]
            if tag in lower_tags:
                found.append(f"{index}. {note}")

        if not found:
            return "Нотаток з таким тегом не знайдено"

        return "\n".join(found)

    def old_sort_by_tags(self):
        """
        Сортує нотатки за тегами.
        """
        if not self.notes:
            return "Список нотаток порожній"

        sorted_notes = sorted(
            self.notes,
            key=lambda note: (
                ", ".join(tag.lower() for tag in note.tags) if note.tags else "zzz"
            ),
        )

        result = []
        for index, note in enumerate(sorted_notes, start=1):
            result.append(f"{index}. {note}")

        return "\n".join(result)

    def old_edit_note(self, index, new_text, new_tags=None):
        """
        Редагує нотатку за її номером.
        """
        if not str(index).isdigit():
            return "Номер нотатки має бути числом"

        index = int(index) - 1

        if index < 0 or index >= len(self.notes):
            return "Нотатку не знайдено"

        if new_text.strip():
            self.notes[index].text = new_text.strip()

        if new_tags is not None:
            self.notes[index].tags = self._clean_tags(new_tags)

        return "Нотатку оновлено"

    def old_delete_note(self, index):
        """
        Видаляє нотатку за її номером.
        """
        if not str(index).isdigit():
            return "Номер нотатки має бути числом"

        index = int(index) - 1

        if index < 0 or index >= len(self.notes):
            return "Нотатку не знайдено"

        self.notes.pop(index)
        return "Нотатку видалено"

    def to_list(self):
        """
        Перетворює всі нотатки у список словників.
        """
        return [note.to_dict() for note in self.notes]

    def load_from_list(self, data):
        """
        Завантажує нотатки зі списку словників.
        """
        self.notes = [Note.from_dict(item) for item in data]
