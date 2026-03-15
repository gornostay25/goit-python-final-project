"""Tests for storage module - Storage class."""

import json

from app.contacts import Contact, ContactBook
from app.storage import Storage


class TestStorageInitialization:
    """Tests for Storage initialization."""

    def test_storage_initialization(self):
        """Test Storage creates with Book and filename."""
        contact_book = ContactBook()
        storage = Storage(contact_book, "contacts.json")
        assert storage.book == contact_book
        assert storage.filename == "contacts.json"


class TestStorageSave:
    """Tests for Storage save functionality."""

    def test_save_creates_file(self, tmp_path):
        """Test save creates JSON file with correct content."""
        contact_book = ContactBook()
        contact_book.append(
            Contact.from_dict(
                {
                    "name": "John Doe",
                    "phone": "+1234567890",
                    "email": "john@example.com",
                }
            )
        )

        filename = tmp_path / "contacts.json"
        storage = Storage(contact_book, str(filename))
        storage.save()

        assert filename.exists()
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        assert len(data) == 1
        assert data[0]["name"] == "John Doe"
        assert data[0]["phone"] == "+1234567890"

    def test_save_overwrites_existing(self, tmp_path):
        """Test save overwrites existing file."""
        contact_book = ContactBook()
        filename = tmp_path / "contacts.json"

        # Create initial file
        with open(filename, "w", encoding="utf-8") as file:
            json.dump([{"old": "data"}], file)

        storage = Storage(contact_book, str(filename))
        contact_book.append(
            Contact.from_dict(
                {
                    "name": "Jane Doe",
                    "phone": "+1234567891",
                }
            )
        )
        storage.save()

        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        assert "old" not in data[0]
        assert data[0]["name"] == "Jane Doe"


class TestStorageLoad:
    """Tests for Storage load functionality."""

    def test_load_existing_file(self, tmp_path):
        """Test load populates Book from JSON file."""
        filename = tmp_path / "contacts.json"

        # Create test data file
        test_data = [
            {
                "name": "John Doe",
                "phone": "+1234567890",
                "email": "john@example.com",
            },
            {
                "name": "Jane Doe",
                "phone": "+1234567891",
                "email": "jane@example.com",
            },
        ]
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(test_data, file)

        contact_book = ContactBook()
        storage = Storage(contact_book, str(filename))
        storage.load()

        assert len(contact_book) == 2
        assert contact_book[0].name == "John Doe"
        assert contact_book[1].name == "Jane Doe"

    def test_load_nonexistent_file(self, tmp_path):
        """Test load handles missing file gracefully."""
        filename = tmp_path / "nonexistent.json"
        contact_book = ContactBook()
        storage = Storage(contact_book, str(filename))

        # Should not raise exception
        storage.load()
        assert len(contact_book) == 0

    def test_load_invalid_json(self, tmp_path):
        """Test load handles corrupt JSON."""
        filename = tmp_path / "invalid.json"

        # Create invalid JSON file
        with open(filename, "w", encoding="utf-8") as file:
            file.write("{ invalid json }")

        contact_book = ContactBook()
        storage = Storage(contact_book, str(filename))

        # Should not raise exception
        storage.load()
        assert len(contact_book) == 0

    def test_load_malformed_items(self, tmp_path):
        """Test load skips malformed items gracefully."""
        filename = tmp_path / "contacts.json"

        # Create file with valid and invalid data
        test_data = [
            {
                "name": "John Doe",
                "phone": "+1234567890",
            },
            {
                "invalid": "item",
                "missing": "fields",
            },
            {
                "name": "Jane Doe",
                "phone": "+1234567891",
            },
        ]
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(test_data, file)

        contact_book = ContactBook()
        storage = Storage(contact_book, str(filename))
        storage.load()

        # Should load only valid items
        assert len(contact_book) == 2
        assert contact_book[0].name == "John Doe"
        assert contact_book[1].name == "Jane Doe"


class TestStorageRoundtrip:
    """Tests for save/load data integrity."""

    def test_save_load_roundtrip(self, tmp_path):
        """Test data integrity through save/load cycle."""
        filename = tmp_path / "contacts.json"

        # Create original data
        original_contacts = [
            Contact.from_dict(
                {
                    "name": "John Doe",
                    "phone": "+1234567890",
                    "email": "john@example.com",
                    "birthday": "01.01.1990",
                    "address": "123 Main St",
                }
            ),
            Contact.from_dict(
                {
                    "name": "Jane Doe",
                    "phone": "+1234567891",
                    "email": "jane@example.com",
                }
            ),
            Contact.from_dict(
                {
                    "name": "Jim Doe",
                    "phone": "+1234567892",
                }
            ),
        ]

        contact_book = ContactBook()
        for contact in original_contacts:
            contact_book.append(contact)

        # Save to file
        storage = Storage(contact_book, str(filename))
        storage.save()

        # Load into new book
        new_contact_book = ContactBook()
        new_storage = Storage(new_contact_book, str(filename))
        new_storage.load()

        # Verify data integrity
        assert len(new_contact_book) == len(original_contacts)
        for i, contact in enumerate(new_contact_book.data):
            assert contact.name == original_contacts[i].name
            assert contact.phone == original_contacts[i].phone
            assert contact.email == original_contacts[i].email
            assert contact.birthday == original_contacts[i].birthday
            assert contact.address == original_contacts[i].address

    def test_empty_book_save_load(self, tmp_path):
        """Test save and load with empty book."""
        filename = tmp_path / "empty.json"

        contact_book = ContactBook()
        storage = Storage(contact_book, str(filename))
        storage.save()

        new_contact_book = ContactBook()
        new_storage = Storage(new_contact_book, str(filename))
        new_storage.load()

        assert len(new_contact_book) == 0
