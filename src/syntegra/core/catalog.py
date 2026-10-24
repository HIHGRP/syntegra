"""Runtime access to the CEDA catalogue (events, metrics, enums, code lists, retention) generated from ceda/model."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_PATH = Path(__file__).resolve().parent / "catalog" / "ceda_catalog.json"


@lru_cache(maxsize=1)
def catalog() -> dict[str, Any]:
    return json.loads(_PATH.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def event(name: str) -> dict[str, Any]:
    try:
        return catalog()["events"][name]  # type: ignore[no-any-return]
    except KeyError as exc:
        raise KeyError(f"event {name} is not in the CEDA event catalogue") from exc


def metric(metric_id: str) -> dict[str, Any]:
    for m in catalog()["metrics"]:
        if m["id"] == metric_id:
            return m  # type: ignore[no-any-return]
    raise KeyError(metric_id)


def enum_values(name: str) -> list[str]:
    return list(catalog()["enums"][name])


def code_list(name: str) -> list[str]:
    return list(catalog()["code_lists"][name])


def ceda_version() -> str:
    return str(catalog()["ceda"]["version"])
