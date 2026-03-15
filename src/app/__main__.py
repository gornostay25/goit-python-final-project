"""Main entry point for the Personal Assistant CLI."""

from app.cli import PersonalAssistantCLI
from app.contacts import Contact, ContactBook
from app.notes import Note, NotesBook
from app.storage import Storage

test_contacts = [
    {
        "name": "John Doe",
        "phone": "+1234567890",
        "email": "john.doe@example.com",
        "birthday": "01.01.1990",
        "address": "123 Main St, Anytown, USA",
    },
    {
        "name": "Jane Doe",
        "phone": "+1234567891",
        "email": "jane.doe@example.com",
        "birthday": "02.02.1991",
        "address": "456 Main St, Anytown, USA",
    },
    {
        "name": "Jim Doe",
        "phone": "+1234567892",
        "email": "jim.doe@example.com",
        "birthday": "03.03.1992",
        "address": "789 Main St, Anytown, USA",
    },
    {
        "name": "Jill Doe",
        "phone": "+1234567893",
        "email": "jill.doe@example.com",
        "birthday": "04.04.1993",
        "address": "101 Main St, Anytown, USA",
    },
    {
        "name": "Jack Doe",
        "phone": "+1234567894",
        "email": "jack.doe@example.com",
        "birthday": "05.05.1994",
        "address": "123 Main St, Anytown, USA",
    },
]

test_notes = [
    Note(
        text="This is another test note\n\nThis is a **test note**\n\nThis *is* a test ~~note~~",
        tags=["test2", "b"],
    ),
    Note(
        text="This is a test note\n\nThis is a **test note**\n\nThis *is* a test ~~note~~",
        tags=["test1", "a"],
    ),
    Note(
        text="This is a fourth test note\n\nThis is a **test note**\n\nThis *is* a test ~~note~~",
        tags=["test4", "d"],
    ),
    Note(
        text="This is a third test note\n\nThis is a **test note**\n\nThis *is* a test ~~note~~",
        tags=["test3", "c"],
    ),
    Note(
        text="This is a fifth test note\n\nThis is a **test note**\n\nThis *is* a test ~~note~~",
        tags=["test5", "e"],
    ),
]

CONTACTS_FILE = "contacts.json"
NOTES_FILE = "notes.json"

if __name__ == "__main__":
    contact_book = ContactBook()
    contact_storage = Storage(contact_book, CONTACTS_FILE)
    contact_storage.load()

    note_book = NotesBook()
    note_storage = Storage(note_book, NOTES_FILE)
    note_storage.load()

    cli = PersonalAssistantCLI(contact_book, note_book)

    if len(contact_book) == 0:
        for contact_data in test_contacts:
            contact_book.append(Contact.from_dict(contact_data))

    if len(note_book) == 0:
        for note in test_notes:
            note_book.append(note)
    try:
        cli.run()
    except KeyboardInterrupt:
        cli.exit(1)
    except Exception:
        cli.console.print_exception(show_locals=True)
    finally:
        contact_storage.save()
        note_storage.save()
