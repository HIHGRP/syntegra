"""Document management for digitised paper records (CR-007, FR-DOC-201–206; MFS §13).

Paper documents scanned at a school are uploaded under that school with a reference number
``<institution code>/<category>/<year>/<sequence>``. The scan is stored write-once and hashed (``core.storage``);
its text (PDF text layer, OCR, transcription) goes into ``document_index`` for MySQL full-text search. Who may see a
document is decided by scope (the school's node), the access level of the active role against the document's
classification, the document permissions — ``document:view`` within one's schools, ``document:search`` to search
across every school in scope (ministry, boards, LGA, records managers) — and, for restricted documents, a declared
purpose. Every upload, search, view, download and Word export is audited.
"""

from __future__ import annotations

import datetime as dt
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.db import connections

from syntegra.core import access, audit, authz, context, storage, uow
from syntegra.core.context import CLASS_ORDER, Context, class_rank
from syntegra.core.errors import Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.core.zones import current_alias
from syntegra.records import text as textmod
from syntegra.records.models import Document, DocumentCategory, DocumentIndex, RecordSeries

# code, title, classification, retention (years kept before review; None = permanent)
CATEGORIES: list[tuple[str, str, str, int | None]] = [
    ("ADM", "Admission registers", "confidential", None),
    ("ATT", "Attendance registers", "confidential", 10),
    ("RES", "Results, broadsheets and report cards", "confidential", None),
    ("CERT", "Certificates, testimonials and transcripts", "confidential", None),
    ("STF", "Staff records and personal files", "restricted", 50),
    ("FIN", "Financial records, receipts and ledgers", "restricted", 7),
    ("DISC", "Discipline records", "restricted", 7),
    ("MIN", "Minutes of meetings (PTA, SBMC, staff, board)", "internal", None),
    ("INSP", "Inspection and quality-assurance reports", "internal", 25),
    ("COR", "Correspondence and circulars", "internal", 10),
    ("LAND", "Land, title and property documents", "internal", None),
    ("LOG", "Log books and visitors' books", "internal", 25),
]
MAX_FILES = 20


def ocr_available() -> bool:
    return textmod.ocr_available()


WORD_RE = re.compile(r"[\w'’-]{3,}", re.UNICODE)


# --------------------------------------------------------------------------- categories
def _state_root() -> Any:
    from syntegra.governance.models import ScopeNode

    q = ScopeNode.objects.filter(level="state")
    return q.filter(ref_kind="tenant").order_by("depth").first() or q.order_by("depth").first()


def ensure_categories() -> None:
    """The standard document categories and their record series (file plan), once per tenant — idempotent."""
    ctx = context.require()
    if DocumentCategory.objects.filter(code__in=[c for c, *_ in CATEGORIES]).count() == len(CATEGORIES):
        return
    root = _state_root()
    if root is None:
        return
    sysctx = context.system(ctx.tenant_id, ctx.state_tenant_id, correlation_id=ctx.correlation_id)
    with uow.command("records", None, action="create", record_kind="document_category", ctx=sysctx) as cmd:
        for code, title, cls, years in CATEGORIES:
            if DocumentCategory.objects.filter(code=code).exists():
                continue
            series = RecordSeries.objects.filter(code=f"DOC-{code}", version=1).first() or cmd.add(
                RecordSeries(
                    tenant_id=sysctx.tenant_id,
                    scope_node_id=root.id,
                    code=f"DOC-{code}",
                    title=title,
                    owner_role="RECM",
                    classification=cls,
                    retention_series="RS-DOC",
                    retention_rule={
                        "trigger": "date of the document",
                        "years": years,
                        "action": "review" if years else "permanent",
                    },
                    version=1,
                    status="published",
                ),
                cross_scope_basis="file plan seeded for the state",
            )
            cmd.add(
                DocumentCategory(
                    tenant_id=sysctx.tenant_id,
                    scope_node_id=root.id,
                    code=code,
                    title=title,
                    record_series_id=series.id,
                    classification=cls,
                    permissions={"view": "document:view", "download": "document:view", "search": "document:search"},
                    is_full_text_indexed=cls != "special",
                ),
                cross_scope_basis="file plan seeded for the state",
            )


def categories() -> list[DocumentCategory]:
    ensure_categories()
    return list(DocumentCategory.objects.filter(code__in=[c for c, *_ in CATEGORIES]).order_by("title"))


# --------------------------------------------------------------------------- helpers
def _institution(institution_id: uuid.UUID) -> Any:
    from syntegra.institutions.models import Institution

    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("Institution", institution_id)
    return inst


def _in_scope(ctx: Context, scope_node_id: uuid.UUID | None) -> bool:
    return ctx.is_system or ctx.scope_ids is None or (scope_node_id is not None and scope_node_id in ctx.scope_ids)


def _visible_classes(ctx: Context) -> list[str]:
    return [c for c in CLASS_ORDER if ctx.cleared_for(c) and c != "special"] if not ctx.is_system else list(CLASS_ORDER)


def _require_any(ctx: Context, *perms: str) -> None:
    if not any(ctx.has(p) for p in perms):
        raise Forbidden(f"Missing permission {perms[0]}.", code="AUTH-PERMISSION")


def _audit(ctx: Context, action: str, record_id: uuid.UUID | None, changes: list[dict[str, Any]] | None = None) -> None:
    from django.db import transaction

    alias = current_alias("records")
    with transaction.atomic(using=alias):
        audit.write_event(alias, ctx, action=action, record_kind="document", record_id=record_id, field_changes=changes)


def _keywords(doc: Document, cat: DocumentCategory, inst: Any) -> str:
    parts = [
        cat.title,
        cat.code,
        inst.name,
        inst.institution_code,
        doc.session_label,
        doc.level_or_class,
        doc.subject_label,
        doc.source_reference,
        doc.description,
        str(doc.date_from.year) if doc.date_from else None,
    ]
    return " · ".join(p for p in parts if p)[:2000]


def _next_reference(alias: str, tenant_id: uuid.UUID, prefix: str) -> str:
    """``prefix/00001``: the next sequence under the prefix, taken under a lock on the reference key range."""
    with connections[alias].cursor() as cur:
        cur.execute(
            "SELECT reference_no FROM document WHERE tenant_id = %s AND reference_no LIKE %s "
            "ORDER BY reference_no DESC LIMIT 1 FOR UPDATE",
            [tenant_id.bytes, prefix + "/%"],
        )
        row = cur.fetchone()
    last = int(str(row[0]).rsplit("/", 1)[1]) if row else 0
    return f"{prefix}/{last + 1:05d}"


# --------------------------------------------------------------------------- upload
@dataclass(frozen=True)
class Upload:
    name: str
    data: bytes


def upload(
    ctx: Context,
    *,
    institution_id: uuid.UUID,
    category_code: str,
    title: str,
    files: list[Upload],
    date_from: dt.date | None = None,
    date_to: dt.date | None = None,
    session_label: str = "",
    level_or_class: str = "",
    subject_label: str = "",
    source_reference: str = "",
    description: str = "",
    transcription: str = "",
    classification: str | None = None,
) -> list[Document]:
    """Store digitised paper documents of one institution (FR-DOC-202/203); one document per file."""
    authz.require("document:upload", ctx)
    inst = _institution(institution_id)
    if not _in_scope(ctx, inst.scope_node_id):
        raise Forbidden("That school is outside your scope.", code="AUTH-SCOPE")
    cat = next((c for c in categories() if c.code == category_code), None)
    if cat is None:
        raise HardValidation("DOC-CATEGORY", "Choose a category", "Choose the kind of document from the list.")
    cls = classification or cat.classification
    if cls not in CLASS_ORDER or class_rank(cls) < class_rank(cat.classification):
        raise HardValidation(
            "DOC-CLASS",
            "Classification too low",
            f"{cat.title} are at least {access.level(cat.classification).label}; "
            "a document can be raised, not lowered.",
        )
    if not ctx.cleared_for(cls):
        raise Forbidden(
            f"You cannot file a document above your own access level ({access.level(ctx.clearance).label})."
        )
    title = (title or "").strip()
    if len(title) < 3:
        raise HardValidation(
            "DOC-TITLE", "Give a title", "Say what the document is, e.g. Admission register 1998–2003."
        )
    if not files:
        raise HardValidation("DOC-FILES", "Choose a file", "Choose at least one scanned file to upload.")
    if len(files) > MAX_FILES:
        raise HardValidation("DOC-FILES", "Too many files", f"Upload at most {MAX_FILES} files at a time.")
    if date_from and date_to and date_to < date_from:
        raise HardValidation("DOC-DATES", "Dates the wrong way round", "The 'to' date is before the 'from' date.")
    limit = int(getattr(settings, "SYNTEGRA_DOCUMENT_MAX_BYTES", 25 * 1024 * 1024))
    prepared = []
    errors = []
    for f in files:
        mime = textmod.sniff(f.data)
        if mime not in textmod.ALLOWED:
            errors.append({"file": f.name, "detail": "Not a PDF, JPEG, PNG, TIFF or text file."})
            continue
        if len(f.data) > limit:
            errors.append({"file": f.name, "detail": f"Larger than {limit // (1024 * 1024)} MB — scan at 200–300 dpi."})
            continue
        prepared.append((f, mime))
    if errors:
        raise HardValidation("DOC-FILE-TYPE", "Some files cannot be accepted", errors[0]["detail"], errors)
    year = (date_from or date_to or dt.date.today()).year
    prefix = f"{inst.institution_code}/{cat.code}/{year}"
    out: list[Document] = []
    with uow.command("records", "document:upload", action="upload", record_kind="document", ctx=ctx) as cmd:
        alias = cmd.alias
        for f, mime in prepared:
            stored = storage.put(f.data, prefix=f"records/{ctx.tenant_id}", ext=textmod.EXTENSIONS[mime])
            dup = Document.objects.filter(sha256=stored.sha256).exclude(status="disposed").first()
            if dup is not None:
                raise HardValidation(
                    "DOC-DUPLICATE",
                    "Already stored",
                    f"{f.name} is already stored as {dup.reference_no} ({dup.title}) — the same scan is kept once.",
                )
            extracted = textmod.extract(f.data, mime, transcription)
            doc = cmd.add(
                Document(
                    tenant_id=ctx.tenant_id,
                    scope_node_id=inst.scope_node_id,
                    category_id=cat.id,
                    reference_no=_next_reference(alias, ctx.tenant_id, prefix),  # type: ignore[arg-type]
                    title=title if len(prepared) == 1 else f"{title} ({f.name})",
                    description=description.strip() or None,
                    source_reference=source_reference.strip() or None,
                    classification=cls,
                    institution_id=inst.id,
                    lga_scope_id=inst.lga_scope_id,
                    date_from=date_from,
                    date_to=date_to,
                    session_label=session_label.strip()[:20] or None,
                    level_or_class=level_or_class.strip()[:80] or None,
                    subject_label=subject_label.strip()[:120] or None,
                    origin="digitised",
                    page_range=f"1–{extracted.pages}",
                    master_object_key=stored.key,
                    mime_type=mime,
                    size_bytes=stored.size,
                    sha256=stored.sha256,
                    captured_at=utcnow(),
                    qa_status="pending",
                    status="active",
                ),
            )
            cmd.emit(
                "DOC.INGESTED", aggregate_id=doc.id, payload={"document_id": str(doc.id), "category_id": str(cat.id)}
            )
            if cat.is_full_text_indexed and cls != "special":
                idx = cmd.add(
                    DocumentIndex(
                        tenant_id=ctx.tenant_id,
                        document_id=doc.id,
                        institution_id=inst.id,
                        reference_no=doc.reference_no,
                        title=doc.title,
                        keywords=_keywords(doc, cat, inst),
                        body_text=extracted.text or None,
                        text_source=extracted.source,
                        char_count=len(extracted.text),
                        indexed_at=utcnow(),
                    )
                )
                cmd.emit(
                    "DOC.INDEXED",
                    aggregate_id=idx.id,
                    aggregate_kind="document_index",
                    payload={"document_id": str(doc.id), "char_count": len(extracted.text)},
                )
            cmd.note("reference_no", None, doc.reference_no)
            out.append(doc)
    return out


# --------------------------------------------------------------------------- search and registers
def _fulltext_ids(tenant_id: uuid.UUID, q: str, institution_id: uuid.UUID | None, limit: int = 1000) -> list[bytes]:
    words = [w.strip("'’-") for w in WORD_RE.findall(q)]
    words = [w for w in words if len(w) >= 3][:12]
    if not words:
        return []
    boolean = " ".join(f"+{w}*" for w in words)
    sql = (
        "SELECT document_id FROM document_index WHERE tenant_id = %s AND "
        "MATCH(title, keywords, body_text) AGAINST (%s IN BOOLEAN MODE)"
    )
    params: list[Any] = [tenant_id.bytes, boolean]
    if institution_id:
        sql += " AND institution_id = %s"
        params.append(institution_id.bytes)
    sql += " ORDER BY MATCH(title, keywords, body_text) AGAINST (%s IN BOOLEAN MODE) DESC LIMIT %s"
    params += [boolean, limit]
    with connections[current_alias("records")].cursor() as cur:
        cur.execute(sql, params)
        return [bytes(r[0]) for r in cur.fetchall()]


def search(
    ctx: Context,
    *,
    q: str = "",
    institution_id: uuid.UUID | None = None,
    category_code: str = "",
    year: int | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Documents matching words, a reference number, a school, category and year (FR-DOC-204), within the caller's
    scope and access level. Searching across schools needs ``document:search`` (FR-DOC-206)."""
    _require_any(ctx, "document:view", "document:search")
    if institution_id is None and not ctx.has("document:search"):
        raise Forbidden(
            "Searching the documents of every school needs the document search permission. Choose your school.",
            code="DOC-SEARCH-PERMISSION",
        )
    if institution_id is not None:
        inst = _institution(institution_id)
        if not _in_scope(ctx, inst.scope_node_id):
            raise Forbidden("That school is outside your scope.", code="AUTH-SCOPE")
    qs = Document.objects.in_scope().filter(classification__in=_visible_classes(ctx)).exclude(status="disposed")
    if institution_id:
        qs = qs.filter(institution_id=institution_id)
    if category_code:
        qs = qs.filter(category__code=category_code)
    if year:
        qs = qs.filter(reference_no__contains=f"/{year}/") | qs.filter(date_from__year=year)
    q = (q or "").strip()
    ranked: list[bytes] = []
    if q:
        if "/" in q and " " not in q:
            qs = qs.filter(reference_no__istartswith=q)
        else:
            assert ctx.tenant_id is not None
            ranked = _fulltext_ids(ctx.tenant_id, q, institution_id)
            qs = qs.filter(id__in=[uuid.UUID(bytes=b) for b in ranked])
    total = qs.count()
    rows = list(qs[: limit if not ranked else 2000])
    if ranked:
        order = {uuid.UUID(bytes=b): i for i, b in enumerate(ranked)}
        rows.sort(key=lambda d: order.get(d.id, 10**9))
    else:
        rows.sort(key=lambda d: (d.reference_no or ""), reverse=True)
    rows = rows[:limit]
    _audit(
        ctx,
        "document_search",
        None,
        [
            {"field": "query", "new": q[:200]},
            {"field": "institution_id", "new": str(institution_id or "")},
            {"field": "results", "new": total},
        ],
    )
    cats = _cats()
    return {"total": total, "rows": [_row(d, cats) for d in rows]}


def _cats() -> dict[uuid.UUID, DocumentCategory]:
    return {c.id: c for c in categories()}


def _row(d: Document, cats: dict[uuid.UUID, DocumentCategory]) -> dict[str, Any]:
    c = cats.get(d.category_id)
    return {
        "id": str(d.id),
        "reference_no": d.reference_no,
        "title": d.title,
        "category": c.title if c else "",
        "category_code": c.code if c else "",
        "institution_id": str(d.institution_id) if d.institution_id else None,
        "date_from": d.date_from,
        "date_to": d.date_to,
        "session_label": d.session_label,
        "classification": d.classification,
        "level": access.level(d.classification),
        "mime_type": d.mime_type,
        "size_bytes": d.size_bytes,
        "captured_at": d.captured_at,
    }


def institutions_with_documents(ctx: Context) -> list[dict[str, Any]]:
    """Schools in scope that have documents, with counts and storage used (space management)."""
    from django.db.models import Count, Sum

    from syntegra.institutions.models import Institution

    _require_any(ctx, "document:view", "document:search")
    agg = (
        Document.objects.in_scope()
        .filter(classification__in=_visible_classes(ctx))
        .exclude(status="disposed")
        .values("institution_id")
        .annotate(n=Count("id"), size=Sum("size_bytes"))
    )
    by = {a["institution_id"]: a for a in agg}
    insts = {i.id: i for i in Institution.objects.filter(id__in=list(by))}
    out = [
        {"id": str(i), "name": insts[i].name, "code": insts[i].institution_code, "documents": a["n"], "size": a["size"]}
        for i, a in by.items()
        if i in insts
    ]
    out.sort(key=lambda r: str(r["name"]))
    return out


def register(ctx: Context, institution_id: uuid.UUID, q: str = "") -> dict[str, Any]:
    """One school's complete document register, grouped by category with reference numbers (FR-DOC-205)."""
    from syntegra.iam.services import format_address

    _require_any(ctx, "document:view", "document:search")
    inst = _institution(institution_id)
    if not _in_scope(ctx, inst.scope_node_id):
        raise Forbidden("That school is outside your scope.", code="AUTH-SCOPE")
    found = search(ctx, q=q, institution_id=institution_id, limit=5000) if q else None
    qs = (
        Document.objects.in_scope()
        .filter(institution_id=institution_id, classification__in=_visible_classes(ctx))
        .exclude(status="disposed")
    )
    cats = _cats()
    docs = [_row(d, cats) for d in qs.order_by("reference_no")] if found is None else found["rows"]
    hidden = (
        Document.objects.filter(institution_id=institution_id).exclude(status="disposed").count() - qs.count()
        if found is None
        else 0
    )
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in docs:
        groups[r["category"] or "Other"].append(r)
    return {
        "institution": {
            "id": str(inst.id),
            "name": inst.name,
            "code": inst.institution_code,
            "address": format_address(inst.address),
        },
        "groups": sorted(groups.items()),
        "total": len(docs),
        "size": sum(int(r["size_bytes"] or 0) for r in docs),
        "hidden_above_level": max(0, hidden),
        "categories": categories(),
    }


# --------------------------------------------------------------------------- one document
def _load(ctx: Context, document_id: uuid.UUID, purpose: str | None, action: str) -> Document:
    _require_any(ctx, "document:view", "document:search")
    d: Document | None = Document.objects.filter(pk=document_id).exclude(status="disposed").first()
    if d is None or not _in_scope(ctx, d.scope_node_id):
        raise NotFound("Document", document_id)
    if not access.covers(ctx.clearance, d.classification) or d.classification == "special":
        raise Forbidden(
            f"This document is {access.level(d.classification).label}; your access level in this role is "
            f"{access.level(ctx.clearance).label}.",
            code="AUTH-LEVEL",
        )
    if class_rank(d.classification) >= class_rank("restricted"):
        ctx = ctx.with_(purpose=authz.validate_purpose(ctx, purpose))
        authz.require_purpose(d.classification, ctx)
    _audit(ctx, action, d.id, [{"field": "purpose", "new": purpose}] if purpose else None)
    return d


def detail(ctx: Context, document_id: uuid.UUID, purpose: str | None = None) -> dict[str, Any]:
    from syntegra.iam.services import format_address

    d = _load(ctx, document_id, purpose, "document_view")
    inst = _institution(d.institution_id) if d.institution_id else None
    idx = DocumentIndex.objects.filter(document_id=d.id).first()
    row = _row(d, _cats())
    row.update(
        {
            "description": d.description,
            "source_reference": d.source_reference,
            "level_or_class": d.level_or_class,
            "subject_label": d.subject_label,
            "pages": d.page_range,
            "sha256": bytes(d.sha256).hex(),
            "institution": {"name": inst.name, "code": inst.institution_code, "address": format_address(inst.address)}
            if inst
            else None,
            "text_source": idx.text_source if idx else "none",
            "char_count": idx.char_count if idx else 0,
            "text_preview": (idx.body_text or "")[:1500] if idx else "",
            "indexed": idx is not None,
            "purpose": purpose,
        }
    )
    return row


def content(ctx: Context, document_id: uuid.UUID, purpose: str | None = None) -> tuple[bytes, str, str]:
    """The master file (hash-verified), its type and a download name."""
    d = _load(ctx, document_id, purpose, "document_download")
    data = storage.get(d.master_object_key, bytes(d.sha256))
    name = f"{(d.reference_no or str(d.id)).replace('/', '-')}.{textmod.EXTENSIONS.get(d.mime_type, 'bin')}"
    return data, d.mime_type, name


def word_copy(ctx: Context, document_id: uuid.UUID, purpose: str | None = None) -> tuple[bytes, str]:
    """An editable Word copy of the document's text, made on demand and never stored (the scan stays the record)."""
    from syntegra.records import docx

    info = detail(ctx, document_id, purpose)
    d = Document.objects.get(pk=document_id)
    idx = DocumentIndex.objects.filter(document_id=d.id).first()
    body = (idx.body_text or "") if idx else ""
    inst = info["institution"] or {}
    facts = [
        ("Reference", d.reference_no or ""),
        ("School or institution", f"{inst.get('name', '')} ({inst.get('code', '')})"),
        ("Address", inst.get("address", "")),
        ("Category", info["category"]),
        ("Dates", " – ".join(x.isoformat() for x in (d.date_from, d.date_to) if x)),
        ("Session / class / subject", " · ".join(x for x in (d.session_label, d.level_or_class, d.subject_label) if x)),
        ("Paper reference", d.source_reference or ""),
        ("Access level", access.level(d.classification).label),
    ]
    note = (
        f"Word copy made by Syntegra on {utcnow():%d %b %Y %H:%M} UTC for {context.require().actor_label()}. "
        "The scanned original is the record; text read by OCR may contain errors — check against the scan."
    )
    data = docx.build(d.title, facts, body, note)
    _audit(ctx, "document_export_word", d.id)
    return data, f"{(d.reference_no or str(d.id)).replace('/', '-')}.docx"
