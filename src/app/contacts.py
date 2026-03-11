import re
from datetime import datetime


class Contact:
    def __init__(
        self,
        name: str,
        phone: str,
        email: str = "",
        address: str = "",
        birthday: str = "",
    ) -> None:
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.birthday = birthday

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "birthday": self.birthday,
        }

    @staticmethod
    def from_dict(data: dict) -> "Contact":
        return Contact(
            data.get("name", ""),
            data.get("phone", ""),
            data.get("email", ""),
            data.get("address", ""),
            data.get("birthday", ""),
        )

    def __str__(self) -> str:
        email_text = self.email if self.email else "не вказано"
        address_text = self.address if self.address else "не вказано"
        birthday_text = self.birthday if self.birthday else "не вказано"
        return (
            f"Ім'я: {self.name}\n"
            f"Телефон: {self.phone}\n"
            f"Email: {email_text}\n"
            f"Адреса: {address_text}\n"
            f"День народження: {birthday_text}"
        )


class ContactBook:
    def __init__(self) -> None:
        self.contacts: list[Contact] = []

    def add_contact(
        self,
        name: str,
        phone: str,
        email: str = "",
        address: str = "",
        birthday: str = "",
    ) -> str:
        if not name.strip():
            return "Ім'я не може бути порожнім"

        if self.find_exact_contact(name):
            return "Контакт з таким ім'ям уже існує"

        if not self.validate_phone(phone):
            return "Некоректний номер телефону. Введіть 10 цифр"

        if email and not self.validate_email(email):
            return "Некоректний email"

        if birthday and not self.validate_birthday(birthday):
            return "Некоректна дата народження. Формат: ДД.ММ.РРРР"

        contact = Contact(
            name.strip(),
            phone.strip(),
            email.strip(),
            address.strip(),
            birthday.strip(),
        )
        self.contacts.append(contact)
        return "Контакт додано"

    def show_all_contacts(self) -> str:
        if not self.contacts:
            return "Список контактів порожній"
        return "\n\n".join(str(contact) for contact in self.contacts)

    def find_exact_contact(self, name: str) -> Contact | None:
        for contact in self.contacts:
            if contact.name.lower() == name.lower():
                return contact
        return None

    def search_contacts(self, keyword: str) -> str:
        keyword_lower = keyword.lower().strip()
        found: list[str] = []

        for contact in self.contacts:
            if (
                keyword_lower in contact.name.lower()
                or keyword_lower in contact.phone
                or keyword_lower in contact.email.lower()
                or keyword_lower in contact.address.lower()
                or keyword_lower in contact.birthday
            ):
                found.append(str(contact))

        if not found:
            return "Контакти не знайдено"
        return "\n\n".join(found)

    def edit_contact(
        self,
        name: str,
        new_phone: str = "",
        new_email: str = "",
        new_address: str = "",
        new_birthday: str = "",
    ) -> str:
        contact = self.find_exact_contact(name)
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

    def delete_contact(self, name: str) -> str:
        contact = self.find_exact_contact(name)
        if not contact:
            return "Контакт не знайдено"
        self.contacts.remove(contact)
        return "Контакт видалено"

    def upcoming_birthdays(self, days: str | int) -> str:
        if not str(days).strip().isdigit():
            return "Кількість днів має бути числом"

        days_int = int(days)
        today = datetime.today().date()
        result: list[str] = []

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
            if 0 <= delta_days <= days_int:
                result.append(
                    f"{contact.name}\n"
                    f"Дата дня народження: {birthday_this_year.strftime('%d.%m.%Y')}\n"
                    f"Через: {delta_days} дн."
                )

        if not result:
            return "Немає контактів з днем народження у вказаний період"
        return "\n\n".join(result)

    @staticmethod
    def validate_phone(phone: str) -> bool:
        return bool(re.fullmatch(r"^\+\d{1,3}\d{9,14}$", phone.strip()))

    @staticmethod
    def validate_email(email: str) -> bool:
        return bool(re.fullmatch(r"^[\w\.-]+@[\w\.-]+\.\w+$", email.strip()))

    @staticmethod
    def validate_birthday(birthday: str) -> bool:
        try:
            datetime.strptime(birthday.strip(), "%d.%m.%Y")
            return True
        except ValueError:
            return False

    def to_list(self) -> list[dict]:
        return [contact.to_dict() for contact in self.contacts]

    def load_from_list(self, data: list[dict]) -> None:
        self.contacts = [Contact.from_dict(item) for item in data]
