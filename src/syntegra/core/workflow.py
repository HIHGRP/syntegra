"""Workflow engine (MFS §7, Book 3 §12): versioned state machines with human tasks.

A ``workflow_definition.definition`` is JSON::

    {"initial": "submitted",
     "transitions": [{"from": "submitted", "on": "approve", "to": "approved", "permission": "admission:decide",
                      "guard": "documents_complete"}, ...],
     "tasks": {"submitted": {"title": "Review application", "role": "ADM", "sla_hours": 72}},
     "final": ["approved", "rejected"]}

An instance runs on the definition version it started with. Each transition is appended to
``workflow_transition`` (append-only); a state with a ``tasks`` entry opens a ``workflow_task`` assigned by
role at the instance's scope, and leaving the state completes it.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from syntegra.core import context, policy, uow
from syntegra.core.errors import ConflictError, Forbidden, NotFound
from syntegra.core.fields import utcnow
from syntegra.core.zones import current_alias


def _definition(key: str, version: int | None = None) -> Any:
    from syntegra.governance.models import WorkflowDefinition

    ctx = context.require()
    qs = WorkflowDefinition.unscoped.using(current_alias("registry")).filter(
        tenant_id=ctx.state_tenant_id, workflow_key=key, status="published"
    )
    if version is not None:
        qs = qs.filter(version=version)
    d = qs.order_by("-version").first()
    if d is None:
        raise NotFound("workflow definition", key)
    return d


def _open_task(cmd: uow.Command, inst: Any, spec: dict[str, Any], state: str) -> None:
    from syntegra.governance.models import WorkflowTask

    task = spec.get("tasks", {}).get(state)
    if not task:
        return
    due = utcnow() + dt.timedelta(hours=int(task["sla_hours"])) if task.get("sla_hours") else None
    t = WorkflowTask(
        tenant_id=inst.tenant_id, scope_node_id=inst.scope_node_id, instance_id=inst.id, step_key=state,
        title=task["title"], assignee_role=task.get("role"), assignee_scope_id=inst.scope_node_id,
        approval_type=task.get("approval_type", "single"), due_at=due, status="open",
    )
    cmd.add(t)


def start(zone: str, key: str, *, subject_kind: str, subject_id: uuid.UUID, scope_node_id: uuid.UUID,
          variables: dict[str, Any] | None = None, cmd: uow.Command | None = None) -> Any:
    from syntegra.governance.models import WorkflowInstance, WorkflowTransition

    d = _definition(key)
    spec = d.definition

    def run(c: uow.Command) -> Any:
        inst = WorkflowInstance(
            scope_node_id=scope_node_id, definition_id=d.id, subject_kind=subject_kind, subject_id=subject_id,
            state=spec["initial"], status="running", started_by=c.ctx.actor_id, context=variables or {},
        )
        c.add(inst)
        c.add(WorkflowTransition(instance_id=inst.id, from_state=None, to_state=spec["initial"],
                                 actor=c.ctx.actor_id, occurred_at=utcnow()))
        _open_task(c, inst, spec, spec["initial"])
        return inst

    if cmd is not None:
        return run(cmd)
    with uow.command(zone, None, action="workflow_start", record_kind="workflow_instance") as c:
        return run(c)


def available(spec: dict[str, Any], state: str) -> list[str]:
    return [t["on"] for t in spec.get("transitions", []) if t["from"] == state]


def fire(zone: str, instance_id: uuid.UUID, event: str, *, reason: str | None = None,
         variables: dict[str, Any] | None = None) -> Any:
    from syntegra.governance.models import WorkflowDefinition, WorkflowInstance, WorkflowTask, WorkflowTransition

    ctx = context.require()
    with uow.command(zone, None, action=f"workflow_{event}", record_kind="workflow_instance", reason=reason) as c:
        inst = c.lock(WorkflowInstance, instance_id)
        if inst.status not in ("running", "waiting"):
            raise ConflictError("WF-CLOSED", "Workflow is closed", f"The workflow is {inst.status}.")
        d = WorkflowDefinition.unscoped.using(current_alias("registry")).get(pk=inst.definition_id)
        spec = d.definition
        match = [t for t in spec.get("transitions", []) if t["from"] == inst.state and t["on"] == event]
        if not match:
            raise ConflictError("WF-TRANSITION", "Action not available",
                                f"'{event}' is not possible from '{inst.state}'. Available: {available(spec, inst.state)}")
        t = match[0]
        if t.get("permission") and not ctx.has(t["permission"]):
            raise Forbidden(f"Missing permission {t['permission']}.", code="AUTH-PERMISSION")
        vars_ = {**(inst.context or {}), **(variables or {})}
        if t.get("guard") and not policy.evaluate(t["guard"], vars_):
            raise ConflictError("WF-GUARD", "Conditions not met", f"The step '{event}' requires: {t['guard']}")
        from_state = inst.state
        for task in WorkflowTask.unscoped.using(c.alias).filter(instance_id=inst.id, status__in=("open", "claimed")):
            c.update(task, status="completed", decision=event, decided_by=ctx.actor_id, decided_at=utcnow())
        final = t["to"] in spec.get("final", [])
        c.update(inst, state=t["to"], context=vars_, status="completed" if final else "running",
                 completed_at=utcnow() if final else None)
        c.add(WorkflowTransition(instance_id=inst.id, from_state=from_state, to_state=t["to"], actor=ctx.actor_id,
                                 reason=reason, occurred_at=utcnow()))
        c.record_id = inst.id
        if not final:
            _open_task(c, inst, spec, t["to"])
        return inst
