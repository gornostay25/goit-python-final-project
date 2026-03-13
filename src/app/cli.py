"""Command-line interface for the Personal Assistant."""

from shlex import split as shlex_split
from time import sleep

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import PromptSession, prompt
from prompt_toolkit.validation import Validator
from pygments.lexer import Lexer
from pygments.lexers.markup import MarkdownLexer
from rich.align import Align
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from app import __authors__, __description__, __version__
from app.contacts import Contact, ContactBook
from app.notes import Note, NotesBook
from app.utils import (
    AVAILABLE_COMMANDS,
    COMMAND_SIGNATURES,
    ERROR_MESSAGES,
    CommandCompleter,
    OperationCancelledError,
    handle_operation_errors,
    suggest_command,
)


class PersonalAssistantCLI:
    """Command-line interface for the Personal Assistant application.

    Provides a Rich-based TUI with colored output, tables, and styled
    messages. Handles both command-line arguments and interactive input.
    """

    def __init__(
        self,
        contact_book: ContactBook = ContactBook(),
        note_book: NotesBook = NotesBook(),
    ):
        """Initialize CLI with Rich console, prompt_toolkit session, and empty message history."""
        self.console = Console()
        self.console.set_window_title("Personal Assistant")
        self.messages: list[tuple[str, RenderableType]] = []

        self.contact_book = contact_book
        self.note_book = note_book

        # Initialize prompt_toolkit session with history and autocompletion
        history = InMemoryHistory()
        completer = CommandCompleter(
            [cmd[0] for cmd in AVAILABLE_COMMANDS], COMMAND_SIGNATURES
        )
        self.command_session = PromptSession(history=history, completer=completer)

    # region Render methods
    def __render_message(self, msg_type: str, msg_text: RenderableType) -> Text:
        """Apply color styling to messages based on type.

        Args:
            msg_type: Message type ("command", "response", "error", "info", "custom").
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

        return msg_text

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
            Layout(name="credits", minimum_size=11),  # 4 padding + authors
            Layout(name="footer", size=3),
        )

        authors_text = [
            item
            for author, role in __authors__.items()
            for item in [
                (f"{author}", "bold"),
                (" - ", ""),
                (f"{role}\n", "yellow"),
                ("\n", ""),
            ]
        ]

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
                    Align.center(Text.assemble(*authors_text)),
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
            self.console.print(self.__render_message(msg_type, msg_content))
            if msg_type != "command":
                self.console.line()

    def __show_header(self):
        """Display application header with name and version at top of console.

        Creates a styled panel showing the application name and version number,
        providing consistent branding across all command interactions.
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

    def __render_contacts_table(self, contacts: list[Contact]):
        table = Table(
            title="Contacts",
            show_lines=True,
        )
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
        return table

    def __render_birthdays_table(self, upcoming_birthdays: list[dict]):
        table = Table(title="Upcoming Birthdays")
        table.add_column("Name", style="cyan", justify="left")
        table.add_column("Birthday", style="magenta", justify="left")
        table.add_column("Days", style="yellow", justify="left")
        for birthday in upcoming_birthdays:
            table.add_row(birthday["name"], birthday["birthday"], str(birthday["days"]))
        return table

    def __render_notes_table(self, notes: list[Note]):
        table = Table(
            title="Notes",
            show_lines=True,
            caption="To see full note, use 'show-notes <index>' command",
        )
        table.add_column("№", style="dim", justify="left")
        table.add_column("Title", style="cyan", justify="left")
        table.add_column("Tags", style="magenta", justify="left")
        for note in notes:
            original_index = self.note_book.data.index(note) + 1
            table.add_row(str(original_index), note.title, note.tags_str)
        return table

    def __render_note_details(self, note: Note):
        return Panel(
            Markdown(note.text),
            subtitle=f"Tags: {note.tags_str}" if len(note.tags) > 0 else None,
            subtitle_align="right",
        )

    # endregion

    # region Input methods
    def __input_command(self) -> str:
        """Prompt for command input with autocompletion and history.

        Returns:
            The user's command, or None if input is empty.
        """
        command = self.command_session.prompt(
            message=HTML("<b fg='yellow'>> </b>")
        ).strip()
        if not command:
            return None
        return command

    def __input_field(
        self,
        message: str,
        optional: bool = False,
        error_message: str = "Invalid input",
        validator: callable = None,
        placeholder: str | None = None,
        default: str = "",
        multiline: bool = False,
        lexer: Lexer | None = None,
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
        ptk_validator = None
        if validator:
            ptk_validator = Validator.from_callable(
                validate_func=lambda x: True if optional and not x else validator(x),
                error_message=error_message,
                move_cursor_to_end=True,
            )

        rprompt = "(Optional)" if optional else None
        toolbar = HTML(
            f"<b>[{'ESC+Enter' if multiline else 'Enter'}] to submit, [Ctrl+C] to cancel</b>"
        )
        while True:
            try:
                value = prompt(
                    f"{message}: ",
                    placeholder=placeholder,
                    default=default,
                    validator=ptk_validator,
                    validate_while_typing=False,
                    rprompt=rprompt,
                    multiline=multiline,
                    bottom_toolbar=toolbar,
                    lexer=lexer,
                )
                return value

            except KeyboardInterrupt:
                self.messages.append(("error", "Operation cancelled"))
                raise OperationCancelledError

    # endregion

    # region Process command methods

    # region Contact methods
    @handle_operation_errors
    def __handle_add_contact_command(self, args: list[str]):
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
        # CLI mode: parse arguments directly (non-interactive)
        # Supports 2-5 arguments: name phone [email] [birthday] [address]
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
                    f"Usage: add-contact {COMMAND_SIGNATURES['add-contact']}",
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

    def __handle_show_contacts_command(self):
        """Display all contacts in a formatted table.

        Shows empty message if no contacts exist.
        """
        contacts = self.contact_book.data
        if not contacts:
            self.messages.append(("response", "No contacts found"))
            return

        self.messages.append(("table", self.__render_contacts_table(contacts)))

    @handle_operation_errors
    def __handle_find_contact_command(self, args: list[str]):
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
            self.messages.append(
                ("error", f"Usage: find-contact {COMMAND_SIGNATURES['find-contact']}")
            )
            return

        contacts = self.contact_book.find(data["search"])
        if not contacts:
            self.messages.append(("response", "No contacts found"))
            return

        self.messages.append(("table", self.__render_contacts_table(contacts)))

    @handle_operation_errors
    def __handle_edit_contact_command(self, args: list[str]):
        """Edit contact fields via CLI args or interactive prompts.

        Supports direct arguments (index [name] [phone] [email] [birthday] [address])
        or interactive mode that shows current values before editing.

        Args:
            args: Command arguments. If empty, prompts interactively.
        """
        fields = {
            "name": None,
            "phone": None,
            "email": None,
            "birthday": None,
            "address": None,
        }
        max_index = len(self.contact_book.data)
        if max_index == 0:
            self.messages.append(("response", "There are no contacts to edit"))
            return
        # CLI mode: parse arguments
        if len(args) > 1 and len(args) <= 6:
            index, *rest = args
            contact = self.contact_book.get(index)
            if not contact:
                self.messages.append(
                    ("error", ERROR_MESSAGES["contacts"]["not_found"](index))
                )
                return

            # Validate optional fields only if provided
            if len(rest) >= 1 and rest[0]:
                name = rest[0]
                if Contact.validate_name(name):
                    fields["name"] = name
                else:
                    self.messages.append(("error", ERROR_MESSAGES["contacts"]["name"]))
                    return

            if len(rest) >= 2 and rest[1]:
                phone = rest[1]
                if Contact.validate_phone(phone):
                    fields["phone"] = phone
                else:
                    self.messages.append(("error", ERROR_MESSAGES["contacts"]["phone"]))
                    return

            if len(rest) >= 3 and rest[2]:
                email = rest[2]
                if Contact.validate_email(email):
                    fields["email"] = email
                else:
                    self.messages.append(("error", ERROR_MESSAGES["contacts"]["email"]))
                    return

            if len(rest) >= 4 and rest[3]:
                birthday = rest[3]
                if Contact.validate_birthday(birthday):
                    fields["birthday"] = birthday
                else:
                    self.messages.append(
                        ("error", ERROR_MESSAGES["contacts"]["birthday"])
                    )
                    return

            if len(rest) >= 5 and rest[4]:
                address = rest[4]
                if address:
                    fields["address"] = address
                else:
                    self.messages.append(
                        ("error", ERROR_MESSAGES["contacts"]["address"])
                    )
                    return

        # Interactive mode: show current values and prompt for changes
        elif len(args) <= 1:
            if len(args) == 0:
                index = self.__input_field(
                    "Enter index",
                    error_message=ERROR_MESSAGES["contacts"]["index"](max_index),
                    validator=self.contact_book.validate_index,
                )
            else:
                index = args[0]
            contact = self.contact_book.get(index)
            if not contact:
                self.messages.append(
                    ("error", ERROR_MESSAGES["contacts"]["not_found"](index))
                )
                return

            name = self.__input_field(
                "Edit name",
                optional=True,
                error_message=ERROR_MESSAGES["contacts"]["name"],
                validator=Contact.validate_name,
                placeholder=contact.name,
            )
            fields["name"] = name if name else None

            phone = self.__input_field(
                "Edit phone",
                optional=True,
                error_message=ERROR_MESSAGES["contacts"]["phone"],
                validator=Contact.validate_phone,
                placeholder=contact.phone,
            )
            fields["phone"] = phone if phone else None

            email = self.__input_field(
                "Edit email",
                optional=True,
                error_message=ERROR_MESSAGES["contacts"]["email"],
                validator=Contact.validate_email,
                placeholder=contact.email,
            )
            fields["email"] = email if email else None

            birthday = self.__input_field(
                "Edit birthday",
                optional=True,
                error_message=ERROR_MESSAGES["contacts"]["birthday"],
                validator=Contact.validate_birthday,
                placeholder=str(contact.birthday) if contact.birthday else None,
            )
            fields["birthday"] = birthday if birthday else None

            address = self.__input_field(
                "Edit address",
                optional=True,
                placeholder=contact.address,
            )
            fields["address"] = address if address else None

        else:
            # Invalid number of arguments
            self.messages.append(
                (
                    "error",
                    f"Usage: edit-contact {COMMAND_SIGNATURES['edit-contact']}",
                )
            )
            return

        # Update contact using the edit method
        if self.contact_book.edit(index, fields):
            self.messages.append(("response", f'Contact "{contact.name}" updated'))
        else:
            self.messages.append(
                ("error", ERROR_MESSAGES["contacts"]["not_found"](index))
            )

    @handle_operation_errors
    def __handle_delete_contact_command(self, args: list[str]):
        """Delete contact from address book by index.

        Args:
            args: Command arguments containing contact index.
        """
        index = None
        max_index = len(self.contact_book.data)
        if max_index == 0:
            self.messages.append(("response", "There are no contacts to delete"))
            return
        if len(args) == 1:
            if self.contact_book.validate_index(args[0]):
                index = args[0]
            else:
                self.messages.append(
                    ("error", ERROR_MESSAGES["contacts"]["index"](max_index))
                )
                return
        elif len(args) == 0:
            index = self.__input_field(
                "Enter index",
                error_message=ERROR_MESSAGES["contacts"]["index"](max_index),
                validator=self.contact_book.validate_index,
            )
        else:
            self.messages.append(
                (
                    "error",
                    f"Usage: delete-contact {COMMAND_SIGNATURES['delete-contact']}",
                )
            )
            return

        if self.contact_book.delete(index):
            self.messages.append(("response", f'Contact with index "{index}" deleted'))
        else:
            self.messages.append(
                ("error", ERROR_MESSAGES["contacts"]["not_found"](index))
            )

    @handle_operation_errors
    def __handle_birthdays_command(self, args: list[str]):
        """Show upcoming birthdays within specified day range.

        Args:
            args: Optional arguments for day range. Defaults to prompt.

        Displays contacts with birthdays occurring in the next N days.
        """
        data = {
            "days": None,
        }
        # Parse days from command line arguments if provided
        if len(args) == 1:
            days = args[0]
            if days.isdigit() and int(days) > 0:
                data["days"] = int(days)
            else:
                self.messages.append(("error", ERROR_MESSAGES["contacts"]["days"]))
                return
        # Otherwise prompt interactively for the day range
        elif len(args) == 0:
            data["days"] = int(
                self.__input_field(
                    "Enter number of days",
                    error_message=ERROR_MESSAGES["contacts"]["days"],
                    validator=lambda x: x.isdigit() and int(x) > 0,
                )
            )
        else:
            self.messages.append(
                ("error", f"Usage: birthdays {COMMAND_SIGNATURES['birthdays']}")
            )
            return
        upcoming_birthdays = self.contact_book.upcoming_birthdays(data["days"])
        if not upcoming_birthdays:
            self.messages.append(("response", "No upcoming birthdays found"))
            return

        self.messages.append(
            ("table", self.__render_birthdays_table(upcoming_birthdays))
        )

    # endregion

    # region Note methods
    @handle_operation_errors
    def __handle_add_note_command(self, args: list[str]):
        """Create new note.

        Args:
            args: Command arguments containing note content.
        """
        data = {
            "text": None,
            "tags": [],
        }
        # CLI mode: parse arguments directly
        if len(args) == 2:
            text, tags = args
            if Note.validate_text(text):
                data["text"] = text
            else:
                self.messages.append(("error", ERROR_MESSAGES["notes"]["text"]))
                return

            if tags:
                data["tags"] = tags.split(",")
            else:
                data["tags"] = []

        elif len(args) == 0:
            data["text"] = self.__input_field(
                "Enter text",
                error_message=ERROR_MESSAGES["notes"]["text"],
                validator=Note.validate_text,
                multiline=True,
                lexer=PygmentsLexer(MarkdownLexer),
            )
            data["tags"] = self.__input_field(
                "Enter tags",
                optional=True,
                error_message=ERROR_MESSAGES["notes"]["tags"],
            ).split(",")
        else:
            self.messages.append(
                ("error", f"Usage: add-note {COMMAND_SIGNATURES['add-note']}")
            )
            return

        note = Note.from_dict(data)
        self.note_book.append(note)
        self.messages.append(
            ("response", f'Note "{note.title}" added with tags "{note.tags_str}"')
        )

    def __show_note(self, index: int):
        note = self.note_book.get(index)
        if not note:
            self.messages.append(("error", ERROR_MESSAGES["notes"]["not_found"](index)))
            return

        self.messages.append(
            (
                "custom",
                self.__render_note_details(note),
            )
        )

    def __handle_show_notes_command(self, args: list[str]):
        """Display all notes in address book."""
        index = None
        max_index = len(self.note_book.data)

        # If index is provided, show the note details
        if len(args) == 1 and max_index > 0:
            index = args[0]
            if self.note_book.validate_index(index):
                index = int(index)
                return self.__show_note(index)
            else:
                self.messages.append(
                    ("error", ERROR_MESSAGES["notes"]["index"](max_index))
                )
                return

        # Otherwise, show all notes
        notes = self.note_book.data
        if not notes:
            self.messages.append(("response", "No notes found"))
            return

        self.messages.append(("table", self.__render_notes_table(notes)))

    @handle_operation_errors
    def __handle_find_note_command(self, args: list[str]):
        """Search notes by content or tags.

        Finds all notes matching the search term in either the note text
        or associated tags. Displays results in a formatted table.

        Args:
            args: Command arguments containing search term.
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
            self.messages.append(
                ("error", f"Usage: find-note {COMMAND_SIGNATURES['find-note']}")
            )
            return

        notes = self.note_book.find(data["search"])
        if not notes:
            self.messages.append(("response", "No notes found"))
            return

        self.messages.append(("table", self.__render_notes_table(notes)))

    @handle_operation_errors
    def __handle_edit_note_command(self, args: list[str]):
        """Edit existing note content and tags.

        Allows modifying the text content and/or tags of an existing note.
        Supports both direct arguments and interactive prompts.

        Args:
            args: Command arguments containing note index and new content.
        """
        fields = {
            "text": None,
            "tags": [],
        }
        max_index = len(self.note_book.data)
        if max_index == 0:
            self.messages.append(("response", "There are no notes to edit"))
            return
        # CLI mode: parse arguments
        if len(args) > 1 and len(args) <= 3:
            index, *rest = args

            note = self.note_book.get(index)
            if not note:
                self.messages.append(
                    ("error", ERROR_MESSAGES["notes"]["not_found"](index))
                )
                return

            if len(rest) >= 1 and rest[0]:
                text = rest[0]
                if Note.validate_text(text):
                    fields["text"] = text
                else:
                    self.messages.append(("error", ERROR_MESSAGES["notes"]["text"]))
                    return

            if len(rest) >= 2 and rest[1]:
                tags = rest[1]
                if tags:
                    fields["tags"] = tags.split(",")
                else:
                    fields["tags"] = []

        # Interactive mode: show current values and prompt for changes
        elif len(args) <= 1:
            if len(args) == 0:
                index = self.__input_field(
                    "Enter index",
                    error_message=ERROR_MESSAGES["notes"]["index"](max_index),
                    validator=self.note_book.validate_index,
                )
            else:
                index = args[0]
            note = self.note_book.get(index)
            if not note:
                self.messages.append(
                    ("error", ERROR_MESSAGES["notes"]["not_found"](index))
                )
                return

            text = self.__input_field(
                "Edit text",
                optional=True,
                error_message=ERROR_MESSAGES["notes"]["text"],
                validator=Note.validate_text,
                default=note.text,
                multiline=True,
                lexer=PygmentsLexer(MarkdownLexer),
            )
            fields["text"] = text if text else None

            tags = self.__input_field(
                "Edit tags",
                optional=True,
                error_message=ERROR_MESSAGES["notes"]["tags"],
                default=note.tags_str,
            ).split(",")
            fields["tags"] = tags if tags else None

        else:
            # Invalid number of arguments
            self.messages.append(
                (
                    "error",
                    f"Usage: edit-contact {COMMAND_SIGNATURES['edit-contact']}",
                )
            )
            return

        # Update contact using the edit method
        if self.note_book.edit(index, fields):
            self.messages.append(("response", f'Note "{note.title}" updated'))
        else:
            self.messages.append(("error", ERROR_MESSAGES["notes"]["not_found"](index)))

    @handle_operation_errors
    def __handle_delete_note_command(self, args: list[str]):
        """Remove note from storage by index.

        Permanently deletes the note at the specified index from the notes book.
        The index corresponds to the position shown in the notes list.

        Args:
            args: Command arguments containing note index.
        """
        index = None
        max_index = len(self.note_book.data)
        if max_index == 0:
            self.messages.append(("response", "There are no notes to delete"))
            return
        if len(args) == 1:
            if self.note_book.validate_index(args[0]):
                index = args[0]
            else:
                self.messages.append(
                    ("error", ERROR_MESSAGES["notes"]["index"](max_index))
                )
                return
        elif len(args) == 0:
            index = self.__input_field(
                "Enter index",
                error_message=ERROR_MESSAGES["notes"]["index"](max_index),
                validator=self.note_book.validate_index,
            )
        else:
            self.messages.append(
                (
                    "error",
                    f"Usage: delete-note {COMMAND_SIGNATURES['delete-note']}",
                )
            )
            return

        if self.note_book.delete(index):
            self.messages.append(("response", f'Note with index "{index}" deleted'))
        else:
            self.messages.append(("error", ERROR_MESSAGES["notes"]["not_found"](index)))

    @handle_operation_errors
    def __handle_find_tag_command(self, args: list[str]):
        """Search notes by content or tags.

        Finds all notes matching the search term in either the note text
        or associated tags. Displays results in a formatted table.

        Args:
            args: Command arguments containing search term.
        """
        data = {
            "tags": [],
        }
        if len(args) >= 1:
            data["tags"] = " ".join(args).split(",")
        elif len(args) == 0:
            data["tags"] = self.__input_field(
                "Enter tags",
            ).split(",")
        else:
            self.messages.append(
                ("error", f"Usage: find-tag {COMMAND_SIGNATURES['find-tag']}")
            )
            return

        notes = self.note_book.find_by_tag(data["tags"])
        if not notes:
            self.messages.append(("response", "No notes found with the given tags"))
            return

        self.messages.append(("table", self.__render_notes_table(notes)))

    def __handle_sort_notes_by_tags_command(self):
        """Display notes grouped and sorted by tags.

        Organizes all notes by their associated tags, creating a grouped view
        that helps users see patterns and categories across their notes.
        Multiple tags per note cause the note to appear under each tag.
        """
        notes = sorted(self.note_book)
        if not notes:
            self.messages.append(("response", "No notes found"))
            return

        self.messages.append(("table", self.__render_notes_table(notes)))

    # endregion

    def __handle_help_command(self):
        """Display all available commands for quick reference."""
        categories: dict[str, list[tuple[str, str]]] = {}
        for command, category in AVAILABLE_COMMANDS:
            if category not in categories:
                categories[category] = []
            categories[category].append((command, COMMAND_SIGNATURES.get(command, "")))

        help_text: list[tuple[str, str]] = []
        for category in categories.keys():
            help_text.append((f"{category.capitalize()} Commands:\n", "bold cyan"))
            help_text.append((("-" * 80) + "\n", "white"))
            for command, signature in categories[category]:
                help_text.append((f"\t{command} ", "green"))
                help_text.append((signature or "", "white"))
                help_text.append(("\n", ""))
            help_text.append(("\n", "white"))

        self.messages.append(("custom", Text.assemble(*help_text)))

    def __handle_command(self, command_str: str) -> str:
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
                self.__handle_help_command()
            case "clear" | "c" | "cls":
                self.messages = []
            case "add-contact":
                self.__handle_add_contact_command(args)
            case "show-contacts":
                self.__handle_show_contacts_command()
            case "find-contact":
                self.__handle_find_contact_command(args)
            case "edit-contact":
                self.__handle_edit_contact_command(args)
            case "delete-contact":
                self.__handle_delete_contact_command(args)
            case "birthdays":
                self.__handle_birthdays_command(args)
            case "add-note":
                self.__handle_add_note_command(args)
            case "show-notes":
                self.__handle_show_notes_command(args)
            case "find-note":
                self.__handle_find_note_command(args)
            case "edit-note":
                self.__handle_edit_note_command(args)
            case "delete-note":
                self.__handle_delete_note_command(args)
            case "find-tag":
                self.__handle_find_tag_command(args)
            case "sort-notes-by-tags":
                self.__handle_sort_notes_by_tags_command()
            case _:
                suggestion = suggest_command(command)
                error_msg = f"Unknown command: `{command}`"
                if suggestion:
                    error_msg += f"\nDid you mean: `{suggestion}`?"
                self.messages.append(("error", error_msg))

    # endregion

    # region Public methods
    def load_content(self) -> None:
        """Load contact and note data from persistent storage.

        Reads saved contacts and notes from disk to restore the application
        state between sessions. Currently displays a placeholder message.
        """
        self.console.print("[bold green]Loading content from files...[/bold green]")

    def save_content(self) -> None:
        """Save contact and note data to persistent storage.

        Persists all contacts and notes to disk to ensure data survives
        application restarts. Currently displays a placeholder message.
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
            self.__handle_command(command)

    # endregion
