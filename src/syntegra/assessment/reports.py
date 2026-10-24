"""Report cards — fully personalised school reports (MFS ASM-04, FR-ASM-06 – FR-ASM-08).

A termly report for every learner of a class, drawn from the class's marksheets and attendance registers: each
subject with its continuous assessment, examination, total out of 100, grade and remark, the learner's position in
the subject and the class's average, highest and lowest; the overall average and position in the class; attendance
for the term; a form teacher's and a head's comment; and the grading key. The comments are drafted for each learner
from their own results and attendance (strongest and weakest subjects, how they stand in the class, attendance
against the 90 % expected) and can be edited before the report cards are issued.

Issue is the head's: it needs every assessment of the term locked and no mark left blank without a reason. Each
learner's report card is written as a PDF with the school's name and address and the state's coat of arms, stored in
the school's document register (category RES, confidential, write-once) and recorded in a report-card run with the
PDF's SHA-256, so a copy can always be proved against the original.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import logging
import unicodedata
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

from syntegra.academic.models import AcademicPeriod, ClassGroup, ClassSubjectPlan, Subject
from syntegra.assessment import services
from syntegra.assessment.markbook import REMARK, _members, current_term, ordinal, positions, terms
from syntegra.assessment.models import Assessment, AssessmentResult, ReportCard, ReportCardRun
from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.core.fields import utcnow

TEMPLATE = "termly-v1"
EXPECTED_ATTENDANCE = 0.90
FONT_DIRS = ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu-sans-fonts", "/usr/share/fonts/dejavu")
KEY = (("A1", "75–100"), ("B2", "70–74"), ("B3", "65–69"), ("C4", "60–64"), ("C5", "55–59"), ("C6", "50–54"),
       ("D7", "45–49"), ("E8", "40–44"), ("F9", "0–39"))  # fmt: skip


def _class(class_id: uuid.UUID) -> ClassGroup:
    cls: ClassGroup | None = ClassGroup.objects.in_scope().filter(pk=class_id).first()
    if cls is None:
        raise NotFound("class", class_id)
    return cls


def _terms(cls: ClassGroup) -> tuple[AcademicPeriod | None, AcademicPeriod | None]:
    """The term being reported on (the one running today, else the last one started) and the next term."""
    term = current_term(cls)
    later = [t for t in terms(cls) if term is not None and t.starts_on > term.starts_on]
    return term, (later[0] if later else None)


def _institution(cls: ClassGroup) -> dict[str, Any]:
    from syntegra.institutions.models import Institution
    from syntegra.people.models import Staff

    inst = Institution.objects.get(pk=cls.institution_id)
    addr = inst.address or {}
    head = Staff.objects.filter(pk=inst.head_staff_id).first() if inst.head_staff_id else None
    primary = cls.education_level.upper().startswith(("P", "ECCDE", "NUR", "KG"))
    return {
        "id": inst.id,
        "name": inst.name,
        "code": inst.institution_code,
        "address": ", ".join(str(addr[k]) for k in ("street", "town", "lga", "state") if addr.get(k)),
        "phone": inst.phone,
        "email": inst.email,
        "head_title": "Head teacher" if primary else "Principal",
        "head_name": f"{head.given_name} {head.family_name}" if head else None,
    }


def _staff_name(staff_id: uuid.UUID | None) -> str | None:
    from syntegra.people.models import Staff

    s = Staff.objects.filter(pk=staff_id).first() if staff_id else None
    return f"{s.given_name} {s.family_name}" if s else None


def _attendance(learner_ids: list[uuid.UUID], start: dt.date, end: dt.date) -> dict[uuid.UUID, dict[str, Any]]:
    from syntegra.attendance.domain import rates
    from syntegra.attendance.models import AttendanceMark

    codes: dict[uuid.UUID, list[str]] = {lid: [] for lid in learner_ids}
    for lid, code in AttendanceMark.objects.filter(
        learner_id__in=learner_ids, session_date__gte=start, session_date__lte=end
    ).values_list("learner_id", "code"):
        codes[lid].append(code)
    out = {}
    for lid, cs in codes.items():
        s = rates.summarise(cs)
        out[lid] = {"possible": s.possible, "attended": s.attended, "late": s.late, "rate": s.rate}
    return out


def _run(cls: ClassGroup, term: AcademicPeriod | None) -> ReportCardRun | None:
    if term is None:
        return None
    for run in ReportCardRun.objects.filter(
        institution_id=cls.institution_id, period_id=term.id, template_code=TEMPLATE
    ).exclude(status="cancelled"):
        if str(cls.id) in [str(x) for x in run.class_group_ids or []]:
            found: ReportCardRun = run
            return found
    return None


# ------------------------------------------------------------------------------------- personalised comments
def _join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def draft_comments(learner: dict[str, Any], of: int) -> dict[str, str]:
    """A form teacher's and a head's comment written for this learner from their own term: how they stand, their
    strongest and weakest subjects, and attendance. Plain rules, so the same results always draft the same words."""
    name = learner["first_name"]
    avg = learner["average"]
    subjects = [s for s in learner["subjects"] if s["total"] is not None]
    if avg is None or not subjects:
        return {"form": f"{name} has no marks recorded this term.", "head": "Results to follow."}
    ranked = sorted(subjects, key=lambda s: -s["total"])
    best = [s["subject"] for s in ranked[:2] if s["total"] >= 60]
    weak = [s for s in ranked[::-1] if s["total"] < 50][:2]
    pos = learner["position"]
    if avg >= 75:
        opening = f"{name} has had an excellent term, finishing {pos} of {of} with an average of {avg:.1f}%."
    elif avg >= 60:
        opening = f"{name} has worked well this term, with an average of {avg:.1f}% ({pos} of {of})."
    elif avg >= 50:
        opening = f"{name} has made steady progress this term, with an average of {avg:.1f}% ({pos} of {of})."
    elif avg >= 40:
        opening = f"{name} has passed this term with an average of {avg:.1f}% ({pos} of {of}) but can do better."
    else:
        opening = f"{name} has found this term difficult, with an average of {avg:.1f}% ({pos} of {of})."
    parts = [opening]
    if best:
        parts.append(f"The work in {_join(best)} is a real strength.")
    if weak:
        parts.append(
            f"More practice is needed in {_join([s['subject'] for s in weak])}"
            f" ({', '.join(f'{s["total"]:.0f}%' for s in weak)})."
        )
    rate = learner["attendance"]["rate"]
    if rate is not None and learner["attendance"]["possible"]:
        if rate < EXPECTED_ATTENDANCE:
            parts.append(
                f"Attendance of {rate * 100:.0f}% is below the 90% expected; coming to school every day will help."
            )
        elif rate >= 0.97:
            parts.append("Attendance has been excellent.")
    weakest = weak[0]["subject"] if weak else ranked[-1]["subject"]
    if avg >= 75:
        head = f"An outstanding result, {name}. Keep it up."
    elif avg >= 60:
        head = f"A good result. Aim higher still in {weakest} next term."
    elif avg >= 50:
        head = f"A fair result. With more effort in {weakest}, {name} can move up the class."
    elif avg >= 40:
        head = f"{name} must work harder next term, above all in {weakest}."
    else:
        head = f"{name} needs support: the school will arrange extra lessons in {weakest}. Parents, please see me."
    return {"form": " ".join(parts), "head": head}


# ---------------------------------------------------------------------------------------- the class's reports
def class_reports(class_id: uuid.UUID) -> dict[str, Any]:
    """Every learner's report for the term, with the class's completeness and any issue already made."""
    ctx = context.require()
    authz.require("assessment:view", ctx)
    cls = _class(class_id)
    term, next_term = _terms(cls)
    plans = {
        p.id: p for p in ClassSubjectPlan.objects.filter(class_group_id=cls.id).exclude(valid_to__lt=dt.date.today())
    }
    names = dict(Subject.objects.filter(id__in=[p.subject_id for p in plans.values()]).values_list("id", "name"))
    order = sorted(plans, key=lambda pid: names.get(plans[pid].subject_id, ""))
    qs = Assessment.objects.filter(class_subject_plan_id__in=list(plans))
    if term is not None:
        qs = qs.filter(assessed_on__gte=term.starts_on, assessed_on__lte=term.ends_on)
    columns = list(qs)
    by_plan: dict[uuid.UUID, list[Assessment]] = {}
    for a in columns:
        by_plan.setdefault(a.class_subject_plan_id, []).append(a)
    learners = _members(cls)
    lids = [lr.id for lr in learners]
    results = {
        (r.assessment_id, r.learner_id): r
        for r in AssessmentResult.objects.filter(assessment_id__in=[a.id for a in columns], learner_id__in=lids)
    }
    # per subject: each learner's CA, examination and total out of 100
    marks: dict[uuid.UUID, dict[uuid.UUID, dict[str, Any]]] = {pid: {} for pid in order}
    missing: dict[uuid.UUID, list[str]] = {}
    for pid in order:
        cols = by_plan.get(pid, [])
        weight = float(sum((a.weight for a in cols), Decimal(0)))
        for lid in lids:
            ca = ex = 0.0
            seen = False
            for a in cols:
                r = results.get((a.id, lid))
                if r is None or r.score is None:
                    if r is None or not r.is_missing_work:
                        missing.setdefault(lid, []).append(f"{names.get(plans[pid].subject_id)} — {a.title}")
                    continue
                part = float(r.score / a.max_mark * a.weight)
                seen = True
                if a.assessment_kind == "examination":
                    ex += part
                else:
                    ca += part
            scale = 100 / weight if weight else 0
            marks[pid][lid] = {
                "ca": round(ca * scale, 1) if seen else None,
                "exam": round(ex * scale, 1) if seen else None,
                "total": round((ca + ex) * scale, 1) if seen else None,
            }
    stats: dict[uuid.UUID, dict[str, Any]] = {}
    for pid in order:
        totals = {lid: m["total"] for lid, m in marks[pid].items() if m["total"] is not None}
        vals = list(totals.values())
        stats[pid] = {
            "positions": positions(totals),
            "average": round(sum(vals) / len(vals), 1) if vals else None,
            "highest": max(vals) if vals else None,
            "lowest": min(vals) if vals else None,
        }
    averages: dict[uuid.UUID, float] = {}
    for lid in lids:
        vals = [marks[pid][lid]["total"] for pid in order if marks[pid][lid]["total"] is not None]
        if vals:
            averages[lid] = round(sum(vals) / len(vals), 1)
    overall = positions(averages)
    end = min(term.ends_on, dt.date.today()) if term is not None else dt.date.today()
    start = term.starts_on if term is not None else end - dt.timedelta(days=90)
    attendance = _attendance(lids, start, end)
    run = _run(cls, term)
    saved = ((run.completeness or {}).get("comments") or {}) if run is not None else {}
    cards = {c.learner_id: c for c in ReportCard.objects.filter(run_id=run.id)} if run is not None else {}
    rows = []
    for lr in learners:
        subjects = []
        for pid in order:
            m = marks[pid][lr.id]
            g = services.grade(m["total"]) if m["total"] is not None else None
            subjects.append(
                {
                    "subject": names.get(plans[pid].subject_id, ""),
                    **m,
                    "grade": g,
                    "remark": REMARK.get(g or "", ""),
                    "position": ordinal(stats[pid]["positions"][lr.id]) if lr.id in stats[pid]["positions"] else None,
                    "average": stats[pid]["average"],
                    "highest": stats[pid]["highest"],
                    "lowest": stats[pid]["lowest"],
                }
            )
        row: dict[str, Any] = {
            "learner_id": lr.id,
            "lrn": lr.global_learner_id,
            "name": " ".join(
                x for x in (lr.legal_family_name.upper(), lr.legal_given_name, lr.legal_middle_names) if x
            ),
            "first_name": lr.preferred_name or lr.legal_given_name,
            "sex": {"m": "Male", "f": "Female"}.get((lr.sex or "").lower()[:1], lr.sex),
            "date_of_birth": lr.date_of_birth,
            "subjects": subjects,
            "taken": sum(1 for s in subjects if s["total"] is not None),
            "total": round(sum(s["total"] for s in subjects if s["total"] is not None), 1),
            "average": averages.get(lr.id),
            "grade": services.grade(averages[lr.id]) if lr.id in averages else None,
            "position": ordinal(overall[lr.id]) if lr.id in overall else None,
            "attendance": attendance[lr.id],
            "missing": missing.get(lr.id, []),
        }
        drafted = draft_comments(row, len(averages))
        mine = saved.get(str(lr.id)) or {}
        row["drafted"] = drafted
        row["comments"] = {k: mine.get(k) or v for k, v in drafted.items()}
        row["edited"] = bool(mine)
        card = cards.get(lr.id)
        row["card"] = {"document_id": card.document_id, "released_at": card.released_at} if card else None
        rows.append(row)
    unlocked = [a for a in columns if a.status != "locked"]
    form_teacher = _staff_name(cls.form_teacher_staff_id)
    return {
        "class": {"id": cls.id, "name": cls.name, "level": cls.education_level, "learners": len(learners)},
        "institution": _institution(cls),
        "form_teacher": form_teacher,
        "term": {"id": term.id, "name": term.name, "starts_on": term.starts_on, "ends_on": term.ends_on}
        if term
        else None,
        "session": AcademicPeriod.objects.filter(pk=cls.period_id).values_list("name", flat=True).first(),
        "next_term": next_term.starts_on if next_term else None,
        "rows": rows,
        "subjects": [names.get(plans[pid].subject_id, "") for pid in order],
        "class_average": round(sum(averages.values()) / len(averages), 1) if averages else None,
        "completeness": {
            "assessments": len(columns),
            "unlocked": [f"{names.get(plans[a.class_subject_plan_id].subject_id)} — {a.title}" for a in unlocked],
            "missing": sum(len(v) for v in missing.values()),
            "ready": bool(columns) and not unlocked and not missing,
        },
        "run": {"id": run.id, "status": run.status, "published_at": run.published_at} if run else None,
        "issued": run is not None and run.status == "issued",
        "can_edit": ctx.has("assessment:manage") or ctx.has("assessment:approve"),
        "can_issue": ctx.has("assessment:approve") and ctx.has("document:upload"),
        "key": KEY,
        "remarks": REMARK,
        "classes": [
            {"id": c.id, "name": c.name}
            for c in ClassGroup.objects.in_scope()
            .filter(institution_id=cls.institution_id, period_id=cls.period_id, status="active")
            .order_by("name")
        ],
    }


def learner_report(class_id: uuid.UUID, learner_id: uuid.UUID) -> dict[str, Any]:
    d = class_reports(class_id)
    row = next((r for r in d["rows"] if r["learner_id"] == learner_id), None)
    if row is None:
        raise NotFound("learner in this class", learner_id)
    return {**d, "row": row, "of": sum(1 for r in d["rows"] if r["average"] is not None)}


def learner_results(learner_id: uuid.UUID) -> dict[str, Any] | None:
    """The learner's results this term in their current class (Learner 360), or None when there is nothing to show."""
    from syntegra.academic.models import ClassMembership

    ctx = context.require()
    if not ctx.has("assessment:view"):
        return None
    today = dt.date.today()
    m = (
        ClassMembership.objects.filter(learner_id=learner_id, valid_from__lte=today)
        .exclude(valid_to__lt=today)
        .order_by("-valid_from")
        .first()
    )
    if m is None or not ClassGroup.objects.in_scope().filter(pk=m.class_group_id).exists():
        return None
    d = learner_report(m.class_group_id, learner_id)
    return d if d["row"]["taken"] else None


def save_comments(class_id: uuid.UUID, comments: dict[str, dict[str, str]]) -> int:
    """Keep the edited comments with the class's report-card run (a draft until issue). Returns how many changed."""
    cls = _class(class_id)
    term, _next = _terms(cls)
    if term is None:
        raise ConflictError("ASM-TERM", "No term set up", "Set up the term in the school calendar first.")
    d = class_reports(class_id)
    if d["issued"]:
        raise ConflictError("ASM-ISSUED", "Report cards already issued", "Issued report cards cannot be changed.")
    drafted = {str(r["learner_id"]): r["drafted"] for r in d["rows"]}
    clean: dict[str, dict[str, str]] = {}
    for lid, pair in comments.items():
        if lid not in drafted:
            continue
        keep = {}
        for k in ("form", "head"):
            text = " ".join((pair.get(k) or "").split())[:600]
            if text and text != drafted[lid][k]:
                keep[k] = text
        if keep:
            clean[lid] = keep
    with uow.command("ops", "assessment:manage", action="save_comments", record_kind="report_card_run") as cmd:
        run = _run(cls, term)
        if run is None:
            run = cmd.add(
                ReportCardRun(
                    scope_node_id=cls.scope_node_id,
                    institution_id=cls.institution_id,
                    period_id=term.id,
                    template_code=TEMPLATE,
                    class_group_ids=[str(cls.id)],
                    completeness={"comments": clean},
                    status="draft",
                )
            )
        else:
            run = cmd.lock(ReportCardRun, run.id)
            cmd.update(run, completeness={**(run.completeness or {}), "comments": clean})
        cmd.record_id = run.id
        return len(clean)


def issue(class_id: uuid.UUID) -> dict[str, Any]:
    """Write every learner's report card as a PDF, file it in the school's register and record the run."""
    from syntegra.records import services as records

    ctx = context.require()
    authz.require("assessment:approve", ctx)
    authz.require("document:upload", ctx)
    d = class_reports(class_id)
    if d["issued"]:
        raise ConflictError(
            "ASM-ISSUED", "Report cards already issued", f"Issued on {d['run']['published_at']:%d %b %Y}."
        )
    done = d["completeness"]
    if not done["assessments"]:
        raise HardValidation("ASM-REPORT-EMPTY", "No assessments this term", "Enter and lock the term's marks first.")
    if done["unlocked"]:
        raise HardValidation(
            "ASM-REPORT-LOCK",
            "Some marks are not locked",
            f"Lock every assessment first: {'; '.join(done['unlocked'][:4])}"
            + (f" and {len(done['unlocked']) - 4} more." if len(done["unlocked"]) > 4 else "."),
        )
    if done["missing"]:
        raise HardValidation(
            "ASM-REPORT-MISSING",
            "Some marks are blank",
            f"{done['missing']} mark(s) are neither entered nor recorded as work not done.",
        )
    cls = _class(class_id)
    term = d["term"]
    issued = []
    for row in d["rows"]:
        if row["average"] is None:
            continue
        pdf = render_pdf({**d, "row": row, "of": sum(1 for r in d["rows"] if r["average"] is not None)})
        doc = records.upload(
            ctx,
            institution_id=cls.institution_id,
            category_code="RES",
            title=f"Report card — {row['name']} — {cls.name}, {term['name']} {d['session'] or ''}".strip(),
            files=[records.Upload(name=f"report-card-{row['lrn']}.pdf", data=pdf)],
            date_from=term["starts_on"],
            date_to=term["ends_on"],
            session_label=(d["session"] or "")[:20],
            level_or_class=cls.name,
            source_reference=row["lrn"],
            description=f"Termly report card ({TEMPLATE}) issued by the school.",
        )[0]
        issued.append((row["learner_id"], doc.id, hashlib.sha256(pdf).digest()))
    with uow.command("ops", "assessment:approve", action="issue_reports", record_kind="report_card_run") as cmd:
        run = _run(cls, AcademicPeriod.objects.get(pk=term["id"]))
        now = utcnow()
        summary = {"learners": len(issued), "assessments": done["assessments"]}
        if run is None:
            run = cmd.add(
                ReportCardRun(
                    scope_node_id=cls.scope_node_id,
                    institution_id=cls.institution_id,
                    period_id=term["id"],
                    template_code=TEMPLATE,
                    class_group_ids=[str(cls.id)],
                    completeness={"comments": {}, **summary},
                    status="issued",
                    published_at=now,
                )
            )
        else:
            run = cmd.lock(ReportCardRun, run.id)
            if run.status == "issued":
                raise ConflictError("ASM-ISSUED", "Report cards already issued", "Another user issued them just now.")
            cmd.update(run, status="issued", published_at=now, completeness={**(run.completeness or {}), **summary})
        assert ctx.tenant_id is not None
        for lid, doc_id, digest in issued:
            cmd.add(
                ReportCard(
                    tenant_id=ctx.tenant_id,
                    run=run,
                    learner_id=lid,
                    document_id=doc_id,
                    content_hash=digest,
                    released_at=now,
                )
            )
        cmd.record_id = run.id
        return {"run_id": run.id, "issued": len(issued)}


# ------------------------------------------------------------------------------------------------- the PDF
def _emblem(ctx: context.Context) -> str | None:
    from django.contrib.staticfiles import finders

    from syntegra.platform.models import Tenant

    t = Tenant.objects.filter(pk=ctx.tenant_id).first() if ctx.tenant_id else None
    found = finders.find(f"img/emblems/{t.state_code.upper()}.png") if t is not None and t.state_code else None
    return str(found) if isinstance(found, str) else None


def _text(text: Any) -> str:
    return str(text)


def _plain(text: Any) -> str:
    """Latin-1 text for the PDF's built-in font when no Unicode font is installed (Ọ → O, — → -)."""
    s = str(text).replace("—", "-").replace("–", "-").replace("’", "'")
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).encode("latin-1", "replace").decode("latin-1")


def render_pdf(d: dict[str, Any]) -> bytes:
    """One learner's report card on one A4 page."""
    from fpdf import FPDF

    logging.getLogger("fontTools").setLevel(logging.WARNING)
    ctx = context.require()
    row, inst = d["row"], d["institution"]
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_title(f"Report card — {row['name']}")
    pdf.set_author(inst["name"])
    pdf.set_creator("Syntegra")
    pdf.set_auto_page_break(auto=True, margin=12)
    font = next((Path(p) for p in FONT_DIRS if (Path(p) / "DejaVuSans.ttf").exists()), None)
    if font is not None:
        pdf.add_font("body", "", str(font / "DejaVuSans.ttf"))
        pdf.add_font(
            "body",
            "B",
            str(font / ("DejaVuSans-Bold.ttf" if (font / "DejaVuSans-Bold.ttf").exists() else "DejaVuSans.ttf")),
        )
        family, t = "body", _text
    else:
        family, t = "Helvetica", _plain
    pdf.add_page()
    pdf.set_margins(12, 12, 12)
    ink, muted, rule = (20, 33, 61), (90, 98, 112), (200, 205, 214)
    emblem = _emblem(ctx)
    text_x = 12.0
    if emblem:
        info = pdf.image(emblem, x=12, y=10, h=24)
        text_x = 12 + float(info.rendered_width) + 5
    pdf.set_xy(text_x, 11)
    pdf.set_text_color(*ink)
    pdf.set_font(family, "B", 15)
    pdf.cell(0, 7, t(inst["name"].upper()), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(text_x)
    pdf.set_font(family, "", 9)
    pdf.set_text_color(*muted)
    contact = " · ".join(x for x in (inst["address"], inst["phone"], inst["email"]) if x)
    pdf.multi_cell(0, 4.5, t(contact or inst["code"]), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(text_x)
    pdf.set_font(family, "B", 11)
    pdf.set_text_color(*ink)
    term = d["term"]["name"] if d["term"] else "Term"
    pdf.cell(0, 6, t(f"TERMLY REPORT CARD — {term}, {d['session'] or ''} session"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(max(pdf.get_y(), 36) + 2)
    pdf.set_draw_color(*rule)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(2)

    def pair(label: str, value: Any, w: float) -> None:
        pdf.set_font(family, "", 8)
        pdf.set_text_color(*muted)
        pdf.cell(w * 0.38, 5, t(label))
        pdf.set_font(family, "B", 9)
        pdf.set_text_color(*ink)
        pdf.cell(w * 0.62, 5, t(value if value not in (None, "") else "—"))

    att = row["attendance"]
    rate = f"{att['rate'] * 100:.0f}%" if att["rate"] is not None else "—"
    lines = [
        (("Name", row["name"]), ("Class", d["class"]["name"])),
        (("Learner number", row["lrn"]), ("Sex", row["sex"])),
        (("Date of birth", f"{row['date_of_birth']:%d %b %Y}"), ("Learners in class", d["of"])),
        (("Attendance", f"{att['attended']} of {att['possible']} sessions ({rate})"),
         ("Next term begins", f"{d['next_term']:%d %b %Y}" if d["next_term"] else None)),
    ]  # fmt: skip
    for left, right in lines:
        pair(*left, 93)
        pair(*right, 93)
        pdf.ln(5)
    pdf.ln(2)
    heads = ("Subject", "CA", "Exam", "Total", "Grade", "Position", "Class avg", "Highest", "Lowest", "Remark")
    widths = (54, 11, 12, 12, 12, 15, 16, 14, 13, 27)
    pdf.set_fill_color(234, 238, 245)
    pdf.set_font(family, "B", 8)
    for h, w in zip(heads, widths, strict=True):
        pdf.cell(w, 6, t(h), border=1, align="L" if h in ("Subject", "Remark") else "C", fill=True)
    pdf.ln(6)
    pdf.set_font(family, "", 8)

    def num(v: Any) -> str:
        return "—" if v is None else f"{v:.0f}" if float(v) == int(v) else f"{v:.1f}"

    for s in row["subjects"]:
        vals = (s["subject"], num(s["ca"]), num(s["exam"]), num(s["total"]), s["grade"] or "—", s["position"] or "—",
                num(s["average"]), num(s["highest"]), num(s["lowest"]), s["remark"] or "—")  # fmt: skip
        for i, (v, w) in enumerate(zip(vals, widths, strict=True)):
            text = t(v)
            while pdf.get_string_width(text) > w - 2 and len(text) > 4:
                text = text[:-2].rstrip() + "…" if family == "body" else text[:-2].rstrip() + "."
            pdf.cell(w, 5.6, text, border=1, align="L" if i in (0, 9) else "C")
        pdf.ln(5.6)
    pdf.ln(2)
    pdf.set_font(family, "B", 8.5)
    avg = f"{row['average']:.1f}%" if row["average"] is not None else "—"
    summary = (
        f"Subjects taken: {row['taken']}",
        f"Total: {num(row['total'])}",
        f"Average: {avg} ({row['grade'] or '—'})",
        f"Position in class: {row['position'] or '—'} of {d['of']}",
        f"Class average: {num(d['class_average'])}%",
    )
    pdf.multi_cell(0, 5, t("   ·   ".join(summary)), align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    for label, text, who in (
        ("Form teacher's comment", row["comments"]["form"], d["form_teacher"]),
        (f"{inst['head_title']}'s comment", row["comments"]["head"], inst["head_name"]),
    ):
        pdf.set_font(family, "B", 9)
        pdf.cell(0, 5, t(label + (f" — {who}" if who else "")), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(family, "", 9)
        pdf.multi_cell(0, 4.8, t(text), border="B", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
    pdf.set_font(family, "B", 8)
    pdf.cell(0, 5, t("Grading key (WAEC / NECO)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(family, "", 7.5)
    for i, (g, band) in enumerate(KEY):
        pdf.cell(37.2, 4.8, t(f"{g}  {band}  {REMARK[g]}"), border=1, align="C")
        if i == 4:
            pdf.ln(4.8)
    pdf.ln(9)
    pdf.set_font(family, "", 8)
    pdf.set_text_color(*muted)
    pdf.cell(93, 5, t("Signature and stamp: ________________________"))
    pdf.cell(93, 5, t(f"Issued {dt.date.today():%d %B %Y}"), align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(
        0, 4,
        t("CA = continuous assessment. Totals are out of 100; positions count equal totals as equal. This report card "
          "is kept in the school's register; its SHA-256 fingerprint is recorded so any copy can be checked."),
        new_x="LMARGIN", new_y="NEXT",
    )  # fmt: skip
    out = io.BytesIO()
    pdf.output(out)
    return out.getvalue()
