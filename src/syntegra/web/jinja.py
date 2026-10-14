"""Jinja2 environment for server-rendered pages (MFS §14 design system)."""

from __future__ import annotations

from typing import Any

from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment, StrictUndefined


def _date(value: Any, fmt: str = "%d %b %Y") -> str:
    return value.strftime(fmt) if value else "—"


def _naira(minor: Any) -> str:
    return "—" if minor is None else f"₦{int(minor) / 100:,.2f}"


def _naira_short(minor: Any) -> str:
    """₦ in thousands, millions or billions for headline tiles (tables keep the exact amount)."""
    if minor is None:
        return "—"
    n = int(minor) / 100
    for size, suffix in ((1e9, "bn"), (1e6, "m"), (1e3, "k")):
        if abs(n) >= size:
            return f"₦{n / size:,.1f}{suffix}"
    return f"₦{n:,.0f}"


def _human(code: Any) -> str:
    return "—" if code is None else str(code).replace("_", " ").capitalize()


def environment(**options: Any) -> Environment:
    options.setdefault("undefined", StrictUndefined)
    env = Environment(**options)  # noqa: S701 — autoescape is enabled in settings.TEMPLATES
    env.globals.update({"static": static, "url": reverse})
    env.filters["date"] = _date
    env.filters["naira"] = _naira
    env.filters["naira_short"] = _naira_short
    env.filters["human"] = _human
    return env
