from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.document_admin import (
    CompanyDocumentAction,
    CompanyDocumentAdministrationRequest,
    CompanyDocumentAdministrationResult,
    CompanyDocumentAdministrationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyDocumentAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            document_id=request.document_id,
            category_id=request.category_id,
            success=True,
        )


def make_context():
    return CompanyPlatformContext.from_core(
        RequestContext(request_id=str(uuid4()), identity_id=uuid4(), organisation_id=uuid4())
    )


def test_request_is_tenant_bound_and_immutable():
    ctx = make_context()
    request = CompanyDocumentAdministrationService.build_request(
        ctx, action=CompanyDocumentAction.CREATE_CATEGORY,
        parameters={"name": "Contracts"},
    )
    assert request.organisation_id == ctx.organisation_id
    with pytest.raises(FrozenInstanceError):
        request.document_id = "changed"


def test_category_and_document_targets_are_required():
    ctx = make_context()
    request = CompanyDocumentAdministrationRequest.create(
        ctx, action=CompanyDocumentAction.UPDATE_CATEGORY,
        parameters={"name": "Updated"},
    )
    with pytest.raises(ValueError, match="category_id"):
        request.validate_for(ctx)

    request = CompanyDocumentAdministrationRequest.create(
        ctx, action=CompanyDocumentAction.REQUEST_DOWNLOAD
    )
    with pytest.raises(ValueError, match="document_id"):
        request.validate_for(ctx)


def test_required_parameters_are_validated():
    ctx = make_context()
    cases = (
        CompanyDocumentAction.CREATE_CATEGORY,
        CompanyDocumentAction.UPDATE_CATEGORY,
        CompanyDocumentAction.UPDATE_DOCUMENT_METADATA,
        CompanyDocumentAction.REQUEST_UPLOAD,
        CompanyDocumentAction.REQUEST_VERSION,
    )
    for action in cases:
        request = CompanyDocumentAdministrationRequest.create(
            ctx, action=action,
            category_id="contracts" if action == CompanyDocumentAction.UPDATE_CATEGORY else None,
            document_id="doc-1" if action in {CompanyDocumentAction.UPDATE_DOCUMENT_METADATA, CompanyDocumentAction.REQUEST_VERSION} else None,
        )
        with pytest.raises(ValueError):
            request.validate_for(ctx)


def test_visibility_requires_scope():
    ctx = make_context()
    request = CompanyDocumentAdministrationRequest.create(
        ctx, action=CompanyDocumentAction.SET_DOCUMENT_VISIBILITY,
        document_id="doc-1",
    )
    with pytest.raises(ValueError, match="scope"):
        request.validate_for(ctx)


def test_cross_tenant_request_is_rejected():
    ctx = make_context()
    request = CompanyDocumentAdministrationRequest(
        action=CompanyDocumentAction.REQUEST_DOWNLOAD,
        organisation_id=uuid4(),
        document_id="doc-1",
    )
    with pytest.raises(PermissionError):
        CompanyDocumentAdministrationService.execute(ctx, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    ctx = make_context()
    executor = RecordingExecutor()
    request = CompanyDocumentAdministrationService.build_request(
        ctx, action=CompanyDocumentAction.REQUEST_DOWNLOAD, document_id="doc-1"
    )
    result = CompanyDocumentAdministrationService.execute(ctx, request, executor)
    assert result.success
    assert executor.requests == [(ctx, request)]


def test_unauthenticated_context_cannot_build_request():
    ctx = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyDocumentAdministrationService.build_request(
            ctx, action=CompanyDocumentAction.REQUEST_DOWNLOAD, document_id="doc-1"
        )
