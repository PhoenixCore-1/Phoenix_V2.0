"""Permission domain model."""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from phoenix_core.errors import ValidationError

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

@dataclass(frozen=True)
class Permission:
    id: UUID
    code: str
    name: str
    created_at: datetime

    @classmethod
    def create(cls, code: str, name: str) -> "Permission":
        code = code.strip().lower()
        name = name.strip()
        if not code or not name:
            raise ValidationError("Permission code and name are required.")
        return cls(uuid4(), code, name, utcnow())
