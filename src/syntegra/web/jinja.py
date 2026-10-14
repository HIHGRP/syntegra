"""Jinja2 environment for server-rendered pages (MFS §14 design system)."""

from __future__ import annotations

from typing import Any

from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment, StrictUndefined


def _date(value: Any, fmt: str = "%d %b %Y") -> str:
    return value.strftime(fmt) if value else "—"


def environment(**options: Any) -> Environment:
    options.setdefault("undefined", StrictUndefined)
    env = Environment(**options)  # noqa: S701 — autoescape is enabled in settings.TEMPLATES
    env.globals.update({"static": static, "url": reverse})
    env.filters["date"] = _date
    return env
