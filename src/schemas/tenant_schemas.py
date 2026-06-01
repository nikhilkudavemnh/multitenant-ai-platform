from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, field_validator


def _parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError("Invalid format. Use YYYY-MM-DD HH:MM:SS")


class CreateTenantRequest(BaseModel):
    name: str
    short_name: str
    plan: str
    expiry_date: datetime

    @field_validator("expiry_date", mode="before")
    @classmethod
    def validate_expiry_date(cls, value):
        return _parse_datetime(value)


class UpdateTenantRequest(BaseModel):
    id: int
    name: str
    short_name: str
    plan: str
    expiry_date: datetime

    @field_validator("expiry_date", mode="before")
    @classmethod
    def validate_expiry_date(cls, value):
        return _parse_datetime(value)


class CreateTenantResponse(BaseModel):
    name: str
    shortName: str
    plan: str
    expiryDate: str


class UpdateTenantResponse(BaseModel):
    id: int
    name: str
    short_name: str
    plan: str


class DeleteTenantRequest(BaseModel):
    id: int
    short_name: str


class ListTenantRequest(BaseModel):
    enable: Optional[bool] = True
    orderBy: Literal["asc", "desc"] = "desc"
