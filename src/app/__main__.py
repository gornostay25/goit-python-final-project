"""Main entry point for the Personal Assistant CLI."""

from app.cli import PersonalAssistantCLI
from app.contacts import Contact, ContactBook
from app.notes import Note, NotesBook

test_contacts = [
    Contact(
        name="John Doe",
        phone="+1234567890",
        email="john.doe@example.com",
        birthday="01.01.1990",
        address="123 Main St, Anytown, USA",
    ),
    Contact(
        name="Jane Doe",
        phone="+1234567891",
        email="jane.doe@example.com",
        birthday="02.02.1991",
        address="456 Main St, Anytown, USA",
    ),
    Contact(
        name="Jim Doe",
        phone="+1234567892",
        email="jim.doe@example.com",
        birthday="03.03.1992",
        address="789 Main St, Anytown, USA",
    ),
    Contact(
        name="Jill Doe",
        phone="+1234567893",
        email="jill.doe@example.com",
        birthday="04.04.1993",
        address="101 Main St, Anytown, USA",
    ),
    Contact(
        name="Jack Doe",
        phone="+1234567894",
        email="jack.doe@example.com",
        birthday="05.05.1994",
        address="123 Main St, Anytown, USA",
    ),
]

test_notes = [
    Note(
        text="This is another test note\nThis is a **test note**\nThis is a test note",
        tags=["test2", "b"],
    ),
    Note(
        text="This is a test note\nThis is a **test note**\nThis is a test note",
        tags=["test1", "a"],
    ),
    Note(
        text="This is a fourth test note\nThis is a **test note**\nThis is a test note",
        tags=["test4", "d"],
    ),
    Note(
        text="This is a third test note\nThis is a **test note**\nThis is a test note",
        tags=["test3", "c"],
    ),
    Note(
        text="This is a fifth test note\nThis is a **test note**\nThis is a test note",
        tags=["test5", "e"],
    ),
]

if __name__ == "__main__":
    contact_book = ContactBook()
    note_book = NotesBook()

    cli = PersonalAssistantCLI(contact_book, note_book)
    cli.load_content()

    if len(contact_book) == 0:
        for contact in test_contacts:
            contact_book.append(contact)

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
        cli.save_content()
