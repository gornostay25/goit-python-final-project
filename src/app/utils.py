from difflib import get_close_matches
from functools import wraps

from prompt_toolkit.completion import Completer, Completion, WordCompleter

AVAILABLE_COMMANDS = [
    ("add-contact", "contacts"),
    ("show-contacts", "contacts"),
    ("find-contact", "contacts"),
    ("edit-contact", "contacts"),
    ("delete-contact", "contacts"),
    ("birthdays", "contacts"),
    ("add-note", "notes"),
    ("show-notes", "notes"),
    ("find-note", "notes"),
    ("edit-note", "notes"),
    ("delete-note", "notes"),
    ("find-tag", "notes"),
    ("sort-notes-by-tags", "notes"),
    ("help", "general"),
    ("exit", "general"),
]

COMMAND_SIGNATURES = {
    "add-contact": "<name> <phone> [email] [birthday] [address]",
    "show-contacts": None,
    "find-contact": "<search>",
    "edit-contact": "<index> [name] [phone] [email] [birthday] [address]",
    "delete-contact": "<index>",
    "birthdays": "<days>",
    "add-note": "<text> [tag,tag,tag...]",
    "show-notes": "[index]",
    "find-note": "<search>",
    "edit-note": "<index> [new_text] [tag,tag,tag...]",
    "delete-note": "<index>",
    "find-tag": "<tag>",
    "sort-notes-by-tags": None,
    "help": None,
    "exit": None,
}

ERROR_MESSAGES = {
    "notes": {
        "index": lambda max_index: (
            f"Invalid index, must be a number between 1 and {max_index}"
        ),
        "not_found": lambda index: f"Note with index '{index}' not found",
        "text": "Invalid text, must be a string",
        "tags": "Invalid tags, must be a list of strings separated by commas",
    },
    "contacts": {
        "index": lambda max_index: (
            f"Invalid index, must be a number between 1 and {max_index}"
        ),
        "not_found": lambda index: f"Contact with index '{index}' not found",
        "name": "Invalid name, must be a string",
        "phone": "Invalid phone, must be in format +380XXXXXXXXX",
        "email": "Invalid email, must be in format example@example.com",
        "birthday": "Invalid birthday, must be in format DD.MM.YYYY",
        "address": "Invalid address, must be a string",
        "days": "Invalid number of days, must be a number greater than 0",
    },
}


class OperationCancelledError(Exception):
    """Exception raised when the user cancels an operation."""

    pass


class CommandCompleter(Completer):
    """Custom completer that shows commands initially and arguments after space."""

    def __init__(self, commands, signatures):
        """Initialize with commands and their argument signatures.

        Args:
            commands: List of available command names.
            signatures: Dict mapping command names to their argument signatures.
        """
        self.commands = commands
        self.signatures = signatures
        self.word_completer = WordCompleter(
            commands, meta_dict=signatures, ignore_case=True
        )

    def get_completions(self, document, complete_event):
        """Return completions based on current context.

        If line is empty or before command completion: show all commands.
        If command typed and space pressed: show that command's signature.
        """
        text = document.text_before_cursor
        words = text.strip().split()

        # No command typed yet - show all commands
        if len(words) == 0:
            for completion in self.word_completer.get_completions(
                document, complete_event
            ):
                yield completion

        # First word (command) typed, no space yet - show matching commands
        elif len(words) == 1 and not text.endswith(" "):
            for completion in self.word_completer.get_completions(
                document, complete_event
            ):
                yield completion

        # Command typed and space pressed - show its signature
        else:
            command = words[0].lower()
            if command in self.signatures:
                signature = self.signatures[command]
                if signature:
                    yield Completion(
                        text=" ",
                        start_position=0,
                        display=f"Arguments: {signature}",
                    )


def handle_operation_errors(func):
    """Decorate command handlers to catch and display errors gracefully.

    Prevents unhandled exceptions from crashing the CLI and provides
    consistent error messaging. Special handling for OperationCancelledError
    (user interruption with Ctrl+C) to avoid displaying error messages.

    Returns:
        Decorated function that catches exceptions and adds error messages.
    """

    @wraps(func)
    def inner(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except OperationCancelledError:
            # Silently handle user cancellation without showing errors
            return
        except Exception as e:
            self.messages.append(("error", f"Error: {e}"))
            return

    return inner


def suggest_command(user_command: str) -> str | None:
    """Find the closest matching command from available commands using fuzzy matching.

    Uses difflib's get_close_matches to suggest commands when a user types
    an incorrect or misspelled command. Helps users discover the correct command
    name without needing to reference documentation.

    Args:
        user_command: The command string to match against available commands.

    Returns:
        The closest matching command name, or None if no adequate match found
        (matches require 50% similarity cutoff).
    """
    matches = get_close_matches(
        user_command, [cmd[0] for cmd in AVAILABLE_COMMANDS], n=1, cutoff=0.5
    )
    if matches:
        return matches[0]
    return None
