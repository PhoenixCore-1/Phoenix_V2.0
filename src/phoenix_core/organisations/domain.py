"""Organisation/tenant domain model."""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from phoenix_core.errors import ValidationError

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

@dataclass(frozen=True)
class Organisation:
    id: UUID
    code: str
    name: str
    status: str
    created_at: datetime

    @classmethod
    def create(cls, code: str, name: str) -> "Organisation":
        code = code.strip().upper()
        name = name.strip()
        if not code:
            raise ValidationError("Organisation code is required.")
        if not name:
            raise ValidationError("Organisation name is required.")
        return cls(uuid4(), code, name, "ACTIVE", utcnow())
