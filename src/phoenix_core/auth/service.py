import hashlib
import secrets
from uuid import UUID

from phoenix_core.errors import AuthenticationError, ValidationError
from phoenix_core.security.passwords import hash_password, verify_password
from phoenix_core.sessions.domain import Session

class AuthenticationService:
    def __init__(self, db):
        self.db = db

    def authenticate(self, username: str, password: str, organisation_id: UUID | None = None):
        username = (username or "").strip()
        if not username or not password:
            raise ValidationError("Username and password are required.")

        row = self.db.execute(
            "SELECT id, identity_id, password_hash, status FROM users WHERE username=?",
            (username,),
        ).fetchone()

        if not row or row["status"] != "ACTIVE" or not verify_password(password, row["password_hash"]):
            raise AuthenticationError("Invalid credentials.")

        if organisation_id is not None:
            membership = self.db.execute(
                "SELECT id, status FROM organisation_memberships "
                "WHERE identity_id=? AND organisation_id=?",
                (row["identity_id"], str(organisation_id)),
            ).fetchone()
            organisation = self.db.execute(
                "SELECT status FROM organisations WHERE id=?",
                (str(organisation_id),),
            ).fetchone()
            if (not membership or membership["status"] != "ACTIVE"
                    or not organisation or organisation["status"] != "ACTIVE"):
                raise AuthenticationError("User is not an active member of this organisation.")

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        session = Session.create(UUID(row["identity_id"]), token_hash)

        self.db.execute(
            "INSERT INTO sessions(id,identity_id,token_hash,expires_at,status,created_at) "
            "VALUES (?,?,?,?,?,?)",
            (
                str(session.id),
                str(session.identity_id),
                session.token_hash,
                session.expires_at.isoformat(),
                session.status,
                session.created_at.isoformat(),
            ),
        )
        self.db.commit()
        return session, token

    def resolve_active_organisation(self, identity_id: UUID) -> UUID:
        """Resolve the user's active organisation context.

        A user must have exactly one active organisation when no explicit
        organisation has been selected. Ambiguous membership is rejected
        rather than silently selecting an organisation.
        """
        rows = self.db.execute(
            """
            SELECT om.organisation_id
            FROM organisation_memberships om
            JOIN organisations o
                ON o.id = om.organisation_id
            WHERE om.identity_id=?
              AND om.status='ACTIVE'
              AND o.status='ACTIVE'
            ORDER BY om.organisation_id
            """,
            (str(identity_id),),
        ).fetchall()

        if not rows:
            raise AuthenticationError(
                "User has no active organisation membership."
            )

        if len(rows) > 1:
            raise AuthenticationError(
                "Multiple active organisations require organisation selection."
            )

        return UUID(str(rows[0]["organisation_id"]))

    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> None:
        if not new_password or len(new_password) < 12:
            raise ValidationError("Password must be at least 12 characters.")

        row = self.db.execute(
            "SELECT password_hash FROM users WHERE id=? AND status='ACTIVE'",
            (str(user_id),),
        ).fetchone()
        if not row or not verify_password(current_password, row["password_hash"]):
            raise AuthenticationError("Current password is incorrect.")

        self.db.execute(
            "UPDATE users SET password_hash=? WHERE id=?",
            (hash_password(new_password), str(user_id)),
        )
        self.db.commit()
