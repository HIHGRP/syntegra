"""Custom Django fields for the CEDA canonical types (CEDA §5.2)."""

from __future__ import annotations

import datetime as dt
import ipaddress
import uuid
from typing import Any

from django.db import models
from django.utils import timezone


def utcnow() -> dt.datetime:
    return timezone.now()


class UUID7Field(models.Field):  # type: ignore[type-arg]
    """``BINARY(16)`` holding a UUID (v7 for keys) — UUID_TO_BIN without byte swap.

    Python side always ``uuid.UUID``; accepts ``str``, ``bytes`` or ``UUID`` on assignment.
    """

    description = "UUID stored as BINARY(16)"

    def db_type(self, connection: Any) -> str:
        return "binary(16)"

    def rel_db_type(self, connection: Any) -> str:
        return "binary(16)"

    def get_internal_type(self) -> str:
        return "UUID7Field"

    @staticmethod
    def coerce(value: Any) -> uuid.UUID | None:
        if value is None or value == "":
            return None
        if isinstance(value, uuid.UUID):
            return value
        if isinstance(value, (bytes, bytearray, memoryview)):
            b = bytes(value)
            return uuid.UUID(bytes=b) if len(b) == 16 else uuid.UUID(b.decode())
        return uuid.UUID(str(value))

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> uuid.UUID | None:
        return self.coerce(value)

    def to_python(self, value: Any) -> uuid.UUID | None:
        return self.coerce(value)

    def get_prep_value(self, value: Any) -> Any:
        value = super().get_prep_value(value)
        if hasattr(value, "resolve_expression"):
            return value
        u = self.coerce(value)
        return u.bytes if u is not None else None

    def value_to_string(self, obj: Any) -> str:
        v = self.value_from_object(obj)
        return "" if v is None else str(v)


class PackedIPField(models.Field):  # type: ignore[type-arg]
    """``VARBINARY(16)`` holding an IPv4/IPv6 address (INET6_ATON format)."""

    def db_type(self, connection: Any) -> str:
        return "varbinary(16)"

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> str | None:
        if value is None:
            return None
        return str(ipaddress.ip_address(bytes(value)))

    def to_python(self, value: Any) -> str | None:
        if value is None or isinstance(value, str):
            return value
        return str(ipaddress.ip_address(bytes(value)))

    def get_prep_value(self, value: Any) -> Any:
        if value is None or value == "":
            return None
        return ipaddress.ip_address(value).packed


class PointField(models.Field):  # type: ignore[type-arg]
    """``POINT SRID 4326`` without GDAL: Python value is ``(longitude, latitude)``.

    Writes ``ST_GeomFromText('POINT(lon lat)', 4326, 'axis-order=long-lat')``; reads with
    ``ST_AsText(col, 'axis-order=long-lat')``.
    """

    def db_type(self, connection: Any) -> str:
        return "point srid 4326"

    def get_placeholder(self, value: Any, compiler: Any, connection: Any) -> str:
        return "ST_GeomFromText(%s, 4326, 'axis-order=long-lat')" if value is not None else "%s"

    def select_format(self, compiler: Any, sql: str, params: Any) -> tuple[str, Any]:
        return f"ST_AsText({sql}, 'axis-order=long-lat')", params

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        lon, lat = value
        return f"POINT({float(lon)} {float(lat)})"

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> tuple[float, float] | None:
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode()
        inner = value[value.index("(") + 1: value.rindex(")")]
        lon, lat = inner.split()
        return float(lon), float(lat)


def generated(field: models.Field) -> models.Field:  # type: ignore[type-arg]
    """Mark a field as a database-generated (STORED) column: excluded from INSERT/UPDATE, read-only."""
    field.generated = True  # type: ignore[attr-defined]
    return field
