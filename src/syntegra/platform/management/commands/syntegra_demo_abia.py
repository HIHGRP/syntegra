"""Load the Abia State demonstration dataset (development and test environments only)."""

from __future__ import annotations

import time
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from syntegra.platform.demo import abia


class Command(BaseCommand):
    help = (
        "Abia State end-to-end demonstration data: ministries and ASUBEB, 5 primary and 5 secondary schools in each "
        "of the 17 LGAs with 500 pupils each, ABSU and ASCETA with 500 students and 150 staff, results and attendance."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        d = abia.Scale()
        parser.add_argument("--schools-per-lga", type=int, default=d.schools_per_lga)
        parser.add_argument("--pupils", type=int, default=d.pupils)
        parser.add_argument("--lgas", type=int, default=None, help="load schools in the first N LGAs only")
        parser.add_argument("--absu-students", type=int, default=d.absu_students)
        parser.add_argument("--asceta-students", type=int, default=d.asceta_students)
        parser.add_argument("--absu-staff", type=int, default=d.absu_staff)
        parser.add_argument("--asceta-staff", type=int, default=d.asceta_staff)
        parser.add_argument("--days", type=int, default=d.days, help="school days of attendance")
        parser.add_argument("--no-extras", action="store_true", help="skip facilities, budgets and the warehouse")
        parser.add_argument("--allow-production", action="store_true")

    def handle(self, *args: Any, **o: Any) -> None:
        if not settings.DEBUG and not o["allow_production"]:
            raise CommandError("demonstration data is for development and test environments")
        scale = abia.Scale(
            schools_per_lga=o["schools_per_lga"], pupils=o["pupils"], lgas=o["lgas"], absu_students=o["absu_students"],
            asceta_students=o["asceta_students"], absu_staff=o["absu_staff"], asceta_staff=o["asceta_staff"],
            days=o["days"], extras=not o["no_extras"],
        )  # fmt: skip
        t0 = time.monotonic()
        out = abia.run(scale, log=lambda m: self.stdout.write(m))
        self.stdout.write(self.style.SUCCESS(
            f"done in {time.monotonic() - t0:.0f}s: {out.schools} schools, {out.pupils} pupils, "
            f"{out.tertiary_students} tertiary students, {out.staff} staff, {out.results} marks, "
            f"{out.attendance_marks} attendance marks"
        ))  # fmt: skip
        for n in out.notes:
            self.stdout.write(f"note: {n}")
        self.stdout.write(f"demonstration users (password {abia.PASSWORD}):")
        for username, role, where in out.users:
            self.stdout.write(f"  {username:45} {role:5} {where}")
