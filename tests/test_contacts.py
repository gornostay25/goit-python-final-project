"""Tests for contacts module - Contact, Birthday, and ContactBook classes."""

from datetime import datetime

import pytest

from app.contacts import Birthday, Contact


class TestBirthday:
    """Tests for Birthday class."""

    @pytest.mark.parametrize(
        "date_str,expected_str",
        [
            ("15.06.1990", "15.06.1990"),
            ("01.01.2000", "01.01.2000"),
            ("31.12.2025", "31.12.2025"),
        ],
    )
    def test_birthday_creation_valid_format(self, date_str, expected_str):
        """Test birthday creation with valid DD.MM.YYYY format."""
        birthday = Birthday(date_str)
        assert str(birthday) == expected_str
        assert birthday.value == datetime.strptime(date_str, "%d.%m.%Y").date()

    @pytest.mark.parametrize(
        "date_str",
        [
            "1990-06-15",
            "15/06/1990",
            "06.15.1990",
            "invalid",
            "32.13.1990",
        ],
    )
    def test_birthday_creation_invalid_format(self, date_str):
        """Test birthday raises ValueError for invalid formats."""
        with pytest.raises(ValueError, match="Invalid date format"):
            Birthday(date_str)

    def test_birthday_none_value(self):
        """Test birthday with None value."""
        birthday = Birthday(None)
        assert birthday.value is None
        assert str(birthday) == ""

    def test_birthday_empty_string(self):
        """Test birthday with empty string."""
        birthday = Birthday("")
        assert birthday.value is None
        assert str(birthday) == ""

    def test_birthday_repr(self):
        """Test __repr__ returns string representation."""
        birthday = Birthday("15.06.1990")
        assert repr(birthday) == "15.06.1990"


class TestContactValidation:
    """Tests for Contact static validation methods."""

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("John Doe", True),
            ("Alice", True),
            ("Bob Smith Jr.", True),
            ("  John  ", True),
            ("", False),
            ("   ", False),
        ],
    )
    def test_validate_name(self, name, expected):
        """Test name validation."""
        assert Contact.validate_name(name) == expected

    @pytest.mark.parametrize(
        "phone,expected",
        [
            pytest.param("+380501234567", True, id="valid_uk_phone"),
            pytest.param("+12345678901234", True, id="valid_international"),
            pytest.param("+441234567890", True, id="valid_uk_international"),
            pytest.param("380501234567", False, id="missing_country_code"),
            pytest.param("+123", False, id="too_short"),
            pytest.param("+380501234", False, id="too_short_with_code"),
            pytest.param("+123456789012345", False, id="too_long"),
            pytest.param("", False, id="empty"),
        ],
    )
    def test_validate_phone(self, phone, expected):
        """Test phone number validation."""
        result = Contact.validate_phone(phone)
        assert result == expected

    @pytest.mark.parametrize(
        "email,expected",
        [
            pytest.param("john@example.com", True, id="valid_simple"),
            pytest.param("alice.smith@domain.co.uk", True, id="valid_with_dots"),
            pytest.param("user_tag@email.org", True, id="valid_with_underscore"),
            pytest.param("john@example", False, id="missing_tld"),
            pytest.param("@example.com", False, id="missing_local_part"),
            pytest.param("john@", False, id="missing_domain"),
            pytest.param("", False, id="empty"),
        ],
    )
    def test_validate_email(self, email, expected):
        """Test email validation."""
        result = Contact.validate_email(email)
        assert result == expected

    @pytest.mark.parametrize(
        "birthday,expected",
        [
            ("15.06.1990", True),
            ("01.01.2000", True),
            ("31.12.2025", True),
            ("1990-06-15", False),
            ("15/06/1990", False),
            ("invalid", False),
            ("32.13.1990", False),
            ("", False),
        ],
    )
    def test_validate_birthday(self, birthday, expected):
        """Test birthday validation."""
        assert Contact.validate_birthday(birthday) == expected


class TestContactDataclass:
    """Tests for Contact dataclass methods."""

    def test_to_dict_all_fields(self, sample_contact):
        """Test to_dict serialization with all fields."""
        result = sample_contact.to_dict()
        assert result["name"] == "John Doe"
        assert result["phone"] == "+380501234567"
        assert result["email"] == "john@example.com"
        assert result["birthday"] == sample_contact.birthday
        assert result["address"] == "123 Main St, City"

    def test_to_dict_required_fields_only(self):
        """Test to_dict with only required fields."""
        contact = Contact(name="Jane Doe", phone="+380509876543")
        result = contact.to_dict()
        assert result["name"] == "Jane Doe"
        assert result["phone"] == "+380509876543"
        assert result["email"] is None
        assert result["birthday"] is None
        assert result["address"] is None

    def test_from_dict_all_fields(self):
        """Test from_dict deserialization with all fields."""
        data = {
            "name": "Alice",
            "phone": "+38050111222333",
            "email": "alice@test.com",
            "birthday": "20.03.1985",
            "address": "456 Oak Ave",
        }
        contact = Contact.from_dict(data)
        assert contact.name == "Alice"
        assert contact.phone == "+38050111222333"
        assert contact.email == "alice@test.com"
        assert str(contact.birthday) == "20.03.1985"
        assert contact.address == "456 Oak Ave"

    def test_from_dict_required_fields_only(self):
        """Test from_dict with only required fields."""
        data = {"name": "Bob", "phone": "+38050222333444"}
        contact = Contact.from_dict(data)
        assert contact.name == "Bob"
        assert contact.phone == "+38050222333444"
        assert contact.email is None
        assert contact.birthday is None
        assert contact.address is None


class TestContactBook:
    """Tests for ContactBook class."""

    @pytest.mark.unit
    def test_find_by_name(self, contact_book):
        """Test find method searching by name."""
        contact_book.append(Contact(name="John Doe", phone="+380501111111"))
        contact_book.append(Contact(name="Jane Smith", phone="+380502222222"))

        results = contact_book.find("john")
        assert len(results) == 1
        assert results[0].name == "John Doe"

    @pytest.mark.unit
    def test_find_by_phone(self, contact_book):
        """Test find method searching by phone."""
        contact_book.append(Contact(name="Alice", phone="+380501111111"))
        contact_book.append(Contact(name="Bob", phone="+380502222222"))

        results = contact_book.find("+380501")
        assert len(results) == 1
        assert results[0].phone == "+380501111111"

    @pytest.mark.unit
    def test_find_by_email(self, contact_book):
        """Test find method searching by email."""
        contact_book.append(
            Contact(name="Alice", phone="+380501111111", email="alice@test.com")
        )
        contact_book.append(
            Contact(name="Bob", phone="+380502222222", email="bob@test.com")
        )

        results = contact_book.find("alice@test.com")
        assert len(results) == 1
        assert results[0].email == "alice@test.com"

    @pytest.mark.unit
    def test_find_by_address(self, contact_book):
        """Test find method searching by address."""
        contact_book.append(
            Contact(name="Alice", phone="+380501111111", address="123 Main St")
        )
        contact_book.append(
            Contact(name="Bob", phone="+380502222222", address="456 Oak Ave")
        )

        results = contact_book.find("main")
        assert len(results) == 1
        assert results[0].address == "123 Main St"

    @pytest.mark.unit
    def test_find_by_birthday(self, contact_book):
        """Test find method searching by birthday."""
        contact_book.append(
            Contact(name="Alice", phone="+380501111111", birthday="15.06.1990")
        )
        contact_book.append(
            Contact(name="Bob", phone="+380502222222", birthday="20.03.1985")
        )

        results = contact_book.find("1990")
        assert len(results) == 1
        assert results[0].name == "Alice"

    @pytest.mark.unit
    def test_find_empty_book(self, contact_book):
        """Test find method returns empty list for empty book."""
        results = contact_book.find("john")
        assert results == []

    @pytest.mark.unit
    def test_find_case_insensitive(self, contact_book):
        """Test find method is case insensitive."""
        contact_book.append(Contact(name="John Doe", phone="+380501111111"))
        contact_book.append(Contact(name="JANE SMITH", phone="+380502222222"))

        results = contact_book.find("doe")
        assert len(results) == 1
        assert results[0].name == "John Doe"

        results = contact_book.find("jane")
        assert len(results) == 1
        assert results[0].name == "JANE SMITH"

    @pytest.mark.unit
    def test_upcoming_birthdays_today(self, contacts_with_birthdays):
        """Test upcoming_birthdays includes birthday today."""
        results = contacts_with_birthdays.upcoming_birthdays(7)
        today_names = [r["name"] for r in results]
        assert "Birthday Today" in today_names

    @pytest.mark.unit
    def test_upcoming_birthdays_tomorrow(self, contacts_with_birthdays):
        """Test upcoming_birthdays includes birthday tomorrow."""
        results = contacts_with_birthdays.upcoming_birthdays(7)
        today_names = [r["name"] for r in results]
        assert "Birthday Tomorrow" in today_names

    @pytest.mark.unit
    def test_upcoming_birthdays_next_week(self, contacts_with_birthdays):
        """Test upcoming_birthdays includes birthday in 7 days."""
        results = contacts_with_birthdays.upcoming_birthdays(7)
        today_names = [r["name"] for r in results]
        assert "Birthday Next Week" in today_names

    @pytest.mark.unit
    def test_upcoming_birthdays_past_wraps_to_next_year(self, contacts_with_birthdays):
        """Test upcoming_birthdays wraps past birthdays to next year."""
        results = contacts_with_birthdays.upcoming_birthdays(365)
        today_names = [r["name"] for r in results]
        # Past birthday should appear when searching far enough ahead
        assert "Birthday Past" in today_names

    @pytest.mark.unit
    def test_upcoming_birthdays_no_birthday_contact(self, contacts_with_birthdays):
        """Test upcoming_birthdays excludes contacts without birthday."""
        results = contacts_with_birthdays.upcoming_birthdays(7)
        today_names = [r["name"] for r in results]
        assert "No Birthday" not in today_names

    @pytest.mark.unit
    def test_upcoming_birthdays_days_parameter(self, contacts_with_birthdays):
        """Test upcoming_birthdays respects days parameter."""
        results_1_day = contacts_with_birthdays.upcoming_birthdays(1)
        results_7_days = contacts_with_birthdays.upcoming_birthdays(7)

        # More birthdays should be found with larger day range
        assert len(results_7_days) >= len(results_1_day)

    @pytest.mark.unit
    def test_edit_name(self, contact_book, sample_contact):
        """Test edit method updates name."""
        contact_book.append(sample_contact)

        result = contact_book.edit(1, {"name": "Jane Doe"})
        assert result is True
        assert contact_book.data[0].name == "Jane Doe"

    @pytest.mark.unit
    def test_edit_phone(self, contact_book, sample_contact):
        """Test edit method updates phone."""
        contact_book.append(sample_contact)

        result = contact_book.edit(1, {"phone": "+380509876543"})
        assert result is True
        assert contact_book.data[0].phone == "+380509876543"

    @pytest.mark.unit
    def test_edit_email(self, contact_book, sample_contact):
        """Test edit method updates email."""
        contact_book.append(sample_contact)

        result = contact_book.edit(1, {"email": "newemail@test.com"})
        assert result is True
        assert contact_book.data[0].email == "newemail@test.com"

    @pytest.mark.unit
    def test_edit_address(self, contact_book, sample_contact):
        """Test edit method updates address."""
        contact_book.append(sample_contact)

        result = contact_book.edit(1, {"address": "New Address"})
        assert result is True
        assert contact_book.data[0].address == "New Address"

    @pytest.mark.unit
    def test_edit_birthday(self, contact_book, sample_contact):
        """Test edit method updates birthday."""
        contact_book.append(sample_contact)

        result = contact_book.edit(1, {"birthday": "20.03.1985"})
        assert result is True
        assert str(contact_book.data[0].birthday) == "20.03.1985"

    @pytest.mark.unit
    def test_edit_multiple_fields(self, contact_book, sample_contact):
        """Test edit method updates multiple fields."""
        contact_book.append(sample_contact)

        result = contact_book.edit(1, {"name": "Jane", "phone": "+380509876543"})
        assert result is True
        assert contact_book.data[0].name == "Jane"
        assert contact_book.data[0].phone == "+380509876543"

    @pytest.mark.unit
    def test_edit_partial_update(self, contact_book, sample_contact):
        """Test edit method only updates provided fields."""
        contact_book.append(sample_contact)
        original_email = sample_contact.email
        original_address = sample_contact.address

        result = contact_book.edit(1, {"name": "Jane Doe"})
        assert result is True
        assert contact_book.data[0].name == "Jane Doe"
        assert contact_book.data[0].email == original_email
        assert contact_book.data[0].address == original_address

    @pytest.mark.unit
    def test_edit_invalid_index(self, contact_book):
        """Test edit method returns False for invalid index."""
        result = contact_book.edit(999, {"name": "Test"})
        assert result is False

    @pytest.mark.unit
    def test_edit_empty_fields(self, contact_book, sample_contact):
        """Test edit method ignores empty field values."""
        contact_book.append(sample_contact)
        original_name = sample_contact.name

        result = contact_book.edit(1, {"name": ""})
        assert result is True
        assert contact_book.data[0].name == original_name

    @pytest.mark.unit
    def test_load_from_list(self, contact_book):
        """Test load_from_list replaces existing data."""
        data = [
            {
                "name": "Contact 1",
                "phone": "+380501111111",
                "email": "contact1@test.com",
            },
            {
                "name": "Contact 2",
                "phone": "+380502222222",
                "birthday": "15.06.1990",
            },
        ]

        contact_book.load_from_list(data)

        assert len(contact_book.data) == 2
        assert contact_book.data[0].name == "Contact 1"
        assert contact_book.data[1].name == "Contact 2"

    @pytest.mark.unit
    def test_load_from_list_empty(self, contact_book):
        """Test load_from_list with empty list."""
        contact_book.append(Contact(name="Existing", phone="+380501111111"))
        contact_book.load_from_list([])

        assert len(contact_book.data) == 0
