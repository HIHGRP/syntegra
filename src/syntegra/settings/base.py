"""Base settings — Syntegra (Django 5.2 LTS, MySQL 9.7 LTS, RHEL 10). See ceda/CEDA.md §16 for the hosting model."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # src/syntegra
REPO_DIR = BASE_DIR.parents[1]


def env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"environment variable {name} is required")
    return value


SECRET_KEY = env("SYNTEGRA_SECRET_KEY", "dev-insecure-change-me")
DEBUG = False
ALLOWED_HOSTS = env("SYNTEGRA_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")

# One Django app per CEDA module (CEDA §4.2). Order: kernel first.
CEDA_APPS = [
    "syntegra.core",
    "syntegra.platform",
    "syntegra.governance",
    "syntegra.iam",
    "syntegra.mdm",
    "syntegra.institutions",
    "syntegra.providers",
    "syntegra.learners",
    "syntegra.families",
    "syntegra.people",
    "syntegra.hr",
    "syntegra.academic",
    "syntegra.curriculum",
    "syntegra.timetable",
    "syntegra.attendance",
    "syntegra.assessment",
    "syntegra.certificates",
    "syntegra.success",
    "syntegra.safeguarding",
    "syntegra.sectors",
    "syntegra.lms",
    "syntegra.comms",
    "syntegra.finance",
    "syntegra.financing",
    "syntegra.clearance",
    "syntegra.security_training",
    "syntegra.operations",
    "syntegra.forms",
    "syntegra.records",
    "syntegra.intelligence",
    "syntegra.reporting",
    "syntegra.integration",
    "syntegra.analytics",
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "syntegra.schema",
    "syntegra.web",
    *CEDA_APPS,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "syntegra.core.middleware.ContextMiddleware",
]

ROOT_URLCONF = "syntegra.urls"
WSGI_APPLICATION = "syntegra.wsgi.application"
ASGI_APPLICATION = "syntegra.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "web" / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {"environment": "syntegra.web.jinja.environment", "autoescape": True},
    },
]

# --------------------------------------------------------------------------- databases (CEDA §6, §16)
# 'default' holds only Django framework tables; every CEDA zone has its own alias/schema.
DB_HOST = env("SYNTEGRA_DB_HOST", "127.0.0.1")
DB_PORT = env("SYNTEGRA_DB_PORT", "3306")
DB_USER = env("SYNTEGRA_DB_USER", "root")
DB_PASSWORD = env("SYNTEGRA_DB_PASSWORD", "ceda")
DB_PREFIX = env("SYNTEGRA_DB_PREFIX", "syn_dev")


def _mysql(name: str) -> dict[str, object]:
    return {
        "ENGINE": "django.db.backends.mysql",
        "NAME": name,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "CONN_MAX_AGE": int(env("SYNTEGRA_DB_CONN_MAX_AGE", "60")),
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {
            "charset": "utf8mb4",
            "isolation_level": "read committed",
            "init_command": "SET time_zone = '+00:00', SESSION sql_mode = "
            "'STRICT_ALL_TABLES,ONLY_FULL_GROUP_BY,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'",
        },
        "TEST": {"CHARSET": "utf8mb4", "COLLATION": "utf8mb4_0900_ai_ci"},
    }


DATABASES = {
    "default": _mysql(f"{DB_PREFIX}_django"),
    "platform": _mysql(f"{DB_PREFIX}_platform"),
    "registry": _mysql(f"{DB_PREFIX}_registry"),
    "ops": _mysql(f"{DB_PREFIX}_ops"),
    "vault": _mysql(f"{DB_PREFIX}_vault"),
    "records": _mysql(f"{DB_PREFIX}_records"),
    "dw": _mysql(f"{DB_PREFIX}_dw"),
}
DATABASE_ROUTERS = ["syntegra.core.routers.ZoneRouter"]

SYNTEGRA_TENANCY = env("SYNTEGRA_TENANCY", "single")  # single | schema
SYNTEGRA_DB_TEMPLATE = _mysql("")
SYNTEGRA_SCHEMA_PATTERNS = {
    "platform": "syn_platform",
    "registry": "syn_reg_{state}",
    "ops": "syn_ops_{tenant}",
    "vault": "syn_vault_{tenant}",
    "records": "syn_rec_{tenant}",
    "dw": "syn_dw_{state}",
}
SYNTEGRA_CEDA_DDL_DIR = Path(env("SYNTEGRA_CEDA_DDL_DIR", str(REPO_DIR / "ceda" / "generated" / "mysql")))
SYNTEGRA_CEDA_RELEASES_DIR = Path(env("SYNTEGRA_CEDA_RELEASES_DIR", str(REPO_DIR / "ceda" / "releases")))
SYNTEGRA_DEFAULT_TENANT_CODE = env("SYNTEGRA_DEFAULT_TENANT_CODE", "ng-ab")

# --------------------------------------------------------------------------- keys (CEDA §8.1)
# Development uses the local key provider derived from SYNTEGRA_MASTER_KEY; production uses the
# HSM/KMIP-backed provider (keys never in settings, images or the database).
SYNTEGRA_KEY_PROVIDER = env("SYNTEGRA_KEY_PROVIDER", "syntegra.core.crypto.LocalKeyProvider")
SYNTEGRA_MASTER_KEY = env("SYNTEGRA_MASTER_KEY", "dev-only-master-key-not-for-production-use-0123456789")
SYNTEGRA_AUDIT_LANES = 16

# --------------------------------------------------------------------------- API (Book 3 §26.1)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["syntegra.core.api.auth.ContextAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["syntegra.core.api.permissions.RequiresContext"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "syntegra.core.api.problems.exception_handler",
    "DEFAULT_PAGINATION_CLASS": "syntegra.core.api.pagination.UUID7CursorPagination",
    "PAGE_SIZE": 50,
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_THROTTLE_RATES": {
        "public_verify": "20/hour",
        "exchange": "1200/minute",
        "anon": "60/minute",
        "user": "600/minute",
    },
}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
if os.environ.get("SYNTEGRA_VALKEY_URL"):
    CACHES["default"] = {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ["SYNTEGRA_VALKEY_URL"],
    }

# --------------------------------------------------------------------------- workers (Celery on RabbitMQ)
CELERY_BROKER_URL = env("SYNTEGRA_BROKER_URL", "memory://")
CELERY_TASK_ALWAYS_EAGER = env("SYNTEGRA_CELERY_EAGER", "true") == "true"
CELERY_TASK_ACKS_LATE = True
CELERY_TIMEZONE = "UTC"

# --------------------------------------------------------------------------- i18n / time
LANGUAGE_CODE = "en-ng"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "web" / "static"]
STATIC_ROOT = REPO_DIR / "var" / "static"

# --------------------------------------------------------------------------- security
SESSION_COOKIE_NAME = "syn_session"
SYNTEGRA_SESSION_IDLE_MINUTES = {"restricted": 30, "special": 30, "default": 480}
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_HTTPONLY = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"format": '{"t":"%(asctime)s","lvl":"%(levelname)s","log":"%(name)s","msg":"%(message)s"}'}
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"handlers": ["console"], "level": env("SYNTEGRA_LOG_LEVEL", "INFO")},
}
