"""Name normalisation and similarity for identity matching (Book 3 §12.1, MFS §13.5)."""

from __future__ import annotations

import re
import unicodedata

TITLES = {"mr", "mrs", "ms", "miss", "dr", "prof", "chief", "alhaji", "alhaja", "hajia", "pastor", "rev", "engr", "barr", "hon", "sir", "lady", "mallam"}

# Nigerian given-name variants and short forms (seed table; extended from steward decisions)
VARIANTS: dict[str, str] = {
    "seun": "oluwaseun", "seyi": "oluwaseyi", "tunde": "babatunde", "tayo": "omotayo", "bayo": "adebayo",
    "funmi": "olufunmilayo", "funmilayo": "olufunmilayo", "dayo": "adedayo", "femi": "olufemi", "kemi": "oluwakemi",
    "tobi": "oluwatobi", "dami": "oluwadamilare", "segun": "olusegun", "yemi": "oluwayemisi", "gbenga": "oluwagbenga",
    "emeka": "chukwuemeka", "chidi": "chidiebere", "nkem": "nkemdirim", "ngozi": "ngozichukwu", "obi": "obinna",
    "ike": "ikechukwu", "uche": "uchechukwu", "chi": "chinyere", "ada": "adaeze", "nnamdi": "nnamdi",
    "musa": "musa", "mohammed": "muhammad", "mohammad": "muhammad", "muhammed": "muhammad", "ahmad": "ahmed",
    "abubakar": "abubakar", "aisha": "aishat", "aishatu": "aishat", "fatima": "fatimah", "fatimatu": "fatimah",
    "ibrahim": "ibrahim", "ibraheem": "ibrahim", "usman": "usman", "uthman": "usman", "yusuf": "yusuf", "yusuff": "yusuf",
}


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def normalise_name(name: str) -> str:
    """NFKC, case-fold, transliterate accents (Yorùbá/Igbo diacritics), strip titles and punctuation."""
    s = unicodedata.normalize("NFKC", name or "").casefold()
    s = strip_accents(s)
    s = re.sub(r"[^a-z\s'-]", " ", s)
    parts = [p.strip("'-") for p in s.split()]
    return " ".join(p for p in parts if p and p not in TITLES)


def canonical_given(name: str) -> str:
    first = normalise_name(name).split(" ")[0] if name else ""
    return VARIANTS.get(first, first)


def phonetic_key(name: str) -> str:
    """Compact phonetic key tuned for Nigerian names (consonant skeleton with common equivalences).

    Not Double Metaphone — a deterministic, explainable key used for blocking only; scoring uses
    Jaro–Winkler on normalised names.
    """
    s = normalise_name(name).replace(" ", "")
    if not s:
        return ""
    rules = [("ph", "f"), ("gh", "g"), ("kw", "k"), ("gb", "b"), ("kp", "p"), ("ch", "c"), ("sh", "s"),
             ("th", "t"), ("ck", "k"), ("q", "k"), ("x", "ks"), ("z", "s"), ("v", "f"), ("j", "g"), ("y", "i")]
    for a, b in rules:
        s = s.replace(a, b)
    head, rest = s[0], s[1:]
    rest = re.sub(r"[aeiouhw'-]", "", rest)
    rest = re.sub(r"(.)\1+", r"\1", rest)
    return (head + rest)[:8].upper()


def name_phonetic(given: str, family: str) -> str:
    return f"{phonetic_key(canonical_given(given))} {phonetic_key(family)}".strip()


def jaro_winkler(a: str, b: str, p: float = 0.1) -> float:
    if a == b:
        return 1.0 if a else 0.0
    la, lb = len(a), len(b)
    if not la or not lb:
        return 0.0
    window = max(la, lb) // 2 - 1
    ma, mb = [False] * la, [False] * lb
    matches = 0
    for i, ch in enumerate(a):
        lo, hi = max(0, i - window), min(lb, i + window + 1)
        for j in range(lo, hi):
            if not mb[j] and b[j] == ch:
                ma[i] = mb[j] = True
                matches += 1
                break
    if not matches:
        return 0.0
    t, k = 0, 0
    for i in range(la):
        if ma[i]:
            while not mb[k]:
                k += 1
            if a[i] != b[k]:
                t += 1
            k += 1
    jaro = (matches / la + matches / lb + (matches - t / 2) / matches) / 3
    prefix = 0
    for x, y in zip(a[:4], b[:4], strict=False):
        if x != y:
            break
        prefix += 1
    return jaro + prefix * p * (1 - jaro)


def name_similarity(a: str, b: str) -> float:
    na, nb = canonical_given(a), canonical_given(b)
    return max(jaro_winkler(na, nb), jaro_winkler(normalise_name(a), normalise_name(b)))
