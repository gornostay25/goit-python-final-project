"""Tests for cli module - PersonalAssistantCLI class."""

from unittest.mock import patch

import pytest

from app.cli import PersonalAssistantCLI
from app.contacts import ContactBook
from app.notes import NotesBook


class TestCLIInitialization:
    """Tests for CLI initialization."""

    def test_initialization_creates_contact_book(self):
        """Test initialization creates ContactBook instance."""
        cli = PersonalAssistantCLI()
        assert isinstance(cli.contact_book, ContactBook)
        assert len(cli.contact_book.data) == 0

    def test_initialization_creates_note_book(self):
        """Test initialization creates NotesBook instance."""
        cli = PersonalAssistantCLI()
        assert isinstance(cli.note_book, NotesBook)
        assert len(cli.note_book.data) == 0

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


class TestCLIPublicMethods:
    """Tests for public CLI methods."""

    @patch("builtins.exit")
    def test_exit_with_code(self, mock_exit):
        """Test exit method calls sys.exit with code."""
        cli = PersonalAssistantCLI()
        cli.exit(42)
        mock_exit.assert_called_once_with(42)

    @patch("rich.console.Console.print")
    def test_load_content_displays_message(self, mock_print):
        """Test load_content displays loading message."""
        cli = PersonalAssistantCLI()
        cli.load_content()
        mock_print.assert_called_once()
        call_args = str(mock_print.call_args)
        assert "Loading content" in call_args

    @patch("rich.console.Console.print")
    def test_save_content_displays_message(self, mock_print):
        """Test save_content displays saving message."""
        cli = PersonalAssistantCLI()
        cli.save_content()
        mock_print.assert_called_once()
        call_args = str(mock_print.call_args)
        assert "Saving content" in call_args
