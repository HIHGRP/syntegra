"""Policy engine (MFS §6, Book 3 §11): versioned rules at scope nodes, inherited down the hierarchy.

* A rule (``policy_rule``) is published at a scope node with a ``rule_key``, an ``expression`` in a small,
  safe expression language and ``parameters`` (thresholds, weights).
* The *effective* rule for a scope is the nearest published, in-force rule on the path to the root.
* ``is_mandatory_below`` makes an upper rule a floor: a lower level may only *tighten* parameters in the
  direction declared under ``parameters._tighten`` (``{"min_rate": "higher"}``); any other override is a
  conflict and the upper value wins (and is recorded as ``policy_conflict`` when attempted by a user).
* An approved ``policy_exception`` for the subject suspends the rule for its period.

The expression language is a subset of Python expressions evaluated over an explicit variable map:
literals, names, arithmetic, comparisons, ``and``/``or``/``not``, ``in``, conditional expressions and the
functions ``min``, ``max``, ``abs``, ``round``, ``len``. No attribute access, subscripts on objects, calls of
other functions, lambdas or comprehensions — anything else is rejected at parse time.
"""

from __future__ import annotations

import ast
import datetime as dt
import operator
import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from syntegra.core.errors import HardValidation

_BIN = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_CMP = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
}
_FUNCS = {"min": min, "max": max, "abs": abs, "round": round, "len": len}
_ALLOWED = (
    ast.Expression,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.IfExp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.List,
    ast.Tuple,
    ast.Subscript,
    ast.And,
    ast.Or,
    ast.Not,
    ast.USub,
    ast.UAdd,
    *_BIN,
    *_CMP,
)


class PolicyExpressionError(HardValidation):
    def __init__(self, detail: str):
        super().__init__("POLICY-EXPRESSION", "Invalid rule expression", detail)


@lru_cache(maxsize=2048)
def compile_expression(source: str) -> ast.Expression:
    try:
        tree = ast.parse(source, mode="eval")
    except SyntaxError as exc:
        raise PolicyExpressionError(str(exc)) from exc
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED):
            raise PolicyExpressionError(f"{type(node).__name__} is not allowed")
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id in _FUNCS):
            raise PolicyExpressionError("only min, max, abs, round and len may be called")
        if isinstance(node, ast.Subscript) and not isinstance(node.value, ast.Name):
            raise PolicyExpressionError("subscripts are allowed on variables only")
    return tree


def evaluate(source: str, variables: dict[str, Any]) -> Any:
    return _eval(compile_expression(source).body, variables)


def _eval(n: ast.AST, v: dict[str, Any]) -> Any:
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.Name):
        if n.id in ("true", "True"):
            return True
        if n.id in ("false", "False"):
            return False
        if n.id not in v:
            raise PolicyExpressionError(f"unknown variable {n.id}")
        return v[n.id]
    if isinstance(n, ast.BoolOp):
        if isinstance(n.op, ast.And):
            return all(_eval(x, v) for x in n.values)
        return any(_eval(x, v) for x in n.values)
    if isinstance(n, ast.UnaryOp):
        x = _eval(n.operand, v)
        return (not x) if isinstance(n.op, ast.Not) else (-x if isinstance(n.op, ast.USub) else +x)
    if isinstance(n, ast.BinOp):
        return _BIN[type(n.op)](_eval(n.left, v), _eval(n.right, v))
    if isinstance(n, ast.Compare):
        left = _eval(n.left, v)
        for op, comp in zip(n.ops, n.comparators, strict=True):
            right = _eval(comp, v)
            if not _CMP[type(op)](left, right):
                return False
            left = right
        return True
    if isinstance(n, ast.IfExp):
        return _eval(n.body, v) if _eval(n.test, v) else _eval(n.orelse, v)
    if isinstance(n, ast.Call):
        return _FUNCS[n.func.id](*[_eval(a, v) for a in n.args])  # type: ignore[attr-defined,operator]
    if isinstance(n, (ast.List, ast.Tuple)):
        return [_eval(x, v) for x in n.elts]
    if isinstance(n, ast.Subscript):
        return _eval(n.value, v)[_eval(n.slice, v)]
    raise PolicyExpressionError(type(n).__name__)


# --------------------------------------------------------------------------- effective rules
@dataclass
class EffectiveRule:
    rule_key: str
    expression: str
    parameters: dict[str, Any]
    source_rule_ids: list[uuid.UUID] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    exception_id: uuid.UUID | None = None

    def evaluate(self, variables: dict[str, Any]) -> Any:
        if self.exception_id:
            return True
        return evaluate(self.expression, {**self.parameters, **variables})


def tighter(direction: str, upper: Any, lower: Any) -> bool:
    if direction == "higher":
        return bool(lower >= upper)
    if direction == "lower":
        return bool(lower <= upper)
    if direction == "subset":
        return set(lower) <= set(upper)
    return False


def merge_chain(chain: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    """Merge rules ordered root → leaf. Returns (parameters, conflicts, expression)."""
    params: dict[str, Any] = {}
    floors: dict[str, tuple[Any, str]] = {}
    conflicts: list[dict[str, Any]] = []
    expression = ""
    expression_locked = False
    for r in chain:
        p = dict(r.get("parameters") or {})
        tighten = p.pop("_tighten", {}) or {}
        for k, val in p.items():
            if k in floors:
                upper, direction = floors[k]
                if not tighter(direction, upper, val):
                    conflicts.append({"rule_id": r.get("id"), "parameter": k, "attempted": val, "floor": upper})
                    continue
            params[k] = val
        if not expression_locked:
            expression = r["expression"]
        if r.get("is_mandatory_below"):
            expression_locked = True
            for k, val in params.items():
                floors[k] = (val, tighten.get(k, floors.get(k, (None, "none"))[1]))
    return params, conflicts, expression


def effective_rule(
    rule_key: str, scope_node_id: uuid.UUID, *, on: dt.date | None = None, subject: tuple[str, uuid.UUID] | None = None
) -> EffectiveRule | None:
    from syntegra.core import authz, context
    from syntegra.core.zones import current_alias
    from syntegra.governance.models import PolicyException, PolicyRule

    ctx = context.require()
    on = on or dt.date.today()
    alias = current_alias("registry")
    path = authz.ancestors(ctx.state_tenant_id, scope_node_id)  # type: ignore[arg-type]
    rules = list(
        PolicyRule.unscoped.using(alias)
        .filter(
            tenant_id=ctx.state_tenant_id,
            rule_key=rule_key,
            status="published",
            scope_node_id__in=path,
            effective_from__lte=on,
        )
        .exclude(effective_to__lt=on)
        .order_by("-version")
    )
    if not rules:
        return None
    by_node: dict[uuid.UUID, Any] = {}
    for r in rules:
        by_node.setdefault(r.scope_node_id, r)  # latest version per node
    chain = [by_node[n] for n in reversed(path) if n in by_node]  # root → leaf
    params, conflicts, expression = merge_chain(
        [
            {
                "id": r.id,
                "expression": r.expression,
                "parameters": r.parameters,
                "is_mandatory_below": r.is_mandatory_below,
            }
            for r in chain
        ]
    )
    eff = EffectiveRule(rule_key, expression, params, [r.id for r in chain], conflicts)
    if subject is not None:
        exc = (
            PolicyException.unscoped.using(alias)
            .filter(
                tenant_id=ctx.state_tenant_id,
                rule_id__in=eff.source_rule_ids,
                subject_kind=subject[0],
                subject_id=subject[1],
                status__in=("approved", "active"),
                start_on__lte=on,
                end_on__gte=on,
            )
            .first()
        )
        eff.exception_id = exc.id if exc else None
    return eff
