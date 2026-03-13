"""Tests for utils module - utility functions and decorators."""

import pytest
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document

from app.utils import (
    CommandCompleter,
    OperationCancelledError,
    handle_operation_errors,
    suggest_command,
)


class TestSuggestCommand:
    """Tests for suggest_command function."""

    def test_suggest_command_exact_match(self):
        """Test suggest_command returns exact match."""
        result = suggest_command("add-contact")
        assert result == "add-contact"

    def test_suggest_command_close_match(self):
        """Test suggest_command returns close match."""
        result = suggest_command("add-contct")  # Typo
        assert result == "add-contact"

    def test_suggest_command_no_match(self):
        """Test suggest_command returns None for no match."""
        result = suggest_command("xyz-invalid-command")
        assert result is None

    def test_suggest_command_partial_match(self):
        """Test suggest_command with partial command."""
        result = suggest_command("add")
        # Should return a command starting with "add"
        assert result is not None
        assert "add" in result.lower()

    def test_suggest_command_similar_commands(self):
        """Test suggest_command chooses closest match."""
        result = suggest_command("show-contact")
        # Should suggest show-contacts (plural)
        assert result == "show-contacts"


class TestHandleOperationErrors:
    """Tests for handle_operation_errors decorator."""

    def test_catches_generic_exception(self):
        """Test decorator catches and displays generic exceptions."""

        class TestClass:
            messages = []

            @handle_operation_errors
            def failing_method(self):
                raise ValueError("Test error")

        obj = TestClass()
        obj.failing_method()

        assert len(obj.messages) == 1
        assert obj.messages[0][0] == "error"
        assert "Test error" in obj.messages[0][1]

    def test_handles_operation_cancelled_error(self):
        """Test decorator handles OperationCancelledError silently."""

        class TestClass:
            messages = []

            @handle_operation_errors
            def cancelling_method(self):
                raise OperationCancelledError()

        obj = TestClass()
        obj.cancelling_method()

        # No error message should be added
        assert len(obj.messages) == 0

    def test_successful_execution(self):
        """Test decorator allows successful execution."""

        class TestClass:
            messages = []

            @handle_operation_errors
            def successful_method(self):
                self.messages.append(("response", "Success"))
                return "result"

        obj = TestClass()
        result = obj.successful_method()

        assert result == "result"
        assert len(obj.messages) == 1
        assert obj.messages[0] == ("response", "Success")

    def test_preserves_method_signature(self):
        """Test decorator preserves method signature."""

        class TestClass:
            messages = []

            @handle_operation_errors
            def method_with_args(self, arg1, arg2, kwarg=None):
                return f"{arg1}-{arg2}-{kwarg}"

        obj = TestClass()
        result = obj.method_with_args("a", "b", kwarg="c")

        assert result == "a-b-c"

    def test_catches_keyerror(self):
        """Test decorator catches KeyError."""

        class TestClass:
            messages = []

            @handle_operation_errors
            def failing_method(self):
                raise KeyError("test_key")

        obj = TestClass()
        obj.failing_method()

        assert len(obj.messages) == 1
        assert obj.messages[0][0] == "error"
        assert "test_key" in obj.messages[0][1]

    def test_catches_type_error(self):
        """Test decorator catches TypeError."""

        class TestClass:
            messages = []

            @handle_operation_errors
            def failing_method(self):
                raise TypeError("Invalid type")

        obj = TestClass()
        obj.failing_method()

        assert len(obj.messages) == 1
        assert obj.messages[0][0] == "error"
        assert "Invalid type" in obj.messages[0][1]


class TestCommandCompleter:
    """Tests for CommandCompleter class."""

    def test_initialization(self):
        """Test CommandCompleter initialization."""
        commands = ["cmd1", "cmd2", "cmd3"]
        signatures = {"cmd1": "<arg>", "cmd2": None, "cmd3": "<arg> [optional]"}

        completer = CommandCompleter(commands, signatures)

        assert completer.commands == commands
        assert completer.signatures == signatures

    def test_get_completions_empty_input(self):
        """Test get_completions shows all commands for empty input."""
        commands = ["add-contact", "show-contacts", "find-contact"]
        signatures = {"add-contact": "<name> <phone>", "show-contacts": None}

        completer = CommandCompleter(commands, signatures)
        document = Document("", 0)
        complete_event = CompleteEvent()

        completions = list(completer.get_completions(document, complete_event))

        assert len(completions) == len(commands)

    def test_get_completions_partial_command(self):
        commands = ["add-contact", "add-note", "edit-contact"]
        signatures = {"add-contact": "<args>", "add-note": "<args>"}

        completer = CommandCompleter(commands, signatures)

        document = Document("add", cursor_position=3)
        complete_event = CompleteEvent(completion_requested=True)

        completions = list(completer.get_completions(document, complete_event))
        texts = [c.text for c in completions]

        assert "add-contact" in texts
        assert "add-note" in texts

    def test_get_completions_shows_signature(self):
        """Test get_completions shows signature after space."""
        commands = ["add-contact"]
        signatures = {"add-contact": "<name> <phone>"}

        completer = CommandCompleter(commands, signatures)
        document = Document("add-contact ", 12)
        complete_event = CompleteEvent()

        completions = list(completer.get_completions(document, complete_event))

        assert len(completions) >= 1

    def test_get_completions_no_signature_for_none(self):
        """Test get_completions handles None signature."""
        commands = ["help"]
        signatures = {"help": None}

        completer = CommandCompleter(commands, signatures)
        document = Document("help ", 5)
        complete_event = CompleteEvent()

        completions = list(completer.get_completions(document, complete_event))

        # Should not add signature completion for None signature
        assert len(completions) == 0


class TestOperationCancelledError:
    """Tests for OperationCancelledError exception."""

    def test_raises_exception(self):
        """Test OperationCancelledError can be raised."""
        with pytest.raises(OperationCancelledError):
            raise OperationCancelledError()

    def test_exception_instance(self):
        """Test OperationCancelledError creates instance."""
        error = OperationCancelledError()
        assert isinstance(error, Exception)

    def test_exception_message(self):
        """Test OperationCancelledError with message."""
        message = "User cancelled operation"
        error = OperationCancelledError(message)
        assert str(error) == message
