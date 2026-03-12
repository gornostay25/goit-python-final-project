"""Shared pytest fixtures for contacts module tests."""

import pytest
from datetime import date, timedelta

from app.contacts import Birthday, Contact, ContactBook


@pytest.fixture
def sample_contact():
    """Provide a complete Contact instance for testing."""
    return Contact(
        name="John Doe",
        phone="+12345678901",
        email="john.doe@example.com",
        birthday=Birthday("15.06.1990"),
        address="123 Main St, City",
    )


@pytest.fixture
def sample_contact_no_birthday():
    """Provide a Contact instance without birthday."""
    return Contact(
        name="Jane Smith",
        phone="+19876543210",
        email="jane.smith@example.com",
        address="456 Oak Ave, Town",
    )


@pytest.fixture
def contact_book(sample_contact, sample_contact_no_birthday):
    """Provide a ContactBook populated with test data."""
    book = ContactBook()
    book.append(sample_contact)
    book.append(sample_contact_no_birthday)
    book.append(
        Contact(
            name="Bob Johnson",
            phone="+15555555555",
            email="bob@example.com",
            birthday=Birthday("01.01.1985"),
        )
    )
    book.append(
        Contact(
            name="Alice Williams",
            phone="+14444444444",
            email="alice@example.com",
        )
    )
    return book


@pytest.fixture
def valid_contacts_data():
    """Provide list of contact dictionaries for serialization tests."""
    return [
        {
            "name": "John Doe",
            "phone": "+12345678901",
            "email": "john.doe@example.com",
            "birthday": "15.06.1990",
            "address": "123 Main St, City",
        },
        {
            "name": "Jane Smith",
            "phone": "+19876543210",
            "email": "jane.smith@example.com",
            "birthday": None,
            "address": "456 Oak Ave, Town",
        },
        {
            "name": "Bob Johnson",
            "phone": "+15555555555",
            "email": "bob@example.com",
            "birthday": "01.01.1985",
            "address": None,
        },
    ]


@pytest.fixture
def today_plus_delta():
    """Helper fixture to get today's date plus delta days."""

    def _get_days(delta: int) -> str:
        return (date.today() + timedelta(days=delta)).strftime("%d.%m.%Y")

    return _get_days


@pytest.fixture
def today_minus_delta():
    """Helper fixture to get today's date minus delta days."""

    def _get_days(delta: int) -> str:
        return (date.today() - timedelta(days=delta)).strftime("%d.%m.%Y")

    return _get_days
