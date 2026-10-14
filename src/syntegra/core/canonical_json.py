"""RFC 8785 JSON Canonicalization Scheme (JCS) for signed payloads (certificates, audit chain, statements).

Supported values: dict (string keys), list/tuple, str, int, bool, None, and finite floats that are whole
numbers or have an exact short representation. Payload designers use integers (minor units) and strings
for decimals, so floats are rare.
"""

from __future__ import annotations

import datetime as dt
import decimal
import json
import math
import uuid
from typing import Any


def _number(n: float | int) -> str:
    if isinstance(n, bool):
        raise TypeError("bool is not a number")
    if isinstance(n, int):
        if abs(n) > 2**53:
            raise ValueError("integer exceeds IEEE-754 safe range; encode as string")
        return str(n)
    if not math.isfinite(n):
        raise ValueError("non-finite number")
    if n == 0:
        return "0"
    if n.is_integer() and abs(n) < 1e21:
        return str(int(n))
    r = repr(n)
    if "e" in r:  # ECMAScript: exponent without '+' padding, e.g. 1e-7
        mant, exp = r.split("e")
        r = f"{mant}e{int(exp):+d}"
    return r


def _ser(v: Any, out: list[str]) -> None:
    if v is None:
        out.append("null")
    elif v is True:
        out.append("true")
    elif v is False:
        out.append("false")
    elif isinstance(v, (int, float)):
        out.append(_number(v))
    elif isinstance(v, str):
        out.append(json.dumps(v, ensure_ascii=False))
    elif isinstance(v, (uuid.UUID, decimal.Decimal)):
        out.append(json.dumps(str(v), ensure_ascii=False))
    elif isinstance(v, (dt.datetime, dt.date)):
        out.append(json.dumps(v.isoformat(), ensure_ascii=False))
    elif isinstance(v, dict):
        out.append("{")
        first = True
        for k in sorted(v, key=lambda s: str(s).encode("utf-16-be")):
            if not first:
                out.append(",")
            first = False
            out.append(json.dumps(str(k), ensure_ascii=False))
            out.append(":")
            _ser(v[k], out)
        out.append("}")
    elif isinstance(v, (list, tuple)):
        out.append("[")
        for i, item in enumerate(v):
            if i:
                out.append(",")
            _ser(item, out)
        out.append("]")
    else:
        raise TypeError(f"cannot canonicalise {type(v).__name__}")


def canonicalize(value: Any) -> bytes:
    out: list[str] = []
    _ser(value, out)
    return "".join(out).encode("utf-8")
