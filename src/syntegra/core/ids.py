"""Identifiers (CEDA §5.3): UUID v7 internal keys and check-digited human identifiers."""

from __future__ import annotations

import os
import re
import threading
import time
import uuid

_lock = threading.Lock()
_last_ms = 0
_counter = 0


def uuid7() -> uuid.UUID:
    """RFC 9562 UUID version 7 — 48-bit Unix milliseconds, then random bits.

    A 12-bit counter in ``rand_a`` keeps values monotonic within one millisecond in this process, so
    InnoDB clustered-index inserts stay sequential (MFS §16.2).
    """
    global _last_ms, _counter
    with _lock:
        ms = time.time_ns() // 1_000_000
        if ms <= _last_ms:
            _counter += 1
            if _counter > 0xFFF:
                _last_ms += 1
                _counter = 0
            ms = _last_ms
        else:
            _last_ms = ms
            _counter = int.from_bytes(os.urandom(2), "big") & 0x3FF
        rand_b = int.from_bytes(os.urandom(8), "big") & ((1 << 62) - 1)
        value = (ms & ((1 << 48) - 1)) << 80
        value |= 0x7 << 76
        value |= (_counter & 0xFFF) << 64
        value |= 0b10 << 62
        value |= rand_b
    return uuid.UUID(int=value)


def uuid7_time_ms(u: uuid.UUID) -> int:
    return u.int >> 80


# --------------------------------------------------------------------------- ISO 7064 MOD 97-10

def mod97_check_digits(digits: str) -> str:
    """Two check digits per ISO 7064 MOD 97-10 (as IBAN): CC = 98 − (N × 100 mod 97)."""
    if not digits.isdigit():
        raise ValueError("digits only")
    return f"{98 - (int(digits) * 100) % 97:02d}"


def mod97_valid(digits_with_check: str) -> bool:
    return digits_with_check.isdigit() and int(digits_with_check) % 97 == 1


# --------------------------------------------------------------------------- Global Learner ID (CD-07)

GLID_RE = re.compile(r"^LRN-(\d{4})-(\d{4})-(\d{2})$")


def format_glid(serial: int) -> str:
    """``LRN-NNNN-NNNN-CC`` from a serial leased from the national GLID block allocator."""
    if not 0 < serial < 100_000_000:
        raise ValueError("GLID serial out of range")
    body = f"{serial:08d}"
    return f"LRN-{body[:4]}-{body[4:]}-{mod97_check_digits(body)}"


def glid_valid(glid: str) -> bool:
    m = GLID_RE.match(glid)
    return bool(m) and mod97_valid(m.group(1) + m.group(2) + m.group(3))


# --------------------------------------------------------------------------- other human identifiers

def format_staff_number(serial: int) -> str:
    body = f"{serial:08d}"
    return f"STF-{body[:4]}-{body[4:]}{mod97_check_digits(body)}"


def format_institution_code(country: str, serial: int) -> str:
    return f"INS-{country.upper()}-{serial:06d}"


CERT_RE = re.compile(r"^([A-Z]{2})-([A-Z0-9]{2,6})-(\d{4})-(\d{6,})(\d{2})$")


def format_certificate_number(country: str, authority: str, year: int, seq: int) -> str:
    """``<country>-<authority>-<year>-<seq><CC>`` (CD-08); the sequence is authority-wide, never reused."""
    body = f"{seq:06d}"
    check = mod97_check_digits(f"{year}{body}")
    return f"{country.upper()}-{authority.upper()}-{year}-{body}{check}"


def certificate_number_valid(number: str) -> bool:
    m = CERT_RE.match(number)
    return bool(m) and mod97_valid(m.group(3) + m.group(4) + m.group(5))


def short_code(n: int = 8) -> str:
    """Human-friendly verification code (no 0/O/1/I), grouped as XXXX-XXXX."""
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    raw = "".join(alphabet[b % len(alphabet)] for b in os.urandom(n))
    return raw[:4] + "-" + raw[4:]
