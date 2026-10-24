"""CR-007 full-text search of documents across schools (FR-DOC-203/204).

InnoDB full-text indexes only see committed rows, so this module runs outside the per-test transaction: it commits
its school and documents for real and removes the documents afterwards (audit events stay, as they always do).
"""

from __future__ import annotations

import uuid
from typing import Any

from tests.conftest import system_ctx, user_ctx


def _pdf(title: str, lines: list[str]) -> bytes:
    from syntegra.platform.demo.abia import _pdf as pdf

    return pdf(title, lines)


def test_search_across_schools_uses_the_full_text_index(django_db_setup: Any, django_db_blocker: Any) -> None:
    from syntegra.core import context
    from syntegra.governance.models import ScopeNode
    from syntegra.iam.models import AppUser, RoleGrant
    from syntegra.institutions import services as inst
    from syntegra.records import services as rec
    from syntegra.records.models import Document, DocumentIndex

    tag = uuid.uuid4().hex[:6]
    created: list[Any] = []
    with django_db_blocker.unblock():
        sysctx = system_ctx()
        with context.use(sysctx):
            admin = AppUser.objects.get(username="admin@abia.gov.ng")
            g = RoleGrant.objects.filter(user_id=admin.id, status="active").first()
            lga = ScopeNode.objects.get(code="AB-UMN")
        assert g is not None
        sta = user_ctx(admin.id, g.id)
        try:
            with context.use(sta):
                school = inst.register(
                    inst.RegisterInstitution(
                        name=f"Search Test School {tag}",
                        category="secondary",
                        ownership="state",
                        lga_scope_id=lga.id,
                        address={"town": "Umuahia"},
                        levels=["jss_1"],
                        gov_reg_no=f"AB/SS/{tag}",
                        location=(7.49, 5.53),
                    )
                )
            sta = user_ctx(admin.id, g.id)  # the new school's node joins the administrator's scope
            with context.use(sta):
                created += rec.upload(
                    sta,
                    institution_id=school.id,
                    category_code="MIN",
                    title=f"PTA minutes {tag}",
                    files=[rec.Upload("m.pdf", _pdf("PTA MINUTES", [f"The borehole levy {tag} was approved."]))],
                )
                created += rec.upload(
                    sta,
                    institution_id=school.id,
                    category_code="LOG",
                    title=f"Log book {tag}",
                    files=[rec.Upload("l.txt", f"Flooding closed the school; visit by the inspector {tag}.".encode())],
                )
                hits = rec.search(sta, q=f"borehole levy {tag}")
                assert [r["title"] for r in hits["rows"]] == [f"PTA minutes {tag}"]
                hits = rec.search(sta, q=f"inspector {tag}")
                assert hits["total"] == 1 and hits["rows"][0]["category_code"] == "LOG"
                assert rec.search(sta, q=f"nothing-like-this {tag}")["total"] == 0
                assert rec.search(sta, q=f"borehole {tag}", institution_id=school.id)["total"] == 1
        finally:
            with context.use(sysctx):
                for d in created:
                    DocumentIndex.objects.filter(document_id=d.id).delete()
                    Document.objects.filter(pk=d.id).delete()


def test_scope_and_purpose_apply_before_the_ranking_limit(django_db_setup: Any, django_db_blocker: Any) -> None:
    """A scoped officer's own schools are never crowded out by better matches elsewhere in the state, and
    restricted documents are searched only for a declared purpose (code review of CR-007)."""
    from syntegra.core import authz, context
    from syntegra.governance.models import ScopeNode
    from syntegra.iam.models import AppUser, RoleGrant
    from syntegra.institutions import services as inst
    from syntegra.records import services as rec
    from syntegra.records.models import Document, DocumentIndex

    tag = uuid.uuid4().hex[:6]
    created: list[Any] = []
    with django_db_blocker.unblock():
        sysctx = system_ctx()
        with context.use(sysctx):
            admin = AppUser.objects.get(username="admin@abia.gov.ng")
            g = RoleGrant.objects.filter(user_id=admin.id, status="active").first()
            umn, abs_ = ScopeNode.objects.get(code="AB-UMN"), ScopeNode.objects.get(code="AB-ABS")
        assert g is not None
        sta = user_ctx(admin.id, g.id)
        schools = {}
        try:
            with context.use(sta):
                for code, lga in (("far", umn), ("near", abs_)):
                    schools[code] = inst.register(
                        inst.RegisterInstitution(
                            name=f"Ranking Test School {code} {tag}",
                            category="secondary",
                            ownership="state",
                            lga_scope_id=lga.id,
                            address={"town": "Aba"},
                            levels=["jss_1"],
                            gov_reg_no=f"AB/RT/{code}/{tag}",
                            location=(7.37, 5.11),
                        )
                    )
            sta = user_ctx(admin.id, g.id)
            with context.use(sta):
                word = f"cassava{tag}"
                created += rec.upload(
                    sta,
                    institution_id=schools["far"].id,
                    category_code="LOG",
                    title=f"Farm log {tag}",
                    files=[rec.Upload("a.txt", (f"{word} " * 40).encode())],
                )
                created += rec.upload(
                    sta,
                    institution_id=schools["near"].id,
                    category_code="LOG",
                    title=f"Visitors {tag}",
                    files=[rec.Upload("b.txt", f"A visitor brought {word} to the school.".encode())],
                )
                created += rec.upload(
                    sta,
                    institution_id=schools["near"].id,
                    category_code="STF",
                    title=f"Staff file {tag}",
                    files=[rec.Upload("c.txt", f"Staff file noting {word} allowance.".encode())],
                )
                classes = rec._visible_classes(sta, restricted=False)
                # state-wide, the far school's document ranks first ...
                top = rec._fulltext_ids(sta, word, None, classes, limit=1)
                assert top == [created[0].id.bytes]
                # ... but an officer scoped to the near school's LGA still gets their own, even with a limit of one
                assert sta.state_tenant_id is not None
                lga_officer = sta.with_(scope_ids=authz.subtree(sta.state_tenant_id, abs_.id))
                assert rec._fulltext_ids(lga_officer, word, None, classes, limit=1) == [created[1].id.bytes]
                # restricted documents are searched only with a purpose
                assert {r["title"] for r in rec.search(sta, q=word)["rows"]} == {f"Farm log {tag}", f"Visitors {tag}"}
                with_purpose = rec.search(sta, q=word, purpose="records_retrieval")
                assert f"Staff file {tag}" in {r["title"] for r in with_purpose["rows"]}
        finally:
            with context.use(sysctx):
                for d in created:
                    DocumentIndex.objects.filter(document_id=d.id).delete()
                    Document.objects.filter(pk=d.id).delete()
