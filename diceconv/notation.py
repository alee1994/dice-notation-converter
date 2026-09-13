"""Parsing and formatting for algebraic dice notation, e.g. '2d6+1d4-3'.

The JSON side of the conversion is a plain dict so it round-trips through
json.dumps/json.loads without needing a custom encoder.
"""

import re
from dataclasses import dataclass
from typing import List, Union

# A dice term looks like '2d6' or 'd20' (count defaults to 1 when omitted).
_DICE_RE = re.compile(r"(?P<count>\d*)d(?P<sides>\d+)", re.IGNORECASE)
# Split 'a+b-c' into ['+a', '+b', '-c'] by looking ahead for a sign, after a
# leading sign has been forced onto the first term in parse_notation().
_SPLIT_RE = re.compile(r"(?=[+-])")


@dataclass
class DiceTerm:
    count: int
    sides: int
    sign: int = 1


@dataclass
class ModifierTerm:
    value: int
    sign: int = 1


Term = Union[DiceTerm, ModifierTerm]


class NotationError(ValueError):
    """Raised when input text or JSON can't be read as dice notation."""


def parse_notation(text: str) -> List[Term]:
    text = text.replace(" ", "")
    if not text:
        raise NotationError("empty dice notation")
    if text[0] not in "+-":
        text = "+" + text
    chunks = [chunk for chunk in _SPLIT_RE.split(text) if chunk]

    terms: List[Term] = []
    for chunk in chunks:
        sign = -1 if chunk[0] == "-" else 1
        body = chunk[1:]
        if not body:
            raise NotationError(f"dangling sign in notation: {chunk!r}")

        dice_match = _DICE_RE.fullmatch(body)
        if dice_match:
            count = int(dice_match.group("count") or "1")
            sides = int(dice_match.group("sides"))
            if count < 1 or sides < 1:
                raise NotationError(f"dice term must use positive numbers: {chunk!r}")
            terms.append(DiceTerm(count=count, sides=sides, sign=sign))
        elif body.isdigit():
            terms.append(ModifierTerm(value=int(body), sign=sign))
        else:
            raise NotationError(f"unrecognised term: {chunk!r}")
    return terms


def format_notation(terms: List[Term]) -> str:
    if not terms:
        raise NotationError("no terms to format")
    pieces = []
    for index, term in enumerate(terms):
        # No leading '+' on the very first positive term, so '2d6+3' round-trips
        # instead of coming back as '+2d6+3'.
        sign = "-" if term.sign < 0 else ("+" if index else "")
        if isinstance(term, DiceTerm):
            count = "" if term.count == 1 else str(term.count)
            pieces.append(f"{sign}{count}d{term.sides}")
        else:
            pieces.append(f"{sign}{term.value}")
    return "".join(pieces)


def spec_to_dict(terms: List[Term]) -> dict:
    out_terms = []
    for term in terms:
        if isinstance(term, DiceTerm):
            out_terms.append(
                {"type": "dice", "count": term.count, "sides": term.sides, "sign": term.sign}
            )
        else:
            out_terms.append({"type": "modifier", "value": term.value, "sign": term.sign})
    return {"terms": out_terms}


def spec_from_dict(data: dict) -> List[Term]:
    try:
        raw_terms = data["terms"]
    except (KeyError, TypeError) as exc:
        raise NotationError("json input must have a top-level 'terms' list") from exc

    terms: List[Term] = []
    for raw in raw_terms:
        sign = raw.get("sign", 1)
        term_type = raw.get("type")
        if term_type == "dice":
            terms.append(DiceTerm(count=raw["count"], sides=raw["sides"], sign=sign))
        elif term_type == "modifier":
            terms.append(ModifierTerm(value=raw["value"], sign=sign))
        else:
            raise NotationError(f"unknown term type: {term_type!r}")
    return terms
