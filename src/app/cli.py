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


def suggest_command(user_command):
    """
    Find the closest matching command from available commands.

    Args:
        user_command: The command string to match against available commands.

    Returns:
        str or None: The closest matching command, or None if no match found.
    """
    matches = get_close_matches(user_command, AVAILABLE_COMMANDS, n=1, cutoff=0.5)
    if matches:
        return matches[0]
    return None


class PersonalAssistantCLI:
    """Command-line interface for the Personal Assistant application.

    This class handles all CLI interactions including rendering the UI,
    processing user input, and executing commands.
    """

    def __init__(self):
        """Initialize the Personal Assistant CLI.

        Sets up the console window title and initializes the messages list.
        """
        self.console = Console()
        self.console.set_window_title("Personal Assistant")
        self.messages: list[tuple[str, str | Table]] = []

    # Render methods

    def __render_message(self, msg_type: str, msg_text: str) -> Text:
        """
        Render a message to the console with appropriate styling.

        Args:
            msg_type: Type of message ("command", "response", "error", "info").
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
        """
        Display the startup screen with application information.

        Shows a splash screen with project details, credits, and a countdown
        before entering the main application loop.
        """
        layout = Layout()

        # Title section
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
            Layout(name="credits"),
            Layout(name="footer", size=3),
        )

        # Credits section - display description and authors in 2 columns
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

        # Create layout once, then only update footer in the loop
        with Live(
            layout, console=self.console, screen=True, auto_refresh=False
        ) as live:
            for i in range(5, 0, -1):
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
        """
        Display all console messages.

        Renders the message history to the console, showing welcome message
        if no messages exist yet.
        """
        if len(self.messages) == 0:
            self.messages.append(
                (
                    "info",
                    "Welcome to Personal Assistant!\nUse 'help' to see available commands.",
                )
            )

        for msg_type, msg_text in self.messages:
            if msg_type == "table":
                self.console.line()
                self.console.print(msg_text)
            else:
                self.console.print(self.__render_message(msg_type, msg_text))

            if msg_type != "command":
                self.console.line()

    def __show_header(self):
        """
        Display the application header.

        Shows a panel with the application name and version at the top of the console.
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

    # Input methods

    def __input_command(self) -> str:
        """
        Prompt the user to enter a command.

        Returns:
            str or None: The user's command, or None if input is empty.
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
        required: bool = True,
        error_message: str = "Invalid input",
        validator: callable = None,
    ) -> str:
        """
        Prompt the user to enter a field with optional validation.

        Args:
            prompt: The message to display as the input prompt.
            required: Whether the field must have a non-empty value.
            error_message: Message to display on validation failure.
            validator: Optional callable function to validate input.

        Returns:
            str or None: The validated input value, or None on cancellation.
        """
        while True:
            try:
                value = self.console.input(
                    f"[bold yellow]{prompt}: [/bold yellow]"
                ).strip()
                if required and not value:
                    self.console.print(
                        self.__render_message("error", "Value cannot be empty")
                    )
                    continue
                if validator and not validator(value):
                    self.console.print(self.__render_message("error", error_message))
                    continue
                return value
            except KeyboardInterrupt:
                self.messages.append(("error", "Operation cancelled"))
                break
        return None

    # Process command methods

    def __process_help_command(self):
        """
        Display help information for all available commands.

        Shows a list of all supported commands with their names.
        """
        help_text = "Available commands:\n"
        for command in AVAILABLE_COMMANDS:
            help_text += f"- {command}\n"
        self.messages.append(("response", help_text))

    def __process_add_contact_command(self, args: list[str]) -> str:
        """
        Process the `add-contact` command.

        Args:
            args: Command arguments containing name and phone (optional).
                   If not provided, prompts user for input.

        Returns:
            str: Contact information or None on cancellation.

        Usage:
            - add-contact <name> <phone> - Add contact with arguments
            - add-contact - Interactive mode, prompts for details
        """
        name = None
        phone = None
        if len(args) == 2:
            name, phone = args
            # TODO: Validate name and phone
        elif len(args) == 0:
            name = self.__input_field(
                "Enter name",
                required=True,
                error_message="Name must be between 4 and 20 characters",
                validator=lambda x: len(x) > 4 and len(x) < 20,
            )
            if not name:
                return
            phone = self.__input_field(
                "Enter phone", required=True, error_message="Phone cannot be empty"
            )
            if not phone:
                return
        else:
            self.messages.append(("error", "Usage: add-contact <name> <phone>"))
            return

        # TODO: Add contact to book
        self.messages.append(("response", f"Contact {name} added with phone {phone}"))

    def __process_show_contacts_command(self):
        """
        Process the `show-contacts` command.

        Displays all contacts in the address book.
        """
        table = Table(title="Contacts")
        table.add_column("Name", style="cyan", justify="left")
        table.add_column("Phone", style="green", justify="left")
        table.add_row("John Doe", "1234567890")
        table.add_row("Jane Smith", "0987654321")
        self.messages.append(("table", table))
        pass

    def __process_find_contact_command(self, args: list[str]):
        """
        Process the `find-contact` command.

        Args:
            args: Command arguments containing search term.

        Searches for contacts matching the provided criteria.
        """
        pass

    def __process_edit_contact_command(self, args: list[str]):
        """
        Process the `edit-contact` command.

        Args:
            args: Command arguments containing contact details.

        Edits an existing contact's information.
        """
        pass

    def __process_delete_contact_command(self, args: list[str]):
        """
        Process the `delete-contact` command.

        Args:
            args: Command arguments containing contact identifier.

        Removes a contact from the address book.
        """
        pass

    def __process_birthdays_command(self, args: list[str]):
        """
        Process the `birthdays` command.

        Args:
            args: Optional arguments for filtering birthday range.

        Displays upcoming birthdays for contacts.
        """
        pass

    def __process_add_note_command(self, args: list[str]):
        """
        Process the `add-note` command.

        Args:
            args: Command arguments containing note content.

        Creates a new note.
        """
        pass

    def __process_show_notes_command(self):
        """
        Process the `show-notes` command.

        Displays all notes.
        """
        pass

    def __process_find_note_command(self, args: list[str]):
        """
        Process the `find-note` command.

        Args:
            args: Command arguments containing search term.

        Searches for notes matching the provided criteria.
        """
        pass

    def __process_edit_note_command(self, args: list[str]):
        """
        Process the `edit-note` command.

        Args:
            args: Command arguments containing note identifier.

        Edits an existing note.
        """
        pass

    def __process_delete_note_command(self, args: list[str]):
        """
        Process the `delete-note` command.

        Args:
            args: Command arguments containing note identifier.

        Removes a note.
        """
        pass

    def __process_find_tag_command(self, args: list[str]):
        """
        Process the `find-tag` command.

        Args:
            args: Command arguments containing tag name.

        Finds notes with a specific tag.
        """
        pass

    def __process_sort_notes_by_tags_command(self):
        """
        Process the `sort-notes-by-tags` command.

        Displays notes sorted by their tags.
        """
        pass

    def __process_command(self, command_str: str) -> str:
        """
        Parse command string and process it.

        Args:
            command_str: Raw command string from user input.

        Returns:
            str: Command status or None.
        """
        command, *args = shlex_split(command_str)
        match command.lower():
            case "exit":
                self.exit(0)
            case "help" | "h" | "?":
                self.__process_help_command()
            case "clear" | "c":
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

    # Public methods

    def load_content(self):
        """
        Load content from files.
        """
        self.console.print("[bold green]Loading content from files...[/bold green]")

    def save_content(self):
        """
        Save content to files.
        """
        self.console.print("[bold green]Saving content to files...[/bold green]")

    def exit(self, code: int = 0):
        """
        Exit the application.

        Args:
            code: Exit code to return (default: 0 for success).
        """
        self.console.clear()
        self.console.print(self.__render_message("response", "Goodbye!"))
        exit(code)

    def run(self):
        """
        Run the main application loop.

        Continuously prompts for commands, processes them, and displays results
        until the user exits.
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
