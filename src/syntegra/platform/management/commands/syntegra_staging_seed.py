"""Staging rehearsal fixtures (CR-008): one school to file documents under and one account the state has created
for single sign-on. Idempotent; refused outside development and staging. Prints the ids as JSON."""

from __future__ import annotations

import json
import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the staging rehearsal school and the account linked to single sign-on (staging only)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--admin", default="admin@abia.gov.ng")
        parser.add_argument("--sso-user", default="sso.officer@abiastate.gov.ng")

    def handle(self, *args: Any, **opts: Any) -> None:
        if os.environ.get("SYNTEGRA_ENVIRONMENT") != "staging" and not settings.DEBUG:
            raise CommandError("syntegra_staging_seed runs only in staging or development")
        from syntegra.core import authz, context
        from syntegra.core.context import Context
        from syntegra.core.tenancy import state_tenant_id
        from syntegra.governance.models import ScopeNode
        from syntegra.iam import services as iam
        from syntegra.iam.models import AppUser, Role, RoleGrant
        from syntegra.institutions import services as inst
        from syntegra.institutions.models import Institution

        t = state_tenant_id("NG-AB")
        sysctx = context.system(t, t, correlation_id="staging-seed")
        with context.use(sysctx):
            admin = AppUser.objects.get(username=opts["admin"])
            grant = RoleGrant.objects.filter(user_id=admin.id, status="active").first()
            lga = ScopeNode.objects.get(code="AB-UMN")
        if grant is None:
            raise CommandError(f"{opts['admin']} has no active role")
        base = Context(tenant_id=t, state_tenant_id=t, actor_kind="user", actor_id=admin.id)
        with context.use(base):
            ctx = authz.grant_context(base, grant.id)
        with context.use(ctx):
            school = Institution.objects.filter(gov_reg_no="AB/SS/STAGING").first()
            if school is None:
                school = inst.register(
                    inst.RegisterInstitution(
                        name="Staging Rehearsal Secondary School",
                        category="secondary",
                        ownership="state",
                        lga_scope_id=lga.id,
                        address={"town": "Umuahia", "lga": "Umuahia North"},
                        levels=["jss_1"],
                        gov_reg_no="AB/SS/STAGING",
                        location=(7.4127, 5.6411),  # an otherwise empty spot, so no near-duplicate is suspected
                    )
                )
        with context.use(sysctx):
            user = AppUser.objects.filter(username=opts["sso_user"]).first()
            if user is None:  # no password: this account signs in only through the state's identity provider
                user = iam.create_user(sysctx, username=opts["sso_user"], display_name="Staging Officer", password=None)
            role_id = Role.objects.get(code="TCH").id
            if not RoleGrant.objects.filter(user_id=user.id, role_id=role_id, status="active").exists():
                iam.grant_role(sysctx, user=user, role_code="TCH", scope_id=school.scope_node_id)
        self.stdout.write(json.dumps({"institution_id": str(school.id), "sso_user": user.username}))
