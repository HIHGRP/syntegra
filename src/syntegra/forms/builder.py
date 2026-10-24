"""The school's own forms (MFS FRM-101 form builder, FRM-102 forms and Daybook; CR-009 phase 4).

The head builds a form from questions — short and long text, number, date, a choice from a list, yes or no, and a
typed signature — each optional or required, and each shown only when an earlier answer has a given value (for
example "Give details" only when "Does your child have a medical condition?" is "Yes"). A form is filled in by
parents, about their child, or by staff, about a learner. Its level (internal, confidential or restricted) decides
who may read the answers: medical details belong at restricted, which the head holds and a teacher does not.

A form is built as a draft and published. Once published it is never changed: editing starts a new version as a
draft, and publishing that supersedes the old one. Every answer keeps the version it was given on, so a later change
to the questions never changes what a parent was asked.

Answers are checked on the server against the version being filled in: required questions (of those shown),
numbers, dates, choices from the list. A parent who fills a form in again for the same child replaces their own
earlier answers to that version; the date of each is kept.
"""

from __future__ import annotations

import datetime as dt
import re
import uuid
from decimal import Decimal, InvalidOperation
from typing import Any

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.families import portal
from syntegra.forms.models import FormDefinition, FormResponse

KINDS = {
    "text": "Short answer",
    "long_text": "Paragraph",
    "number": "Number",
    "date": "Date",
    "choice": "Choose one from a list",
    "yes_no": "Yes or no",
    "signature": "Signature (typed full name)",
}
FILLED_BY = {"parents": "Parents, about their child", "staff": "Staff, about a learner"}
LEVELS = {"internal": "Internal", "confidential": "Confidential", "restricted": "Restricted (e.g. medical details)"}
MAX_FIELDS = 30
MAX_TEXT = {"text": 200, "long_text": 2000, "signature": 120}


def _institution(institution_id: uuid.UUID) -> Any:
    from syntegra.institutions.models import Institution

    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def _form(form_id: uuid.UUID) -> FormDefinition:
    f: FormDefinition | None = FormDefinition.objects.in_scope().filter(pk=form_id).first()
    if f is None:
        raise NotFound("form_definition", form_id)
    return f


def _fields(f: FormDefinition) -> list[dict[str, Any]]:
    return list((f.field_schema or {}).get("fields", []))


def _who(f: FormDefinition) -> str:
    roles = f.raised_by_roles or []
    return "parents" if "parents" in roles else "staff"


def create(institution_id: uuid.UUID, *, title: str, intro: str | None, filled_by: str, level: str) -> FormDefinition:
    inst = _institution(institution_id)
    title = (title or "").strip()
    if len(title) < 4:
        raise HardValidation("FRM-TITLE", "Give the form a title", "For example: Medical information.")
    if filled_by not in FILLED_BY:
        raise HardValidation("FRM-WHO", "Who fills it in", "Parents or staff.")
    if level not in LEVELS:
        raise HardValidation("FRM-LEVEL", "Who may read the answers", ", ".join(LEVELS.values()))
    code = re.sub(r"[^A-Z0-9]+", "-", title.upper()).strip("-")[:30] or "FORM"
    taken = set(FormDefinition.objects.filter(scope_node_id=inst.scope_node_id).values_list("code", flat=True))
    base, n = code, 2
    while code in taken:
        code = f"{base[:27]}-{n}"
        n += 1
    with uow.command("ops", "form:manage", action="create_form", record_kind="form_definition") as cmd:
        return cmd.add(
            FormDefinition(
                scope_node_id=inst.scope_node_id,
                code=code,
                title=title,
                field_schema={"intro": (intro or "").strip()[:1000] or None, "fields": []},
                raised_by_roles=[filled_by],
                confidentiality=level,
                requires_payment_before_continue=False,
                files_to="learner",
                is_template_library=False,
                version=1,
                status="draft",
            )
        )


def _draft(form_id: uuid.UUID) -> FormDefinition:
    f = _form(form_id)
    if f.status != "draft":
        raise ConflictError("FRM-PUBLISHED", "A published form is not changed", "Start a new version to edit it.")
    return f


def add_field(
    form_id: uuid.UUID,
    *,
    label: str,
    kind: str,
    required: bool,
    options: list[str] | None = None,
    help_text: str | None = None,
    show_if_key: str | None = None,
    show_if_value: str | None = None,
) -> FormDefinition:
    f = _draft(form_id)
    fields = _fields(f)
    label = (label or "").strip()
    if len(label) < 3:
        raise HardValidation("FRM-FIELD", "Write the question", "At least a few words.")
    if kind not in KINDS:
        raise HardValidation("FRM-FIELD", "Choose the kind of answer", ", ".join(KINDS.values()))
    if len(fields) >= MAX_FIELDS:
        raise HardValidation("FRM-FIELD", "The form is long enough", f"At most {MAX_FIELDS} questions.")
    opts = [o.strip() for o in (options or []) if o.strip()]
    if kind == "choice" and not (2 <= len(opts) <= 12):
        raise HardValidation("FRM-FIELD", "Give the choices", "Between 2 and 12, one per line.")
    field: dict[str, Any] = {
        "key": f"q{max((int(x['key'][1:]) for x in fields), default=0) + 1}",
        "label": label[:300],
        "kind": kind,
        "required": bool(required),
        "options": opts if kind == "choice" else [],
        "help": (help_text or "").strip()[:300] or None,
        "show_if": None,
    }
    if show_if_key:
        src = next((x for x in fields if x["key"] == show_if_key), None)
        if src is None or src["kind"] not in ("yes_no", "choice"):
            raise HardValidation("FRM-FIELD", "Show it after a yes/no or a choice question", "Pick one above it.")
        allowed = ["yes", "no"] if src["kind"] == "yes_no" else src["options"]
        if show_if_value not in allowed:
            raise HardValidation("FRM-FIELD", "Choose the answer that shows it", ", ".join(allowed))
        field["show_if"] = {"key": show_if_key, "equals": show_if_value}
    schema = dict(f.field_schema or {})
    schema["fields"] = [*fields, field]
    with uow.command("ops", "form:manage", action="edit_form", record_kind="form_definition") as cmd:
        return cmd.update(f, field_schema=schema)


def remove_field(form_id: uuid.UUID, key: str) -> FormDefinition:
    f = _draft(form_id)
    fields = _fields(f)
    if not any(x["key"] == key for x in fields):
        raise NotFound("form field", key)
    if any((x.get("show_if") or {}).get("key") == key for x in fields):
        raise ConflictError("FRM-FIELD", "Another question depends on this one", "Remove that question first.")
    schema = dict(f.field_schema or {})
    schema["fields"] = [x for x in fields if x["key"] != key]
    with uow.command("ops", "form:manage", action="edit_form", record_kind="form_definition") as cmd:
        return cmd.update(f, field_schema=schema)


def publish(form_id: uuid.UUID) -> FormDefinition:
    f = _draft(form_id)
    if not _fields(f):
        raise HardValidation("FRM-EMPTY", "The form has no questions", "Add at least one question.")
    with uow.command("ops", "form:manage", action="publish_form", record_kind="form_definition") as cmd:
        for old in FormDefinition.objects.filter(scope_node_id=f.scope_node_id, code=f.code, status="published"):
            cmd.update(old, status="superseded")
        return cmd.update(f, status="published")


def new_version(form_id: uuid.UUID) -> FormDefinition:
    f = _form(form_id)
    if f.status != "published":
        raise ConflictError("FRM-DRAFT", "Only a published form gets a new version", "Edit the draft directly.")
    if FormDefinition.objects.filter(scope_node_id=f.scope_node_id, code=f.code, status="draft").exists():
        raise ConflictError("FRM-DRAFT", "A new version is already being drafted", "Open it from the list.")
    with uow.command("ops", "form:manage", action="new_form_version", record_kind="form_definition") as cmd:
        return cmd.add(
            FormDefinition(
                scope_node_id=f.scope_node_id,
                code=f.code,
                title=f.title,
                field_schema=f.field_schema,
                raised_by_roles=f.raised_by_roles,
                confidentiality=f.confidentiality,
                requires_payment_before_continue=False,
                files_to=f.files_to,
                is_template_library=False,
                version=f.version + 1,
                status="draft",
            )
        )


def withdraw(form_id: uuid.UUID) -> FormDefinition:
    f = _form(form_id)
    if f.status != "published":
        raise ConflictError("FRM-STATE", "Only a published form is withdrawn", "")
    with uow.command("ops", "form:manage", action="withdraw_form", record_kind="form_definition") as cmd:
        return cmd.update(f, status="withdrawn")


def _view(f: FormDefinition) -> dict[str, Any]:
    fields = _fields(f)
    labels = {x["key"]: x["label"] for x in fields}
    return {
        "id": f.id,
        "code": f.code,
        "title": f.title,
        "intro": (f.field_schema or {}).get("intro"),
        "fields": [
            {
                **x,
                "kind_label": KINDS.get(x["kind"], x["kind"]),
                "show_if_label": labels.get((x.get("show_if") or {}).get("key", "")),
            }
            for x in fields
        ],
        "filled_by": _who(f),
        "filled_by_label": FILLED_BY[_who(f)],
        "level": f.confidentiality,
        "level_label": LEVELS.get(f.confidentiality, f.confidentiality),
        "version": f.version,
        "status": f.status,
    }


def school_forms(institution_id: uuid.UUID) -> dict[str, Any]:
    """The head's list: each form's current published version and any draft, with the number of answers."""
    authz.require("form:manage")
    inst = _institution(institution_id)
    rows: dict[str, dict[str, Any]] = {}
    for f in FormDefinition.objects.in_scope().filter(scope_node_id=inst.scope_node_id).order_by("code", "version"):
        r = rows.setdefault(
            f.code, {"code": f.code, "published": None, "draft": None, "withdrawn": None, "versions": 0, "answers": 0}
        )
        r["versions"] += 1
        if f.status == "published":
            r["published"] = _view(f)
        elif f.status == "draft":
            r["draft"] = _view(f)
        elif f.status == "withdrawn" and r["published"] is None:
            r["withdrawn"] = _view(f)
    ids = list(FormDefinition.objects.filter(scope_node_id=inst.scope_node_id).values_list("id", "code"))
    by_id = dict(ids)
    for fid in FormResponse.objects.filter(form_id__in=list(by_id), status="submitted").values_list(
        "form_id", flat=True
    ):
        rows[by_id[fid]]["answers"] += 1
    return {
        "institution": {"id": inst.id, "name": inst.name},
        "forms": sorted(rows.values(), key=lambda r: (r["published"] or r["draft"] or {}).get("title", r["code"])),
        "kinds": KINDS,
        "filled_by": FILLED_BY,
        "levels": LEVELS,
    }


def form(form_id: uuid.UUID) -> dict[str, Any]:
    f = _form(form_id)
    if f.status == "draft":
        authz.require("form:manage")
    return _view(f)


# --------------------------------------------------------------------------- filling in
def _shown(field: dict[str, Any], answers: dict[str, Any]) -> bool:
    cond = field.get("show_if")
    return not cond or answers.get(cond["key"]) == cond["equals"]


def check(f: FormDefinition, raw: dict[str, str]) -> dict[str, Any]:
    """The answers to keep, checked against the form; raises with every problem listed."""
    answers: dict[str, Any] = {}
    problems = []
    for x in _fields(f):
        if not _shown(x, answers):
            continue
        v = (raw.get(x["key"]) or "").strip()
        if not v:
            if x["required"]:
                problems.append(f"“{x['label']}” needs an answer")
            continue
        kind = x["kind"]
        if kind in MAX_TEXT and len(v) > MAX_TEXT[kind]:
            problems.append(f"“{x['label']}” is too long (at most {MAX_TEXT[kind]} characters)")
        elif kind == "number":
            try:
                answers[x["key"]] = str(Decimal(v.replace(",", "")))
                continue
            except InvalidOperation:
                problems.append(f"“{x['label']}” must be a number")
        elif kind == "date":
            try:
                answers[x["key"]] = dt.date.fromisoformat(v).isoformat()
                continue
            except ValueError:
                problems.append(f"“{x['label']}” must be a date")
        elif kind == "choice" and v not in x["options"]:
            problems.append(f"“{x['label']}”: choose from the list")
        elif kind == "yes_no" and v not in ("yes", "no"):
            problems.append(f"“{x['label']}”: answer yes or no")
        elif kind == "signature" and len(v.split()) < 2:
            problems.append(f"“{x['label']}”: type your full name")
        answers[x["key"]] = v
    if problems:
        raise HardValidation("FRM-ANSWERS", "Please check the form", "; ".join(problems) + ".")
    return answers


def for_parent() -> list[dict[str, Any]]:
    """The published forms parents fill in, for each child, with when this parent last sent each."""
    kids = portal.children()
    if not kids:
        return []
    forms = list(FormDefinition.objects.in_scope().filter(status="published").order_by("title"))
    forms = [f for f in forms if _who(f) == "parents"]
    me = context.require().actor_id
    sent = {
        (r.form_id, r.subject_id): r
        for r in FormResponse.objects.filter(
            form_id__in=[f.id for f in forms], subject_id__in=[k["id"] for k in kids], submitted_by=me
        ).order_by("submitted_at")
    }
    return [
        {
            **k,
            "forms": [
                {
                    "id": f.id,
                    "title": f.title,
                    "version": f.version,
                    "sent_at": sent[(f.id, k["id"])].submitted_at if (f.id, k["id"]) in sent else None,
                }
                for f in forms
            ],
        }
        for k in kids
    ]


def for_staff(institution_id: uuid.UUID) -> list[dict[str, Any]]:
    inst = _institution(institution_id)
    return [
        _view(f)
        for f in FormDefinition.objects.in_scope()
        .filter(scope_node_id=inst.scope_node_id, status="published")
        .order_by("title")
        if _who(f) == "staff"
    ]


def previous(form_id: uuid.UUID, learner_id: uuid.UUID) -> dict[str, Any] | None:
    """The signed-in person's own earlier answers to this version, to fill the form with."""
    r = FormResponse.objects.filter(
        form_id=form_id, subject_id=learner_id, submitted_by=context.require().actor_id, status="submitted"
    ).first()
    return {"answers": r.answers, "at": r.submitted_at} if r else None


def submit(form_id: uuid.UUID, learner_id: uuid.UUID, raw: dict[str, str]) -> tuple[FormResponse, bool]:
    """Send the form about a learner. Returns the response and whether it replaced this person's earlier one."""
    from syntegra.academic.models import ClassGroup, ClassMembership

    ctx = context.require()
    f = _form(form_id)
    if f.status != "published":
        raise ConflictError("FRM-CLOSED", "This form is no longer in use", "The school has replaced or withdrawn it.")
    if _who(f) == "parents":
        authz.require("form:submit", ctx)
        portal.require_child(learner_id)
    else:
        authz.require("form:fill", ctx)
        cls = (
            ClassMembership.objects.filter(learner_id=learner_id, is_arm=True, valid_to__isnull=True)
            .values_list("class_group_id", flat=True)
            .first()
        )
        if cls is None or not ClassGroup.objects.in_scope().filter(pk=cls, scope_node_id=f.scope_node_id).exists():
            raise HardValidation("FRM-LEARNER", "The learner is not at this school", "Choose a learner from a class.")
    answers = check(f, raw)
    now = utcnow()
    with uow.command("ops", None, action="submit_form", record_kind="form_response") as cmd:
        earlier = FormResponse.objects.filter(
            form_id=f.id, subject_id=learner_id, submitted_by=ctx.actor_id, status="submitted"
        ).first()
        if earlier is not None:
            return cmd.update(earlier, answers=answers, submitted_at=now), True
        return (
            cmd.add(
                FormResponse(
                    scope_node_id=f.scope_node_id,
                    form_id=f.id,
                    form_version=f.version,
                    subject_kind="learner",
                    subject_id=learner_id,
                    submitted_by=ctx.actor_id,
                    answers=answers,
                    submitted_at=now,
                    status="submitted",
                )
            ),
            False,
        )


def responses(form_id: uuid.UUID, class_id: uuid.UUID | None = None) -> dict[str, Any]:
    """Every answer to the form (all its versions), by learner. Needs the form's level."""
    from syntegra.academic.models import ClassGroup, ClassMembership
    from syntegra.iam.models import AppUser
    from syntegra.learners.models import Learner

    ctx = context.require()
    authz.require("form:manage", ctx)
    f = _form(form_id)
    if not ctx.cleared_for(f.confidentiality):
        raise Forbidden(
            f"The answers to this form are {LEVELS[f.confidentiality].lower()}; your access level does not cover them.",
            code="AUTH-LEVEL",
        )
    versions = {v.id: v for v in FormDefinition.objects.filter(scope_node_id=f.scope_node_id, code=f.code)}
    rs = list(FormResponse.objects.filter(form_id__in=list(versions), status="submitted").order_by("-submitted_at"))
    members = {
        m.learner_id: m.class_group_id
        for m in ClassMembership.objects.filter(
            learner_id__in={r.subject_id for r in rs}, is_arm=True, valid_to__isnull=True
        )
    }
    if class_id is not None:
        rs = [r for r in rs if members.get(r.subject_id) == class_id]
    learners = {lr.id: lr for lr in Learner.objects.filter(id__in={r.subject_id for r in rs})}
    classes = {c.id: c.name for c in ClassGroup.objects.filter(id__in=set(members.values()))}
    people = {u.id: u.display_name for u in AppUser.objects.filter(id__in={r.submitted_by for r in rs})}
    latest = versions[max(versions, key=lambda k: versions[k].version)]
    columns = _fields(latest)
    for v in sorted(versions.values(), key=lambda v: -v.version):
        for x in _fields(v):
            if x["key"] not in {c["key"] for c in columns}:
                columns.append(x)
    return {
        "form": _view(f),
        "columns": [{"key": c["key"], "label": c["label"]} for c in columns],
        "rows": [
            {
                "learner": (
                    f"{learners[r.subject_id].legal_family_name}, {learners[r.subject_id].legal_given_name}"
                    if r.subject_id in learners
                    else "Learner"
                ),
                "class": classes.get(members.get(r.subject_id), ""),
                "by": people.get(r.submitted_by, ""),
                "at": r.submitted_at,
                "version": r.form_version,
                "answers": r.answers,
            }
            for r in rs
        ],
        "classes": sorted(classes.items(), key=lambda x: x[1]),
    }
