"""Development settings: single-tenant zone aliases on a local MySQL 9.7 (see deploy/compose.yaml)."""

from .base import *  # noqa: F403

DEBUG = True
SYNTEGRA_TENANCY = "single"
