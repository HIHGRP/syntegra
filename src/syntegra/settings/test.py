"""Test settings: real MySQL 9.7 (MFS §16.7 — never SQLite); Django creates test_<schema> per zone alias."""

from .base import *  # noqa: F403
from .base import DATABASES, REST_FRAMEWORK

SYNTEGRA_TENANCY = "single"
SYNTEGRA_AUDIT_LANES = 4
CELERY_TASK_ALWAYS_EAGER = True
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {"public_verify": "1000/hour", "exchange": "10000/minute", "anon": "1000/minute", "user": "10000/minute"},
}
for _alias, _cfg in DATABASES.items():
    _cfg["CONN_MAX_AGE"] = 0
