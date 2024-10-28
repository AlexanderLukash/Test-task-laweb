from abc import ABC
from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime


@dataclass
class BaseEntity(ABC):
    registration_date: str = field(
        default_factory=lambda: datetime.now().isoformat(),
        kw_only=True,
    )
