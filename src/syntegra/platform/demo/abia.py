"""Abia State demonstration dataset — end-to-end test load of the whole platform (``syntegra_demo_abia``).

What it creates (all through the platform's own services, with bulk paths where the volume demands it):

* the state's education bodies: the Abia State Ministry of Education, the Abia State Universal Basic and Secondary
  Education Board (ASUBEB) under it, and the Abia State Ministry of Tertiary Education — as authority nodes of the
  governance hierarchy and as bodies in the regulators' directory, with every Abia institution's supervision links
  moved from the generic state bodies to these;
* all 17 LGAs; ``schools_per_lga`` government primary and secondary schools in each, each with a head of
  institution account, classes (two arms per level), its roll imported (pupils and their guardians), subjects, a
  continuous assessment and a first-term examination per subject, marks for every pupil and ``days`` days of
  attendance registers;
* Abia State University (ABSU) and the Abia State College of Education (Technical), Arochukwu (ASCETA), with
  faculties or schools, departments and programmes, their students (with JAMB and matriculation numbers), course
  results, and academic and support staff appointed through HR;
* sample facilities, budgets, imprest and funding so that every module has data, then the daily jobs (facility
  rules, warehouse load).

Every school, person and score is synthetic (seeded random) and the load is idempotent: a school whose roll is
already imported is skipped. Demonstration users share the password in ``PASSWORD`` (development only).
"""

from __future__ import annotations

import datetime as dt
import random
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from syntegra.core import authz, context, uow
from syntegra.core.context import Context
from syntegra.core.fields import utcnow
from syntegra.core.ids import uuid7
from syntegra.platform.demo import abia_data as D

PASSWORD = "Demo-password-2026"
STATE = "NG-AB"
Log = Callable[[str], None]


@dataclass
class Scale:
    schools_per_lga: int = 5
    pupils: int = 500
    lgas: int | None = None  # None: all 17
    absu_students: int = 380
    asceta_students: int = 120
    absu_staff: int = 100
    asceta_staff: int = 50
    days: int = 10
    seed: int = 2026
    extras: bool = True  # facilities, budgets, funding samples and the warehouse load


@dataclass
class Loaded:
    lgas: int = 0
    schools: int = 0
    pupils: int = 0
    tertiary_students: int = 0
    staff: int = 0
    results: int = 0
    attendance_marks: int = 0
    users: list[tuple[str, str, str]] = field(default_factory=list)  # username, role, where
    notes: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- contexts and users
def _sys() -> Context:
    from syntegra.core.tenancy import state_tenant_id

    t = state_tenant_id(STATE)
    return context.system(t, t, correlation_id="demo-abia")


def _user(username: str, display: str, role: str, scope_id: uuid.UUID, out: Loaded, where: str) -> Context:
    """The demo user (created on first use) as a signed-in context holding ``role`` at ``scope_id``."""
    from syntegra.iam import services as iam
    from syntegra.iam.models import AppUser, RoleGrant

    sysctx = _sys()
    with context.use(sysctx):
        u = AppUser.objects.filter(username=username).first()
        if u is None:
            u = iam.create_user(sysctx, username=username, display_name=display, password=PASSWORD)
        g = RoleGrant.objects.filter(user_id=u.id, scope_id=scope_id, status="active").first()
        if g is None:
            from syntegra.iam.models import Role

            role_id = Role.objects.get(code=role).id
            g = RoleGrant.objects.filter(user_id=u.id, role_id=role_id, scope_id=scope_id).first() or iam.grant_role(
                sysctx, user=u, role_code=role, scope_id=scope_id
            )
    if (username, role, where) not in out.users:
        out.users.append((username, role, where))
    base = Context(tenant_id=sysctx.tenant_id, state_tenant_id=sysctx.state_tenant_id, actor_kind="user", actor_id=u.id)
    with context.use(base):
        return authz.grant_context(base, g.id)


def _node(code: str) -> Any:
    from syntegra.governance.models import ScopeNode

    return ScopeNode.objects.filter(code=code).first()


# --------------------------------------------------------------------------- governance and the state's bodies
def _lgas(scale: Scale, out: Loaded) -> list[tuple[Any, tuple[str, ...], bool]]:
    from syntegra.governance import services as gov

    state = _node(STATE)
    result = []
    with uow.command("registry", None, action="create", record_kind="scope_node") as cmd:
        for code, name, towns, urban in D.LGAS:  # every LGA exists; schools are loaded for the first ``scale.lgas``
            node = _node(code) or gov.add_node(cmd, parent=state, level="lga", code=code, name=name)
            result.append((node, towns, urban))
    out.lgas = len(result)
    return result


def _authorities(out: Loaded) -> dict[str, Any]:
    """Ministry of Education → ASUBEB, and the Ministry of Tertiary Education: authority nodes (for their own staff),
    directory bodies with their dependencies, and Abia's supervision links moved onto them."""
    from syntegra.governance import services as gov
    from syntegra.regulation import services as reg

    state = _node(STATE)
    nodes = {}
    with uow.command("registry", None, action="create", record_kind="scope_node") as cmd:
        moe = _node("AB-MOE") or gov.add_node(
            cmd, parent=state, level="authority", code="AB-MOE", name="Abia State Ministry of Education"
        )
        nodes["AB-MOE"] = moe
        nodes["AB-ASUBEB"] = _node("AB-ASUBEB") or gov.add_node(
            cmd,
            parent=moe,
            level="authority",
            code="AB-ASUBEB",
            name="Abia State Universal Basic and Secondary Education Board (ASUBEB)",
        )
        nodes["AB-MOTE"] = _node("AB-MOTE") or gov.add_node(
            cmd, parent=state, level="authority", code="AB-MOTE", name="Abia State Ministry of Tertiary Education"
        )
    nb, nd = reg.seed_directory()
    moved = reg.localise_registry()
    out.notes.append(f"directory: {nb} bodies and {nd} dependencies added; supervision links {moved}")
    return nodes


def _people_users(nodes: dict[str, Any], out: Loaded) -> None:
    state = _node(STATE)
    _user("commissioner.education@abia.gov.ng", "Commissioner for Education", "COMM", state.id, out, "Abia State")
    _user(
        "commissioner.tertiary@abia.gov.ng", "Commissioner for Tertiary Education", "COMM", state.id, out, "Abia State"
    )
    _user("chairman.asubeb@abia.gov.ng", "Executive Chairman, ASUBEB", "COMM", state.id, out, "Abia State (ASUBEB)")
    _user(
        "director.planning@abia.gov.ng",
        "Director of Planning, Research and Statistics",
        "STA",
        state.id,
        out,
        "Abia State",
    )


# --------------------------------------------------------------------------- the session and subjects
def _calendar() -> tuple[Any, Any]:
    from syntegra.academic import services as academic
    from syntegra.academic.models import AcademicPeriod

    state = _node(STATE)
    session = AcademicPeriod.objects.filter(name="2026/2027", kind="session", scope_node_id=state.id).first()
    if session is None:
        session = academic.create_session(state.id, "2026/2027", dt.date(2026, 9, 14), dt.date(2027, 7, 23))
    term = AcademicPeriod.objects.filter(parent_id=session.id, kind="term", name="First Term").first()
    if term is None:
        term = academic.create_session(
            state.id, "First Term", dt.date(2026, 9, 14), dt.date(2026, 12, 18), kind="term", parent_id=session.id
        )
    return session, term


def _subjects() -> dict[str, Any]:
    from syntegra.academic import services as academic
    from syntegra.academic.models import Subject

    state = _node(STATE)
    out = {}
    for code, name, levels in D.SUBJECTS:
        s = Subject.objects.filter(scope_node_id=state.id, code=f"AB-{code}").first()
        out[code] = s or academic.create_subject(state.id, f"AB-{code}", name, list(levels))
    return out


# --------------------------------------------------------------------------- synthetic people
class _Names:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.used: set[tuple[str, str, dt.date, str]] = set()
        self.phone = 0

    def person(self, sex: str, dob_from: dt.date, dob_days: int = 365) -> tuple[str, str, str, dt.date]:
        for _ in range(50):
            given = self.rng.choice(D.MALE if sex == "male" else D.FEMALE)
            middle = self.rng.choice(D.MALE if sex == "male" else D.FEMALE)
            family = self.rng.choice(D.FAMILY)
            dob = dob_from + dt.timedelta(days=self.rng.randrange(dob_days))
            key = (given.lower(), family.lower(), dob, sex)
            if key not in self.used and middle != given:
                self.used.add(key)
                return given, middle, family, dob
        raise RuntimeError("could not generate a unique synthetic person")

    def next_phone(self) -> str:
        self.phone += 1
        return f"0803{self.phone:07d}"


def _guardian(names: _Names, family: str) -> Any:
    from syntegra.families.services import GuardianInput

    mother = names.rng.random() < 0.55
    return GuardianInput(
        given=names.rng.choice(D.FEMALE if mother else D.MALE),
        family=family,
        relationship="mother" if mother else "father",
        title=names.rng.choice(D.TITLES_F if mother else D.TITLES_M),
        phone=names.next_phone(),
        has_parental_responsibility=True,
        lives_with=True,
        is_authorised_collector=True,
        is_payer=True,
    )


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# --------------------------------------------------------------------------- one school
def _school_days(days: int) -> list[dt.date]:
    out: list[dt.date] = []
    d = dt.date.today() - dt.timedelta(days=1)
    while len(out) < days:
        if d.weekday() < 5 and d >= dt.date(2026, 9, 14):
            out.append(d)
        d -= dt.timedelta(days=1)
        if d < dt.date(2026, 9, 1):
            break
    return sorted(out)


def _bulk_ops(model: Any, objs: list[Any], ctx: Context, alias: str) -> None:
    now = utcnow()
    for o in objs:
        o.tenant_id = ctx.tenant_id
        if hasattr(o, "created_by"):
            o.created_by, o.created_at = ctx.actor_id, now
        if hasattr(o, "updated_at"):
            o.updated_at = now
    model.unscoped.using(alias).bulk_create(objs, batch_size=2000)


def load_school(
    inst: Any,
    kind: str,
    head: Context,
    session: Any,
    subjects: dict[str, Any],
    names: _Names,
    scale: Scale,
    quality: float,
    out: Loaded,
    *,
    levels: tuple[str, ...] | None = None,
    pupils: int | None = None,
    groups: tuple[str, ...] = ("A", "B"),
    rows_for: Callable[[str, int], list[Any]] | None = None,
    group_of: Callable[[Any, int], str] | None = None,
    plan_codes: Callable[[str, str], tuple[str, ...]] | None = None,
    ca_weight: int = 40,
) -> None:
    """Classes, roll, subjects, assessments with marks and attendance for one institution (bulk, one command per
    step). Classes are one per level and group — arms A and B in schools, programmes in tertiary institutions."""
    from syntegra.academic.models import ClassGroup, ClassMembership, ClassSubjectPlan
    from syntegra.assessment.models import Assessment, AssessmentResult
    from syntegra.assessment.services import grade
    from syntegra.attendance.models import AttendanceMark, AttendanceRegister
    from syntegra.learners import roll

    rng = names.rng
    levels = levels or (D.PRIMARY_LEVELS if kind == "primary" else D.SECONDARY_LEVELS)
    n = pupils or scale.pupils
    per_level = [n // len(levels) + (1 if i < n % len(levels) else 0) for i in range(len(levels))]

    def class_name(lv: str, g: str) -> str:
        if kind == "tertiary":
            return f"{g} {lv}"
        return lv.replace("PRY", "Primary ").replace("JSS", "JSS ").replace("SSS", "SS ") + g

    # 1. classes (ops zone); existing ones are reused on a re-run
    with context.use(head), uow.command("ops", "class:manage", action="create", record_kind="class_group") as cmd:
        have = {c.name: c for c in ClassGroup.objects.filter(institution_id=inst.id, period_id=session.id)}
        classes: dict[tuple[str, str], Any] = {}
        new = []
        for lv in levels:
            for g in groups:
                c = have.get(class_name(lv, g))
                if c is None:
                    c = ClassGroup(
                        id=uuid7(),
                        scope_node_id=inst.scope_node_id,
                        institution_id=inst.id,
                        period_id=session.id,
                        kind="cohort" if kind == "tertiary" else "arm",
                        education_level=lv,
                        name=class_name(lv, g),
                        capacity=45 if kind == "primary" else 50 if kind == "secondary" else 200,
                        status="active",
                    )
                    new.append(c)
                classes[(lv, g)] = c
        _bulk_ops(ClassGroup, new, cmd.ctx, cmd.alias)
        cmd.note("classes", None, len(new))
    # 2. the roll (registry zone, through the roll-import service)
    rows: list[Any] = []
    group_by_row: list[str] = []
    for lv, count in zip(levels, per_level, strict=True):
        if rows_for is not None:
            level_rows = rows_for(lv, count)
        else:
            level_rows = []
            for _ in range(count):
                sex = "female" if rng.random() < 0.5 else "male"
                given, middle, family, dob = names.person(sex, dt.date(2026 - D.AGE[lv] - 1, 9, 1))
                level_rows.append(
                    roll.RollRow(given=given, middle=middle, family=family, date_of_birth=dob, sex=sex,
                                 education_level=lv, guardian=_guardian(names, family))
                )  # fmt: skip
        for i, r in enumerate(level_rows):
            g = group_of(r, i) if group_of else groups[i % len(groups)]
            r.class_group_id = classes[(lv, g)].id
            group_by_row.append(g)
        rows.extend(level_rows)
    imported = _resume(inst)
    if not imported:
        with context.use(head):
            res = roll.import_roll(inst.id, rows, start_on=session.starts_on)
        if res["errors"]:
            raise RuntimeError(f"{inst.name}: roll import refused: {res['errors'][:3]}")
        imported = res["imported"]
    if kind == "tertiary":
        out.tertiary_students += len(imported)
    else:
        out.pupils += len(imported)
    # 3. memberships, subject plans, assessments, marks and attendance (ops zone)
    days = _school_days(scale.days)
    att_base = _clamp(0.92 + quality / 160, 0.72, 0.99)
    with (
        context.use(head),
        uow.command("ops", "assessment:enter", action="load_results", record_kind="assessment") as cmd,
    ):
        ctx, alias = cmd.ctx, cmd.alias
        _bulk_ops(
            ClassMembership,
            [
                ClassMembership(
                    class_group_id=it.row.class_group_id,
                    learner_id=it.learner_id,
                    enrolment_id=it.enrolment_id,
                    is_arm=True,
                    valid_from=session.starts_on,
                )
                for it in imported
            ],
            ctx,
            alias,
        )
        plans, assessments, results, registers, marks = [], [], [], [], []
        by_class: dict[uuid.UUID, list[Any]] = {}
        for it in imported:
            by_class.setdefault(it.row.class_group_id, []).append(it)
        ability = {it.learner_id: rng.gauss(0, 11) for it in imported}
        presence = {
            it.learner_id: _clamp(att_base + rng.gauss(0, 0.04) + ability[it.learner_id] / 450, 0.45, 1)
            for it in imported
        }
        for (lv, g), c in classes.items():
            if plan_codes is not None:
                codes = plan_codes(lv, g)
            else:
                codes = (
                    D.PRIMARY_SUBJECTS
                    if lv.startswith("PRY")
                    else D.JSS_SUBJECTS
                    if lv.startswith("JSS")
                    else D.SSS_SUBJECTS
                )
            pupils_ = by_class.get(c.id, [])
            for code in codes:
                p = ClassSubjectPlan(
                    id=uuid7(), class_group_id=c.id, subject_id=subjects[code].id,
                    is_mandatory=True, periods_per_week=5, valid_from=session.starts_on,
                )  # fmt: skip
                plans.append(p)
                name = subjects[code].name
                ca = Assessment(
                    id=uuid7(), scope_node_id=inst.scope_node_id, class_subject_plan_id=p.id,
                    title=f"First term continuous assessment — {name}", assessment_kind="ca_test",
                    max_mark=Decimal(ca_weight), weight=Decimal(ca_weight), assessed_on=dt.date(2026, 10, 9),
                    status="locked", locked_at=utcnow(),
                )  # fmt: skip
                ex = Assessment(
                    id=uuid7(), scope_node_id=inst.scope_node_id, class_subject_plan_id=p.id,
                    title=f"First term examination — {name}", assessment_kind="examination",
                    max_mark=Decimal(100 - ca_weight), weight=Decimal(100 - ca_weight), assessed_on=dt.date(2026, 10, 13),
                    status="locked", locked_at=utcnow(),
                )  # fmt: skip
                assessments += [ca, ex]
                bias = D.SUBJECT_BIAS.get(code[-3:] if kind != "tertiary" else "", 0.0)
                for it in pupils_:
                    base = 54 + quality + ability[it.learner_id] + bias
                    for a, sd in ((ca, 7), (ex, 9)):
                        pct = _clamp(base + rng.gauss(0, sd), 3, 99)
                        score = round(float(a.max_mark) * pct / 100)
                        results.append(
                            AssessmentResult(assessment_id=a.id, learner_id=it.learner_id, score=Decimal(score),
                                             grade_label=grade(score / float(a.max_mark) * 100), entered_by=ctx.actor_id)
                        )  # fmt: skip
            for day in days:
                reg = AttendanceRegister(
                    id=uuid7(), scope_node_id=inst.scope_node_id, class_group_id=c.id,
                    register_kind="daily", session_date=day, due_at=dt.datetime.combine(day, dt.time(8, 30), tzinfo=dt.UTC),
                    submitted_at=dt.datetime.combine(day, dt.time(8, 20), tzinfo=dt.UTC), marks_count=len(pupils_),
                    status="submitted",
                )  # fmt: skip
                registers.append(reg)
                for it in pupils_:
                    r = rng.random()
                    p_ = presence[it.learner_id]
                    code_ = "P" if r < p_ * 0.94 else "L" if r < p_ else ("M" if rng.random() < 0.25 else "A")
                    marks.append(
                        AttendanceMark(
                            id=uuid7(), register_id=reg.id, learner_id=it.learner_id,
                            enrolment_id=it.enrolment_id, session_date=day, code=code_,
                            minutes_late=rng.randint(5, 40) if code_ == "L" else None, reason_source="teacher",
                            recorded_by=ctx.actor_id, source="teacher",
                        )
                    )  # fmt: skip
        _bulk_ops(ClassSubjectPlan, plans, ctx, alias)
        _bulk_ops(Assessment, assessments, ctx, alias)
        _bulk_ops(AssessmentResult, results, ctx, alias)
        _bulk_ops(AttendanceRegister, registers, ctx, alias)
        _bulk_ops(AttendanceMark, marks, ctx, alias)
        cmd.record_id = inst.id
        cmd.note("loaded", None, {"results": len(results), "registers": len(registers), "marks": len(marks)})
    out.results += len(results)
    out.attendance_marks += len(marks)


def _register_school(
    lga: Any, town: str, name: str, category: str, levels: tuple[str, ...], k: int, sta: Context
) -> Any:
    from syntegra.institutions import services as inst_svc
    from syntegra.institutions.models import Institution

    found = Institution.objects.filter(name=name, lga_scope_id=lga.id).first()
    if found is not None:
        return found
    lat, lon = D.CENTRES.get(lga.code, (5.5, 7.5))
    with context.use(sta):
        return inst_svc.register(
            inst_svc.RegisterInstitution(
                name=name,
                category=category,
                ownership="state",
                lga_scope_id=lga.id,
                address={"town": town, "lga": lga.name, "state": "Abia", "demo": True},
                levels=list(levels),
                location=(
                    round(lat + 0.012 * (k + 1), 5),
                    round(lon + (0.009 if category == "primary" else -0.009) * (k + 1), 5),
                ),
                capacity=600,
                day_boarding="day",
                gender_intake="girls" if "Girls'" in name else "boys" if "Boys'" in name else "mixed",
            ),
            override_reason="Demonstration dataset: a distinct school in a different town",
        )


def _has_roll(inst: Any) -> bool:
    """Fully loaded: the roll is imported and its marks are recorded (a half-loaded school is resumed)."""
    from syntegra.assessment.models import Assessment

    return Assessment.objects.filter(scope_node_id=inst.scope_node_id).exists()


def _resume(inst: Any) -> list[Any]:
    """The roll of a school whose import completed before an interruption, rebuilt from its enrolments. Learners
    enrolled earlier by hand (without a class) are left as they are and do not count as the demonstration roll."""
    from syntegra.learners import roll
    from syntegra.learners.models import Enrolment

    items = []
    for e in Enrolment.objects.filter(institution_id=inst.id, status="active", class_group_id__isnull=False):
        row = roll.RollRow(given="", family="", date_of_birth=dt.date(2000, 1, 1), sex="", education_level=e.education_level,
                           programme_id=e.programme_id, class_group_id=e.class_group_id)  # fmt: skip
        items.append(roll.Imported(e.learner_id, e.id, "", row))
    return items


def _schools(lgas: list[tuple[Any, tuple[str, ...], bool]], session: Any, subjects: dict[str, Any],
             names: _Names, scale: Scale, out: Loaded, log: Log) -> list[Any]:  # fmt: skip
    state = _node(STATE)
    sta = _user(
        "director.planning@abia.gov.ng",
        "Director of Planning, Research and Statistics",
        "STA",
        state.id,
        out,
        "Abia State",
    )
    schools = []
    for lga, towns, urban in lgas:
        for kind, names_, category, levels in (
            ("primary", D.PRIMARY_NAMES, "primary", D.PRIMARY_LEVELS),
            ("secondary", D.SECONDARY_NAMES, "combined_secondary", D.SECONDARY_LEVELS),
        ):
            for k in range(scale.schools_per_lga):
                town = towns[k % len(towns)]
                inst = _register_school(lga, town, f"{names_[k % len(names_)]}, {town}", category, levels, k, sta)
                short = "".join(w[0] for w in inst.name.replace(",", "").split()[:4]).upper()
                head_user = f"head.{kind}.{lga.code[3:].lower()}{k + 1}@abia.demo"
                head = _user(head_user, f"Head, {inst.name}", "HEAD", inst.scope_node_id, out, inst.name)
                schools.append(inst)
                if _has_roll(inst):
                    continue
                quality = names.rng.gauss(0, 7) + (3 if urban else 0)
                load_school(inst, kind, head, session, subjects, names, scale, quality, out)
                out.schools += 1
                log(f"  {lga.name}: {inst.name} ({short}) — {scale.pupils} pupils")
    return schools


# --------------------------------------------------------------------------- tertiary
def _org_units(inst: Any, key: str, sta: Context) -> dict[str, tuple[Any, Any]]:
    """Faculties/schools and departments (org units) and academic departments; returns programme code → (dept, unit)."""
    from syntegra.academic.models import Department
    from syntegra.institutions.models import OrgUnit

    out: dict[str, tuple[Any, Any]] = {}
    with context.use(sta), uow.command("registry", None, action="create", record_kind="org_unit") as cmd:
        for (fcode, fname), depts in D.FACULTIES[key].items():
            fac = OrgUnit.objects.filter(institution_id=inst.id, code=fcode).first() or cmd.add(
                OrgUnit(scope_node_id=inst.scope_node_id, institution_id=inst.id,
                        unit_type="faculty" if key == "ABSU" else "school", code=fcode, name=fname,
                        valid_from=dt.date(2026, 1, 1))
            )  # fmt: skip
            for pcode, _pname, dname, _terms in depts:
                unit = OrgUnit.objects.filter(institution_id=inst.id, code=pcode).first() or cmd.add(
                    OrgUnit(scope_node_id=inst.scope_node_id, institution_id=inst.id, parent_id=fac.id,
                            unit_type="department", code=pcode, name=dname, valid_from=dt.date(2026, 1, 1))
                )  # fmt: skip
                dept = Department.objects.filter(org_unit_id=unit.id).first() or cmd.add(
                    Department(scope_node_id=inst.scope_node_id, institution_id=inst.id, org_unit_id=unit.id,
                               faculty_org_unit_id=fac.id, name=dname, status="active")
                )  # fmt: skip
                out[pcode] = (dept, unit)
    return out


def _programmes(inst: Any, key: str, depts: dict[str, tuple[Any, Any]], sta: Context) -> dict[str, Any]:
    from syntegra.academic import services as academic
    from syntegra.academic.models import Programme

    out = {}
    for _fac, rows in D.FACULTIES[key].items():
        for pcode, pname, _dname, terms in rows:
            with context.use(sta):
                p = Programme.objects.filter(institution_id=inst.id, code=pcode).first() or academic.create_programme(
                    inst.id, pcode, pname, duration_terms=terms, accreditation_status="full"
                )
                if p.department_id != depts[pcode][0].id:
                    with uow.command("registry", None, action="update", record_kind="programme") as cmd:
                        p = cmd.update(p, department_id=depts[pcode][0].id)
            out[pcode] = p
    return out


def _tertiary(lgas: dict[str, Any], session: Any, names: _Names, scale: Scale, out: Loaded, log: Log) -> dict[str, Any]:
    from syntegra.academic import services as academic
    from syntegra.academic.models import Subject
    from syntegra.institutions import services as inst_svc
    from syntegra.institutions.models import Institution
    from syntegra.learners import roll

    state = _node(STATE)
    sta = _user(
        "director.planning@abia.gov.ng",
        "Director of Planning, Research and Statistics",
        "STA",
        state.id,
        out,
        "Abia State",
    )
    result = {}
    for key, (name, short, category, lga_code, town, levels, (lat, lon)) in D.TERTIARY.items():
        inst = Institution.objects.filter(name=name).first()
        if inst is None:
            with context.use(sta):
                inst = inst_svc.register(
                    inst_svc.RegisterInstitution(
                        name=name, short_name=short, category=category, ownership="state",
                        lga_scope_id=lgas[lga_code].id, address={"town": town, "state": "Abia"},
                        levels=list(levels), location=(lat, lon), capacity=25000 if key == "ABSU" else 6000,
                    )
                )  # fmt: skip
        elif inst.lga_scope_id != lgas[lga_code].id:
            out.notes.append(f"{short} was registered earlier under another LGA; left in place")
        result[key] = inst
        depts = _org_units(inst, key, sta)
        progs = _programmes(inst, key, depts, sta)
        head = _user(f"{'vc' if key == 'ABSU' else 'provost'}.{short.lower()}@abia.demo",
                     "Vice-Chancellor" if key == "ABSU" else "Provost", "HEAD", inst.scope_node_id, out, name)  # fmt: skip
        _user(f"registrar.{short.lower()}@abia.demo", f"Registrar, {short}", "REG", inst.scope_node_id, out, name)
        _user(f"bursar.{short.lower()}@abia.demo", f"Bursar, {short}", "FINO", inst.scope_node_id, out, name)
        _user(f"hr.{short.lower()}@abia.demo", f"Head of Establishments, {short}", "HR", inst.scope_node_id, out, name)
        # course "subjects" of the institution: three first-semester courses per programme
        subjects: dict[str, Any] = {}
        with context.use(sta):
            for pcode in progs:
                for i, title in enumerate(D.COURSES, start=1):
                    scode = f"{short}-{pcode}{100 + i}"
                    subjects[scode] = Subject.objects.filter(scope_node_id=inst.scope_node_id, code=scode).first() or (
                        academic.create_subject(inst.scope_node_id, scode, f"{pcode} {100 + i} {title}",
                                                list(levels), mandatory=True)
                    )  # fmt: skip
        if _has_roll(inst):
            continue
        total = scale.absu_students if key == "ABSU" else scale.asceta_students
        codes = list(progs)
        code_of = {p.id: c for c, p in progs.items()}
        levels_used = ("UG100", "UG200", "UG300", "UG400") if key == "ABSU" else ("NCE",)
        serial = {"n": 0}
        rng = names.rng

        def rows_for(level: str, count: int, *, _codes: list[str] = codes, _progs: dict[str, Any] = progs,
                     _short: str = short, _key: str = key) -> list[Any]:  # fmt: skip
            rows = []
            for i in range(count):
                pcode = _codes[i % len(_codes)]
                year = 2026 - (int(level[2]) - 1 if level.startswith("UG") else rng.randrange(3))
                sex = "female" if rng.random() < 0.52 else "male"
                given, middle, family, dob = names.person(sex, dt.date(year - 21, 1, 1), 900)  # 18+ at entry
                serial["n"] += 1
                jamb = f"{year}{rng.randrange(10**8):08d}{rng.choice('ABCDEFGH')}{rng.choice('JKLMNPQR')}"
                rows.append(
                    roll.RollRow(
                        given=given, middle=middle, family=family, date_of_birth=dob, sex=sex,
                        education_level=level, programme_id=_progs[pcode].id,
                        cohort_label=f"{year}/{year + 1} entry" if _key == "ABSU" else f"NCE {2027 - year}",
                        identifiers={"JAMB-REG": jamb, "INST-ID": f"{_short}/{year}/{pcode}/{serial['n']:04d}"},
                    )
                )  # fmt: skip
            return rows

        def group_of(row: Any, _i: int, *, _code_of: dict[Any, str] = code_of) -> str:
            return _code_of[row.programme_id]

        def plan_codes(level: str, group: str, *, _short: str = short) -> tuple[str, ...]:
            return tuple(f"{_short}-{group}{100 + i}" for i in range(1, len(D.COURSES) + 1))

        load_school(
            inst, "tertiary", head, session, subjects, names, scale, names.rng.gauss(2, 4), out,
            levels=levels_used, pupils=total, groups=tuple(codes), rows_for=rows_for, group_of=group_of,
            plan_codes=plan_codes, ca_weight=30,
        )  # fmt: skip
        log(f"  {name}: {total} students in {len(progs)} programmes")
    return result


def _staff(tertiary: dict[str, Any], names: _Names, scale: Scale, out: Loaded, log: Log) -> None:
    """Academic and support staff through HR: cadres, positions, staff masters and appointments."""
    from syntegra.hr import establishment as est
    from syntegra.hr.models import Cadre, EmploymentRecord, Position
    from syntegra.people import services as people

    state = _node(STATE)
    sta = _user(
        "director.planning@abia.gov.ng",
        "Director of Planning, Research and Statistics",
        "STA",
        state.id,
        out,
        "Abia State",
    )
    with context.use(sta):
        if not Cadre.objects.filter(code="LECTURER").exists():
            est.create_cadre(
                state.id, "LECTURER", "Academic staff (lecturers)", staff_category="lecturer", is_teaching=True,
                salary_structure_code="AB-TSS-ILLUSTRATIVE", entry_grade_level=8, max_grade_level=15,
                retirement_age=65, max_years_service=35,
            )  # fmt: skip
        if not Cadre.objects.filter(code="NONACAD").exists():
            est.create_cadre(
                state.id, "NONACAD", "Non-academic (senior and junior) staff", staff_category="administrative",
                is_teaching=False, salary_structure_code="AB-TSS-ILLUSTRATIVE", entry_grade_level=3,
                max_grade_level=14, retirement_age=60, max_years_service=35,
            )  # fmt: skip
    rng = names.rng
    for key, total in (("ABSU", scale.absu_staff), ("ASCETA", scale.asceta_staff)):
        inst = tertiary[key]
        short = D.TERTIARY[key][1]
        hr_ctx = _user(
            f"hr.{short.lower()}@abia.demo",
            f"Head of Establishments, {short}",
            "HR",
            inst.scope_node_id,
            out,
            inst.name,
        )
        with context.use(hr_ctx):
            positions = list(Position.objects.filter(institution_id=inst.id).values_list("id", flat=True))
            have = EmploymentRecord.objects.filter(position_id__in=positions).count()
        if have >= total:
            continue
        ranks = D.UNIVERSITY_RANKS if key == "ABSU" else D.COLLEGE_RANKS
        depts = [d for rows in D.FACULTIES[key].values() for _p, _n, d, _t in rows]
        academic_n = int(total * 0.72)
        for i in range(have, total):
            academic_ = i < academic_n
            title, gl = ranks[i % len(ranks)] if academic_ else D.SUPPORT_POSTS[i % len(D.SUPPORT_POSTS)]
            where = depts[i % len(depts)].replace("Department of ", "")
            sex = "female" if rng.random() < 0.45 else "male"
            given, _m, family, dob = names.person(sex, dt.date(1968, 1, 1), 365 * 27)  # all below retirement age
            with context.use(hr_ctx):
                pos = est.create_position(
                    est.NewPosition(
                        title=f"{title}, {where}" if academic_ else f"{title} ({short})",
                        cadre_code="LECTURER" if academic_ else "NONACAD",
                        employer_scope_id=inst.scope_node_id,
                        grade_level_min=max(8 if academic_ else 3, gl - 1),
                        grade_level_max=min(15 if academic_ else 14, gl + 1),
                        institution_id=inst.id,
                    )
                )
                staff = people.create_staff_master(given, family, date_of_birth=dob, sex=sex)
                first = dt.date(rng.randrange(min(2023, max(1995, dob.year + 22)), 2024), rng.randrange(1, 13), 1)
                est.appoint(
                    est.Appointment(
                        staff_id=staff.id, position_id=pos.id, appointment_type="first_appointment",
                        first_appointment_on=first, grade_level=gl, step=rng.randrange(1, 8),
                        confirmed_on=first + dt.timedelta(days=730) if first.year < 2024 else None,
                    )
                )  # fmt: skip
            out.staff += 1
        log(f"  {inst.name}: {total} academic and support staff appointed")


# --------------------------------------------------------------------------- facilities, budgets, funding samples
def _extras(schools: list[Any], tertiary: dict[str, Any], names: _Names, out: Loaded, log: Log) -> None:
    from syntegra.estate import services as estate
    from syntegra.estate.models import PropertySite
    from syntegra.finance import budgets
    from syntegra.finance.models import BudgetLine, CostCentre

    rng = names.rng
    sample = schools[:: max(1, len(schools) // 12)][:12] + list(tertiary.values())
    for inst in sample:
        if PropertySite.objects.filter(institution_id=inst.id).exists():
            continue
        head = _user(f"estate.{inst.institution_code.lower()}@abia.demo", f"Facilities officer, {inst.name}", "OPSM",
                     inst.scope_node_id, out, inst.name)  # fmt: skip
        with context.use(head):
            site = estate.register_site(
                inst.id, site_code=f"SITE-{str(inst.id)[:6]}", name=f"{inst.name} — main site",
                owner="state_government", title_document=rng.choice(["certificate_of_occupancy", "none_or_unknown", "gazette"]),
                area_sqm=rng.randrange(8000, 60000), fenced=rng.choice(["fully_fenced", "partly_fenced", "not_fenced"]),
                encroachment=rng.choice(["none", "none", "none", "suspected"]),
            )  # fmt: skip
            water, power = rng.random() < 0.7, rng.random() < 0.55
            estate.assess("site", site.id, condition_grade="fair", usability="fully_usable", structural_risk="info",
                          in_use=True, utilities={"water": water, "power": power}, assessor_kind="estate_officer")  # fmt: skip
            for b in range(2):
                block = estate.add_building(inst.id, f"Classroom block {'AB'[b]}", built_year=rng.randrange(1965, 2018),
                                            facilities={"water": water, "power": power})  # fmt: skip
                grade_ = rng.choices(["good", "fair", "poor", "unsafe"], [3, 4, 2, 1])[0]
                use = {"good": "fully_usable", "fair": "usable_minor_repairs", "poor": "usable_major_repairs",
                       "unsafe": "unsafe_restricted"}[grade_]  # fmt: skip
                estate.assess("building", block.id, condition_grade=grade_, usability=use,
                              structural_risk={"good": "info", "fair": "moderate", "poor": "high", "unsafe": "critical"}[grade_],
                              in_use=True, repair_estimate_minor=0 if grade_ == "good" else rng.randrange(5, 60) * 100_000_00,
                              assessor_kind="engineer")  # fmt: skip
                for r in range(4):
                    room = estate.add_room(block.id, f"{'AB'[b]}{r + 1}", "classroom", 45)
                    if grade_ in ("poor", "unsafe") and r == 0:
                        estate.assess("room", room.id, condition_grade="unsafe" if grade_ == "unsafe" else "poor",
                                      usability="unusable" if grade_ == "unsafe" else "usable_major_repairs",
                                      structural_risk="high", in_use=grade_ != "unsafe", learners_affected=45,
                                      repair_estimate_minor=rng.randrange(2, 9) * 100_000_00)  # fmt: skip
                estate.add_room(block.id, f"{'AB'[b]}T", "toilet", 8)
            gen = estate.add_asset(inst.id, f"GEN-{str(inst.id)[:6]}", "Generator 30 kVA", "generator",
                                   safety_check_due_on=dt.date.today() + dt.timedelta(days=rng.randrange(-20, 40)))  # fmt: skip
            estate.schedule_maintenance("asset", gen.id, task="Generator 250-hour service", task_kind="generator_service",
                                        frequency_days=60, next_due_on=dt.date.today() + dt.timedelta(days=rng.randrange(-10, 30)))  # fmt: skip
    log(f"  facilities registered and assessed for {len(sample)} institutions")
    # budgets and imprest at ABSU
    absu = tertiary.get("ABSU")
    if absu is not None and not CostCentre.objects.filter(institution_id=absu.id).exists():
        bursar = _user("bursar.absu@abia.demo", "Bursar, ABSU", "FINO", absu.scope_node_id, out, absu.name)
        vc = _user("vc.absu@abia.demo", "Vice-Chancellor", "HEAD", absu.scope_node_id, out, absu.name)
        with context.use(bursar):
            centres = {code: budgets.create_cost_centre(absu.id, code, name, kind) for code, name, kind in (
                ("REG", "Registry", "administration"), ("WORKS", "Works and Services", "estate"),
                ("ICT", "ICT Directorate", "ict"), ("LIB", "University Library", "library"),
            )}  # fmt: skip
            budget = budgets.prepare_budget(absu.id, 2026, [
                budgets.LineInput(centres["REG"].id, "22020301", 45_000_000_00, description="Office stationery and consumables"),
                budgets.LineInput(centres["WORKS"].id, "22020403", 180_000_000_00, description="Maintenance of buildings"),
                budgets.LineInput(centres["ICT"].id, "22020404", 95_000_000_00, description="ICT equipment maintenance"),
                budgets.LineInput(centres["LIB"].id, "22020302", 60_000_000_00, description="Books and journals"),
                budgets.LineInput(centres["WORKS"].id, "23030121", 420_000_000_00, "capital_allocation", "Rehabilitation of lecture theatres"),
            ])  # fmt: skip
        with context.use(vc):
            budgets.approve_budget(budget.id)
        lines = {ln.economic_code: ln for ln in BudgetLine.objects.filter(budget_id=budget.id)}
        with context.use(bursar):
            c = budgets.commit(lines["22020403"].id, 62_500_000_00, source_kind="purchase_order", source_id=uuid.uuid4(),
                               description="Roof repairs, Faculty of Law block")  # fmt: skip
            budgets.spend(c.id, 58_200_000_00, final=True)
            budgets.commit(lines["22020404"].id, 31_000_000_00, source_kind="requisition", source_id=uuid.uuid4(),
                           description="Servers and network switches")  # fmt: skip
        log("  ABSU budget approved, committed and partly spent")
    if absu is not None:
        _funding_samples(absu, out, log)


def _teachers(schools: list[Any], names: _Names, out: Loaded, log: Log, per_school: int = 8) -> None:
    """Teachers (employed by ASUBEB) at the sample secondary schools that have facilities — the invigilators for
    the examination seating demonstration."""
    from syntegra.estate.models import PropertySite
    from syntegra.hr import establishment as est
    from syntegra.hr.models import EmploymentRecord, Position
    from syntegra.people import services as people

    board = _node("AB-ASUBEB")
    sta = _user("hr.ministry@abia.gov.ng", "Director of Establishments, Ministry of Education", "HR",
                _node(STATE).id, out, "Abia State")  # fmt: skip
    rng = names.rng
    subjects = ("Mathematics", "English Language", "Basic Science", "Civic Education", "Biology", "Igbo Language",
                "Physics", "Chemistry")  # fmt: skip
    done = 0
    for inst in schools:
        if inst.category != "combined_secondary" or not PropertySite.objects.filter(institution_id=inst.id).exists():
            continue
        positions = list(Position.objects.filter(institution_id=inst.id).values_list("id", flat=True))
        if EmploymentRecord.objects.filter(position_id__in=positions).exists():
            continue
        with context.use(sta):
            for i in range(per_school):
                sex = "female" if rng.random() < 0.55 else "male"
                given, _m, family, dob = names.person(sex, dt.date(1972, 1, 1), 365 * 24)
                gl = rng.randrange(8, 13)
                pos = est.create_position(
                    est.NewPosition(
                        title=f"Teacher, {subjects[i % len(subjects)]}",
                        cadre_code="TEACHER",
                        employer_scope_id=board.id,
                        grade_level_min=max(7, gl - 1),
                        grade_level_max=min(16, gl + 1),
                        institution_id=inst.id,
                    )
                )
                staff = people.create_staff_master(given, family, date_of_birth=dob, sex=sex)
                first = dt.date(rng.randrange(min(2023, max(2000, dob.year + 23)), 2024), rng.randrange(1, 13), 1)
                est.appoint(
                    est.Appointment(
                        staff_id=staff.id, position_id=pos.id, appointment_type="first_appointment",
                        first_appointment_on=first, grade_level=gl, step=rng.randrange(1, 6),
                        confirmed_on=first + dt.timedelta(days=730) if first.year < 2024 else None,
                    )
                )  # fmt: skip
                out.staff += 1
        done += 1
    if done:
        log(f"  {done * per_school} teachers appointed at {done} secondary schools (employer: ASUBEB)")


def _classrooms(schools: list[Any], out: Loaded, log: Log) -> None:
    """At the sample secondary schools: a teacher's sign-in, home rooms for the classes (never a room assessed unsafe),
    and, in SS 2A, a learner with an authorised front-seat adjustment and three pairs of learners whose (synthetic)
    behaviour evidence says they should not sit together — for the classroom seating demonstration."""
    from syntegra.academic.models import ClassGroup, ClassMembership
    from syntegra.estate.models import PropertySite
    from syntegra.estate.services import UNSAFE_USABILITY, room_usability
    from syntegra.operations.models import Room
    from syntegra.people.models import Staff, StaffPost
    from syntegra.success.models import Adjustment, InfluenceScore

    done = 0
    for inst in schools:
        if inst.category != "combined_secondary" or not PropertySite.objects.filter(institution_id=inst.id).exists():
            continue
        post = StaffPost.objects.filter(institution_id=inst.id, valid_to__isnull=True).order_by("staff_id").first()
        if post is None:
            continue
        teacher = Staff.objects.get(pk=post.staff_id)
        tch = _user(f"teacher.{inst.institution_code.lower()}@abia.demo",
                    f"{teacher.given_name} {teacher.family_name}, teacher", "TCH", inst.scope_node_id, out, inst.name)  # fmt: skip
        classes = list(ClassGroup.objects.filter(institution_id=inst.id).order_by("name"))
        if all(c.room_id for c in classes):
            continue
        rooms = list(Room.objects.filter(scope_node_id=inst.scope_node_id, room_type="classroom").order_by("code"))
        use = room_usability([r.id for r in rooms])
        rooms = [r for r in rooms if use.get(r.id) not in UNSAFE_USABILITY]
        head = _user(f"estate.{inst.institution_code.lower()}@abia.demo", "Facilities officer", "OPSM",
                     inst.scope_node_id, out, inst.name)  # fmt: skip
        ss2a = next((c for c in classes if c.name == "SS 2A"), None)
        with context.use(head), uow.command("ops", None, action="demo_classrooms", record_kind="class_group") as cmd:
            for i, c in enumerate(classes):
                if rooms and not c.room_id:
                    cmd.update(
                        c, room_id=rooms[i % len(rooms)].id, form_teacher_staff_id=teacher.id if c is ss2a else None
                    )
            if ss2a is not None:
                learners = sorted(
                    ClassMembership.objects.filter(class_group_id=ss2a.id, valid_to__isnull=True).values_list(
                        "learner_id", flat=True
                    ),
                    key=str,
                )
                if len(learners) >= 8:
                    cmd.add(Adjustment(learner_id=learners[0], adjustment_kind="seating",
                                       parameters={"note": "front row — short-sighted, glasses on order"},
                                       applies_to=["lessons", "rooms"], authorised_by=tch.actor_id,
                                       valid_from=dt.date(2026, 9, 14)))  # fmt: skip
                    now = utcnow()
                    for a, b, shared, neg_adj, neg_apart in ((1, 2, 31, 9, 2), (3, 4, 26, 7, 1), (5, 6, 24, 6, 2)):
                        x, y = sorted((learners[a], learners[b]), key=str)
                        cmd.add(InfluenceScore(class_group_id=ss2a.id, learner_a_id=x, learner_b_id=y,
                                               shared_events=shared, negative_adjacent=neg_adj,
                                               negative_apart=neg_apart, positive_adjacent=1, positive_apart=3,
                                               computed_at=now))  # fmt: skip
        done += 1
    if done:
        log(f"  classroom seating samples at {done} secondary schools (teacher sign-in, home rooms, SS 2A)")


def _funding_samples(absu: Any, out: Loaded, log: Log) -> None:
    """Imprest, a staff co-operative loan and a TETFund intervention at ABSU, each through its full approval chain."""
    from syntegra.finance import budgets
    from syntegra.finance.models import Budget, BudgetLine, Imprest
    from syntegra.funding import services as funding
    from syntegra.funding.models import FundingApplication, FundingProgramme
    from syntegra.hr.models import EmploymentRecord, Position

    if FundingApplication.objects.filter(institution_id=absu.id).exists():
        return
    approved = Budget.objects.filter(scope_node_id=absu.scope_node_id, status="approved").first()
    positions = list(Position.objects.filter(institution_id=absu.id).values_list("id", flat=True))
    staff_ids = list(
        EmploymentRecord.objects.filter(position_id__in=positions).order_by("id").values_list("staff_id", flat=True)[:2]
    )
    if approved is None or len(staff_ids) < 2:
        return
    lines = {ln.economic_code: ln for ln in BudgetLine.objects.filter(budget_id=approved.id)}
    state = _node(STATE)
    where = absu.name
    bursar = _user("bursar.absu@abia.demo", "Bursar, ABSU", "FINO", absu.scope_node_id, out, where)
    vc = _user("vc.absu@abia.demo", "Vice-Chancellor", "HEAD", absu.scope_node_id, out, where)
    hr = _user("hr.absu@abia.demo", "Head of Establishments, ABSU", "HR", absu.scope_node_id, out, where)
    dps = _user("director.planning@abia.gov.ng", "Director of Planning, Research and Statistics", "STA", state.id,
                out, "Abia State")  # fmt: skip
    if not Imprest.objects.filter(scope_node_id=absu.scope_node_id).exists():
        with context.use(bursar):
            imp = budgets.request_imprest(staff_ids[0], lines["22020301"].id, "Matriculation ceremony — logistics",
                                          2_400_000_00, dt.date.today() + dt.timedelta(days=21))  # fmt: skip
        with context.use(vc):
            budgets.approve_imprest(imp.id)
    progs = {p.code: p for p in FundingProgramme.objects.filter(code__in=("STAFF-COOP", "TETFUND-AI"))}
    if "STAFF-COOP" in progs:
        with context.use(hr):
            loan = funding.apply(progs["STAFF-COOP"].id, applicant_kind="staff", applicant_id=staff_ids[1],
                                 institution_id=absu.id, amount_minor=1_500_000_00,
                                 purpose_detail="Children's school fees and household items")  # fmt: skip
        with context.use(vc):
            funding.recommend(loan.id, "Confirmed staff in good standing; recommended for approval.")
        with context.use(dps):
            funding.decide(loan.id, True, "Within the co-operative limit and affordable from pay.")
            agreement = funding.sign_agreement(loan.id, gross_pay_minor=450_000_00)
        with context.use(bursar):
            funding.disburse(agreement.id, 1_500_000_00, payee_kind="beneficiary", purpose="Loan disbursement",
                             reference=f"COOP-{agreement.agreement_number[-6:]}")  # fmt: skip
    if "TETFUND-AI" in progs:
        with context.use(vc):
            grant = funding.apply(progs["TETFUND-AI"].id, applicant_kind="institution", applicant_id=absu.id,
                                  institution_id=absu.id, amount_minor=350_000_000_00,
                                  purpose_detail="Rehabilitation of the Faculty of Science lecture theatres")  # fmt: skip
        with context.use(hr):
            funding.recommend(grant.id, "Project is in the approved capital plan and the site has been assessed.")
        with context.use(dps):
            funding.decide(grant.id, True, "Approved under the annual direct disbursement allocation.")
            agreement = funding.sign_agreement(grant.id)
        with context.use(bursar):
            funding.disburse(agreement.id, 175_000_000_00, payee_kind="institution", purpose="First tranche (50 %)",
                             reference="TETF-AI-2026-01", budget_line_id=lines["23030121"].id)  # fmt: skip
    log("  imprest, a staff loan and a TETFund intervention taken through approval at ABSU")


# --------------------------------------------------------------------------- entry point
def run(scale: Scale | None = None, log: Log = print) -> Loaded:
    scale = scale or Scale()
    out = Loaded()
    names = _Names(random.Random(scale.seed))
    with context.use(_sys()):
        log("1/6 governance: LGAs, ministries and ASUBEB")
        lgas = _lgas(scale, out)
        nodes = _authorities(out)
        _people_users(nodes, out)
        session, _term = _calendar()
        subjects = _subjects()
        n_lgas = scale.lgas or len(lgas)
        log(
            f"2/6 schools: {scale.schools_per_lga} primary and {scale.schools_per_lga} secondary in each of {n_lgas} LGAs"
        )
        # learners already in the state keep their names unique
        from syntegra.learners.models import Learner

        names.used |= {
            (g.lower(), f.lower(), d, s)
            for g, f, d, s in Learner.objects.values_list(
                "legal_given_name", "legal_family_name", "date_of_birth", "sex"
            )
        }
        schools = _schools(lgas[: scale.lgas] if scale.lgas else lgas, session, subjects, names, scale, out, log)
        log("3/6 tertiary: ABSU and ASCETA")
        tertiary = _tertiary({n.code: n for n, _t, _u in lgas}, session, names, scale, out, log)
        log("4/6 staff")
        _staff(tertiary, names, scale, out, log)
        if scale.extras:
            log("5/6 facilities and budgets")
            _extras(schools, tertiary, names, out, log)
            _teachers(schools, names, out, log)
            _classrooms(schools, out, log)
            log("6/6 daily jobs: facility rules and the warehouse")
            from syntegra.analytics import warehouse
            from syntegra.estate import services as estate

            estate.run_daily()
            out.notes.append(f"warehouse: {warehouse.load()}")
    return out
