"""Phoenix Core background-job application service."""

import json
from datetime import datetime
from uuid import UUID

from phoenix_core.errors import ConflictError, NotFoundError, ValidationError
from phoenix_core.jobs.contracts import JobRequest
from phoenix_core.jobs.domain import JOB_STATUSES, Job
from phoenix_core.infrastructure import SQLiteDatabase


def _dt(value):
    return value.isoformat() if value is not None else None


class JobService:
    """Authoritative Core service for job creation and queue persistence."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def enqueue(self, request: JobRequest, *, max_attempts: int = 3) -> Job:
        if not request.request_id or not request.request_id.strip():
            raise ValidationError("request_id is required.")

        if not request.job_type or not request.job_type.strip():
            raise ValidationError("job_type is required.")

        if max_attempts < 1:
            raise ValidationError("max_attempts must be at least 1.")

        if request.idempotency_key is not None:
            if not request.idempotency_key.strip():
                raise ValidationError("idempotency_key cannot be empty.")

            if request.organisation_id is None:
                raise ValidationError(
                    "organisation_id is required when using idempotency_key."
                )

            existing = self.db.execute(
                """
                SELECT id
                FROM jobs
                WHERE organisation_id=?
                  AND idempotency_key=?
                """,
                (
                    str(request.organisation_id),
                    request.idempotency_key,
                ),
            ).fetchone()

            if existing:
                return self.get(UUID(existing["id"]))

        job = Job.create(
            request.request_id,
            request.job_type,
            organisation_id=request.organisation_id,
            identity_id=request.identity_id,
            payload=request.payload,
            scheduled_at=request.scheduled_at,
            idempotency_key=request.idempotency_key,
            max_attempts=max_attempts,
        )

        payload = (
            json.dumps(request.payload)
            if request.payload is not None
            else None
        )

        try:
            self.db.execute(
                """
                INSERT INTO jobs(
                    id,
                    request_id,
                    job_type,
                    organisation_id,
                    identity_id,
                    payload,
                    status,
                    scheduled_at,
                    created_at,
                    attempt_count,
                    max_attempts,
                    idempotency_key
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    str(job.id),
                    job.request_id,
                    job.job_type,
                    (
                        str(job.organisation_id)
                        if job.organisation_id
                        else None
                    ),
                    (
                        str(job.identity_id)
                        if job.identity_id
                        else None
                    ),
                    payload,
                    job.status,
                    _dt(job.scheduled_at),
                    _dt(job.created_at),
                    job.attempt_count,
                    job.max_attempts,
                    job.idempotency_key,
                ),
            )
            self.db.commit()
        except Exception as exc:
            self.db.rollback()

            if "UNIQUE" in str(exc).upper():
                raise ConflictError("Job already exists.") from exc

            raise

        return job

    def get(self, job_id: UUID) -> Job:
        row = self.db.execute(
            """
            SELECT
                id,
                request_id,
                job_type,
                organisation_id,
                identity_id,
                payload,
                status,
                scheduled_at,
                created_at,
                started_at,
                completed_at,
                failed_at,
                attempt_count,
                max_attempts,
                idempotency_key,
                error_code,
                error_message
            FROM jobs
            WHERE id=?
            """,
            (str(job_id),),
        ).fetchone()

        if not row:
            raise NotFoundError("Job not found.")

        return self._from_row(row)

    def list(
        self,
        *,
        organisation_id: UUID | None = None,
        status: str | None = None,
        job_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Job]:
        if limit < 1 or limit > 500:
            raise ValidationError("limit must be between 1 and 500.")

        if offset < 0:
            raise ValidationError("offset must be zero or greater.")

        if status is not None and status not in JOB_STATUSES:
            raise ValidationError("Invalid job status.")

        clauses = []
        params = []

        if organisation_id is not None:
            clauses.append("organisation_id=?")
            params.append(str(organisation_id))

        if status is not None:
            clauses.append("status=?")
            params.append(status)

        if job_type is not None:
            clauses.append("job_type=?")
            params.append(job_type)

        sql = """
            SELECT
                id,
                request_id,
                job_type,
                organisation_id,
                identity_id,
                payload,
                status,
                scheduled_at,
                created_at,
                started_at,
                completed_at,
                failed_at,
                attempt_count,
                max_attempts,
                idempotency_key,
                error_code,
                error_message
            FROM jobs
        """

        if clauses:
            sql += " WHERE " + " AND ".join(clauses)

        sql += " ORDER BY created_at, id LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = self.db.execute(sql, params).fetchall()

        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row) -> Job:
        payload = (
            json.loads(row["payload"])
            if row["payload"] is not None
            else None
        )

        return Job(
            id=UUID(row["id"]),
            request_id=row["request_id"],
            job_type=row["job_type"],
            organisation_id=(
                UUID(row["organisation_id"])
                if row["organisation_id"]
                else None
            ),
            identity_id=(
                UUID(row["identity_id"])
                if row["identity_id"]
                else None
            ),
            payload=payload,
            status=row["status"],
            scheduled_at=(
                datetime.fromisoformat(row["scheduled_at"])
                if row["scheduled_at"]
                else None
            ),
            created_at=datetime.fromisoformat(row["created_at"]),
            started_at=(
                datetime.fromisoformat(row["started_at"])
                if row["started_at"]
                else None
            ),
            completed_at=(
                datetime.fromisoformat(row["completed_at"])
                if row["completed_at"]
                else None
            ),
            failed_at=(
                datetime.fromisoformat(row["failed_at"])
                if row["failed_at"]
                else None
            ),
            attempt_count=row["attempt_count"],
            max_attempts=row["max_attempts"],
            idempotency_key=row["idempotency_key"],
            error_code=row["error_code"],
            error_message=row["error_message"],
        )
