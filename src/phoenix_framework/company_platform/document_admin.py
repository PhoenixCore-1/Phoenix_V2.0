"""Controlled Company Platform document administration boundary."""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyDocumentAction(str, Enum):
    """Supported tenant document administration operations."""

    CREATE_CATEGORY = "create_category"
    UPDATE_CATEGORY = "update_category"
    ENABLE_CATEGORY = "enable_category"
    DISABLE_CATEGORY = "disable_category"
    UPDATE_DOCUMENT_METADATA = "update_document_metadata"
    SET_DOCUMENT_VISIBILITY = "set_document_visibility"
    REQUEST_UPLOAD = "request_upload"
    REQUEST_DOWNLOAD = "request_download"
    REQUEST_DELETE = "request_delete"
    REQUEST_VERSION = "request_version"


@dataclass(frozen=True)
class CompanyDocumentAdministrationRequest:
    """Immutable tenant-bound document operation."""

    action: CompanyDocumentAction
    organisation_id: UUID
    document_id: str | None = None
    category_id: str | None = None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyDocumentAction,
        document_id: str | None = None,
        category_id: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyDocumentAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            document_id=document_id,
            category_id=category_id,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Document request does not match request organisation")

        category_actions = {
            CompanyDocumentAction.UPDATE_CATEGORY,
            CompanyDocumentAction.ENABLE_CATEGORY,
            CompanyDocumentAction.DISABLE_CATEGORY,
        }
        document_actions = {
            CompanyDocumentAction.UPDATE_DOCUMENT_METADATA,
            CompanyDocumentAction.SET_DOCUMENT_VISIBILITY,
            CompanyDocumentAction.REQUEST_DOWNLOAD,
            CompanyDocumentAction.REQUEST_DELETE,
            CompanyDocumentAction.REQUEST_VERSION,
        }

        if self.action in category_actions and not self.category_id:
            raise ValueError("This document operation requires a category_id")
        if self.action in document_actions and not self.document_id:
            raise ValueError("This document operation requires a document_id")
        if self.action == CompanyDocumentAction.CREATE_CATEGORY and not self.parameters:
            raise ValueError("Creating a document category requires parameters")
        if self.action == CompanyDocumentAction.UPDATE_CATEGORY and not self.parameters:
            raise ValueError("Updating a document category requires parameters")
        if self.action == CompanyDocumentAction.UPDATE_DOCUMENT_METADATA and not self.parameters:
            raise ValueError("Updating document metadata requires parameters")
        if self.action == CompanyDocumentAction.SET_DOCUMENT_VISIBILITY and "scope" not in {k for k, _ in self.parameters}:
            raise ValueError("Document visibility requires a scope parameter")
        if self.action == CompanyDocumentAction.REQUEST_UPLOAD and not self.parameters:
            raise ValueError("Document upload requires upload parameters")
        if self.action == CompanyDocumentAction.REQUEST_VERSION and not self.parameters:
            raise ValueError("Document version request requires version parameters")


@dataclass(frozen=True)
class CompanyDocumentAdministrationResult:
    """Immutable result envelope returned by the authoritative executor."""

    action: CompanyDocumentAction
    organisation_id: UUID
    document_id: str | None
    category_id: str | None
    success: bool
    message: str = ""


class CompanyDocumentAdministrationExecutor(Protocol):
    """Authoritative Core/document application boundary."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyDocumentAdministrationRequest,
    ) -> CompanyDocumentAdministrationResult: ...


class CompanyDocumentAdministrationService:
    """Framework facade; validates and delegates document operations."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyDocumentAction,
        document_id: str | None = None,
        category_id: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyDocumentAdministrationRequest:
        return CompanyDocumentAdministrationRequest.create(
            context,
            action=action,
            document_id=document_id,
            category_id=category_id,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyDocumentAdministrationRequest,
        executor: CompanyDocumentAdministrationExecutor,
    ) -> CompanyDocumentAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
