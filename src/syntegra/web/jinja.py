"""Jinja2 environment for server-rendered pages (MFS §14 design system)."""

from __future__ import annotations

from typing import Any

from django.middleware.csrf import get_token
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment, StrictUndefined


def environment(**options: Any) -> Environment:
    options.setdefault("undefined", StrictUndefined)
    env = Environment(**options)  # noqa: S701 — autoescape is set in settings.TEMPLATES
    env.globals.update({"static": static, "url": reverse, "csrf_token": get_token})
    return env
