"""Evidence-grade handling of document masters (CR-008): retention locks, searchable access copies and releases.

* The master is stored once, write-once, and — on object storage — locked in compliance mode until the end of its
  file-plan retention (``retain_until``); it is never altered.
* A scanned document gets a searchable PDF access copy (``document_rendition``): the page images with the OCR words
  laid invisibly over them, stored write-once with its own hash and the hash of the master it was made from.
* Every copy that leaves the system is a release (``document_release``): stamped on every page with the recipient,
  time, purpose and a release code — or, for holders of ``document:certify`` with a reason, a certified true copy of
  the master, byte for byte. The register records the hash of what was released, so a copy presented later can be
  checked against it.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import secrets
import uuid
from dataclasses import dataclass
from typing import Any

from django.conf import settings

from syntegra.core import storage, uow
from syntegra.core.context import Context
from syntegra.core.errors import Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.records import pdfcopy
from syntegra.records import text as textmod
from syntegra.records.models import Document, DocumentRelease, DocumentRendition

RELEASE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I: codes are read aloud and typed from paper
KINDS = {
    "stamped_original": "Stamped copy of the scan",
    "stamped_searchable": "Stamped searchable copy",
    "word_copy": "Word copy (stamped)",
    "certified_original": "Certified true copy of the master",
}


# --------------------------------------------------------------------------- retention locks
def retain_until(category_code: str, captured: dt.date) -> dt.date:
    """End of the file-plan retention for the category; permanent records are locked for a long configured period."""
    from syntegra.records.services import CATEGORIES

    years = next((y for c, _t, _cls, y in CATEGORIES if c == category_code), None)
    if years is None:
        years = int(getattr(settings, "SYNTEGRA_PERMANENT_RETENTION_YEARS", 100))
    try:
        return captured.replace(year=captured.year + years)
    except ValueError:  # 29 February
        return captured.replace(year=captured.year + years, day=28)


# --------------------------------------------------------------------------- searchable access copy
def make_searchable(cmd: uow.Command, doc: Document, extracted: textmod.Extracted) -> DocumentRendition | None:
    """A searchable PDF of a scanned document, from the pages OCR has just read (no second OCR pass)."""
    if not extracted.ocr:
        return None
    import tesserocr

    engine = tesserocr.tesseract_version().splitlines()[0]
    data = pdfcopy.searchable_pdf(
        extracted.ocr, title=f"{doc.reference_no} — {doc.title}", producer=f"Syntegra searchable copy; {engine}"
    )
    stored = storage.put(
        data,
        prefix=f"records/{doc.tenant_id}/copies",
        ext="pdf",
        retain_until=doc.master_retain_until,
        content_type=textmod.PDF,
    )
    rendition = cmd.add(
        DocumentRendition(
            tenant_id=doc.tenant_id,
            document_id=doc.id,
            kind="searchable_pdf",
            object_key=stored.key,
            store=stored.store,
            mime_type=textmod.PDF,
            size_bytes=stored.size,
            sha256=stored.sha256,
            source_sha256=bytes(doc.sha256),
            pages=len(extracted.ocr),
            generator=f"Syntegra searchable copy; {engine}"[:120],
        )
    )
    cmd.emit(
        "DOC.RENDITION_CREATED",
        aggregate_id=rendition.id,
        aggregate_kind="document_rendition",
        payload={"document_id": str(doc.id), "kind": "searchable_pdf"},
    )
    return rendition


def searchable_copy(document_id: uuid.UUID) -> DocumentRendition | None:
    return DocumentRendition.objects.filter(document_id=document_id, kind="searchable_pdf").first()


# --------------------------------------------------------------------------- releases
@dataclass(frozen=True)
class Released:
    data: bytes
    mime: str
    filename: str
    code: str
    kind: str


def _code() -> str:
    raw = "".join(secrets.choice(RELEASE_ALPHABET) for _ in range(12))
    return f"{raw[:4]}-{raw[4:8]}-{raw[8:]}"


def _recipient(ctx: Context) -> str:
    from syntegra.iam.models import AppUser

    u = AppUser.unscoped.using(_registry()).filter(pk=ctx.actor_id).first() if ctx.actor_id else None
    name = u.display_name if u else "system"
    return f"{name} ({ctx.role_code})" if ctx.role_code else name


def _registry() -> str:
    from syntegra.core.zones import current_alias

    return current_alias("registry")


def _local(ts: dt.datetime) -> str:
    from django.utils import timezone

    local = timezone.localtime(ts)
    return f"{local:%d %b %Y %H:%M} {local.tzname() or 'UTC'}"


def release(
    ctx: Context,
    document_id: uuid.UUID,
    kind: str,
    *,
    purpose: str | None = None,
    reason: str | None = None,
) -> Released:
    """Release one copy of a document: stamped (scan, searchable copy or Word) or a certified true copy of the
    master. Access is checked as for viewing; the copy and its hash are entered in the release register."""
    from syntegra.records import services as rec

    if kind not in KINDS:
        raise HardValidation("DOC-RELEASE-KIND", "Unknown kind of copy", "Choose the scan, searchable copy or Word.")
    if kind == "certified_original":
        if not ctx.has("document:certify"):
            raise Forbidden("A certified true copy needs the document:certify permission.", code="AUTH-PERMISSION")
        if len((reason or "").strip()) < 10:
            raise HardValidation(
                "DOC-CERTIFY-REASON",
                "Give the reason",
                "Say why a certified true copy is needed, e.g. the court order.",
            )
    d = rec._load(ctx, document_id, purpose, f"document_release_{kind}")
    master = storage.get(d.master_object_key, bytes(d.sha256), d.master_store)
    code = _code()
    now = utcnow()
    stamp = pdfcopy.Stamp(
        recipient=_recipient(ctx),
        released_at=_local(now),
        purpose=purpose or "",
        code=code,
        reference=d.reference_no or str(d.id),
        issuer=str(getattr(settings, "SYNTEGRA_RELEASE_ISSUER", "Syntegra")),
    )
    base = (d.reference_no or str(d.id)).replace("/", "-")
    if kind == "certified_original":
        data, mime = master, d.mime_type
        filename = f"{base}-certified-{code}.{textmod.EXTENSIONS.get(d.mime_type, 'bin')}"
    elif kind == "stamped_searchable":
        r = searchable_copy(d.id)
        if r is None:
            raise NotFound("Searchable copy", d.id)
        copy = storage.get(r.object_key, bytes(r.sha256), r.store)
        data, mime, filename = pdfcopy.stamp_pdf(copy, stamp), textmod.PDF, f"{base}-searchable-{code}.pdf"
    elif kind == "word_copy":
        data, filename = rec.word_copy_bytes(d, stamp), f"{base}-{code}.docx"
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif d.mime_type == textmod.PDF:
        data, mime, filename = pdfcopy.stamp_pdf(master, stamp), textmod.PDF, f"{base}-{code}.pdf"
    elif d.mime_type in textmod.IMAGES:
        as_pdf = pdfcopy.images_to_pdf(master, d.mime_type, f"{d.reference_no} — {d.title}")
        data, mime, filename = pdfcopy.stamp_pdf(as_pdf, stamp), textmod.PDF, f"{base}-{code}.pdf"
    else:  # a text file: the stamp leads the text
        head = "\n".join(stamp.lines()) + "\n" + "-" * 72 + "\n"
        data, mime, filename = head.encode() + master, "text/plain; charset=utf-8", f"{base}-{code}.txt"
    with uow.command("records", None, action="document_release", record_kind="document_release", ctx=ctx) as cmd:
        if reason:
            cmd.reason = reason.strip()[:500]
        row = cmd.add(
            DocumentRelease(
                tenant_id=d.tenant_id,
                document_id=d.id,
                release_code=code,
                kind=kind,
                released_to=ctx.actor_id,
                released_to_name=stamp.recipient[:200],
                purpose=purpose,
                reason=(reason or "").strip()[:500] or None,
                sha256=hashlib.sha256(data).digest(),
                size_bytes=len(data),
                released_at=now,
            )
        )
        cmd.emit(
            "DOC.RELEASED",
            aggregate_id=row.id,
            aggregate_kind="document_release",
            payload={"document_id": str(d.id), "kind": kind, "release_code": code},
        )
    return Released(data, mime, filename, code, kind)


def _release_row(r: DocumentRelease, docs: dict[uuid.UUID, Document]) -> dict[str, Any]:
    d = docs.get(r.document_id)
    return {
        "code": r.release_code,
        "kind": r.kind,
        "kind_label": KINDS.get(r.kind, r.kind),
        "document_id": str(r.document_id),
        "reference_no": d.reference_no if d else "",
        "title": d.title if d else "",
        "released_to": r.released_to_name,
        "purpose": r.purpose or "",
        "reason": r.reason or "",
        "sha256": bytes(r.sha256).hex(),
        "size_bytes": r.size_bytes,
        "released_at": r.released_at,
    }


def _require_register(ctx: Context) -> None:
    if not (ctx.has("document:releases") or ctx.is_system):
        raise Forbidden("The release register needs the document:releases permission.", code="AUTH-PERMISSION")


def releases(ctx: Context, *, document_id: uuid.UUID | None = None, limit: int = 200) -> list[dict[str, Any]]:
    """Recent releases of documents in the caller's scope (DOC-109)."""
    _require_register(ctx)
    docs_qs = Document.objects.in_scope()
    if document_id:
        docs_qs = docs_qs.filter(pk=document_id)
    qs = DocumentRelease.objects.filter(document_id__in=docs_qs.values("id")).order_by("-released_at")[:limit]
    rows = list(qs)
    docs = {d.id: d for d in Document.objects.filter(id__in=[r.document_id for r in rows])}
    return [_release_row(r, docs) for r in rows]


def lookup(ctx: Context, code: str, presented: bytes | None = None) -> dict[str, Any]:
    """Who received the copy carrying this release code; with ``presented``, whether a file is that exact copy."""
    from syntegra.records import services as rec

    _require_register(ctx)
    code = (code or "").strip().upper().replace(" ", "")
    if len(code) == 12 and "-" not in code:
        code = f"{code[:4]}-{code[4:8]}-{code[8:]}"
    r = DocumentRelease.objects.filter(release_code=code).first()
    d = Document.objects.filter(pk=r.document_id).first() if r else None
    if r is None or d is None or not rec._in_scope(ctx, d.scope_node_id):
        raise NotFound("Release", code)
    row = _release_row(r, {d.id: d})
    if presented is not None:
        digest = hashlib.sha256(presented).digest()
        row["presented_sha256"] = digest.hex()
        row["presented_matches"] = digest == bytes(r.sha256)
        row["presented_is_master"] = digest == bytes(d.sha256)
    rec._audit(ctx, "document_release_checked", d.id, [{"field": "release_code", "new": code}])
    return row
