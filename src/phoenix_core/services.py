"""First Phoenix Core V2 application-service layer."""

import hashlib
import secrets
from uuid import UUID, uuid4

from phoenix_core.audit.domain import AuditEvent
from phoenix_core.errors import AuthenticationError, AuthorizationError, ConflictError, NotFoundError, ValidationError
from phoenix_core.identity.domain import Identity
from phoenix_core.infrastructure import SQLiteDatabase
from phoenix_core.organisations.domain import Organisation
from phoenix_core.organisations.membership import Membership
from phoenix_core.roles.domain import Role
from phoenix_core.security.passwords import hash_password, verify_password
from phoenix_core.sessions.domain import Session
from phoenix_core.users.domain import User

def _dt(value):
    return value.isoformat()

class CoreFoundationService:
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def initialise(self):
        schema = open(
            __import__("pathlib").Path(__file__).resolve().parents[2] / "migrations" / "001_core_foundation.sql",
            encoding="utf-8",
        ).read()
        self.db.executescript(schema)
        self.db.commit()

    def create_organisation(self, code: str, name: str) -> Organisation:
        org = Organisation.create(code, name)
        try:
            self.db.execute(
                "INSERT INTO organisations(id,code,name,status,created_at) VALUES (?,?,?,?,?)",
                (str(org.id), org.code, org.name, org.status, _dt(org.created_at)),
            )
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            if "UNIQUE" in str(exc).upper():
                raise ConflictError("Organisation code or name already exists.") from exc
            raise
        return org

    def create_user(self, username: str, display_name: str, password: str) -> User:
        identity = Identity.create("HUMAN")
        user = User.create(identity.id, username, display_name, hash_password(password))
        try:
            self.db.execute(
                "INSERT INTO identities(id,identity_type,status,created_at) VALUES (?,?,?,?)",
                (str(identity.id), identity.identity_type, identity.status, _dt(identity.created_at)),
            )
            self.db.execute(
                "INSERT INTO users(id,identity_id,username,display_name,password_hash,status,created_at) VALUES (?,?,?,?,?,?,?)",
                (str(user.id), str(user.identity_id), user.username, user.display_name,
                 user.password_hash, user.status, _dt(user.created_at)),
            )
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            if "UNIQUE" in str(exc).upper():
                raise ConflictError("Username already exists.") from exc
            raise
        return user


    def get_user(self, user_id: UUID) -> User:
        row = self.db.execute(
            "SELECT id,identity_id,username,display_name,password_hash,status,created_at FROM users WHERE id=?",
            (str(user_id),),
        ).fetchone()
        if not row:
            raise NotFoundError("User not found.")
        from datetime import datetime
        return User(
            UUID(row["id"]), UUID(row["identity_id"]), row["username"], row["display_name"],
            row["password_hash"], row["status"], datetime.fromisoformat(row["created_at"]),
        )

    def get_identity(self, identity_id: UUID) -> Identity:
        row = self.db.execute(
            "SELECT id,identity_type,status,created_at FROM identities WHERE id=?",
            (str(identity_id),),
        ).fetchone()
        if not row:
            raise NotFoundError("Identity not found.")
        from datetime import datetime
        return Identity(UUID(row["id"]), row["identity_type"], row["status"], datetime.fromisoformat(row["created_at"]))

    def update_user(self, user_id: UUID, *, username: str | None = None, display_name: str | None = None) -> User:
        current = self.get_user(user_id)
        new_username = current.username if username is None else username.strip()
        new_display_name = current.display_name if display_name is None else display_name.strip()
        if not new_username:
            raise ValidationError("Username is required.")
        if not new_display_name:
            raise ValidationError("Display name is required.")
        try:
            self.db.execute("UPDATE users SET username=?,display_name=? WHERE id=?",
                            (new_username, new_display_name, str(user_id)))
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            if "UNIQUE" in str(exc).upper():
                raise ConflictError("Username already exists.") from exc
            raise
        return self.get_user(user_id)

    def deactivate_user(self, user_id: UUID) -> None:
        self._set_user_status(user_id, "DISABLED")

    def reactivate_user(self, user_id: UUID) -> None:
        self._set_user_status(user_id, "ACTIVE")

    def suspend_user(self, user_id: UUID) -> None:
        self._set_user_status(user_id, "SUSPENDED")

    def _set_user_status(self, user_id: UUID, status: str) -> None:
        current = self.get_user(user_id)
        if current.status == status:
            return
        self.db.execute("UPDATE users SET status=? WHERE id=?", (status, str(user_id)))
        self.db.execute("UPDATE identities SET status=? WHERE id=?", (status, str(current.identity_id)))
        if status != "ACTIVE":
            self.db.execute("UPDATE sessions SET status='REVOKED' WHERE identity_id=? AND status='ACTIVE'", (str(current.identity_id),))
        self.db.commit()

    def add_membership(self, identity_id: UUID, organisation_id: UUID) -> Membership:
        membership = Membership.create(identity_id, organisation_id)
        try:
            if not self.db.execute("SELECT 1 FROM identities WHERE id=?", (str(identity_id),)).fetchone():
                raise NotFoundError("Identity not found.")
            if not self.db.execute("SELECT 1 FROM organisations WHERE id=?", (str(organisation_id),)).fetchone():
                raise NotFoundError("Organisation not found.")
            self.db.execute(
                "INSERT INTO organisation_memberships(id,identity_id,organisation_id,status,created_at) VALUES (?,?,?,?,?)",
                (str(membership.id), str(identity_id), str(organisation_id), membership.status, _dt(membership.created_at)),
            )
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            if isinstance(exc, NotFoundError):
                raise
            if "UNIQUE" in str(exc).upper():
                raise ConflictError("Membership already exists.") from exc
            raise
        return membership

    def create_role(self, organisation_id: UUID, code: str, name: str) -> Role:
        role = Role.create(organisation_id, code, name)
        if not self.db.execute("SELECT 1 FROM organisations WHERE id=?", (str(organisation_id),)).fetchone():
            raise NotFoundError("Organisation not found.")
        try:
            self.db.execute(
                "INSERT INTO roles(id,organisation_id,code,name,scope,status,created_at) VALUES (?,?,?,?,?,?,?)",
                (str(role.id), str(role.organisation_id), role.code, role.name, role.scope, role.status, _dt(role.created_at)),
            )
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            if "UNIQUE" in str(exc).upper():
                raise ConflictError("Role code already exists for this organisation.") from exc
            raise
        return role

    def assign_role(self, membership_id: UUID, role_id: UUID):
        membership = self.db.execute(
            "SELECT organisation_id FROM organisation_memberships WHERE id=? AND status='ACTIVE'",
            (str(membership_id),),
        ).fetchone()
        if not membership:
            raise NotFoundError("Active membership not found.")
        role = self.db.execute(
            "SELECT organisation_id FROM roles WHERE id=? AND status='ACTIVE'",
            (str(role_id),),
        ).fetchone()
        if not role:
            raise NotFoundError("Active role not found.")
        if membership["organisation_id"] != role["organisation_id"]:
            raise AuthorizationError("Role and membership belong to different organisations.")
        assignment_id = str(uuid4())
        try:
            self.db.execute(
                "INSERT INTO role_assignments(id,membership_id,role_id,created_at) VALUES (?,?,?,datetime('now'))",
                (assignment_id, str(membership_id), str(role_id)),
            )
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            if "UNIQUE" in str(exc).upper():
                raise ConflictError("Role is already assigned.") from exc
            raise
        return assignment_id

    def authenticate(self, username: str, password: str, lifetime_minutes: int = 60):
        row = self.db.execute(
            "SELECT identity_id,password_hash,status FROM users WHERE username=?",
            (username.strip(),),
        ).fetchone()
        if not row or row["status"] != "ACTIVE" or not verify_password(password, row["password_hash"]):
            raise AuthenticationError("Invalid credentials.")
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        session = Session.create(UUID(row["identity_id"]), token_hash, lifetime_minutes)
        self.db.execute(
            "INSERT INTO sessions(id,identity_id,token_hash,expires_at,status,created_at) VALUES (?,?,?,?,?,?)",
            (str(session.id), str(session.identity_id), session.token_hash, _dt(session.expires_at),
             session.status, _dt(session.created_at)),
        )
        self.db.commit()
        return session, token

    def revoke_session(self, token: str):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        cur = self.db.execute(
            "UPDATE sessions SET status='REVOKED' WHERE token_hash=? AND status='ACTIVE'",
            (token_hash,),
        )
        self.db.commit()
        return cur.rowcount == 1

    def effective_permissions(self, identity_id: UUID, organisation_id: UUID) -> set[str]:
        rows = self.db.execute(
            """
            SELECT DISTINCT p.code
            FROM organisation_memberships m
            JOIN role_assignments ra ON ra.membership_id = m.id
            JOIN roles r ON r.id = ra.role_id
            JOIN role_permissions rp ON rp.role_id = r.id
            JOIN permissions p ON p.id = rp.permission_id
            WHERE m.identity_id=? AND m.organisation_id=?
              AND m.status='ACTIVE' AND r.status='ACTIVE'
            """,
            (str(identity_id), str(organisation_id)),
        ).fetchall()
        return {row["code"] for row in rows}

    def authorize(self, identity_id: UUID, organisation_id: UUID, permission: str) -> bool:
        return permission in self.effective_permissions(identity_id, organisation_id)

    def record_audit(self, event: AuditEvent):
        self.db.execute(
            """
            INSERT INTO audit_events
            (id,organisation_id,identity_id,action,target_type,target_id,request_id,created_at)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                str(event.id),
                str(event.organisation_id) if event.organisation_id else None,
                str(event.identity_id) if event.identity_id else None,
                event.action,
                event.target_type,
                str(event.target_id) if event.target_id else None,
                event.request_id,
                _dt(event.created_at),
            ),
        )
        self.db.commit()
