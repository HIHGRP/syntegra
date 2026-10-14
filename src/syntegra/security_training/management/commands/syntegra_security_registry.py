"""Provision the Federal Security Education registry and load the security agencies' reference data (CR-004)."""

from __future__ import annotations

import os
import secrets
from typing import Any

from django.core.management.base import BaseCommand

from syntegra.security_training import registry


class Command(BaseCommand):
    help = (
        "Create the national sector registry ng-fse (idempotent) and seed agencies, structures, ranks, "
        "institutions and courses."
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--admin", help="first administrator (granted SADM at the registry root)")
        parser.add_argument("--host", action="append", dest="hosts")

    def handle(self, *args: Any, **opts: Any) -> None:
        password = None
        if opts["admin"]:
            password = os.environ.get("SYNTEGRA_BOOTSTRAP_PASSWORD") or secrets.token_urlsafe(18)
        p = registry.provision(admin_username=opts["admin"], admin_password=password, hosts=opts["hosts"])
        n = registry.seed_reference()
        self.stdout.write(self.style.SUCCESS(f"{registry.NAME}: tenant {p.tenant_id}"))
        self.stdout.write(
            f"added {n.agencies} agencies, {n.units} units, {n.ranks} ranks, {n.institutions} institutions, "
            f"{n.courses} courses, {n.modules} modules (reference data is illustrative — each agency confirms its own)"
        )
        if password and "SYNTEGRA_BOOTSTRAP_PASSWORD" not in os.environ:
            self.stdout.write(f"administrator {opts['admin']} — initial password (shown once): {password}")
