"""Development settings: single-tenant zone aliases on a local MySQL 9.7 (see deploy/compose.yaml)."""

from .base import *  # noqa: F403

DEBUG = True
SYNTEGRA_TENANCY = "single"
# the demonstration accounts sign in without an authenticator unless asked for (SYNTEGRA_MFA_REQUIRED_CLEARANCE)
SYNTEGRA_MFA_REQUIRED_CLEARANCE = env("SYNTEGRA_MFA_REQUIRED_CLEARANCE", "")  # noqa: F405
