from dataclasses import dataclass, field


@dataclass
class Note:
    """
    Клас для зберігання однієї нотатки.
    """

    text: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self):
        """
        Перетворює нотатку у словник для JSON.
        """
        return {"text": self.text, "tags": self.tags}

    @staticmethod
    def from_dict(data):
        """
        Створює об'єкт Note зі словника.
        """
        return Note(data.get("text", ""), data.get("tags", []))

    def __str__(self):
        """
        Повертає красивий текстовий вигляд нотатки.
        """
        tags_text = ", ".join(self.tags) if self.tags else "без тегів"
        return f"Нотатка: {self.text} | Теги: {tags_text}"


class NotesBook:
    """
    Клас для роботи з усіма нотатками.
    """

    def __init__(self):
        self.notes = []

    def add_note(self, text: str, tags: list[str] | None = None) -> str:
        """
        Додає нову нотатку.
        """
        if not text.strip():
            return "Текст нотатки не може бути порожнім"

        cleaned_tags = self._clean_tags(tags)
        note = Note(text.strip(), cleaned_tags)
        self.notes.append(note)
        return "Нотатку додано"

    def show_all_notes(self):
        """
        Повертає всі нотатки.
        """
        if not self.notes:
            return "Список нотаток порожній"

        result = []
        for index, note in enumerate(self.notes, start=1):
            result.append(f"{index}. {note}")
        return "\n".join(result)

    def find_notes(self, keyword):
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

    def find_by_tag(self, tag):
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

    def sort_by_tags(self):
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

    def edit_note(self, index, new_text, new_tags=None):
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

    def delete_note(self, index):
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

    def _clean_tags(self, tags):
        """
        Очищає теги:
        - прибирає пробіли
        - прибирає дублікати
        - не додає порожні значення
        """
        if not tags:
            return []

        cleaned = []
        seen = set()

        for tag in tags:
            tag = tag.strip()
            if tag and tag.lower() not in seen:
                cleaned.append(tag)
                seen.add(tag.lower())

        return cleaned

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
