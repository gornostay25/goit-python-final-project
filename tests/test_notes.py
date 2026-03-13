"""Tests for notes module - Note and NotesBook classes."""

import pytest

from app.notes import Note


class TestNoteValidation:
    """Tests for Note validation methods."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Sample note text", True),
            ("  Valid text with spaces  ", True),
            ("Singleword", True),
            ("", False),
            ("   ", False),
            ("\t\n", False),
        ],
    )
    def test_validate_text(self, text, expected):
        """Test text validation."""
        assert Note.validate_text(text) == expected

    @pytest.mark.parametrize(
        "tags,expected",
        [
            (["tag1", "tag2", "tag3"], ["tag1", "tag2", "tag3"]),
            (["TAG1", "Tag2", "tag3"], ["tag1", "tag2", "tag3"]),
            (["  tag1  ", " tag2 "], ["tag1", "tag2"]),
            (["tag1", "tag1", "tag2"], ["tag1", "tag2"]),
            ([], []),
            (None, []),
            (["  ", ""], []),
        ],
    )
    def test_clean_tags(self, tags, expected):
        """Test _clean_tags strips, lowercases and deduplicates tags."""
        result = Note._clean_tags(tags)
        assert result == expected


class TestNoteProperties:
    """Tests for Note property methods."""

    def test_title_extracts_first_line(self, sample_note):
        """Test title extracts first 10 characters of first line."""
        assert sample_note.title == "This is a"

    def test_title_single_line_short(self):
        """Test title with short text."""
        note = Note(text="Short")
        assert note.title == "Short"

    def test_title_multiline(self):
        """Test title only uses first line."""
        note = Note(text="First line\nSecond line\nThird line")
        assert note.title == "First line"

    def test_title_truncates_to_10_chars(self):
        """Test title is limited to 10 characters."""
        note = Note(text="This is a very long title that should be truncated")
        assert note.title == "This is a"

    def test_title_strips_whitespace(self):
        """Test title strips trailing whitespace."""
        note = Note(text="Text   ")
        assert note.title == "Text"

    def test_tags_str_with_tags(self, sample_note):
        """Test tags_str formats tags with commas."""
        # Note: tags are sorted during __post_init__
        expected_tags = sorted(["important", "urgent", "work"])
        assert sample_note.tags_str == ", ".join(expected_tags)

    def test_tags_str_single_tag(self):
        """Test tags_str with single tag."""
        note = Note(text="Note", tags=["work"])
        assert note.tags_str == "work"

    def test_tags_str_no_tags(self):
        """Test tags_str with no tags."""
        note = Note(text="Note without tags")
        assert note.tags_str == ""

    def test_lt_sorts_by_tags(self):
        """Test __lt__ compares notes by tags."""
        note1 = Note(text="Note 1", tags=["work", "important"])
        note2 = Note(text="Note 2", tags=["personal"])

        # tags_str:
        # note1 -> "important, work"
        # note2 -> "personal"
        #
        # "important, work" < "personal"
        # because 'i' < 'p'

        assert note1 < note2
        assert not (note2 < note1)

    def test_lt_tags_no_tags_last(self):
        """Test notes without tags sort last."""
        note1 = Note(text="Note 1", tags=["work"])
        note2 = Note(text="Note 2")

        # "work" < "zzz_no_tags" is True
        # So note1 < note2 should be True
        assert note1 < note2
        assert not (note2 < note1)

    def test_lt_same_tags(self):
        """Test notes with same tags maintain order."""
        note1 = Note(text="Note 1", tags=["work"])
        note2 = Note(text="Note 2", tags=["work"])

        # Should be stable when tags are equal
        assert not (note1 < note2)
        assert not (note2 < note1)


class TestNoteDataclass:
    """Tests for Note dataclass methods."""

    def test_to_dict_with_tags(self, sample_note):
        """Test to_dict serialization with tags."""
        result = sample_note.to_dict()
        # Note: tags are sorted and cleaned during __post_init__
        expected_tags = sorted(["important", "urgent", "work"])
        assert result["text"] == "This is a sample note for testing purposes."
        assert sorted(result["tags"]) == expected_tags

    def test_to_dict_no_tags(self):
        """Test to_dict serialization without tags."""
        note = Note(text="Note without tags")
        result = note.to_dict()
        assert result == {
            "text": "Note without tags",
            "tags": [],
        }

    def test_from_dict_with_all_fields(self):
        """Test from_dict deserialization with all fields."""
        data = {
            "text": "Sample note",
            "tags": ["work", "important"],
        }
        note = Note.from_dict(data)
        assert note.text == "Sample note"
        # Note: tags are sorted and cleaned during __post_init__
        expected_tags = sorted(["important", "work"])
        assert sorted(note.tags) == expected_tags

    def test_from_dict_no_tags(self):
        """Test from_dict deserialization without tags."""
        data = {"text": "Note"}
        note = Note.from_dict(data)
        assert note.text == "Note"
        assert note.tags == []

    def test_from_dict_empty_text_uses_default(self):
        """Test from_dict uses empty string default for missing text."""
        data = {}
        note = Note.from_dict(data)
        assert note.text == ""
        assert note.tags == []

    def test_post_init_cleans_tags(self):
        """Test __post_init__ cleans tags on creation."""
        note = Note(text="Note", tags=["  TAG  ", "Tag", "  "])
        # Tags should be cleaned: deduplicated, lowercased
        assert note.tags == ["tag"]

    def test_post_init_empty_tags_list(self):
        """Test __post_init__ handles empty tags."""
        note = Note(text="Note", tags=[])
        assert note.tags == []

    def test_post_init_none_tags(self):
        """Test __post_init__ handles None tags."""
        note = Note(text="Note", tags=None)
        assert note.tags == []


class TestNotesBook:
    """Tests for NotesBook class."""

    @pytest.mark.unit
    def test_find_by_text(self, note_book):
        """Test find method searches in note text."""
        note_book.append(Note(text="Python is great", tags=["tech"]))
        note_book.append(Note(text="Testing is fun", tags=["work"]))

        results = note_book.find("python")
        assert len(results) == 1
        assert results[0].text == "Python is great"

    @pytest.mark.unit
    def test_find_by_tag(self, note_book):
        """Test find method searches in tags."""
        note_book.append(Note(text="Note 1", tags=["work", "important"]))
        note_book.append(Note(text="Note 2", tags=["personal"]))

        results = note_book.find("work")
        assert len(results) == 1
        assert "work" in results[0].tags

    @pytest.mark.unit
    def test_find_case_insensitive_text(self, note_book):
        """Test find method is case insensitive for text."""
        note_book.append(Note(text="PYTHON Code", tags=["tech"]))
        note_book.append(Note(text="Testing", tags=["work"]))

        results = note_book.find("python")
        assert len(results) == 1
        assert results[0].text == "PYTHON Code"

    @pytest.mark.unit
    def test_find_case_insensitive_tags(self, note_book):
        """Test find method is case insensitive for tags."""
        note_book.append(Note(text="Note 1", tags=["WORK", "important"]))
        note_book.append(Note(text="Note 2", tags=["personal"]))

        results = note_book.find("work")
        assert len(results) == 1
        assert "work" in results[0].tags

    @pytest.mark.unit
    def test_find_empty_book(self, note_book):
        """Test find method returns empty list for empty book."""
        results = note_book.find("search")
        assert results == []

    @pytest.mark.unit
    def test_find_no_matches(self, note_book):
        """Test find method returns empty list when no matches."""
        note_book.append(Note(text="Note 1", tags=["work"]))
        note_book.append(Note(text="Note 2", tags=["personal"]))

        results = note_book.find("nonexistent")
        assert results == []

    @pytest.mark.unit
    def test_find_by_tag_single_tag(self, note_book):
        """Test find_by_tag with single tag."""
        note_book.append(Note(text="Note 1", tags=["work", "urgent"]))
        note_book.append(Note(text="Note 2", tags=["personal"]))

        results = note_book.find_by_tag(["work"])
        assert len(results) == 1
        assert "work" in results[0].tags

    @pytest.mark.unit
    def test_find_by_tag_multiple_tags(self, note_book):
        """Test find_by_tag with multiple tags."""
        note_book.append(Note(text="Note 1", tags=["work"]))
        note_book.append(Note(text="Note 2", tags=["personal"]))
        note_book.append(Note(text="Note 3", tags=["urgent"]))

        results = note_book.find_by_tag(["work", "urgent"])
        assert len(results) == 2
        result_tags = [tags for note in results for tags in note.tags]
        assert "work" in result_tags
        assert "urgent" in result_tags

    @pytest.mark.unit
    def test_find_by_tag_case_insensitive(self, note_book):
        """Test find_by_tag is case insensitive."""
        note_book.append(Note(text="Note 1", tags=["WORK", "important"]))
        note_book.append(Note(text="Note 2", tags=["personal"]))

        results = note_book.find_by_tag(["work"])
        assert len(results) == 1
        assert "work" in results[0].tags

    @pytest.mark.unit
    def test_find_by_tag_no_matches(self, note_book):
        """Test find_by_tag returns empty list when no matches."""
        note_book.append(Note(text="Note 1", tags=["work"]))
        note_book.append(Note(text="Note 2", tags=["personal"]))

        results = note_book.find_by_tag(["urgent"])
        assert results == []

    @pytest.mark.unit
    def test_edit_text(self, note_book, sample_note):
        """Test edit method updates text."""
        note_book.append(sample_note)

        result = note_book.edit(1, {"text": "Updated text"})
        assert result is True
        assert note_book.data[0].text == "Updated text"

    @pytest.mark.unit
    def test_edit_tags(self, note_book, sample_note):
        """Test edit method updates tags."""
        note_book.append(sample_note)

        result = note_book.edit(1, {"tags": ["new", "tags"]})
        assert result is True
        assert "new" in note_book.data[0].tags
        assert "tags" in note_book.data[0].tags

    @pytest.mark.unit
    def test_edit_both_fields(self, note_book, sample_note):
        """Test edit method updates both text and tags."""
        note_book.append(sample_note)

        result = note_book.edit(1, {"text": "New text", "tags": ["new"]})
        assert result is True
        assert note_book.data[0].text == "New text"
        assert "new" in note_book.data[0].tags

    @pytest.mark.unit
    def test_edit_partial_update(self, note_book, sample_note):
        """Test edit method only updates provided fields."""
        note_book.append(sample_note)
        original_text = sample_note.text

        result = note_book.edit(1, {"tags": ["new"]})
        assert result is True
        assert note_book.data[0].text == original_text
        assert "new" in note_book.data[0].tags

    @pytest.mark.unit
    def test_edit_empty_fields(self, note_book, sample_note):
        """Test edit method ignores empty field values."""
        note_book.append(sample_note)
        original_text = sample_note.text

        result = note_book.edit(1, {"text": ""})
        assert result is True
        # Empty fields are not updated, so text stays the same
        assert note_book.data[0].text == original_text

    @pytest.mark.unit
    def test_edit_invalid_index(self, note_book):
        """Test edit method returns False for invalid index."""
        result = note_book.edit(999, {"text": "Test"})
        assert result is False

    @pytest.mark.unit
    def test_get_with_integer_index(self, note_book):
        """Test get method with integer index."""
        note_book.append(Note(text="Note 1"))
        note_book.append(Note(text="Note 2"))

        note = note_book.get(2)
        assert note is not None
        assert note.text == "Note 2"

    @pytest.mark.unit
    def test_get_with_string_index(self, note_book):
        """Test get method with string index."""
        note_book.append(Note(text="Note 1"))
        note_book.append(Note(text="Note 2"))

        note = note_book.get("1")
        assert note is not None
        assert note.text == "Note 1"

    @pytest.mark.unit
    def test_get_invalid_index(self, note_book):
        """Test get method returns None for invalid index."""
        note_book.append(Note(text="Note 1"))

        result = note_book.get(999)
        assert result is None

    @pytest.mark.unit
    def test_get_invalid_string_index(self, note_book):
        """Test get method returns None for non-numeric string."""
        note_book.append(Note(text="Note 1"))

        result = note_book.get("abc")
        assert result is None

    @pytest.mark.unit
    def test_load_from_list(self, note_book):
        """Test load_from_list replaces existing data."""
        data = [
            {"text": "Note 1", "tags": ["work"]},
            {"text": "Note 2", "tags": ["personal"]},
        ]

        note_book.load_from_list(data)

        assert len(note_book.data) == 2
        assert note_book.data[0].text == "Note 1"
        assert note_book.data[1].text == "Note 2"

    @pytest.mark.unit
    def test_load_from_list_empty(self, note_book):
        """Test load_from_list with empty list."""
        note_book.append(Note(text="Existing"))
        note_book.load_from_list([])

        assert len(note_book.data) == 0

    @pytest.mark.unit
    def test_sorted_by_tags(self, note_book):
        """Test sorted() sorts notes by tags alphabetically."""
        note_book.append(Note(text="Z", tags=["z"]))
        note_book.append(Note(text="A", tags=["a"]))
        note_book.append(Note(text="M", tags=["m"]))
        note_book.append(Note(text="No tags"))

        sorted_notes = sorted(note_book)

        assert sorted_notes[0].text == "A"
        assert sorted_notes[1].text == "M"
        assert sorted_notes[2].text == "Z"
        assert sorted_notes[3].text == "No tags"

    @pytest.mark.unit
    def test_sorted_preserves_no_tags_notes_at_end(self, note_book):
        """Test sorted() places notes without tags at the end."""
        note_book.append(Note(text="With tags", tags=["work"]))
        note_book.append(Note(text="Without tags"))

        sorted_notes = sorted(note_book)

        assert sorted_notes[0].text == "With tags"
        assert sorted_notes[1].text == "Without tags"

    @pytest.mark.unit
    def test_sorted_multiple_tags_same_prefix(self, note_book):
        """Test sorted() handles notes with similar tag prefixes."""
        note_book.append(Note(text="1", tags=["alpha"]))
        note_book.append(Note(text="2", tags=["alpha-beta"]))
        note_book.append(Note(text="3", tags=["alpha", "beta"]))

        sorted_notes = sorted(note_book)

        # "alpha, beta" should come before "alpha-beta"
        # Because when sorted: ["alpha", "beta"] vs "alpha, beta"
        # "alpha, beta" < "alpha-beta"
        assert sorted_notes[0].text == "1"
        assert sorted_notes[1].text == "3"
        assert sorted_notes[2].text == "2"
