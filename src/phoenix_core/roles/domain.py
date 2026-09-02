"""Role domain model."""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from phoenix_core.errors import ValidationError

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

@dataclass(frozen=True)
class Role:
    id: UUID
    organisation_id: UUID
    code: str
    name: str
    scope: str
    status: str
    created_at: datetime

    @classmethod
    def create(cls, organisation_id: UUID, code: str, name: str, scope: str = "ORGANISATION") -> "Role":
        code = code.strip().upper()
        name = name.strip()
        if not code or not name:
            raise ValidationError("Role code and name are required.")
        if scope not in {"SYSTEM", "ORGANISATION"}:
            raise ValidationError("Invalid role scope.")
        return cls(uuid4(), organisation_id, code, name, scope, "ACTIVE", utcnow())
