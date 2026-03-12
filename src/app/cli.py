"""Command-line interface for the Personal Assistant."""

from app import __version__, __authors__, __description__
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.layout import Layout
from time import sleep
from difflib import get_close_matches
from shlex import split as shlex_split
from app.contacts import Contact, ContactBook
from functools import wraps


AVAILABLE_COMMANDS = [
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

ERROR_MESSAGES = {
    "contacts": {
        "name": "Invalid name, must be a string",
        "phone": "Invalid phone, must be in format +380XXXXXXXXX",
        "email": "Invalid email, must be in format example@example.com",
        "birthday": "Invalid birthday, must be in format DD.MM.YYYY",
        "address": "Invalid address, must be a string",
        "days": "Invalid number of days, must be a number greater than 0",
    }
}


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
            # User cancelled - no error message needed
            return
        except Exception as e:
            self.messages.append(("error", f"Error: {str(e)}"))
            return

    return inner


class PersonalAssistantCLI:
    """Command-line interface for the Personal Assistant application.

    Provides a Rich-based TUI with colored output, tables, and styled
    messages. Handles both command-line arguments and interactive input.
    """

    def __init__(self):
        """Initialize CLI with Rich console and empty message history."""
        self.console = Console()
        self.console.set_window_title("Personal Assistant")
        self.messages: list[tuple[str, str | Table]] = []

        self.contact_book = ContactBook()

    # region Render methods
    def __render_message(self, msg_type: str, msg_text: str) -> Text:
        """Apply color styling to messages based on type.

        Args:
            msg_type: Message type ("command", "response", "error", "info").
            msg_text: The text content to render.

        Returns:
            Text: Styled text object ready for display.
        """
        if msg_type == "command":
            return Text(f"> {msg_text}", style="green bold")
        elif msg_type == "response":
            return Text(msg_text, style="white")
        elif msg_type == "error":
            return Text(msg_text, style="red")
        elif msg_type == "info":
            return Text(msg_text, style="cyan")
        return Text(msg_text)

    def __show_startup_screen(self):
        """Display splash screen with project info and countdown.

        Creates visual introduction using Rich Layout with ASCII logo,
        project description, and animated countdown before entering main loop.
        """
        TIMEOUT_SEC = 3
        layout = Layout()

        title_text = Text.assemble(
            (
                "\n".join(
                    [
                        "░█▀█░█▀▀░█▀▄░█▀▀░█▀█░█▀█░█▀█░█░░░█▀█░█▀▀░█▀▀░▀█▀░█▀▀░▀█▀░█▀█░█▀█░▀█▀",
                        "░█▀▀░█▀▀░█▀▄░▀▀█░█░█░█░█░█▀█░█░░░█▀█░▀▀█░▀▀█░░█░░▀▀█░░█░░█▀█░█░█░░█░",
                        "░▀░░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░▀░░▀░▀░▀░▀░░▀░",
                    ]
                ),
                "cyan bold",
            ),
            (f" v{__version__}", "dim"),
        )

        layout.split_column(
            Layout(
                Panel(
                    Align.center(title_text),
                    border_style="cyan",
                ),
                name="logo",
                size=5,
            ),
            Layout(name="credits", minimum_size=8),  # 4 padding and 4 for authors
            Layout(name="footer", size=3),
        )

        credits_layout = Layout()
        credits_layout.split_row(
            Layout(
                Panel(
                    Align.center(
                        Text.assemble((__description__, "bold white"), style="cyan")
                    ),
                    title="Description",
                    border_style="cyan",
                    padding=(1, 0),
                ),
                name="description",
            ),
            Layout(
                Panel(
                    Align.center(
                        Text.assemble(
                            "\n".join([f"{author}" for author in __authors__]),
                            style="white",
                        ),
                    ),
                    title="Authors",
                    border_style="magenta",
                    padding=(1, 0),
                ),
                name="authors",
            ),
        )
        layout["credits"].update(credits_layout)

        with Live(
            layout, console=self.console, screen=True, auto_refresh=False
        ) as live:
            for i in range(TIMEOUT_SEC, 0, -1):
                footer_text = Text.assemble(
                    (f"Starting in {i} second{'s' if i != 1 else ''}...", "dim")
                )
                footer_content = Align.center(footer_text)
                footer_panel = Panel(
                    footer_content,
                    border_style="dim",
                )
                layout["footer"].update(footer_panel)
                live.update(layout, refresh=True)
                sleep(1)

    def __show_console(self):
        """Display message history in terminal.

        Renders all stored messages; shows welcome message if no history exists.
        Tables are rendered directly, other messages get styling applied.
        """
        if len(self.messages) == 0:
            self.messages.append(
                (
                    "info",
                    "Welcome to Personal Assistant!\nUse 'help' to see available commands.",
                )
            )

        for msg_type, msg_content in self.messages:
            if msg_type == "table":
                self.console.line()
                self.console.print(msg_content)
            else:
                self.console.print(self.__render_message(msg_type, msg_content))

            # Skip spacing after command echo for cleaner look
            if msg_type != "command":
                self.console.line()

    def __show_header(self):
        """
        Display application header with name and version at top of console.
        """
        self.console.print(
            Panel(
                Text.assemble(
                    ("Personal Assistant", "bold cyan"),
                    (f" v{__version__}", "dim"),
                    justify="center",
                ),
                border_style="light_slate_grey",
                padding=(0, 2),
            )
        )
        self.console.line()

    # endregion

    # region Input methods
    def __input_command(self) -> str:
        """Prompt for command input and return stripped value.

        Returns:
            The user's command, or None if input is empty.
        """
        command = self.console.input(
            "[bold yellow]Enter command: [/bold yellow]"
        ).strip()
        if not command:
            return None
        return command

    def __input_field(
        self,
        prompt: str,
        optional: bool = False,
        error_message: str = "Invalid input",
        validator: callable = None,
    ) -> str:
        """Prompt for field input with optional validation and cancellation.

        Loops until valid input received or user cancels with Ctrl+C.
        Empty input is allowed for optional fields.

        Args:
            prompt: Message to display as input prompt.
            optional: Whether field can be left empty.
            error_message: Message shown on validation failure.
            validator: Optional callable to validate input.

        Returns:
            The validated input value.

        Raises:
            OperationCancelledError: If user interrupts with Ctrl+C.
        """
        while True:
            try:
                str_value = self.console.input(
                    f"[bold yellow]{prompt}{' (optional)' if optional else ''}: [/bold yellow]"
                ).strip()
                # Required fields must not be empty
                if not optional and not str_value:
                    self.console.print(
                        self.__render_message("error", "Value cannot be empty")
                    )
                    continue
                # Validate non-empty values if validator provided
                if str_value and validator and not validator(str_value):
                    self.console.print(self.__render_message("error", error_message))
                    continue

                return str_value
            except KeyboardInterrupt:
                self.messages.append(("error", "Operation cancelled"))
                raise OperationCancelledError

    # endregion

    # region Process command methods

    # region Contact methods
    @handle_operation_errors
    def __process_add_contact_command(self, args: list[str]) -> str:
        """Add new contact via CLI args or interactive prompts.

        Supports both direct arguments (name phone [email] [birthday] [address])
        and interactive input for each field.

        Args:
            args: Command arguments. If empty, prompts interactively.

        Returns:
            Contact information or None on cancellation.
        """
        data = {
            "name": None,
            "phone": None,
            "email": None,
            "birthday": None,
            "address": None,
        }
        # CLI mode: parse arguments directly
        if len(args) >= 2 and len(args) <= 5:
            name, phone, *rest = args
            # Validate required fields
            if Contact.validate_name(name):
                data["name"] = name
            else:
                self.messages.append(("error", ERROR_MESSAGES["contacts"]["name"]))
                return

            if Contact.validate_phone(phone):
                data["phone"] = phone
            else:
                self.messages.append(("error", ERROR_MESSAGES["contacts"]["phone"]))
                return

            # Validate optional fields only if provided
            if len(rest) >= 1 and rest[0]:
                email = rest[0]
                if Contact.validate_email(email):
                    data["email"] = email
                else:
                    self.messages.append(("error", ERROR_MESSAGES["contacts"]["email"]))
                    return

            if len(rest) >= 2 and rest[1]:
                birthday = rest[1]
                if Contact.validate_birthday(birthday):
                    data["birthday"] = birthday
                else:
                    self.messages.append(
                        ("error", ERROR_MESSAGES["contacts"]["birthday"])
                    )
                    return

            if len(rest) >= 3 and rest[2]:
                address = rest[2]
                if address:
                    data["address"] = address
                else:
                    self.messages.append(
                        ("error", ERROR_MESSAGES["contacts"]["address"])
                    )
                    return

        # Interactive mode: prompt for each field
        elif len(args) == 0:
            data["name"] = self.__input_field(
                "Enter name",
                error_message=ERROR_MESSAGES["contacts"]["name"],
                validator=Contact.validate_name,
            )

            data["phone"] = self.__input_field(
                "Enter phone",
                error_message=ERROR_MESSAGES["contacts"]["phone"],
                validator=Contact.validate_phone,
            )

            email = self.__input_field(
                "Enter email",
                optional=True,
                error_message=ERROR_MESSAGES["contacts"]["email"],
                validator=Contact.validate_email,
            )
            data["email"] = email if email else None

            birthday = self.__input_field(
                "Enter birthday",
                optional=True,
                error_message=ERROR_MESSAGES["contacts"]["birthday"],
                validator=Contact.validate_birthday,
            )
            data["birthday"] = birthday if birthday else None

            data["address"] = self.__input_field(
                "Enter address",
                optional=True,
                error_message=ERROR_MESSAGES["contacts"]["address"],
            )

        else:
            # Invalid number of arguments
            self.messages.append(
                (
                    "error",
                    "Usage: add-contact <name> <phone> [email] [birthday] [address]",
                )
            )
            return

        contact = Contact.from_dict(data)
        self.contact_book.append(contact)
        self.messages.append(
            (
                "response",
                f'Contact "{data["name"]}" added with phone "{data["phone"]}" {data["email"] or ""} {data["birthday"] or ""} {data["address"] or ""}',
            )
        )
        return

    def __process_show_contacts_command(self):
        """Display all contacts in a formatted table.

        Shows empty message if no contacts exist.
        """
        contacts = self.contact_book.data
        if not contacts:
            self.messages.append(("response", "No contacts found"))
            return
        table = Table(title="Contacts")
        table.add_column("Name", style="cyan", justify="left")
        table.add_column("Phone", style="green", justify="left")
        table.add_column("Email", style="blue", justify="left")
        table.add_column("Birthday", style="magenta", justify="left")
        table.add_column("Address", style="yellow", justify="left")
        for contact in contacts:
            table.add_row(
                contact.name,
                contact.phone,
                contact.email,
                str(contact.birthday) if contact.birthday else "",
                contact.address,
            )
        self.messages.append(("table", table))

    @handle_operation_errors
    def __process_find_contact_command(self, args: list[str]):
        """Search contacts by matching term across all fields.

        Args:
            args: Command arguments containing search term.

        Displays results in table, or message if no matches found.
        """
        data = {
            "search": None,
        }
        if len(args) >= 1:
            data["search"] = " ".join(args)
        elif len(args) == 0:
            data["search"] = self.__input_field(
                "Enter search term",
            )
        else:
            self.messages.append(("error", "Usage: find-contact <search>"))
            return

        contacts = self.contact_book.find(data["search"])
        if not contacts:
            self.messages.append(("response", "No contacts found"))
            return

        table = Table(title="Contacts")
        table.add_column("Name", style="cyan", justify="left")
        table.add_column("Phone", style="green", justify="left")
        table.add_column("Email", style="blue", justify="left")
        table.add_column("Birthday", style="magenta", justify="left")
        table.add_column("Address", style="yellow", justify="left")
        for contact in contacts:
            table.add_row(
                contact.name,
                contact.phone,
                contact.email,
                str(contact.birthday) if contact.birthday else "",
                contact.address,
            )
        self.messages.append(("table", table))

    @handle_operation_errors
    def __process_edit_contact_command(self, args: list[str]):
        """Edit contact fields via CLI args or interactive prompts.

        Supports direct arguments (name [phone] [email] [birthday] [address])
        or interactive mode that shows current values before editing.

        Args:
            args: Command arguments. If empty, prompts interactively.
        """
        fields = {
            "phone": None,
            "email": None,
            "birthday": None,
            "address": None,
        }
        # CLI mode: parse arguments
        if len(args) >= 1 and len(args) <= 5:
            name, *rest = args
            contact = self.contact_book.find_exact(name)
            if not contact:
                self.messages.append(("error", f'Contact "{name}" not found'))
                return

            # Validate optional fields only if provided
            if len(rest) >= 1 and rest[0]:
                email = rest[0]
                if Contact.validate_email(email):
                    fields["email"] = email
                else:
                    self.messages.append(("error", ERROR_MESSAGES["contacts"]["email"]))
                    return

            if len(rest) >= 2 and rest[1]:
                birthday = rest[1]
                if Contact.validate_birthday(birthday):
                    fields["birthday"] = birthday
                else:
                    self.messages.append(
                        ("error", ERROR_MESSAGES["contacts"]["birthday"])
                    )
                    return

            if len(rest) >= 3 and rest[2]:
                address = rest[2]
                if address:
                    fields["address"] = address
                else:
                    self.messages.append(
                        ("error", ERROR_MESSAGES["contacts"]["address"])
                    )
                    return

        # Interactive mode: show current values and prompt for changes
        elif len(args) == 0:
            name = self.__input_field(
                "Enter name",
                error_message=ERROR_MESSAGES["contacts"]["name"],
                validator=Contact.validate_name,
            )
            contact = self.contact_book.find_exact(name)
            if not contact:
                self.messages.append(("error", f'Contact "{name}" not found'))
                return

            self.console.print(
                self.__render_message(
                    "info",
                    f"\nEditing contact: {name}\n"
                    f"Current phone: {contact.phone}\n"
                    f"Current email: {contact.email or 'Not set'}\n"
                    f"Current birthday: {str(contact.birthday) if contact.birthday else 'Not set'}\n"
                    f"Current address: {contact.address or 'Not set'}\n",
                )
            )
            phone = self.__input_field(
                "Enter phone",
                optional=True,
                error_message=ERROR_MESSAGES["contacts"]["phone"],
                validator=Contact.validate_phone,
            )
            fields["phone"] = phone if phone else None

            email = self.__input_field(
                "Enter email",
                optional=True,
                error_message=ERROR_MESSAGES["contacts"]["email"],
                validator=Contact.validate_email,
            )
            fields["email"] = email if email else None

            birthday = self.__input_field(
                "Enter birthday",
                optional=True,
                error_message=ERROR_MESSAGES["contacts"]["birthday"],
                validator=Contact.validate_birthday,
            )
            fields["birthday"] = birthday if birthday else None

            address = self.__input_field(
                "Enter address",
                optional=True,
            )
            fields["address"] = address if address else None

        else:
            # Invalid number of arguments
            self.messages.append(
                (
                    "error",
                    "Usage: edit-contact <name> [phone] [email] [birthday] [address]",
                )
            )
            return

        # Update contact using the edit method
        if self.contact_book.edit(name, fields):
            self.messages.append(("response", f'Contact "{name}" updated'))
        else:
            self.messages.append(("error", f'Contact "{name}" not found'))

    @handle_operation_errors
    def __process_delete_contact_command(self, args: list[str]):
        """Delete contact from address book by name.

        Args:
            args: Command arguments containing contact name.
        """
        data = {
            "name": None,
        }
        if len(args) >= 1:
            name = " ".join(args)
            if Contact.validate_name(name):
                data["name"] = name
            else:
                self.messages.append(("error", ERROR_MESSAGES["contacts"]["name"]))
                return
        elif len(args) == 0:
            data["name"] = self.__input_field(
                "Enter name",
                error_message=ERROR_MESSAGES["contacts"]["name"],
                validator=Contact.validate_name,
            )
        else:
            self.messages.append(("error", "Usage: delete-contact <name>"))
            return

        if self.contact_book.delete(data["name"]):
            self.messages.append(("response", f'Contact "{data["name"]}" deleted'))
        else:
            self.messages.append(("error", f'Contact "{data["name"]}" not found'))
        return

    @handle_operation_errors
    def __process_birthdays_command(self, args: list[str]):
        """Show upcoming birthdays within specified day range.

        Args:
            args: Optional arguments for day range. Defaults to prompt.

        Displays contacts with birthdays occurring in the next N days.
        """
        data = {
            "days": None,
        }
        if len(args) == 1:
            days = args[0]
            if days.isdigit() and int(days) > 0:
                data["days"] = int(days)
            else:
                self.messages.append(("error", ERROR_MESSAGES["contacts"]["days"]))
                return
        elif len(args) == 0:
            data["days"] = int(
                self.__input_field(
                    "Enter number of days",
                    error_message=ERROR_MESSAGES["contacts"]["days"],
                    validator=lambda x: x.isdigit() and int(x) > 0,
                )
            )
        else:
            self.messages.append(("error", "Usage: birthdays <days>"))
            return
        upcoming_birthdays = self.contact_book.upcoming_birthdays(data["days"])
        if not upcoming_birthdays:
            self.messages.append(("response", "No upcoming birthdays found"))
            return
        table = Table(title="Upcoming Birthdays")
        table.add_column("Name", style="cyan", justify="left")
        table.add_column("Birthday", style="magenta", justify="left")
        table.add_column("Days", style="yellow", justify="left")
        for birthday in upcoming_birthdays:
            table.add_row(birthday["name"], birthday["birthday"], str(birthday["days"]))
        self.messages.append(("table", table))

    # endregion

    # region Note methods
    def __process_add_note_command(self, args: list[str]):
        """Create new note.

        Args:
            args: Command arguments containing note content.
        """
        pass

    def __process_show_notes_command(self):
        """Display all notes in address book."""
        pass

    def __process_find_note_command(self, args: list[str]):
        """Search notes by content or tags.

        Args:
            args: Command arguments containing search term.
        """
        pass

    def __process_edit_note_command(self, args: list[str]):
        """Edit existing note content.

        Args:
            args: Command arguments containing note identifier.
        """
        pass

    def __process_delete_note_command(self, args: list[str]):
        """Remove note from storage.

        Args:
            args: Command arguments containing note identifier.
        """
        pass

    def __process_find_tag_command(self, args: list[str]):
        """Find notes with specific tag.

        Args:
            args: Command arguments containing tag name.
        """
        pass

    def __process_sort_notes_by_tags_command(self):
        """Display notes grouped by tags."""
        pass

    # endregion

    def __process_help_command(self):
        """Display all available commands for quick reference."""
        help_text = "Available commands:\n"
        for command in AVAILABLE_COMMANDS:
            help_text += f"- {command}\n"
        self.messages.append(("response", help_text))

    def __process_command(self, command_str: str) -> str:
        """Parse command string and dispatch to appropriate handler.

        Args:
            command_str: Raw command string from user input.

        Returns:
            Command status or None.
        """
        command, *args = shlex_split(command_str)
        match command.lower():
            case "exit" | "q" | "quit":
                self.exit(0)
            case "help" | "h" | "?":
                self.__process_help_command()
            case "clear" | "c" | "cls":
                self.messages = []
            case "add-contact":
                self.__process_add_contact_command(args)
            case "show-contacts":
                self.__process_show_contacts_command()
            case "find-contact":
                self.__process_find_contact_command(args)
            case "edit-contact":
                self.__process_edit_contact_command(args)
            case "delete-contact":
                self.__process_delete_contact_command(args)
            case "birthdays":
                self.__process_birthdays_command(args)
            case "add-note":
                self.__process_add_note_command(args)
            case "show-notes":
                self.__process_show_notes_command()
            case "find-note":
                self.__process_find_note_command(args)
            case "edit-note":
                self.__process_edit_note_command(args)
            case "delete-note":
                self.__process_delete_note_command(args)
            case "find-tag":
                self.__process_find_tag_command(args)
            case "sort-notes-by-tags":
                self.__process_sort_notes_by_tags_command()
            case _:
                suggestion = suggest_command(command)
                error_msg = f"Unknown command: `{command}`"
                if suggestion:
                    error_msg += f"\nDid you mean: `{suggestion}`?"
                self.messages.append(("error", error_msg))

    # endregion

    # region Public methods
    def load_content(self):
        """
        Load contact and note data from persistent storage.
        """
        self.console.print("[bold green]Loading content from files...[/bold green]")

    def save_content(self):
        """
        Save contact and note data to persistent storage.
        """
        self.console.print("[bold green]Saving content to files...[/bold green]")

    def exit(self, code: int = 0):
        """Exit the application cleanly with specified code.

        Args:
            code: Exit code to return (default: 0 for success).
        """
        self.console.clear()
        self.console.print(self.__render_message("response", "Goodbye!"))
        exit(code)

    def run(self):
        """Main application loop.

        Displays startup screen, then continuously prompts for commands,
        processes them, and displays results until user exits.
        """
        self.__show_startup_screen()

        while True:
            self.console.clear()
            self.__show_header()
            self.__show_console()
            command = self.__input_command()
            if not command:
                self.messages.append(("error", "Command cannot be empty"))
                continue
            self.messages.append(("command", command))
            self.__process_command(command)

    # endregion


class OperationCancelledError(Exception):
    """Exception raised when the user cancels an operation."""

    pass


def suggest_command(user_command):
    """
    Find the closest matching command from available commands.

    Args:
        user_command: The command string to match against available commands.

    Returns:
        The closest matching command, or None if no match found.
    """
    matches = get_close_matches(user_command, AVAILABLE_COMMANDS, n=1, cutoff=0.5)
    if matches:
        return matches[0]
    return None
