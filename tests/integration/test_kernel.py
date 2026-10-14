"""Kernel guarantees: schema parity, tenant context, audit chain, outbox, append-only."""

import uuid

import pytest
from django.apps import apps
from django.db import connections

from syntegra.core import audit, context
from syntegra.core.errors import AppendOnlyViolation

pytestmark = pytest.mark.django_db(databases="__all__")

# Replicated kernel tables carry tenant_id outside the platform zone; they are written with SQL (core.audit,
# core.outbox), so their ORM model reflects the platform shape.
REPLICATED_KERNEL = {"audit_event", "audit_chain_head", "audit_anchor", "outbox_event"}


def test_every_model_matches_its_table_in_every_zone() -> None:
    checked = 0
    for m in apps.get_models():
        for zone in getattr(m, "ceda_zones", ()):
            with connections[zone].cursor() as cur:
                cur.execute(
                    "SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() "
                    "AND table_name = %s",
                    [m._meta.db_table],
                )
                cols = {r[0] for r in cur.fetchall()}
            model_cols = {f.column for f in m._meta.concrete_fields}
            if m.ceda_entity in REPLICATED_KERNEL and zone != "platform":
                model_cols |= {"tenant_id"}
            assert cols == model_cols, (zone, m.ceda_entity, cols ^ model_cols)
            checked += 1
    assert checked == 513


def test_tenant_data_cannot_be_queried_without_context() -> None:
    from syntegra.learners.models import Learner

    with pytest.raises(context.ContextMissing):
        list(Learner.objects.all())


def test_audit_chain_is_append_only_and_tamper_evident(world: object) -> None:
    with connections["registry"].cursor() as cur:
        cur.execute(
            "SELECT chain_id, tenant_id, last_seq, last_hash FROM audit_chain_head ORDER BY last_seq DESC LIMIT 1"
        )
        chain_id, tenant_id, last, last_hash = cur.fetchone()
    chain = uuid.UUID(bytes=bytes(chain_id))
    ok, n = audit.verify_chain("registry", chain)
    assert ok and n == last
    with pytest.raises(Exception, match="append-only"), connections["registry"].cursor() as cur:
        cur.execute("UPDATE audit_event SET reason = 'edited' WHERE chain_id = %s", [chain.bytes])
    # a forged event appended behind the writer's back breaks the chain at that point
    with connections["registry"].cursor() as cur:
        cur.execute(
            "INSERT INTO audit_event (tenant_id, chain_id, chain_seq, occurred_at, event_id, actor_kind, action, "
            "record_kind, field_changes, correlation_id, prev_hash, hash, created_at) VALUES "
            "(%s, %s, %s, UTC_TIMESTAMP(6), %s, 'system', 'update', 'learner', '[]', 'forged', %s, %s, "
            "UTC_TIMESTAMP(6))",
            [bytes(tenant_id), chain.bytes, last + 1, uuid.uuid4().bytes, bytes(last_hash), b"\x01" * 32],
        )
    assert audit.verify_chain("registry", chain) == (False, last)


def test_outbox_events_written_with_the_change(world: object) -> None:
    with connections["registry"].cursor() as cur:
        cur.execute("SELECT event_type, payload FROM outbox_event WHERE event_type = 'INS.REGISTERED'")
        rows = cur.fetchall()
    assert len(rows) >= 2


def test_append_only_refused_in_orm_and_database(world: object) -> None:
    from syntegra.certificates.models import Verification
    from syntegra.core.fields import utcnow
    from tests.conftest import system_ctx

    with context.use(system_ctx()):
        v = Verification(queried_number="X", channel="web_number", result="not_found", verified_at=utcnow())
        v.save(using="registry")
        with pytest.raises(AppendOnlyViolation):
            v.save(using="registry")
        with pytest.raises(AppendOnlyViolation):
            v.delete(using="registry")
    with pytest.raises(Exception, match="append-only"), connections["registry"].cursor() as cur:
        cur.execute("DELETE FROM verification")
