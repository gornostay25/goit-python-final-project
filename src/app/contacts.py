import re
from dataclasses import dataclass
from datetime import date, datetime

from app.book import Book, Item

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_REGEX = r"^\+\d{1,3}\d{9,11}$"
DATE_FORMAT = "%d.%m.%Y"


class Birthday:
    """Encapsulates birthday date with validation for contact entries.

    Wraps datetime.date to provide consistent string representation
    and DD.MM.YYYY format validation for user input.
    """

    def __init__(self, value):
        self.value = value

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, Birthday):
            return self.value == value.value
        if isinstance(value, str):
            return self.value == datetime.strptime(value, DATE_FORMAT).date()
        return False

    def __str__(self):
        return self.value.strftime(DATE_FORMAT) if self.value else ""

    def __repr__(self):
        return self.__str__()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        try:
            if new_value is not None and not isinstance(
                new_value, (str, date, Birthday)
            ):
                raise ValueError(f"Invalid type: {type(new_value)}")

            if isinstance(new_value, str) and len(new_value.strip()) > 0:
                self._value = datetime.strptime(new_value, DATE_FORMAT).date()
            elif isinstance(new_value, date):
                self._value = new_value
            elif isinstance(new_value, Birthday):
                self._value = new_value.value
            else:
                self._value = None

        except ValueError as e:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from e


@dataclass
class Contact(Item):
    """Represents a contact in the address book.

    Stores personal information including name, phone, email, birthday,
    and address.

    Attributes:
        name: Contact name (required).
        phone: Contact phone number in international format (required).
        email: Contact email address (optional).
        birthday: Contact birthday in DD.MM.YYYY format (optional).
        address: Contact physical address (optional).
    """

    name: str
    phone: str
    email: str = None
    birthday: Birthday = None
    address: str = None

    def __post_init__(self):
        self.name = self.name.strip()
        self.phone = self.phone.strip()
        self.email = self.email.strip() if self.email else None
        self.address = self.address.strip() if self.address else None
        self.birthday = Birthday(self.birthday) if self.birthday else None

    # region Validation methods
    @staticmethod
    def validate_name(name: str) -> bool:
        """Check name is not empty after stripping whitespace.

        Args:
            name: Contact name to validate.

        Returns:
            True if valid, False otherwise.
        """
        return len(name.strip()) > 0

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format.

        Pattern ensures phone can be used globally: country code prefix
        followed by 9-14 digits (E.164 standard).

        Args:
            phone: Phone number to validate.

        Returns:
            True if format matches, False otherwise.
        """
        return bool(re.fullmatch(PHONE_REGEX, phone.strip()))

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.

        Args:
            email: Email address to validate.

        Returns:
            True if format matches, False otherwise.
        """
        return bool(re.fullmatch(EMAIL_REGEX, email.strip()))

    @staticmethod
    def validate_birthday(birthday: str) -> bool:
        """Validate birthday format.

        Birthday must be in DD.MM.YYYY format and represent a valid date.

        Args:
            birthday: Birthday string to validate.

        Returns:
            True if format matches and date is valid, False otherwise.
        """
        try:
            datetime.strptime(birthday.strip(), DATE_FORMAT)
            return True
        except ValueError:
            return False

    # endregion


class ContactBook(Book[Contact]):
    """Manages contact collection with search, edit, and birthday tracking.

    Extends UserList to provide list-like access while adding domain-specific
    operations for contact management.
    """

    item_type = Contact

    def find(self, search: str) -> list[Contact]:
        """Search all contact fields for matching terms.

        Performs case-insensitive substring search in text fields and
        exact match on phone digits. Returns all matching contacts,
        preserving order of discovery.

        Args:
            search: Search term to match against contact fields.

        Returns:
            List of matching Contact instances in order of discovery.
        """
        keywords = search.casefold().strip()
        found: list[Contact] = []
        for contact in self.data:
            if keywords in contact.name.casefold():
                found.append(contact)
            elif keywords in contact.phone:
                found.append(contact)
            elif contact.email and keywords in contact.email.casefold():
                found.append(contact)
            elif contact.address and keywords in contact.address.casefold():
                found.append(contact)
            elif contact.birthday and keywords in str(contact.birthday):
                found.append(contact)
        return found

    def upcoming_birthdays(self, days: int) -> list[dict]:
        """Find contacts with birthdays occurring within the next N days.

        Calculates upcoming birthdays for the current year, wrapping to
        next year if the birthday has already passed. This ensures we don't
        miss birthdays that occurred earlier in the year.

        Args:
            days: Number of days to look ahead (must be positive).

        Returns:
            List of dictionaries with name, birthday date, and days until.
        """

        today = datetime.today().date()
        result: list[dict] = []

        for contact in self.data:
            if not contact.birthday or not contact.birthday.value:
                continue

            # Calculate birthday for this year, then next year if passed
            birthday_this_year = contact.birthday.value.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            delta_days = (birthday_this_year - today).days
            if 0 <= delta_days <= days:
                result.append(
                    {
                        "name": contact.name,
                        "birthday": birthday_this_year.strftime("%d.%m.%Y"),
                        "days": delta_days,
                    }
                )

        return result

    def edit(self, index: int | str, fields: dict) -> bool:
        """Update contact fields with validated values.

        Only updates fields that are present and non-empty in the dictionary.
        This partial update pattern allows editing specific contact attributes
        without requiring full contact data.

        Args:
            index: 1-based index of contact to edit.
            fields: Dictionary containing fields to update. Valid keys:
                    'name', 'phone', 'email', 'address', 'birthday'.

        Returns:
            True if contact was found and updated, False otherwise.
        """
        contact = self.get(index)
        if not contact:
            return False

        if "name" in fields and fields["name"]:
            contact.name = fields["name"].strip()

        if "phone" in fields and fields["phone"]:
            contact.phone = fields["phone"].strip()

        if "email" in fields and fields["email"]:
            contact.email = fields["email"].strip()

        if "address" in fields and fields["address"]:
            contact.address = fields["address"].strip()

        if "birthday" in fields and fields["birthday"]:
            contact.birthday = Birthday(fields["birthday"])

        return True
