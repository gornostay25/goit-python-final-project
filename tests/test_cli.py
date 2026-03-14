"""Tests for cli module - PersonalAssistantCLI class."""

from unittest.mock import patch

import pytest

from app.cli import PersonalAssistantCLI
from app.contacts import ContactBook
from app.notes import NotesBook


class TestCLIInitialization:
    """Tests for CLI initialization."""

    def test_initialization_creates_contact_book_and_note_book(self):
        """Test initialization creates ContactBook and NotesBook instances."""
        cli = PersonalAssistantCLI()
        assert isinstance(cli.contact_book, ContactBook)
        assert isinstance(cli.note_book, NotesBook)

    def test_initialization_sets_up_console(self):
        """Test initialization creates Console instance."""
        cli = PersonalAssistantCLI()
        assert cli.console is not None

    def test_initialization_sets_up_messages(self):
        """Test initialization initializes empty messages list."""
        cli = PersonalAssistantCLI()
        assert isinstance(cli.messages, list)
        assert len(cli.messages) == 0


class TestCommandParsing:
    """Tests for command parsing and dispatch."""

    @pytest.mark.parametrize(
        "command",
        ["exit", "q", "quit"],
    )
    def test_exit_command_triggers_exit(self, command):
        """Test exit/quit commands trigger exit."""
        cli = PersonalAssistantCLI()
        with patch.object(cli, "exit") as mock_exit:
            cli._PersonalAssistantCLI__handle_command(command)
            mock_exit.assert_called_once_with(0)

    def test_help_command_displays_help(self):
        """Test help command displays available commands."""
        cli = PersonalAssistantCLI()
        cli._PersonalAssistantCLI__handle_command("help")
        assert len(cli.messages) == 1
        assert cli.messages[0][0] == "custom"

    @pytest.mark.parametrize(
        "command",
        ["clear", "c", "cls"],
    )
    def test_clear_command_empties_messages(self, command):
        """Test clear command empties messages list."""
        cli = PersonalAssistantCLI()
        cli.messages.append(("info", "Test message"))
        assert len(cli.messages) == 1

        cli._PersonalAssistantCLI__handle_command(command)

        assert len(cli.messages) == 0

    def test_unknown_command_shows_error(self):
        """Test unknown command shows error message."""
        cli = PersonalAssistantCLI()
        cli._PersonalAssistantCLI__handle_command("invalid-cmd")
        assert len(cli.messages) == 1
        assert cli.messages[0][0] == "error"
        assert "Unknown command" in cli.messages[0][1]

    def test_unknown_command_suggests_alternative(self):
        """Test unknown command shows suggestion for similar commands."""
        cli = PersonalAssistantCLI()
        cli._PersonalAssistantCLI__handle_command("add-conact")  # Typo
        assert len(cli.messages) == 1
        assert "Did you mean" in cli.messages[0][1]


class TestCommandParsingErrors:
    """Tests for handling malformed command input."""

    @pytest.mark.parametrize(
        "malformed_command",
        [
            "\\",  # Single backslash
            '"',  # Unclosed double quote
            "'",  # Unclosed single quote
        ],
    )
    def test_malformed_command_shows_error_message(self, malformed_command):
        """Test that malformed input (like unclosed quotes) shows a user-friendly error."""
        # Arrange
        cli = PersonalAssistantCLI()

        # Act
        # This call should NOT raise an exception
        cli._PersonalAssistantCLI__handle_command(malformed_command)

        # Assert
        # 1. An error message should have been added to the messages list.
        assert len(cli.messages) == 1
        # 2. The message should be the specific error we defined.
        assert cli.messages[0] == ("error", "Invalid command")

    @patch("app.cli.shlex_split")
    def test_unexpected_exception_during_parsing_is_caught(self, mock_shlex_split):
        """Test that any unexpected exception during parsing is caught and reported."""
        # Arrange
        cli = PersonalAssistantCLI()
        # Force shlex_split to raise a generic, unexpected exception
        mock_shlex_split.side_effect = RuntimeError("Unexpected disk failure!")

        # Act
        cli._PersonalAssistantCLI__handle_command("any command")

        # Assert
        assert len(cli.messages) == 1
        assert cli.messages[0][0] == "error"
        # Check that the exception message is included in the output
        assert "Unexpected disk failure!" in cli.messages[0][1]
