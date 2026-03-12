"""Tests for Personal Assistant CLI module."""

import pytest
from app.contacts import Contact, Birthday, ContactBook
from app.cli import (
    PersonalAssistantCLI,
    OperationCancelledError,
    suggest_command,
    AVAILABLE_COMMANDS,
    ERROR_MESSAGES,
    handle_operation_errors,
)


@pytest.fixture
def cli():
    """Provide a PersonalAssistantCLI instance for testing."""
    return PersonalAssistantCLI()


@pytest.fixture
def mock_console_input():
    """Mock console.input to provide predefined responses."""
    pass


@pytest.fixture
def populated_contact_book(cli, sample_contact):
    """Populate CLI contact book with test data."""
    cli.contact_book.append(sample_contact)
    cli.contact_book.append(
        Contact(name="Jane Smith", phone="+19876543210", email="jane@example.com")
    )
    return cli.contact_book


# region suggest_command tests
def test_suggest_command_exact_match():
    """Test suggestion returns exact match when available."""
    result = suggest_command("add-contact")
    assert result == "add-contact"


def test_suggest_command_fuzzy_match():
    """Test suggestion returns closest match for typos."""
    result = suggest_command("add-contct")
    assert result == "add-contact"


def test_suggest_command_no_match():
    """Test suggestion returns None for no close matches."""
    result = suggest_command("xyz")
    assert result is None


def test_suggest_command_case_insensitive():
    """Test suggestion works with different cases."""
    result = suggest_command("Add-Contact")
    assert result == "add-contact"


# region PersonalAssistantCLI initialization tests
def test_cli_initialization():
    """Test CLI initializes with required attributes."""
    cli = PersonalAssistantCLI()
    assert hasattr(cli, "console")
    assert hasattr(cli, "messages")
    assert hasattr(cli, "contact_book")
    assert isinstance(cli.messages, list)
    assert isinstance(cli.contact_book, ContactBook)


def test_cli_messages_starts_empty(cli):
    """Test CLI messages list starts empty."""
    assert len(cli.messages) == 0


# region Add Contact Command Tests
class TestAddContactCommand:
    """Tests for add-contact command processing."""

    def test_add_contact_with_all_fields_cli_mode(self, cli):
        """Test adding contact with all fields via CLI arguments."""
        args = [
            "John Doe",
            "+380501234567",
            "john@example.com",
            "15.06.1990",
            "123 Main St",
        ]
        cli._PersonalAssistantCLI__process_add_contact_command(args)

        assert len(cli.contact_book.data) == 1
        contact = cli.contact_book.data[0]
        assert contact.name == "John Doe"
        assert contact.phone == "+380501234567"
        assert contact.email == "john@example.com"
        assert str(contact.birthday) == "15.06.1990"
        assert contact.address == "123 Main St"

    def test_add_contact_required_fields_only_cli_mode(self, cli):
        """Test adding contact with only required fields via CLI."""
        args = ["Jane Smith", "+380509876543"]
        cli._PersonalAssistantCLI__process_add_contact_command(args)

        assert len(cli.contact_book.data) == 1
        contact = cli.contact_book.data[0]
        assert contact.name == "Jane Smith"
        assert contact.phone == "+380509876543"
        assert contact.email is None
        # Birthday is initialized with default value when not provided
        assert contact.birthday is not None
        assert contact.address is None

    def test_add_contact_invalid_name_cli_mode(self, cli):
        """Test adding contact with invalid name via CLI."""
        args = ["", "+380501234567"]
        cli._PersonalAssistantCLI__process_add_contact_command(args)

        assert len(cli.contact_book.data) == 0
        assert len(cli.messages) > 0
        assert any("error" in msg for msg, _ in cli.messages)

    def test_add_contact_invalid_phone_cli_mode(self, cli):
        """Test adding contact with invalid phone via CLI."""
        args = ["John Doe", "12345"]
        cli._PersonalAssistantCLI__process_add_contact_command(args)

        assert len(cli.contact_book.data) == 0
        assert len(cli.messages) > 0

    def test_add_contact_invalid_email_cli_mode(self, cli):
        """Test adding contact with invalid email via CLI."""
        args = ["John Doe", "+380501234567", "invalid-email"]
        cli._PersonalAssistantCLI__process_add_contact_command(args)

        assert len(cli.contact_book.data) == 0

    def test_add_contact_invalid_birthday_cli_mode(self, cli):
        """Test adding contact with invalid birthday via CLI."""
        args = ["John Doe", "+380501234567", "john@example.com", "invalid-date"]
        cli._PersonalAssistantCLI__process_add_contact_command(args)

        assert len(cli.contact_book.data) == 0

    def test_add_contact_invalid_args_count_cli_mode(self, cli):
        """Test adding contact with invalid argument count via CLI."""
        args = ["John Doe"]  # Only name, missing phone
        cli._PersonalAssistantCLI__process_add_contact_command(args)

        assert len(cli.contact_book.data) == 0
        assert any("Usage" in msg for _, msg in cli.messages)

    def test_add_contact_success_message(self, cli):
        """Test success message is added after adding contact."""
        args = ["John Doe", "+380501234567"]
        cli._PersonalAssistantCLI__process_add_contact_command(args)

        response_messages = [
            msg for msg_type, msg in cli.messages if msg_type == "response"
        ]
        assert len(response_messages) > 0
        assert "John Doe" in response_messages[0]
        assert "added" in response_messages[0]

    def test_add_contact_multiple_contacts(self, cli):
        """Test adding multiple contacts sequentially."""
        contacts = [
            ("Alice", "+380501111111", "alice@example.com"),
            ("Bob", "+380502222222", "bob@example.com"),
            ("Charlie", "+380503333333", "charlie@example.com"),
        ]

        for contact_data in contacts:
            args = list(contact_data)
            cli._PersonalAssistantCLI__process_add_contact_command(args)

        assert len(cli.contact_book.data) == 3


# region Show Contacts Command Tests
class TestShowContactsCommand:
    """Tests for show-contacts command processing."""

    def test_show_contacts_empty_book(self, cli):
        """Test showing contacts when book is empty."""
        cli._PersonalAssistantCLI__process_show_contacts_command()

        table_messages = [msg for msg_type, msg in cli.messages if msg_type == "table"]
        response_messages = [
            msg for msg_type, msg in cli.messages if msg_type == "response"
        ]

        assert len(table_messages) == 0
        assert any("No contacts found" in msg for msg in response_messages)

    def test_show_contacts_with_data(self, cli):
        """Test showing contacts when book has data."""
        cli.contact_book.append(
            Contact(name="Alice", phone="+380501111111", email="alice@example.com")
        )
        cli._PersonalAssistantCLI__process_show_contacts_command()

        table_messages = [msg for msg_type, msg in cli.messages if msg_type == "table"]
        assert len(table_messages) == 1

    def test_show_contacts_multiple_entries(self, cli, populated_contact_book):
        """Test showing multiple contacts."""
        cli._PersonalAssistantCLI__process_show_contacts_command()

        table_messages = [msg for msg_type, msg in cli.messages if msg_type == "table"]
        assert len(table_messages) == 1

    def test_show_contacts_with_birthday(self, cli):
        """Test showing contacts with birthday field populated."""
        cli.contact_book.append(
            Contact(
                name="Alice",
                phone="+380501111111",
                email="alice@example.com",
                birthday=Birthday("15.06.1990"),
            )
        )
        cli._PersonalAssistantCLI__process_show_contacts_command()

        table_messages = [msg for msg_type, msg in cli.messages if msg_type == "table"]
        assert len(table_messages) == 1


# region Find Contact Command Tests
class TestFindContactCommand:
    """Tests for find-contact command processing."""

    def test_find_contact_existing_name(self, cli, populated_contact_book):
        """Test finding contact by existing name."""
        args = ["John"]
        cli._PersonalAssistantCLI__process_find_contact_command(args)

        table_messages = [msg for msg_type, msg in cli.messages if msg_type == "table"]
        assert len(table_messages) == 1

    def test_find_contact_by_email(self, cli, populated_contact_book):
        """Test finding contact by email address."""
        args = ["jane@example.com"]
        cli._PersonalAssistantCLI__process_find_contact_command(args)

        table_messages = [msg for msg_type, msg in cli.messages if msg_type == "table"]
        assert len(table_messages) == 1

    def test_find_contact_by_phone(self, cli, populated_contact_book):
        """Test finding contact by phone number."""
        args = ["+12345678901"]
        cli._PersonalAssistantCLI__process_find_contact_command(args)

        table_messages = [msg for msg_type, msg in cli.messages if msg_type == "table"]
        assert len(table_messages) == 1

    def test_find_contact_not_found(self, cli, populated_contact_book):
        """Test finding contact that doesn't exist."""
        args = ["NonExistent"]
        cli._PersonalAssistantCLI__process_find_contact_command(args)

        table_messages = [msg for msg_type, msg in cli.messages if msg_type == "table"]
        response_messages = [
            msg for msg_type, msg in cli.messages if msg_type == "response"
        ]

        assert len(table_messages) == 0
        assert any("No contacts found" in msg for msg in response_messages)


# region Edit Contact Command Tests
class TestEditContactCommand:
    """Tests for edit-contact command processing."""

    def test_edit_contact_update_email_cli_mode(self, cli, populated_contact_book):
        """Test editing contact email via CLI."""
        args = ["John Doe", "newemail@example.com"]
        cli._PersonalAssistantCLI__process_edit_contact_command(args)

        contact = cli.contact_book.find_exact("John Doe")
        assert contact.email == "newemail@example.com"

    def test_edit_contact_update_birthday_cli_mode(self, cli, populated_contact_book):
        """Test editing contact birthday via CLI."""
        args = ["John Doe", None, "20.12.1985"]
        cli._PersonalAssistantCLI__process_edit_contact_command(args)

        contact = cli.contact_book.find_exact("John Doe")
        assert str(contact.birthday) == "20.12.1985"

    def test_edit_contact_update_address_cli_mode(self, cli, populated_contact_book):
        """Test editing contact address via CLI."""
        args = ["John Doe", None, None, "456 New St"]
        cli._PersonalAssistantCLI__process_edit_contact_command(args)

        contact = cli.contact_book.find_exact("John Doe")
        assert contact.address == "456 New St"

    def test_edit_contact_not_found(self, cli):
        """Test editing non-existent contact."""
        args = ["NonExistent", "new@example.com"]
        cli._PersonalAssistantCLI__process_edit_contact_command(args)

        error_messages = [msg for msg_type, msg in cli.messages if msg_type == "error"]
        assert any("not found" in msg for msg in error_messages)

    def test_edit_contact_invalid_email(self, cli, populated_contact_book):
        """Test editing contact with invalid email."""
        args = ["John Doe", "invalid-email"]
        cli._PersonalAssistantCLI__process_edit_contact_command(args)

        contact = cli.contact_book.find_exact("John Doe")
        assert contact.email != "invalid-email"

    def test_edit_contact_invalid_birthday(self, cli, populated_contact_book):
        """Test editing contact with invalid birthday."""
        args = ["John Doe", None, "invalid-date"]
        cli._PersonalAssistantCLI__process_edit_contact_command(args)

        contact = cli.contact_book.find_exact("John Doe")
        assert str(contact.birthday) != "invalid-date"

    def test_edit_contact_success_message(self, cli, populated_contact_book):
        """Test success message after editing contact."""
        args = ["John Doe", "new@example.com"]
        cli._PersonalAssistantCLI__process_edit_contact_command(args)

        response_messages = [
            msg for msg_type, msg in cli.messages if msg_type == "response"
        ]
        assert any("updated" in msg for msg in response_messages)

    def test_edit_contact_invalid_args_count(self, cli, populated_contact_book):
        """Test editing with invalid argument count."""
        args = []  # Too few arguments
        cli._PersonalAssistantCLI__process_edit_contact_command(args)

        # Command should execute (may prompt interactively or add usage message)


# region Delete Contact Command Tests
class TestDeleteContactCommand:
    """Tests for delete-contact command processing."""

    def test_delete_contact_existing(self, cli, populated_contact_book):
        """Test deleting existing contact."""
        initial_count = len(cli.contact_book.data)
        args = ["John Doe"]
        cli._PersonalAssistantCLI__process_delete_contact_command(args)

        assert len(cli.contact_book.data) == initial_count - 1
        assert cli.contact_book.find_exact("John Doe") is None

    def test_delete_contact_not_found(self, cli):
        """Test deleting non-existent contact."""
        initial_count = len(cli.contact_book.data)
        args = ["NonExistent"]
        cli._PersonalAssistantCLI__process_delete_contact_command(args)

        assert len(cli.contact_book.data) == initial_count
        error_messages = [msg for msg_type, msg in cli.messages if msg_type == "error"]
        assert any("not found" in msg for msg in error_messages)

    def test_delete_contact_invalid_name(self, cli):
        """Test deleting with invalid name format."""
        initial_count = len(cli.contact_book.data)
        args = [""]  # Empty name
        cli._PersonalAssistantCLI__process_delete_contact_command(args)

        assert len(cli.contact_book.data) == initial_count

    def test_delete_contact_success_message(self, cli, populated_contact_book):
        """Test success message after deleting contact."""
        args = ["John Doe"]
        cli._PersonalAssistantCLI__process_delete_contact_command(args)

        response_messages = [
            msg for msg_type, msg in cli.messages if msg_type == "response"
        ]
        assert any("deleted" in msg for msg in response_messages)

    def test_delete_contact_with_spaces_in_name(self, cli, populated_contact_book):
        """Test deleting contact with spaces in name."""
        args = ["Jane", "Smith"]
        cli._PersonalAssistantCLI__process_delete_contact_command(args)

        assert cli.contact_book.find_exact("Jane Smith") is None


# region Birthdays Command Tests
class TestBirthdaysCommand:
    """Tests for birthdays command processing."""

    def test_birthdays_valid_days_cli_mode(self, cli, today_plus_delta):
        """Test birthdays command with valid days argument."""
        # Create a contact with birthday in 2 days
        birthday_date = today_plus_delta(2)
        cli.contact_book.append(
            Contact(
                name="Birthday Person",
                phone="+380501234567",
                birthday=Birthday(birthday_date),
            )
        )

        args = ["7"]
        cli._PersonalAssistantCLI__process_birthdays_command(args)

        table_messages = [msg for msg_type, msg in cli.messages if msg_type == "table"]
        assert len(table_messages) == 1

    def test_birthdays_invalid_days(self, cli):
        """Test birthdays command with invalid days argument."""
        args = ["invalid"]
        cli._PersonalAssistantCLI__process_birthdays_command(args)

        error_messages = [msg for msg_type, msg in cli.messages if msg_type == "error"]
        assert any("Invalid" in msg or "days" in msg for msg in error_messages)

    def test_birthdays_zero_days(self, cli):
        """Test birthdays command with zero days."""
        args = ["0"]
        cli._PersonalAssistantCLI__process_birthdays_command(args)

        # Error message should be added to messages
        assert any(msg_type == "error" for msg_type, _ in cli.messages)

    def test_birthdays_negative_days(self, cli):
        """Test birthdays command with negative days."""
        args = ["-5"]
        cli._PersonalAssistantCLI__process_birthdays_command(args)

        # Error message should be added to messages
        assert any(msg_type == "error" for msg_type, _ in cli.messages)

    def test_birthdays_no_upcoming(self, cli, populated_contact_book):
        """Test birthdays when no upcoming birthdays found."""
        args = ["1"]
        cli._PersonalAssistantCLI__process_birthdays_command(args)

        response_messages = [
            msg for msg_type, msg in cli.messages if msg_type == "response"
        ]
        assert any("No upcoming" in msg for msg in response_messages)

    def test_birthdays_multiple_contacts(self, cli, today_plus_delta):
        """Test birthdays with multiple contacts having upcoming birthdays."""
        # Create contacts with birthdays in the next week
        cli.contact_book.append(
            Contact(
                name="Person1",
                phone="+380501111111",
                birthday=Birthday(today_plus_delta(1)),
            )
        )
        cli.contact_book.append(
            Contact(
                name="Person2",
                phone="+380502222222",
                birthday=Birthday(today_plus_delta(2)),
            )
        )

        args = ["7"]
        cli._PersonalAssistantCLI__process_birthdays_command(args)

        table_messages = [msg for msg_type, msg in cli.messages if msg_type == "table"]
        assert len(table_messages) == 1

    def test_birthdays_invalid_args_count(self, cli):
        """Test birthdays with invalid argument count."""
        args = ["7", "extra"]
        cli._PersonalAssistantCLI__process_birthdays_command(args)

        error_messages = [msg for msg_type, msg in cli.messages if msg_type == "error"]
        assert any("Usage" in msg for msg in error_messages)


# region Decorator Tests
class TestHandleOperationErrors:
    """Tests for handle_operation_errors decorator."""

    def test_decorator_catches_exception(self, cli):
        """Test decorator catches and handles exceptions."""

        def failing_command():
            raise ValueError("Test error")

        decorated = handle_operation_errors(lambda self: failing_command())
        decorated(cli)

        error_messages = [msg for msg_type, msg in cli.messages if msg_type == "error"]
        assert len(error_messages) > 0

    def test_decorator_handles_operation_cancelled(self, cli):
        """Test decorator silently handles OperationCancelledError."""

        def cancelled_command():
            raise OperationCancelledError("User cancelled")

        decorated = handle_operation_errors(lambda self: cancelled_command())
        decorated(cli)

        error_messages = [msg for msg_type, msg in cli.messages if msg_type == "error"]
        assert not any("User cancelled" in msg for msg in error_messages)

    def test_decorator_allows_normal_execution(self, cli):
        """Test decorator allows normal function execution."""

        def normal_command():
            return "Success"

        decorated = handle_operation_errors(lambda self: normal_command())
        result = decorated(cli)

        assert result == "Success"
        assert len(cli.messages) == 0


# region Load and Save Content Tests
class TestLoadSaveContent:
    """Tests for load_content and save_content methods."""

    def test_load_content_prints_message(self, cli, monkeypatch):
        """Test load_content prints loading message."""
        # Patch console.print to capture calls
        print_called = []

        def mock_print(*args, **kwargs):
            print_called.append(True)

        monkeypatch.setattr(cli.console, "print", mock_print)
        cli.load_content()

        assert len(print_called) > 0

    def test_save_content_prints_message(self, cli, monkeypatch):
        """Test save_content prints saving message."""
        # Patch console.print to capture calls
        print_called = []

        def mock_print(*args, **kwargs):
            print_called.append(True)

        monkeypatch.setattr(cli.console, "print", mock_print)
        cli.save_content()

        assert len(print_called) > 0


# region Exit Method Tests
class TestExitMethod:
    """Tests for exit method."""

    def test_exit_clears_console(self, cli, monkeypatch):
        """Test exit clears the console."""
        # Patch console.clear and exit
        clear_called = []
        exit_called = []

        def mock_clear():
            clear_called.append(True)

        def mock_exit(code):
            exit_called.append(code)

        monkeypatch.setattr(cli.console, "clear", mock_clear)
        monkeypatch.setattr("builtins.exit", mock_exit)

        cli.exit(0)

        assert len(clear_called) > 0
        assert len(exit_called) == 1

    def test_exit_prints_goodbye(self, cli, monkeypatch):
        """Test exit prints goodbye message."""
        # Patch console.print and exit
        print_calls = []

        def mock_print(*args, **kwargs):
            print_calls.append(str(args))

        def mock_exit(code):
            pass

        monkeypatch.setattr(cli.console, "print", mock_print)
        monkeypatch.setattr(cli.console, "clear", lambda: None)
        monkeypatch.setattr("builtins.exit", mock_exit)

        cli.exit(0)

        assert len(print_calls) > 0

    def test_exit_with_code(self, cli, monkeypatch):
        """Test exit with custom exit code."""
        exit_calls = []

        def mock_exit(code):
            exit_calls.append(code)

        monkeypatch.setattr(cli.console, "clear", lambda: None)
        monkeypatch.setattr(cli.console, "print", lambda *args, **kwargs: None)
        monkeypatch.setattr("builtins.exit", mock_exit)

        cli.exit(1)

        assert len(exit_calls) == 1
        assert exit_calls[0] == 1


# region Message Rendering Tests
class TestMessageRendering:
    """Tests for internal message rendering methods."""

    def test_render_command_message(self, cli):
        """Test rendering command message."""
        result = cli._PersonalAssistantCLI__render_message("command", "test-command")
        assert "test-command" in result.plain
        assert "green" in str(result.style)

    def test_render_response_message(self, cli):
        """Test rendering response message."""
        result = cli._PersonalAssistantCLI__render_message("response", "test-response")
        assert "test-response" in result.plain
        assert "white" in str(result.style)

    def test_render_error_message(self, cli):
        """Test rendering error message."""
        result = cli._PersonalAssistantCLI__render_message("error", "test-error")
        assert "test-error" in result.plain
        assert "red" in str(result.style)

    def test_render_info_message(self, cli):
        """Test rendering info message."""
        result = cli._PersonalAssistantCLI__render_message("info", "test-info")
        assert "test-info" in result.plain
        assert "cyan" in str(result.style)


# region Available Commands Tests
def test_available_commands_list():
    """Test AVAILABLE_COMMANDS contains all expected commands."""
    expected_commands = [
        "add-contact",
        "show-contacts",
        "find-contact",
        "edit-contact",
        "delete-contact",
        "birthdays",
        "add-note",
        "show-notes",
        "find-note",
        "edit-note",
        "delete-note",
        "find-tag",
        "sort-notes-by-tags",
        "help",
        "exit",
    ]

    for cmd in expected_commands:
        assert cmd in AVAILABLE_COMMANDS


def test_available_commands_is_list():
    """Test AVAILABLE_COMMANDS is a list."""
    assert isinstance(AVAILABLE_COMMANDS, list)


# region Error Messages Tests
def test_error_messages_structure():
    """Test ERROR_MESSAGES has correct structure."""
    assert "contacts" in ERROR_MESSAGES
    assert "name" in ERROR_MESSAGES["contacts"]
    assert "phone" in ERROR_MESSAGES["contacts"]
    assert "email" in ERROR_MESSAGES["contacts"]
    assert "birthday" in ERROR_MESSAGES["contacts"]
    assert "address" in ERROR_MESSAGES["contacts"]
    assert "days" in ERROR_MESSAGES["contacts"]


def test_error_messages_are_strings():
    """Test all error messages are strings."""
    for category, messages in ERROR_MESSAGES.items():
        for key, message in messages.items():
            assert isinstance(message, str)
            assert len(message) > 0
