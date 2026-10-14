"""Production settings: schema-per-tenant tenancy, secrets from the environment (injected from Vault)."""

import os

from .base import *  # noqa: F403

DEBUG = False
SYNTEGRA_TENANCY = os.environ.get("SYNTEGRA_TENANCY", "schema")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SYNTEGRA_KEY_PROVIDER = os.environ["SYNTEGRA_KEY_PROVIDER"]
for _cfg in DATABASES.values():  # noqa: F405
    _cfg["OPTIONS"]["ssl_mode"] = "VERIFY_IDENTITY"  # type: ignore[index]
