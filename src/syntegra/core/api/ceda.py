"""Generic read-only CEDA API: ``GET /api/v1/ceda/{entity}`` and ``/{entity}/{id}`` for every entity.

Permission ``ceda:view`` plus ``{entity}:view`` (or ``{entity}:*``) is required; rows are restricted to the
caller's tenant (manager) and, for owned-scope entities, to the grant subtree; columns above the caller's
clearance and every secret/hash column are trimmed. Special-category and vault entities are never served
here — they have purpose-bound endpoints in their modules.
"""

from __future__ import annotations

import uuid
from typing import Any

from django.apps import apps
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core import authz, context
from syntegra.core.api.pagination import UUID7CursorPagination
from syntegra.core.api.views import row
from syntegra.core.errors import Forbidden, NotFound

_BLOCKED_ZONES = {"vault", "dw"}


def _model(entity: str) -> Any:
    for m in apps.get_models():
        if getattr(m, "ceda_entity", None) == entity:
            zones = set(getattr(m, "ceda_zones", ()))
            if zones & _BLOCKED_ZONES or len(zones) > 1 or getattr(m, "ceda_class", "") == "special":
                raise Forbidden(f"{entity} is not available through the generic API.", code="CEDA-BLOCKED")
            return m
    raise NotFound("entity", entity)


def _queryset(model: Any) -> Any:
    ctx = context.require()
    authz.require("ceda:view", ctx)
    entity = model.ceda_entity
    if not (ctx.has(f"{entity}:view") or ctx.has(f"{entity}:list")):
        # module-level resources (institution, learner …) map 1:1; others need an explicit grant
        raise Forbidden(f"Missing permission {entity}:view.", code="AUTH-PERMISSION")
    qs = model.objects.all()
    if "scope_node_id" in model.ceda_fields and ctx.scope_ids is not None and not ctx.is_system:
        qs = qs.filter(scope_node_id__in=list(ctx.scope_ids))
    elif model.ceda_scope not in ("none", "") and ctx.scope_ids is not None and not ctx.is_system:
        raise Forbidden(f"{entity} has derived scope; use its module endpoint.", code="CEDA-DERIVED-SCOPE")
    if getattr(model, "ceda_class", "internal") in ("restricted",):
        authz.require_purpose("restricted", ctx)
    return qs


class EntityList(APIView):
    def get(self, request: Request, entity: str) -> Response:
        model = _model(entity)
        qs = _queryset(model)
        for k, v in request.query_params.items():
            if k in model.ceda_fields and k not in ("cursor", "limit"):
                qs = qs.filter(**{model._meta.get_field(k).attname if k.endswith("_id") else k: v})
        if "id" not in model.ceda_fields:
            raise NotFound("entity without an id key", entity)
        pager = UUID7CursorPagination()
        page = pager.paginate_queryset(qs, request, self)
        return pager.get_paginated_response([row(o) for o in page])


class EntityDetail(APIView):
    def get(self, request: Request, entity: str, pk: uuid.UUID) -> Response:
        model = _model(entity)
        obj = _queryset(model).filter(pk=pk).first()
        if obj is None:
            raise NotFound(entity, pk)
        resp = Response(row(obj))
        if hasattr(obj, "row_version"):
            resp["ETag"] = f'W/"{obj.row_version}"'
        return resp


class Catalogue(APIView):
    def get(self, request: Request) -> Response:
        from syntegra.core import catalog

        authz.require("ceda:view")
        c = catalog.catalog()
        return Response(
            {
                "ceda": c["ceda"],
                "zones": c["zones"],
                "events": sorted(c["events"]),
                "metrics": [{"id": m["id"], "name": m["name"], "group": m["group"]} for m in c["metrics"]],
            }
        )
