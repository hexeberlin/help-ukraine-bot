"""Domain models - Immutable value objects for the application."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ChatContext:
    """Immutable context information about a chat interaction."""
    chat_id: int
    user_id: int
    message_id: int
    is_admin: bool


@dataclass(frozen=True)
class CommandRequest:
    """Immutable request object for command handling."""
    command: str
    parameter: Optional[str]
    chat_context: ChatContext
