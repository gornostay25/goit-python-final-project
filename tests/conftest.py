"""Pytest configuration and shared fixtures."""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from rich.console import Console

from app.contacts import Birthday, Contact, ContactBook
from app.notes import Note, NotesBook


@pytest.fixture
def contact_book():
    """Provide fresh ContactBook instance for each test."""
    return ContactBook()


@pytest.fixture
def note_book():
    """Provide fresh NotesBook instance for each test."""
    return NotesBook()


@pytest.fixture
def sample_contact():
    """Provide sample contact with all fields populated."""
    return Contact(
        name="John Doe",
        phone="+380501234567",
        email="john@example.com",
        birthday=Birthday("15.06.1990"),
        address="123 Main St, City",
    )


@pytest.fixture
def sample_note():
    """Provide sample note with text and tags."""
    return Note(
        text="This is a sample note for testing purposes.",
        tags=["important", "work", "urgent"],
    )


@pytest.fixture
def mock_console():
    """Provide mock Console for CLI tests."""
    console = Mock(spec=Console)
    return console


@pytest.fixture
def contacts_with_birthdays():
    """Provide ContactBook with contacts having various birthdays."""
    book = ContactBook()
    today = datetime.today().date()

    # Birthday today
    book.append(
        Contact(
            name="Birthday Today",
            phone="+380501111111",
            birthday=Birthday(today.strftime("%d.%m.%Y")),
        )
    )

    # Birthday tomorrow
    tomorrow = today + timedelta(days=1)
    book.append(
        Contact(
            name="Birthday Tomorrow",
            phone="+380502222222",
            birthday=Birthday(tomorrow.strftime("%d.%m.%Y")),
        )
    )

    # Birthday in 7 days
    next_week = today + timedelta(days=7)
    book.append(
        Contact(
            name="Birthday Next Week",
            phone="+380503333333",
            birthday=Birthday(next_week.strftime("%d.%m.%Y")),
        )
    )

    # Birthday past this year
    past_date = today - timedelta(days=100)
    book.append(
        Contact(
            name="Birthday Past",
            phone="+380504444444",
            birthday=Birthday(past_date.strftime("%d.%m.%Y")),
        )
    )

    # Contact without birthday
    book.append(
        Contact(
            name="No Birthday",
            phone="+380505555555",
        )
    )

    return book
