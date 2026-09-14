"""Phoenix Connect HTTP transport endpoints.

The router resolves authenticated Core context first, then delegates all
communication authority to CommunicationsService. Browser-supplied identity
and organisation values are never trusted as authoritative identity.
"""

from uuid import UUID

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from phoenix_core.communications.service import CommunicationsService
from phoenix_core.http_api.authorization import resolve_request_context

router = APIRouter(prefix="/api/v1/connect", tags=["Phoenix Connect"])


def _service(request: Request) -> CommunicationsService:
    return request.app.state.communications_service


class ChannelCreatePayload(BaseModel):
    channel_type: str
    name: str
    visibility: str = "PRIVATE"


class DirectChannelPayload(BaseModel):
    target_identity_id: UUID


class GroupChannelPayload(BaseModel):
    name: str
    member_identity_ids: list[UUID] = Field(default_factory=list)
    visibility: str = "PRIVATE"


class MemberPayload(BaseModel):
    identity_id: UUID


class MessagePayload(BaseModel):
    content: str
    parent_message_id: UUID | None = None
    context_type: str | None = None
    context_id: str | None = None


class ReactionPayload(BaseModel):
    reaction: str


class ReadPayload(BaseModel):
    message_id: UUID | None = None


class PresencePayload(BaseModel):
    status: str


@router.get("/channels")
async def list_channels(request: Request):
    context = await resolve_request_context(request)
    result = _service(request).list_channels(context.identity_id, context.organisation_id)
    return {"data": {"items": result}, "request_id": context.request_id}


@router.post("/channels")
async def create_channel(request: Request, payload: ChannelCreatePayload):
    context = await resolve_request_context(request)
    result = _service(request).create_channel(context.identity_id, context.organisation_id, payload.channel_type, payload.name, payload.visibility)
    return {"data": result, "request_id": context.request_id}


@router.get("/channels/{channel_id}")
async def get_channel(request: Request, channel_id: UUID):
    context = await resolve_request_context(request)
    result = _service(request).get_channel(channel_id, context.identity_id)
    return {"data": result, "request_id": context.request_id}


@router.post("/channels/direct")
async def create_direct_channel(request: Request, payload: DirectChannelPayload):
    context = await resolve_request_context(request)
    result = _service(request).create_direct_channel(context.identity_id, context.organisation_id, payload.target_identity_id)
    return {"data": result, "request_id": context.request_id}


@router.post("/channels/group")
async def create_group_channel(request: Request, payload: GroupChannelPayload):
    context = await resolve_request_context(request)
    result = _service(request).create_group_channel(context.identity_id, context.organisation_id, payload.name, payload.member_identity_ids, payload.visibility)
    return {"data": result, "request_id": context.request_id}


@router.post("/channels/{channel_id}/members")
async def add_member(request: Request, channel_id: UUID, payload: MemberPayload):
    context = await resolve_request_context(request)
    _service(request).add_member(channel_id, context.identity_id, payload.identity_id)
    return {"data": {"added": True, "channel_id": str(channel_id), "identity_id": str(payload.identity_id)}, "request_id": context.request_id}


@router.post("/channels/{channel_id}/messages")
async def send_message(request: Request, channel_id: UUID, payload: MessagePayload):
    context = await resolve_request_context(request)
    result = _service(request).send_message(channel_id, context.identity_id, payload.content, payload.parent_message_id, payload.context_type, payload.context_id)
    return {"data": result, "request_id": context.request_id}


@router.get("/channels/{channel_id}/messages")
async def list_messages(request: Request, channel_id: UUID, limit: int = 50, before_id: UUID | None = None):
    context = await resolve_request_context(request)
    result = _service(request).list_messages(channel_id, context.identity_id, limit, before_id)
    return {"data": {"items": result, "limit": limit, "before_id": str(before_id) if before_id else None}, "request_id": context.request_id}


@router.post("/messages/{message_id}/reactions")
async def add_reaction(request: Request, message_id: UUID, payload: ReactionPayload):
    context = await resolve_request_context(request)
    _service(request).add_reaction(message_id, context.identity_id, payload.reaction)
    return {"data": {"added": True, "message_id": str(message_id), "reaction": payload.reaction}, "request_id": context.request_id}


@router.post("/channels/{channel_id}/read")
async def mark_read(request: Request, channel_id: UUID, payload: ReadPayload):
    context = await resolve_request_context(request)
    _service(request).mark_read(channel_id, context.identity_id, payload.message_id)
    return {"data": {"marked_read": True, "channel_id": str(channel_id), "message_id": str(payload.message_id) if payload.message_id else None}, "request_id": context.request_id}


@router.post("/presence")
async def set_presence(request: Request, payload: PresencePayload):
    context = await resolve_request_context(request)
    _service(request).set_presence(context.identity_id, context.organisation_id, payload.status)
    return {"data": {"status": payload.status}, "request_id": context.request_id}


@router.get("/presence/{identity_id}")
async def get_presence(request: Request, identity_id: UUID):
    context = await resolve_request_context(request)
    result = _service(request).get_presence(context.identity_id, identity_id, context.organisation_id)
    return {"data": result, "request_id": context.request_id}
