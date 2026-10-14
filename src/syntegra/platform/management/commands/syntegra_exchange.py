"""National clearance network operations (CR-002): directory, remote peers and national lookup tokens."""

from __future__ import annotations

import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from syntegra.clearance import federation
from syntegra.core import context
from syntegra.core.tenancy import state_tenant_id
from syntegra.platform.models import ExchangePeer


class Command(BaseCommand):
    help = "directory | onboard <NG-XX> --endpoint https://… --jwk '{…}' --agreement REF | suspend <NG-XX> | backfill <NG-XX>"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("action", choices=["directory", "onboard", "suspend", "backfill"])
        parser.add_argument("state_code", nargs="?")
        parser.add_argument("--endpoint")
        parser.add_argument("--jwk", help="the remote registry's ES256 public JWK (JSON)")
        parser.add_argument("--agreement", default="NG-NCX-2026-001")
        parser.add_argument("--batch", type=int, default=1000)

    def handle(self, *args: Any, **opts: Any) -> None:
        action, code = opts["action"], (opts["state_code"] or "").upper()
        if action == "directory":
            rows = ExchangePeer.objects.using("platform").order_by("state_code")
            active = 0
            for p in rows:
                active += p.status == "active"
                seen = p.last_seen_at.isoformat(timespec="minutes") if p.last_seen_at else "-"
                self.stdout.write(f"{p.state_code:6} {p.status:15} {p.hosting:10} {seen:17} {p.state_name}")
            self.stdout.write(f"{active} of {rows.count()} states on the network")
            return
        if not code:
            raise CommandError("give the state code")
        try:
            if action == "onboard":
                if not opts["endpoint"] or not opts["jwk"]:
                    raise CommandError("--endpoint and --jwk are required")
                peer = federation.onboard_remote(code, opts["endpoint"], json.loads(opts["jwk"]),
                                                 agreement_ref=opts["agreement"])
                self.stdout.write(self.style.SUCCESS(f"{peer.state_code} active at {peer.endpoint_url}"))
            elif action == "suspend":
                n = ExchangePeer.objects.using("platform").filter(state_code=code).update(status="suspended")
                self.stdout.write(f"{code} suspended" if n else f"{code} not in the directory")
            else:
                tid = state_tenant_id(code)
                total = 0
                with context.use(context.system(tid, tid, correlation_id="backfill-national-tokens")):
                    while n := federation.backfill_national_tokens(opts["batch"]):
                        total += n
                self.stdout.write(f"{code}: {total} NIN identifiers given a national lookup token")
        except federation.ExchangeRefused as exc:
            raise CommandError(exc.detail) from exc
