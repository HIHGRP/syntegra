"""Provision the first state tenant, hierarchy, roles, policies and administrator (idempotent)."""

from __future__ import annotations

import os
from typing import Any

from django.core.management.base import BaseCommand

from syntegra.platform.bootstrap import bootstrap


class Command(BaseCommand):
    help = "Provision the seed state tenant (Abia), hierarchy, roles, policies and first administrator."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--admin", default="admin@abia.gov.ng")
        parser.add_argument("--host", action="append", dest="hosts")

    def handle(self, *args: Any, **opts: Any) -> None:
        password = os.environ.get("SYNTEGRA_BOOTSTRAP_PASSWORD", "change-me-now-please")
        seeded = bootstrap(admin_username=opts["admin"], admin_password=password, hosts=opts["hosts"])
        self.stdout.write(self.style.SUCCESS(
            f"state tenant {seeded.state_tenant_id}; state scope {seeded.state_scope_id}; admin {opts['admin']}"
        ))
