"""Production settings: schema-per-tenant tenancy, secrets from the environment (injected from Vault)."""

import os

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = os.environ["SYNTEGRA_SECRET_KEY"]
SYNTEGRA_MASTER_KEY = ""  # never used in production: keys come from the HSM-backed provider
SYNTEGRA_TRUST_PROXY = True  # behind the API gateway / load balancer
SYNTEGRA_TENANCY = os.environ.get("SYNTEGRA_TENANCY", "schema")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SYNTEGRA_KEY_PROVIDER = os.environ["SYNTEGRA_KEY_PROVIDER"]
# keys derived from one configured secret are for development and the staging rehearsal only, never production
if SYNTEGRA_KEY_PROVIDER.endswith(".LocalKeyProvider") and os.environ.get("SYNTEGRA_ENVIRONMENT") != "staging":
    raise RuntimeError("SYNTEGRA_KEY_PROVIDER must be the HSM-backed provider in production")
for _cfg in DATABASES.values():  # noqa: F405
    _cfg["OPTIONS"]["ssl_mode"] = "VERIFY_IDENTITY"  # type: ignore[index]
# CR-008: masters are held only in object storage under object lock in production (FR-DOC-301)
SYNTEGRA_OBJECT_STORE = "s3"
if not SYNTEGRA_S3_BUCKET:  # noqa: F405
    raise RuntimeError("SYNTEGRA_S3_BUCKET is required: production keeps document masters under object lock")
if not SYNTEGRA_MFA_REQUIRED_CLEARANCE:  # noqa: F405
    raise RuntimeError("SYNTEGRA_MFA_REQUIRED_CLEARANCE cannot be empty in production (CR-003 FR-AUT-01)")
