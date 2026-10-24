"""Opaque cursor pagination on UUID v7 primary keys (Book 3 §26.1: ``?cursor=…&limit=…``).

UUID v7 is time-ordered, so ``id > cursor ORDER BY id`` gives stable, index-only keyset pages.
"""

from __future__ import annotations

import base64
import uuid
from typing import Any

from rest_framework.pagination import BasePagination
from rest_framework.request import Request
from rest_framework.response import Response

MAX_LIMIT = 200


def encode(u: uuid.UUID) -> str:
    return base64.urlsafe_b64encode(u.bytes).decode().rstrip("=")


def decode(s: str) -> uuid.UUID:
    return uuid.UUID(bytes=base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)))


class UUID7CursorPagination(BasePagination):
    page_size = 50
    ordering_field = "id"

    def paginate_queryset(self, queryset: Any, request: Request, view: Any = None) -> list[Any]:
        try:
            self.limit = min(int(request.query_params.get("limit", self.page_size)), MAX_LIMIT)
        except ValueError:
            self.limit = self.page_size
        cursor = request.query_params.get("cursor")
        qs = queryset.order_by(self.ordering_field)
        if cursor:
            try:
                qs = qs.filter(**{f"{self.ordering_field}__gt": decode(cursor)})
            except (ValueError, TypeError):
                qs = qs.none()
        rows = list(qs[: self.limit + 1])
        self.has_more = len(rows) > self.limit
        self.page = rows[: self.limit]
        return self.page

    def get_paginated_response(self, data: Any) -> Response:
        nxt = encode(getattr(self.page[-1], self.ordering_field)) if self.has_more and self.page else None
        return Response({"data": data, "page": {"next_cursor": nxt, "limit": self.limit}})

    def get_paginated_response_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        return {"type": "object", "properties": {"data": schema, "page": {"type": "object"}}}
