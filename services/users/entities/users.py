from dataclasses import (
    dataclass,
    field,
)
from typing import List

from services.users.entities.base import BaseEntity


@dataclass
class UserEntity(BaseEntity):
    """Сутність користувача."""

    id: int
    status: str = "demo"
    applications_sent: int = 0
    whitelist: List[str] = field(default_factory=list)
    active_sessions: List[str] = field(default_factory=list)
