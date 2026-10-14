"""Publish outstanding learner obligations from the institution's ledger to the state clearance register (FR-FCL-01).

Runs nightly per institution (and on demand from FCL-02). Only issued invoices that are overdue beyond the grace
period are published, grouped per learner and obligation kind; the evidence is the list of invoice numbers with
their content hashes, so a claim can always be traced to issued, immutable invoices. Learners whose balance
returned to zero have their obligation settled. SDAF lines are never published (state revenue only).
"""

from __future__ import annotations

import datetime as dt
import uuid
from collections import defaultdict
from typing import Any

from syntegra.clearance import services as clearance
from syntegra.clearance.domain.rules import kind_for_charge
from syntegra.clearance.models import LearnerObligation
from syntegra.core import authz, context
from syntegra.finance.models import ChargeType, Invoice, InvoiceLine
from syntegra.institutions.models import Institution

OPEN_INVOICE = ("issued", "part_paid", "overdue")
GRACE_DAYS = 30


def _kinds_for(invoice_ids: list[uuid.UUID]) -> dict[uuid.UUID, dict[str | None, int]]:
    """Each invoice's net amount by obligation kind (``None`` = never published, e.g. SDAF lines)."""
    codes = dict(ChargeType.objects.values_list("id", "code"))
    out: dict[uuid.UUID, dict[str | None, int]] = defaultdict(lambda: defaultdict(int))
    for ln in InvoiceLine.objects.filter(invoice_id__in=invoice_ids):
        out[ln.invoice_id][kind_for_charge(codes.get(ln.charge_type_id, "OTHER"))] += ln.net_minor
    return out


def publish_from_ledger(
    institution_id: uuid.UUID, *, as_of: dt.date | None = None, grace_days: int = GRACE_DAYS
) -> dict[str, Any]:
    ctx = context.require()
    authz.require("clearance:publish", ctx)
    as_of = as_of or dt.date.today()
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise ValueError("unknown institution")
    authz.require_scope(inst.scope_node_id, ctx)
    cutoff = as_of - dt.timedelta(days=grace_days)
    invoices = list(
        Invoice.objects.filter(
            scope_node_id=inst.scope_node_id,
            learner_id__isnull=False,
            status__in=OPEN_INVOICE,
            due_on__lte=cutoff,
            balance_minor__gt=0,
        )
    )
    shares = _kinds_for([i.id for i in invoices])
    grouped: dict[tuple[uuid.UUID, str], dict[str, Any]] = {}
    for inv in invoices:
        parts = shares.get(inv.id) or {"tuition_fees": inv.total_minor}
        total = sum(parts.values()) or 1
        for kind, part in parts.items():
            if kind is None or part <= 0:
                continue  # the SDAF share of the balance is pursued by state revenue only — never published
            owed = inv.balance_minor * part // total  # balance attributed pro rata to the invoice's lines
            g = grouped.setdefault(
                (inv.learner_id, kind),
                {"amount": 0, "oldest": inv.due_on, "evidence": [], "periods": set(), "payer": inv.payer_kind},
            )
            g["amount"] += owed
            g["oldest"] = min(g["oldest"], inv.due_on)
            g["evidence"].append(
                {"invoice": inv.invoice_number, "content_hash": bytes(inv.content_hash).hex(), "balance_minor": owed}
            )
            if inv.period_label:
                g["periods"].add(inv.period_label)
    published = settled = 0
    for (learner_id, kind), g in grouped.items():
        if g["amount"] > 0:
            clearance.publish(
                learner_id=learner_id,
                creditor_institution_id=inst.id,
                kind=kind,
                amount_minor=g["amount"],
                oldest_due_on=g["oldest"],
                evidence=g["evidence"],
                periods=sorted(g["periods"]),
                payer_kind=g["payer"],
            )
            published += 1
    # obligations previously published that the ledger no longer supports are settled
    for ob in LearnerObligation.objects.filter(
        creditor_institution_id=inst.id, source="ledger", status__in=("outstanding", "payment_plan")
    ):
        if (ob.learner_id, ob.obligation_kind) not in grouped:
            clearance.publish(
                learner_id=ob.learner_id,
                creditor_institution_id=inst.id,
                kind=ob.obligation_kind,
                amount_minor=0,
                oldest_due_on=ob.oldest_due_on,
                evidence=[],
            )
            settled += 1
    return {"institution_id": inst.id, "as_of": as_of, "published": published, "settled": settled}
