"""Type definitions for the Personal Assistant application.

Provides TypedDict and Literal types for enhanced type safety and better
IDE support throughout the application.
"""

from typing import Literal, TypedDict


class ContactEditFields(TypedDict, total=False):
    """TypedDict for contact field updates.

    All fields are optional (total=False) to support partial updates.
    """

    name: str | None
    phone: str | None
    email: str | None
    birthday: str | None
    address: str | None


class NoteEditFields(TypedDict, total=False):
    """TypedDict for note field updates.

    All fields are optional (total=False) to support partial updates.
    """

    text: str | None
    tags: list[str] | None


class BirthdayInfo(TypedDict):
    """TypedDict for birthday information in upcoming birthdays list.

    Represents a single contact's upcoming birthday information.
    """

    name: str
    birthday: str
    days: int


MessageType = Literal["command", "response", "error", "info", "custom", "table"]
"""Literal type for message types in CLI.

Valid message types:
- "command": User input commands
- "response": Command output messages
- "error": Error messages
- "info": Informational messages
- "custom": Custom rendered objects (tables, panels, etc.)
- "table": Table representations
"""
