"""Staging: the production settings and image, run against real infrastructure before a release goes to production
(CR-008) — MySQL 9.7 over verified TLS, S3-compatible object storage with compliance object lock, an OpenID Connect
identity provider, and backups that are restored and checked.

Only these differ from production, each for a stated reason:

* keys come from ``LocalKeyProvider`` with a staging-only secret: the HSM-backed provider is configured per state
  and is not part of the rehearsal (``prod`` refuses it unless ``SYNTEGRA_ENVIRONMENT=staging``);
* the test identity provider may be reached over http inside the staging network.
"""

import os

if os.environ.get("SYNTEGRA_ENVIRONMENT") != "staging":
    raise RuntimeError("syntegra.settings.staging needs SYNTEGRA_ENVIRONMENT=staging")

from .prod import *  # noqa: F403

SYNTEGRA_MASTER_KEY = os.environ["SYNTEGRA_STAGING_MASTER_KEY"]
SYNTEGRA_SSO_ALLOW_HTTP = os.environ.get("SYNTEGRA_SSO_ALLOW_HTTP", "1") == "1"
