"""Education watchdogs (CR-005): load the national directory and give every institution its regulatory profile."""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from syntegra.regulation import services


class Command(BaseCommand):
    help = (
        "Load the education watchdog directory and apply the regulatory rules to every institution in every registry."
    )

    def handle(self, *args: Any, **opts: Any) -> None:
        nb, nd = services.seed_directory()
        self.stdout.write(f"directory: {nb} bodies and {nd} dependencies added")
        for code, n in services.apply_all().items():
            self.stdout.write(f"{code}: {n} regulatory links added")
