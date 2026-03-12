"""Tests for contacts module - Birthday, Contact, and ContactBook classes."""

import pytest
from app.contacts import Birthday, Contact, ContactBook


@pytest.mark.unit
class TestBirthday:
    """Test cases for Birthday class."""

    def test_birthday_valid_format(self):
        """Test successful creation with DD.MM.YYYY format."""
        birthday = Birthday("15.06.1990")
        assert birthday.value.day == 15
        assert birthday.value.month == 6
        assert birthday.value.year == 1990

    def test_birthday_invalid_format_wrong_separator(self):
        """Test ValueError for wrong date separator."""
        with pytest.raises(ValueError, match="Invalid date format"):
            Birthday("15-06-1990")

    def test_birthday_invalid_format_wrong_order(self):
        """Test ValueError for wrong date order."""
        with pytest.raises(ValueError, match="Invalid date format"):
            Birthday("1990.06.15")

    def test_birthday_invalid_format_invalid_day(self):
        """Test ValueError for invalid day."""
        with pytest.raises(ValueError, match="Invalid date format"):
            Birthday("32.06.1990")

    def test_birthday_invalid_format_invalid_month(self):
        """Test ValueError for invalid month."""
        with pytest.raises(ValueError, match="Invalid date format"):
            Birthday("15.13.1990")

    def test_birthday_invalid_format_invalid_date(self):
        """Test ValueError for non-existent date (February 30)."""
        with pytest.raises(ValueError, match="Invalid date format"):
            Birthday("30.02.2020")

    def test_birthday_empty_value(self):
        """Test that None is accepted for optional birthday."""
        birthday = Birthday("")
        assert birthday.value is None

    def test_birthday_none_value(self):
        """Test that None is accepted for optional birthday."""
        birthday = Birthday(None)
        assert birthday.value is None

    def test_birthday_string_representation(self):
        """Test __str__ returns correct format."""
        birthday = Birthday("15.06.1990")
        assert str(birthday) == "15.06.1990"

    def test_birthday_repr(self):
        """Test __repr__ returns same as __str__."""
        birthday = Birthday("15.06.1990")
        assert repr(birthday) == str(birthday)

    def test_birthday_leap_year(self):
        """Test birthday with leap year date."""
        birthday = Birthday("29.02.2020")
        assert birthday.value.day == 29
        assert birthday.value.month == 2
        assert birthday.value.year == 2020


@pytest.mark.unit
class TestContactValidation:
    """Test cases for Contact validation methods."""

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("John Doe", True),
            ("Jane", True),
            ("  John  ", True),
            ("J", True),
            ("", False),
            ("   ", False),
            ("\t\n", False),
        ],
    )
    def test_validate_name(self, name, expected):
        """Test name validation with parametrization."""
        assert Contact.validate_name(name) == expected

    @pytest.mark.parametrize(
        "phone,expected",
        [
            ("+12345678901", True),
            ("+380677773783", True),
            ("+38268461336", True),
            ("+123456789012345", True),
            ("+1234567890", True),
            ("  +12345678901  ", True),
            ("12345678901", False),
            ("+123456789", False),
            ("+1234567890123456", True),
            ("+1-234-567-8901", False),
            ("", False),
            ("+", False),
        ],
    )
    def test_validate_phone(self, phone, expected):
        """Test phone number validation (E.164 format)."""
        assert Contact.validate_phone(phone) == expected

    @pytest.mark.parametrize(
        "email,expected",
        [
            ("user@example.com", True),
            ("test.user@domain.co.uk", True),
            ("  email@example.com  ", True),
            ("user@localhost", False),
            ("invalid", False),
            ("@example.com", False),
            ("user@", False),
            ("user@", False),
            ("", False),
            ("   ", False),
        ],
    )
    def test_validate_email(self, email, expected):
        """Test email format validation."""
        assert Contact.validate_email(email) == expected

    @pytest.mark.parametrize(
        "birthday,expected",
        [
            ("15.06.1990", True),
            ("01.01.2000", True),
            ("31.12.2023", True),
            ("  15.06.1990  ", True),
            ("15-06-1990", False),
            ("1990.06.15", False),
            ("32.06.1990", False),
            ("30.02.2020", False),
            ("", False),
            ("   ", False),
        ],
    )
    def test_validate_birthday(self, birthday, expected):
        """Test birthday format validation."""
        assert Contact.validate_birthday(birthday) == expected


@pytest.mark.unit
class TestContactClass:
    """Test cases for Contact dataclass."""

    def test_contact_creation(self, sample_contact):
        """Test Contact dataclass creation."""
        assert sample_contact.name == "John Doe"
        assert sample_contact.phone == "+12345678901"
        assert sample_contact.email == "john.doe@example.com"
        assert sample_contact.birthday.value.day == 15
        assert sample_contact.birthday.value.month == 6
        assert sample_contact.birthday.value.year == 1990
        assert sample_contact.address == "123 Main St, City"

    def test_contact_with_optional_fields(self):
        """Test Contact with only required fields."""
        contact = Contact(name="Test User", phone="+12345678901")
        assert contact.name == "Test User"
        assert contact.phone == "+12345678901"
        assert contact.email is None
        assert contact.birthday is None
        assert contact.address is None

    def test_contact_to_dict(self, sample_contact):
        """Test serialization to dictionary."""
        result = sample_contact.to_dict()
        assert result["name"] == "John Doe"
        assert result["phone"] == "+12345678901"
        assert result["email"] == "john.doe@example.com"
        # Birthday is a Birthday object, not a string after `asdict`
        assert str(result["birthday"]) == "15.06.1990"
        assert result["address"] == "123 Main St, City"

    def test_contact_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "name": "Test User",
            "phone": "+12345678901",
            "email": "test@example.com",
            "birthday": "01.01.1990",
            "address": "Test Address",
        }
        contact = Contact.from_dict(data)
        assert contact.name == "Test User"
        assert contact.phone == "+12345678901"
        assert contact.email == "test@example.com"
        assert str(contact.birthday) == "01.01.1990"
        assert contact.address == "Test Address"

    def test_contact_from_dict_with_none_values(self):
        """Test deserialization with None values."""
        data = {
            "name": "Test User",
            "phone": "+12345678901",
            "email": None,
            "birthday": None,
            "address": None,
        }
        contact = Contact.from_dict(data)
        assert contact.name == "Test User"
        assert contact.phone == "+12345678901"
        assert contact.email is None
        assert contact.birthday.value is None
        assert contact.address is None


@pytest.mark.unit
class TestContactBook:
    """Test cases for ContactBook class."""

    def test_contact_book_add_contact(self, sample_contact):
        """Test adding contacts to ContactBook."""
        book = ContactBook()
        book.append(sample_contact)
        assert len(book) == 1
        assert book[0] == sample_contact

    def test_contact_book_initialization_empty(self):
        """Test ContactBook initialization with no contacts."""
        book = ContactBook()
        assert len(book) == 0
        assert list(book) == []

    # Find Exact Tests
    def test_find_exact(self, contact_book):
        """Test exact name matching (case-insensitive)."""
        result = contact_book.find_exact("John Doe")
        assert result is not None
        assert result.name == "John Doe"

    def test_find_exact_case_insensitive(self, contact_book):
        """Test exact name matching with different cases."""
        result = contact_book.find_exact("JOHN DOE")
        assert result is not None
        assert result.name == "John Doe"

        result = contact_book.find_exact("john doe")
        assert result is not None
        assert result.name == "John Doe"

    def test_find_exact_not_found(self, contact_book):
        """Test when contact doesn't exist."""
        result = contact_book.find_exact("Unknown Person")
        assert result is None

    # Find Tests
    def test_find_by_name(self, contact_book):
        """Test searching by name (substring, case-insensitive)."""
        results = contact_book.find("John Doe")
        assert len(results) == 1
        assert results[0].name == "John Doe"

    def test_find_by_name_case_insensitive(self, contact_book):
        """Test name search with different cases."""
        results = contact_book.find("john doe")
        assert len(results) == 1
        assert results[0].name == "John Doe"

    def test_find_by_phone(self, contact_book):
        """Test searching by phone number."""
        results = contact_book.find("+12345678901")
        assert len(results) == 1
        assert results[0].phone == "+12345678901"

    def test_find_by_email(self, contact_book):
        """Test searching by email."""
        results = contact_book.find("john.doe@example.com")
        assert len(results) == 1
        assert results[0].email == "john.doe@example.com"

    def test_find_by_email_case_insensitive(self, contact_book):
        """Test email search with different cases."""
        results = contact_book.find("john.doe@example.com".upper())
        assert len(results) == 1

    def test_find_by_address(self, contact_book):
        """Test searching by address."""
        results = contact_book.find("Main St")
        assert len(results) == 1
        assert "Main St" in results[0].address

    def test_find_by_birthday(self, contact_book):
        """Test searching by birthday."""
        results = contact_book.find("15.06.1990")
        assert len(results) == 1
        assert results[0].name == "John Doe"

    def test_find_multiple_results(self, contact_book):
        """Test finding multiple matching contacts."""
        book = ContactBook()
        book.append(Contact(name="John Doe", phone="+11111111111"))
        book.append(Contact(name="John Smith", phone="+22222222222"))
        book.append(Contact(name="Jane Doe", phone="+33333333333"))
        results = book.find("John")
        assert len(results) == 2

    def test_find_no_results(self, contact_book):
        """Test search with no matching results."""
        results = contact_book.find("NonExistentTerm")
        assert len(results) == 0

    # Delete Tests
    def test_delete_contact(self, contact_book):
        """Test deleting existing contact."""
        initial_length = len(contact_book)
        result = contact_book.delete("John Doe")
        assert result is True
        assert len(contact_book) == initial_length - 1
        assert contact_book.find_exact("John Doe") is None

    def test_delete_contact_case_insensitive(self, contact_book):
        """Test deleting contact with different case."""
        initial_length = len(contact_book)
        result = contact_book.delete("JOHN DOE")
        assert result is True
        assert len(contact_book) == initial_length - 1

    def test_delete_nonexistent_contact(self, contact_book):
        """Test deleting non-existing contact."""
        initial_length = len(contact_book)
        result = contact_book.delete("Unknown Person")
        assert result is False
        assert len(contact_book) == initial_length

    # Edit Tests
    def test_edit_contact_phone(self, contact_book):
        """Test editing phone field."""
        result = contact_book.edit("John Doe", {"phone": "+99999999999"})
        assert result is True
        contact = contact_book.find_exact("John Doe")
        assert contact.phone == "+99999999999"

    def test_edit_contact_email(self, contact_book):
        """Test editing email field."""
        result = contact_book.edit("John Doe", {"email": "newemail@example.com"})
        assert result is True
        contact = contact_book.find_exact("John Doe")
        assert contact.email == "newemail@example.com"

    def test_edit_contact_address(self, contact_book):
        """Test editing address field."""
        result = contact_book.edit("John Doe", {"address": "New Address 123"})
        assert result is True
        contact = contact_book.find_exact("John Doe")
        assert contact.address == "New Address 123"

    def test_edit_contact_birthday(self, contact_book):
        """Test editing birthday field."""
        result = contact_book.edit("John Doe", {"birthday": "20.07.1995"})
        assert result is True
        contact = contact_book.find_exact("John Doe")
        assert str(contact.birthday) == "20.07.1995"

    def test_edit_multiple_fields(self, contact_book):
        """Test editing multiple fields at once."""
        result = contact_book.edit(
            "John Doe",
            {
                "phone": "+99999999999",
                "email": "new@example.com",
                "address": "New Addr",
            },
        )
        assert result is True
        contact = contact_book.find_exact("John Doe")
        assert contact.phone == "+99999999999"
        assert contact.email == "new@example.com"
        assert contact.address == "New Addr"

    def test_edit_with_whitespace(self, contact_book):
        """Test editing with whitespace gets stripped."""
        result = contact_book.edit("John Doe", {"phone": "  +99999999999  "})
        assert result is True
        contact = contact_book.find_exact("John Doe")
        assert contact.phone == "+99999999999"

    def test_edit_nonexistent_contact(self, contact_book):
        """Test editing non-existing contact."""
        result = contact_book.edit("Unknown Person", {"phone": "+99999999999"})
        assert result is False

    # Upcoming Birthdays Tests
    def test_upcoming_birthdays_within_range(self, contact_book, today_plus_delta):
        """Test finding contacts with upcoming birthdays within range."""
        # Add a contact with birthday in 5 days
        birthday_in_5_days = today_plus_delta(5)
        contact_book.append(
            Contact(
                name="Upcoming Birthday",
                phone="+11111111111",
                birthday=Birthday(birthday_in_5_days),
            )
        )
        results = contact_book.upcoming_birthdays(days=7)
        assert len(results) >= 1
        assert any(r["name"] == "Upcoming Birthday" for r in results)

    def test_upcoming_birthdays_year_wrap(self, contact_book, today_plus_delta):
        """Test birthday wrapping to next year when passed this year."""
        # Add a contact with birthday that was 5 days ago this year
        birthday_past = today_plus_delta(5)
        contact = Contact(
            name="Past Birthday",
            phone="+11111111111",
            birthday=Birthday(birthday_past),
        )
        print(contact)
        contact_book.append(contact)
        results = contact_book.upcoming_birthdays(days=7)
        assert len(results) >= 1
        assert any(r["name"] == "Past Birthday" for r in results)

    def test_upcoming_birthdays_no_birthday_set(
        self, sample_contact_no_birthday, today_plus_delta
    ):
        """Test contacts without birthdays are excluded."""
        book = ContactBook()
        book.append(sample_contact_no_birthday)
        results = book.upcoming_birthdays(days=365)
        assert len(results) == 0

    def test_upcoming_birthdays_beyond_range(self, contact_book, today_plus_delta):
        """Test contacts with birthdays beyond range are excluded."""
        birthday_far = today_plus_delta(100)
        contact_book.append(
            Contact(
                name="Far Birthday",
                phone="+11111111111",
                birthday=Birthday(birthday_far),
            )
        )
        results = contact_book.upcoming_birthdays(days=30)
        assert not any(r["name"] == "Far Birthday" for r in results)

    def test_upcoming_birthdays_exactly_today(self, today_plus_delta):
        """Test contact with birthday exactly today."""
        birthday_today = today_plus_delta(0)
        book = ContactBook()
        book.append(
            Contact(
                name="Today Birthday",
                phone="+11111111111",
                birthday=Birthday(birthday_today),
            )
        )
        results = book.upcoming_birthdays(days=7)
        assert len(results) == 1
        assert results[0]["days"] == 0

    def test_upcoming_birthdays_result_format(self, contact_book, today_plus_delta):
        """Test upcoming birthdays returns correct format."""
        birthday_in_3_days = today_plus_delta(3)
        contact_book.append(
            Contact(
                name="Test Birthday",
                phone="+11111111111",
                birthday=Birthday(birthday_in_3_days),
            )
        )
        results = contact_book.upcoming_birthdays(days=7)
        result = next(r for r in results if r["name"] == "Test Birthday")
        assert "name" in result
        assert "birthday" in result
        assert "days" in result
        assert result["name"] == "Test Birthday"
        assert isinstance(result["days"], int)

    # Serialization Tests
    def test_to_list(self, contact_book):
        """Test serializing ContactBook to list of dicts."""
        result = contact_book.to_list()
        assert isinstance(result, list)
        assert len(result) == len(contact_book)
        assert all(isinstance(item, dict) for item in result)
        assert all("name" in item and "phone" in item for item in result)

    def test_to_list_empty_book(self):
        """Test serializing empty ContactBook."""
        book = ContactBook()
        result = book.to_list()
        assert result == []

    def test_load_from_list(self, valid_contacts_data):
        """Test deserializing list of dicts to ContactBook."""
        book = ContactBook()
        book.load_from_list(valid_contacts_data)
        assert len(book) == len(valid_contacts_data)
        assert book.find_exact("John Doe") is not None
        assert book.find_exact("Jane Smith") is not None
        assert book.find_exact("Bob Johnson") is not None

    def test_load_from_list_replaces_data(self, contact_book, valid_contacts_data):
        """Test that load_from_list replaces existing data."""
        initial_length = len(contact_book)
        contact_book.load_from_list(valid_contacts_data)
        assert len(contact_book) != initial_length
        assert len(contact_book) == len(valid_contacts_data)

    def test_load_from_list_empty(self, contact_book):
        """Test loading empty list clears ContactBook."""
        contact_book.load_from_list([])
        assert len(contact_book) == 0
