import re
from dataclasses import dataclass, asdict
from datetime import datetime

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_REGEX = r"^\+\d{1,3}\d{9,14}$"


@dataclass
class Contact:
    """Represents a contact in the address book.

    Attributes:
        name: Contact name (required).
        phone: Contact phone number in international format.
        email: Contact email address.
        birthday: Contact birthday in DD.MM.YYYY format.
        address: Contact physical address.
    """

    name: str
    phone: str
    email: str = ""
    birthday: str = ""
    address: str = ""

    def to_dict(self) -> dict:
        """Convert contact to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        """
        Create Contact instance from dictionary.

        Args:
            data: Dictionary containing contact fields with optional values.

        Returns:
            Contact: New Contact instance with values from dict.
        """
        return cls(
            data.get("name", ""),
            data.get("phone", ""),
            data.get("email", ""),
            data.get("birthday", ""),
            data.get("address", ""),
        )

    # region Validation methods
    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate name contains only alphabetic characters and is not empty.

        Args:
            name: Contact name to validate.

        Returns:
            True if valid, False otherwise.
        """
        stripped_name = name.strip()
        return stripped_name.isalpha() and len(stripped_name)

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format.

        Phone must match international format: + followed by 1-3 digits,
        then 9-14 digits (e.g., +380123456789).

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
            datetime.strptime(birthday.strip(), "%d.%m.%Y")
            return True
        except ValueError:
            return False

    # endregion


class ContactBook:
    """Manages a collection of contacts with search and edit capabilities."""

    def __init__(self):
        """Initialize an empty contact book."""
        self.contacts: list[Contact] = []

    def add(self, contact: Contact):
        """Add a new contact to the address book.

        Args:
            contact: Contact instance to add.
        """
        self.contacts.append(contact)

    def get_all(self):
        """Return all contacts in the address book.

        Returns:
            List of all Contact instances.
        """
        return self.contacts

    def find_exact(self, name: str) -> Contact | None:
        """Find a contact by exact name match.

        Args:
            name: Contact name to search for.

        Returns:
            Contact instance if found, None otherwise.
        """
        for contact in self.contacts:
            if contact.name.casefold() == name.casefold():
                return contact
        return None

    def find(self, search: str) -> list[Contact]:
        """Find contacts matching search term across all fields.

        Searches case-insensitively in name, email, address, and birthday,
        and directly in phone number.

        Args:
            search: Search term to match against contact fields.

        Returns:
            List of matching Contact instances.
        """
        keywords = search.casefold().strip()
        found: list[Contact] = []
        for contact in self.contacts:
            if keywords in contact.name.casefold():
                found.append(contact)
            elif keywords in contact.phone:
                found.append(contact)
            elif keywords in contact.email.casefold():
                found.append(contact)
            elif keywords in contact.address.casefold():
                found.append(contact)
            elif keywords in contact.birthday.casefold():
                found.append(contact)
        return found

    def delete(self, name: str) -> bool:
        """Delete a contact by name.

        Args:
            name: Contact name to delete.

        Returns:
            True if contact was found and deleted, False otherwise.
        """
        contact = self.find_exact(name)
        if not contact:
            return False
        self.contacts.remove(contact)
        return True

    def upcoming_birthdays(self, days: int) -> list[dict]:
        """Find contacts with birthdays within specified number of days.

        Calculates birthdays for the current year or next year if already passed.

        Args:
            days: Number of days to look ahead (must be numeric).

        Returns:
            Formatted string of contacts with upcoming birthdays or message
            if none found.
        """

        today = datetime.today().date()
        result: list[dict] = []

        for contact in self.contacts:
            if not contact.birthday:
                continue
            try:
                birthday_date = datetime.strptime(
                    contact.birthday.strip(), "%d.%m.%Y"
                ).date()
            except ValueError:
                continue

            birthday_this_year = birthday_date.replace(year=today.year)
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

    # OLD METHODS

    def edit_contact(
        self,
        name: str,
        new_phone: str = "",
        new_email: str = "",
        new_address: str = "",
        new_birthday: str = "",
    ) -> str:
        """Edit an existing contact's fields.

        Validates each field before updating. Only non-empty fields are updated.

        Args:
            name: Contact name to edit.
            new_phone: New phone number.
            new_email: New email address.
            new_address: New physical address.
            new_birthday: New birthday in DD.MM.YYYY format.

        Returns:
            Success or error message.
        """
        contact = self.find_exact(name)
        if not contact:
            return "Контакт не знайдено"

        if new_phone:
            if not self.validate_phone(new_phone):
                return "Некоректний номер телефону. Введіть 10 цифр"
            contact.phone = new_phone.strip()

        if new_email:
            if not self.validate_email(new_email):
                return "Некоректний email"
            contact.email = new_email.strip()

        if new_address:
            contact.address = new_address.strip()

        if new_birthday:
            if not self.validate_birthday(new_birthday):
                return "Некоректна дата народження. Формат: ДД.ММ.РРРР"
            contact.birthday = new_birthday.strip()

        return "Контакт оновлено"

    def to_list(self) -> list[dict]:
        """Convert all contacts to list of dictionaries.

        Returns:
            List of contact dictionaries.
        """
        return [contact.to_dict() for contact in self.contacts]

    def load_from_list(self, data: list[dict]) -> None:
        """Load contacts from list of dictionaries.

        Args:
            data: List of contact dictionaries to load.
        """
        self.contacts = [Contact.from_dict(item) for item in data]
