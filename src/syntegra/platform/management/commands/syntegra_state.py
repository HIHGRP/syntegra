"""Provision any of the 36 states or the FCT on this platform and join it to the national clearance network."""

from __future__ import annotations

import os
import secrets
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from syntegra.platform.bootstrap import provision_state
from syntegra.platform.states import STATES


class Command(BaseCommand):
    help = "Provision a state tenant (e.g. NG-LA), or --all for every state and the FCT (idempotent)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("state_code", nargs="?", help="ISO 3166-2 code, e.g. NG-LA or NG-FC")
        parser.add_argument("--all", action="store_true", help="provision all 36 states and the FCT")
        parser.add_argument("--admin", help="administrator username (single state only)")
        parser.add_argument("--host", action="append", dest="hosts")

    def handle(self, *args: Any, **opts: Any) -> None:
        if opts["all"] == bool(opts["state_code"]):
            raise CommandError("give a state code or --all")
        codes = [c for c, _n, _cap in STATES] if opts["all"] else [opts["state_code"].upper()]
        for code in codes:
            password = None
            if opts["admin"] and not opts["all"]:
                password = os.environ.get("SYNTEGRA_BOOTSTRAP_PASSWORD") or secrets.token_urlsafe(18)
            try:
                seeded = provision_state(
                    code, admin_username=opts["admin"], admin_password=password, hosts=opts["hosts"]
                )
            except ValueError as exc:
                raise CommandError(str(exc)) from exc
            self.stdout.write(self.style.SUCCESS(f"{code}: tenant {seeded.state_tenant_id}, on the clearance network"))
            if password and "SYNTEGRA_BOOTSTRAP_PASSWORD" not in os.environ:
                self.stdout.write(f"administrator {opts['admin']} — initial password (shown once): {password}")
