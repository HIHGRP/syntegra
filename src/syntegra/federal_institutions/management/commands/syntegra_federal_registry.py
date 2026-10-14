"""Provision the Federal Institutions registry, load its reference data, or import an official list (CR-005)."""

from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from syntegra.core import context
from syntegra.federal_institutions import registry, services


class Command(BaseCommand):
    help = "seed (default): create ng-fed and load the reference data | import <file.csv> [--dry-run]"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("action", nargs="?", default="seed", choices=["seed", "import"])
        parser.add_argument("file", nargs="?")
        parser.add_argument("--admin")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args: Any, **opts: Any) -> None:
        if opts["action"] == "import":
            if not opts["file"]:
                raise CommandError("give the CSV file")
            with context.use(registry.system_context()):
                r = services.import_csv(Path(opts["file"]).read_text(encoding="utf-8"), dry_run=opts["dry_run"])
            self.stdout.write(str(r))
            if r["errors"]:
                raise CommandError(f"{len(r['errors'])} rows need correcting; nothing was imported")
            return
        password = None
        if opts["admin"]:
            password = os.environ.get("SYNTEGRA_BOOTSTRAP_PASSWORD") or secrets.token_urlsafe(18)
        p = registry.provision(admin_username=opts["admin"], admin_password=password)
        n = registry.seed_reference()
        self.stdout.write(self.style.SUCCESS(f"{registry.NAME}: tenant {p.tenant_id}"))
        self.stdout.write(
            f"added {n.bodies} bodies, {n.units} units, {n.institutions} institutions, "
            f"{n.regulatory_links} regulatory links (reference data to be confirmed by each body)"
        )
        if password and "SYNTEGRA_BOOTSTRAP_PASSWORD" not in os.environ:
            self.stdout.write(f"administrator {opts['admin']} — initial password (shown once): {password}")
