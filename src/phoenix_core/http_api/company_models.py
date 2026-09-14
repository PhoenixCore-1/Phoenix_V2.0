"""Typed request models for Company Platform HTTP mutations."""

from pydantic import BaseModel


class CompanyUserCreatePayload(BaseModel):
    username: str
    display_name: str
    password: str


class CompanyUserUpdatePayload(BaseModel):
    username: str | None = None
    display_name: str | None = None


class CompanyRoleCreatePayload(BaseModel):
    code: str
    name: str


class CompanyRoleUpdatePayload(BaseModel):
    code: str | None = None
    name: str | None = None
