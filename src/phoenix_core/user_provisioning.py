"""Atomic Core user and organisation membership provisioning."""

from phoenix_core.errors import AuthorizationError, ConflictError, NotFoundError
from phoenix_core.identity.domain import Identity
from phoenix_core.organisations.membership import Membership
from phoenix_core.security.passwords import hash_password
from phoenix_core.users.domain import User


def _dt(value):
    return value.isoformat()


class CoreUserProvisioningService:
    """Create a human identity, user and tenant membership in one transaction."""

    def __init__(self, db):
        self.db = db

    def provision(self, username: str, display_name: str, password: str, organisation_id):
        identity = Identity.create("HUMAN")
        user = User.create(identity.id, username, display_name, hash_password(password))
        membership = Membership.create(identity.id, organisation_id)
        try:
            organisation = self.db.execute(
                "SELECT status FROM organisations WHERE id=?", (str(organisation_id),)
            ).fetchone()
            if not organisation:
                raise NotFoundError("Organisation not found.")
            if organisation["status"] != "ACTIVE":
                raise AuthorizationError("Membership can only be added to an active organisation.")

            self.db.execute(
                "INSERT INTO identities(id,identity_type,status,created_at) VALUES (?,?,?,?)",
                (str(identity.id), identity.identity_type, identity.status, _dt(identity.created_at)),
            )
            self.db.execute(
                "INSERT INTO users(id,identity_id,username,display_name,password_hash,status,created_at) VALUES (?,?,?,?,?,?,?)",
                (str(user.id), str(user.identity_id), user.username, user.display_name,
                 user.password_hash, user.status, _dt(user.created_at)),
            )
            self.db.execute(
                "INSERT INTO organisation_memberships(id,identity_id,organisation_id,status,created_at) VALUES (?,?,?,?,?)",
                (str(membership.id), str(membership.identity_id), str(membership.organisation_id),
                 membership.status, _dt(membership.created_at)),
            )
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            if isinstance(exc, (NotFoundError, AuthorizationError)):
                raise
            if "UNIQUE" in str(exc).upper():
                raise ConflictError("Username or membership already exists.") from exc
            raise
        return user, membership
