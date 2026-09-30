"""Rolling parsed dice terms with a random number generator."""

import random
from dataclasses import dataclass
from typing import List, Optional

from .notation import DiceTerm, ModifierTerm, NotationError, Term, format_notation


@dataclass
class TermResult:
    term: Term
    kept: List[int]
    dropped: List[int]
    # Signed contribution of this term to the total.
    subtotal: int


@dataclass
class RollResult:
    parts: List[TermResult]
    total: int


def _roll_dice(term: DiceTerm, rng: random.Random) -> List[int]:
    rolls = []
    pending = term.count
    while pending:
        pending -= 1
        value = rng.randint(1, term.sides)
        rolls.append(value)
        # Extra dice from explosions are separate dice, so they count toward a
        # keep selector the same way the originals do.
        if term.explode and value == term.sides:
            pending += 1
    return rolls


def _split_keep(term: DiceTerm, rolls: List[int]):
    if term.keep_mode is None:
        return rolls, []
    ranked = sorted(range(len(rolls)), key=lambda i: rolls[i], reverse=term.keep_mode == "h")
    keep_indexes = set(ranked[: term.keep_count])
    kept = [value for i, value in enumerate(rolls) if i in keep_indexes]
    dropped = [value for i, value in enumerate(rolls) if i not in keep_indexes]
    return kept, dropped


def roll_terms(terms: List[Term], rng: Optional[random.Random] = None) -> RollResult:
    rng = rng or random.Random()
    parts = []
    total = 0
    for term in terms:
        if isinstance(term, DiceTerm):
            # A die that always rolls its maximum would explode forever.
            if term.explode and term.sides < 2:
                raise NotationError("exploding dice need at least two sides")
            kept, dropped = _split_keep(term, _roll_dice(term, rng))
            subtotal = term.sign * sum(kept)
            parts.append(TermResult(term, kept, dropped, subtotal))
        elif isinstance(term, ModifierTerm):
            subtotal = term.sign * term.value
            parts.append(TermResult(term, [], [], subtotal))
        else:
            raise NotationError(f"cannot roll term: {term!r}")
        total += subtotal
    return RollResult(parts=parts, total=total)


def format_result(result: RollResult) -> str:
    # Labels come from the notation formatter, so advantage shows as 2d20kh1,
    # the same as when converting.
    lines = []
    for index, part in enumerate(result.parts):
        label = format_notation([part.term])
        if index and part.term.sign > 0:
            label = "+" + label
        if isinstance(part.term, DiceTerm):
            line = f"{label}  {part.kept}"
            if part.dropped:
                line += f" dropped {part.dropped}"
            line += f" = {part.subtotal}"
        else:
            line = label
        lines.append(line)
    lines.append(f"total: {result.total}")
    return "\n".join(lines)
