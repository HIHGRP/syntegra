"""Messages between the school and parents (MFS COM-01, COM-101, FAM-03; CR-009 phase 4).

A member of staff writes to the parents of one learner, of several, or of a whole class in one step. Each parent gets
the message in their own conversation with that member of staff about that child, so a parent's reply is seen by the
sender and nobody else, and one parent never sees another's. A parent can also start a conversation with any of
their child's teachers, or the form teacher.

Who is written to: guardians with parental responsibility whose link to the learner is not contact-restricted (the
court order behind a restriction is held by the safeguarding lead; the safe reading of an order the school office
cannot see is "no contact"). A parent with a Syntegra account receives the message in the app at once; a parent
without one is sent it by SMS — the message is queued for the school's SMS gateway and shows as queued until the
gateway reports delivery. No gateway is connected in this release, so SMS messages stay queued: the page says so.

Each conversation records who is in it, and each message when it was sent, delivered and read. A member of staff
sees their own conversations; the head sees every conversation at the school (the communication log).
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from syntegra.comms.models import ChannelContact, Conversation, Message, MessageChannel
from syntegra.core import authz, context, crypto, uow
from syntegra.core.errors import Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.families import portal

MAX_BODY = 1000
MAX_LEARNERS = 60


def _institution(institution_id: uuid.UUID) -> Any:
    from syntegra.institutions.models import Institution

    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def _body(text: str | None) -> str:
    body = (text or "").strip()
    if len(body) < 2:
        raise HardValidation("COM-BODY", "Write the message", "The message is empty.")
    if len(body) > MAX_BODY:
        raise HardValidation(
            "COM-BODY", "The message is too long", f"Keep it to {MAX_BODY} characters; it is {len(body)}."
        )
    return body


def _in_app_channel(cmd: uow.Command, inst: Any) -> MessageChannel:
    ch: MessageChannel | None = MessageChannel.objects.filter(
        scope_node_id=inst.scope_node_id, channel="in_app", status="active"
    ).first()
    if ch is None:
        ch = cmd.add(
            MessageChannel(
                scope_node_id=inst.scope_node_id,
                channel="in_app",
                provider="syntegra",
                display_name=f"{inst.name} — messages in Syntegra",
                address=inst.institution_code,
                credentials_vault_ref="none: in-app delivery needs no provider",
                quiet_hours={"from": "20:00", "to": "07:00"},
                status="active",
            )
        )
    return ch


def _endpoint(guardian_id: uuid.UUID) -> str:
    return f"guardian:{guardian_id}"


def _contact(cmd: uow.Command, guardian_id: uuid.UUID) -> ChannelContact:
    """The guardian's in-app contact (one per guardian; the endpoint is the guardian, not a device)."""
    ctx = cmd.ctx
    hm = crypto.lookup_hmac(_endpoint(guardian_id), scheme="contact:in_app", tenant_id=ctx.tenant_id)
    c: ChannelContact | None = ChannelContact.objects.filter(channel="in_app", endpoint_hmac=hm).first()
    if c is None:
        c = cmd.add(
            ChannelContact(
                person_kind="guardian",
                person_id=guardian_id,
                channel="in_app",
                endpoint_hmac=hm,
                endpoint_enc=crypto.encrypt(_endpoint(guardian_id), purpose="channel_contact", tenant_id=ctx.tenant_id),
                endpoint_last4=None,
                is_verified=True,
            )
        )
    return c


def _staff_id(user_id: uuid.UUID | None) -> uuid.UUID | None:
    from syntegra.iam.models import AppUser

    if user_id is None:
        return None
    u = AppUser.objects.filter(pk=user_id).first()
    return u.person_id if u is not None and u.person_kind == "staff" else None


def _conversation(
    cmd: uow.Command, inst: Any, contact: ChannelContact, learner_id: uuid.UUID, staff_user_id: uuid.UUID
) -> Conversation:
    conv: Conversation | None = Conversation.objects.filter(
        scope_node_id=inst.scope_node_id,
        contact_id=contact.id,
        linked_record_kind="learner",
        linked_record_id=learner_id,
        assigned_user_id=staff_user_id,
    ).first()
    if conv is None:
        conv = cmd.add(
            Conversation(
                scope_node_id=inst.scope_node_id,
                channel_id=_in_app_channel(cmd, inst).id,
                contact_id=contact.id,
                linked_record_kind="learner",
                linked_record_id=learner_id,
                assigned_office="class_teacher",
                assigned_user_id=staff_user_id,
                status="open",
            )
        )
    elif conv.status != "open":
        cmd.update(conv, status="open")
    return conv


def _message(cmd: uow.Command, conv: Conversation, *, direction: str, body: str, parent: dict[str, Any] | None,
             staff_id: uuid.UUID | None) -> Message:  # fmt: skip
    """One message. Outbound to a parent with an account is delivered in the app at once; to a parent without one it
    is queued for SMS. Inbound (from a parent) is delivered to the member of staff in the app."""
    now = utcnow()
    ctx = cmd.ctx
    if direction == "outbound":
        assert parent is not None
        in_app = parent["user_id"] is not None
        channel = "in_app" if in_app else "sms"
        status = "delivered" if in_app else "queued"
        recipient_kind, recipient_id = "guardian", parent["guardian_id"]
    else:
        channel, status, recipient_kind, recipient_id = "in_app", "delivered", "staff", staff_id
    m = Message(
        tenant_id=ctx.tenant_id,
        created_on=now.date(),
        conversation_id=conv.id,
        direction=direction,
        channel=channel,
        recipient_kind=recipient_kind,
        recipient_id=recipient_id,
        about_learner_id=conv.linked_record_id,
        language=(parent or {}).get("language"),
        body=body,
        priority="normal",
        delivery_status=status,
        delivered_at=now if status == "delivered" else None,
        sent_by=ctx.actor_id,
        created_by=ctx.actor_id,
    )
    Message.unscoped.using(cmd.alias).bulk_create([m])
    cmd.note(f"message:{m.id}", None, {"direction": direction, "channel": channel, "status": status})
    return m


# --------------------------------------------------------------------------- staff side
def _learners_at(inst: Any, learner_ids: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, Any]]:
    """The learners, each with their class, when they are on roll at the school."""
    from syntegra.academic.models import ClassGroup, ClassMembership
    from syntegra.learners.models import Learner

    today = dt.date.today()
    members = {
        m.learner_id: m
        for m in ClassMembership.objects.filter(learner_id__in=learner_ids, is_arm=True, valid_from__lte=today).exclude(
            valid_to__lt=today
        )
    }
    groups = {
        c.id: c
        for c in ClassGroup.objects.in_scope().filter(
            institution_id=inst.id, id__in=[m.class_group_id for m in members.values()]
        )
    }
    out = {}
    for lr in Learner.objects.filter(id__in=[lid for lid, m in members.items() if m.class_group_id in groups]):
        cls = groups[members[lr.id].class_group_id]
        out[lr.id] = {"id": lr.id, "name": f"{lr.legal_given_name} {lr.legal_family_name}", "class": cls.name}
    return out


def compose(institution_id: uuid.UUID, class_id: uuid.UUID | None = None) -> dict[str, Any]:
    """What the message form needs: the school's classes and, for the chosen class, its learners with the parents the
    school can reach about each (in the app or by SMS) — and the ones it cannot."""
    from syntegra.academic.models import ClassGroup, ClassMembership

    authz.require("message:send")
    inst = _institution(institution_id)
    classes = list(
        ClassGroup.objects.in_scope().filter(institution_id=inst.id, status="active", kind="arm").order_by("name")
    )
    out: dict[str, Any] = {
        "institution": {"id": inst.id, "name": inst.name},
        "classes": [{"id": c.id, "name": c.name} for c in classes],
        "class": None,
        "learners": [],
    }
    cls = next((c for c in classes if c.id == class_id), None)
    if cls is None:
        return out
    today = dt.date.today()
    ids = list(
        ClassMembership.objects.filter(class_group_id=cls.id, valid_from__lte=today)
        .exclude(valid_to__lt=today)
        .values_list("learner_id", flat=True)
    )
    names = _learners_at(inst, ids)
    parents = portal.parents_of(list(names))
    rows = []
    for lid, info in names.items():
        ps = parents.get(lid, [])
        rows.append(
            {
                **info,
                "parents": ps,
                "in_app": sum(1 for p in ps if p["user_id"]),
                "sms": sum(1 for p in ps if not p["user_id"] and p["phone"]),
                "unreachable": not any(p["user_id"] or p["phone"] for p in ps),
            }
        )
    out["class"] = {"id": cls.id, "name": cls.name}
    out["learners"] = sorted(rows, key=lambda r: r["name"])
    return out


def send(institution_id: uuid.UUID, learner_ids: list[uuid.UUID], body: str) -> dict[str, Any]:
    """Send the message to the parents of each learner: a separate conversation per parent and learner."""
    ctx = context.require()
    authz.require("message:send", ctx)
    inst = _institution(institution_id)
    text = _body(body)
    if not learner_ids:
        raise HardValidation("COM-TO", "Choose who the message is about", "Tick at least one learner.")
    if len(learner_ids) > MAX_LEARNERS:
        raise HardValidation(
            "COM-TO", "Too many learners at once", f"Send to at most {MAX_LEARNERS} learners in one message."
        )
    learners = _learners_at(inst, list(dict.fromkeys(learner_ids)))
    if len(learners) != len(set(learner_ids)):
        raise HardValidation("COM-TO", "A learner is not on roll here", "Choose learners from the class lists.")
    parents = portal.parents_of(list(learners))
    tally: dict[str, Any] = {"in_app": 0, "sms": 0, "learners": len(learners), "unreachable": []}
    with uow.command("ops", "message:send", action="send_message", record_kind="conversation") as cmd:
        for lid, info in learners.items():
            reachable = [p for p in parents.get(lid, []) if p["user_id"] or p["phone"]]
            if not reachable:
                tally["unreachable"].append(info["name"])
                continue
            for p in reachable:
                conv = _conversation(cmd, inst, _contact(cmd, p["guardian_id"]), lid, ctx.actor_id)  # type: ignore[arg-type]
                m = _message(cmd, conv, direction="outbound", body=text, parent=p, staff_id=None)
                tally[m.channel] += 1
    return tally


def _guardian_label(contact_ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    from syntegra.families.models import Guardian

    contacts = {c.id: c.person_id for c in ChannelContact.objects.filter(id__in=contact_ids)}
    people = {g.id: portal.guardian_name(g) for g in Guardian.objects.filter(id__in=set(contacts.values()))}
    return {cid: people.get(gid, "Parent") for cid, gid in contacts.items()}


def _user_names(ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    from syntegra.iam.models import AppUser

    return {u.id: u.display_name for u in AppUser.objects.filter(id__in=ids)}


def _summaries(convs: list[Conversation], *, unread_direction: str) -> list[dict[str, Any]]:
    """Each conversation with its last message and the number unread by the viewer."""
    from syntegra.learners.models import Learner

    ids = [c.id for c in convs]
    msgs = list(Message.objects.filter(conversation_id__in=ids).order_by("created_at"))
    last: dict[uuid.UUID, Message] = {}
    unread: dict[uuid.UUID, int] = {}
    for m in msgs:
        last[m.conversation_id] = m
        if m.direction == unread_direction and m.read_at is None and m.channel == "in_app":
            unread[m.conversation_id] = unread.get(m.conversation_id, 0) + 1
    learners = {
        lr.id: f"{lr.legal_given_name} {lr.legal_family_name}"
        for lr in Learner.objects.filter(id__in={c.linked_record_id for c in convs})
    }
    parents = _guardian_label({c.contact_id for c in convs if c.contact_id})
    staff = _user_names({c.assigned_user_id for c in convs if c.assigned_user_id})
    rows = []
    for c in convs:
        m = last.get(c.id)
        if m is None:
            continue
        rows.append(
            {
                "id": c.id,
                "learner": learners.get(c.linked_record_id, "Learner"),
                "parent": parents.get(c.contact_id, "Parent"),
                "staff": staff.get(c.assigned_user_id, "Staff"),
                "last": (m.body or "")[:140],
                "last_at": m.created_at,
                "last_from_parent": m.direction == "inbound",
                "unread": unread.get(c.id, 0),
                "status": c.status,
            }
        )
    return sorted(rows, key=lambda r: r["last_at"], reverse=True)


def inbox(institution_id: uuid.UUID, everyone: bool = False) -> dict[str, Any]:
    """A member of staff's conversations with parents; the head can see every conversation at the school."""
    ctx = context.require()
    authz.require("message:send", ctx)
    inst = _institution(institution_id)
    qs = Conversation.objects.in_scope().filter(scope_node_id=inst.scope_node_id, linked_record_kind="learner")
    can_all = ctx.has("message:manage")
    if not (everyone and can_all):
        qs = qs.filter(assigned_user_id=ctx.actor_id)
    rows = _summaries(list(qs), unread_direction="inbound")
    return {
        "institution": {"id": inst.id, "name": inst.name},
        "conversations": rows,
        "unread": sum(r["unread"] for r in rows),
        "everyone": everyone and can_all,
        "can_all": can_all,
    }


def unread_for_staff() -> int:
    ctx = context.require()
    if not ctx.has("message:send"):
        return 0
    ids = list(Conversation.objects.in_scope().filter(assigned_user_id=ctx.actor_id).values_list("id", flat=True))
    return Message.objects.filter(conversation_id__in=ids, direction="inbound", read_at__isnull=True).count()


# --------------------------------------------------------------------------- one conversation
def _open(conversation_id: uuid.UUID) -> tuple[Conversation, str, dict[str, Any] | None]:
    """The conversation and who is looking: 'staff' (its member of staff, or the head) or 'parent' (the guardian in
    it, while the child is still theirs at this school)."""
    ctx = context.require()
    conv: Conversation | None = Conversation.objects.in_scope().filter(pk=conversation_id).first()
    if conv is None or conv.linked_record_kind != "learner":
        raise NotFound("conversation", conversation_id)
    g = portal.guardian()
    if g is not None:
        contact = ChannelContact.objects.filter(pk=conv.contact_id).first()
        if contact is None or contact.person_kind != "guardian" or contact.person_id != g.id:
            raise NotFound("conversation", conversation_id)
        child = portal.require_child(conv.linked_record_id)
        return conv, "parent", child
    if conv.assigned_user_id == ctx.actor_id and ctx.has("message:send"):
        return conv, "staff", None
    if ctx.has("message:manage"):
        return conv, "head", None
    raise Forbidden("This conversation is between a parent and another member of staff.", code="COM-OWN")


def thread(conversation_id: uuid.UUID) -> dict[str, Any]:
    """The conversation's messages, oldest first; opening it marks the other side's messages as read."""
    from syntegra.families.models import Guardian
    from syntegra.learners.models import Learner

    ctx = context.require()
    conv, viewer, child = _open(conversation_id)
    msgs = list(Message.objects.filter(conversation_id=conv.id).order_by("created_at"))
    incoming = "outbound" if viewer == "parent" else "inbound"
    unread = [m for m in msgs if m.direction == incoming and m.read_at is None and m.channel == "in_app"]
    if unread and viewer != "head":
        now = utcnow()
        with uow.command("ops", None, action="read_messages", record_kind="conversation") as cmd:
            cmd.record_id = conv.id
            for m in unread:
                Message.unscoped.using(cmd.alias).filter(id=m.id, created_on=m.created_on).update(
                    read_at=now, delivery_status="read"
                )
                m.read_at, m.delivery_status = now, "read"
            cmd.note("read", None, len(unread))
    contact = ChannelContact.objects.filter(pk=conv.contact_id).first()
    g = Guardian.objects.filter(pk=contact.person_id).first() if contact else None
    lr = Learner.objects.filter(pk=conv.linked_record_id).first()
    staff_name = _user_names({conv.assigned_user_id}).get(conv.assigned_user_id, "Staff")
    parent_name = portal.guardian_name(g) if g else "Parent"
    return {
        "id": conv.id,
        "viewer": viewer,
        "learner": {"id": lr.id, "name": f"{lr.legal_given_name} {lr.legal_family_name}"} if lr else None,
        "parent": parent_name,
        "staff": staff_name,
        "status": conv.status,
        "can_reply": viewer in ("staff", "parent") and conv.status != "closed",
        "messages": [
            {
                "id": m.id,
                "mine": (m.direction == "inbound") == (viewer == "parent"),
                "from": parent_name if m.direction == "inbound" else staff_name,
                "body": m.body,
                "at": m.created_at,
                "channel": m.channel,
                "status": m.delivery_status,
                "read_at": m.read_at,
            }
            for m in msgs
        ],
        "child": child,
        "me": ctx.actor_id,
    }


def reply(conversation_id: uuid.UUID, body: str) -> Message:
    """Reply in the conversation: the parent to the member of staff, or the member of staff to the parent."""
    conv, viewer, _child = _open(conversation_id)
    if viewer == "head":
        raise Forbidden("Only the member of staff in this conversation replies in it.", code="COM-OWN")
    text = _body(body)
    with uow.command("ops", None, action="reply_message", record_kind="conversation") as cmd:
        cmd.record_id = conv.id
        if conv.status != "open":
            cmd.update(conv, status="open")
        if viewer == "parent":
            return _message(cmd, conv, direction="inbound", body=text, parent=None,
                            staff_id=_staff_id(conv.assigned_user_id))  # fmt: skip
        contact = ChannelContact.objects.get(pk=conv.contact_id)
        p = next(
            (x for x in portal.parents_of([conv.linked_record_id]).get(conv.linked_record_id, [])
             if x["guardian_id"] == contact.person_id),
            None,
        )  # fmt: skip
        if p is None:
            raise Forbidden(
                "This parent can no longer be contacted about the learner (the link has ended or is restricted).",
                code="COM-RESTRICTED",
            )
        return _message(cmd, conv, direction="outbound", body=text, parent=p, staff_id=None)


def resolve(conversation_id: uuid.UUID) -> None:
    conv, viewer, _child = _open(conversation_id)
    if viewer == "parent":
        raise Forbidden("The school closes conversations.", code="COM-OWN")
    with uow.command("ops", "message:send", action="resolve_conversation", record_kind="conversation") as cmd:
        cmd.update(conv, status="resolved")


# --------------------------------------------------------------------------- parent side
def teachers_of(learner_id: uuid.UUID) -> list[dict[str, Any]]:
    """The child's form teacher and subject teachers who have a Syntegra account — whom a parent can write to."""
    from syntegra.academic import teaching
    from syntegra.iam.models import AppUser

    child = portal.require_child(learner_id)
    roles = teaching.teachers_of_class(child["class_id"])
    accounts = {
        u.person_id: u for u in AppUser.objects.filter(person_kind="staff", person_id__in=list(roles), status="active")
    }
    rows = [
        {"user_id": accounts[sid].id, "name": accounts[sid].display_name, "roles": r}
        for sid, r in roles.items()
        if sid in accounts
    ]
    return sorted(rows, key=lambda r: (r["roles"][0] != "Form teacher", r["name"]))


def parent_start(learner_id: uuid.UUID, staff_user_id: uuid.UUID, body: str) -> Conversation:
    """A parent writes to one of their child's teachers (or continues the conversation they already have)."""
    from syntegra.institutions.models import Institution

    authz.require("message:parent")
    g = portal.guardian()
    if g is None:
        raise Forbidden("Only a parent's account writes to a child's teachers here.", code="FAM-OWN")
    child = portal.require_child(learner_id)
    if staff_user_id not in {t["user_id"] for t in teachers_of(learner_id)}:
        raise HardValidation("COM-TO", "Choose one of your child's teachers", "Pick a name from the list.")
    text = _body(body)
    inst = Institution.objects.get(pk=child["institution_id"])
    with uow.command("ops", "message:parent", action="parent_message", record_kind="conversation") as cmd:
        conv = _conversation(cmd, inst, _contact(cmd, g.id), learner_id, staff_user_id)
        _message(cmd, conv, direction="inbound", body=text, parent=None, staff_id=_staff_id(staff_user_id))
        return conv


def parent_inbox() -> dict[str, Any]:
    """The signed-in parent's conversations about their children at this school."""
    g = portal.guardian()
    if g is None:
        return {"conversations": [], "unread": 0}
    contacts = list(ChannelContact.objects.filter(person_kind="guardian", person_id=g.id).values_list("id", flat=True))
    mine = {c["id"] for c in portal.children()}
    convs = [
        c
        for c in Conversation.objects.in_scope().filter(contact_id__in=contacts, linked_record_kind="learner")
        if c.linked_record_id in mine
    ]
    rows = _summaries(convs, unread_direction="outbound")
    return {"conversations": rows, "unread": sum(r["unread"] for r in rows)}
