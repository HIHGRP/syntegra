"""Registry-wide jobs: ``upgrade`` after a release, ``daily`` from the scheduler (CR-006)."""

from __future__ import annotations

import datetime as dt
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from syntegra.platform import jobs


class Command(BaseCommand):
    help = (
        "upgrade: re-apply registry configuration and reference data; daily: facilities, imprest, arrears, warehouse."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("job", choices=["upgrade", "daily"])
        parser.add_argument("--date", help="Run the daily job as of YYYY-MM-DD (default today)")
        parser.add_argument("--no-warehouse", action="store_true", help="Skip the warehouse load")

    def handle(self, *args: Any, **opts: Any) -> None:
        if opts["job"] == "upgrade":
            result = jobs.upgrade()
        else:
            on = dt.date.fromisoformat(opts["date"]) if opts.get("date") else None
            result = jobs.daily(on, warehouse=not opts["no_warehouse"])
        for code, res in result.items():
            self.stdout.write(f"{code}: {res}")
