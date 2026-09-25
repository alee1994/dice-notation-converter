# diceconv

Tabletop tools disagree on how to write dice rolls. A character sheet app
wants `2d6+3`. A VTT's API wants a structured object it can validate and
store. Hand-translating between the two whenever you're wiring one tool up
to another gets old, so this converts a roll in either direction.

Standard notation:

```
2d6+1d4-3
```

Structured JSON:

```json
{
  "terms": [
    {"type": "dice", "count": 2, "sides": 6, "sign": 1},
    {"type": "dice", "count": 1, "sides": 4, "sign": 1},
    {"type": "modifier", "value": 3, "sign": -1}
  ]
}
```

## Usage

From a file, format auto-detected from content:

```
$ python -m diceconv.cli roll.txt
```

From stdin, explicit direction:

```
$ echo "2d6+3" | python -m diceconv.cli --to json
{
  "terms": [
    {"type": "dice", "count": 2, "sides": 6, "sign": 1},
    {"type": "modifier", "value": 3, "sign": 1}
  ]
}
```

Round-tripping JSON back to notation:

```
$ cat roll.json | python -m diceconv.cli --from json --to notation
2d6+3
```

With no `--from`/`--to`, the tool guesses the input format (JSON if it
starts with `{`, notation otherwise) and converts to the other one.

## Notation supported so far

- Any number of dice groups and flat modifiers joined with `+` or `-`,
  e.g. `4d8-1d4+2`.
- Omitted dice count means one die: `d20` is the same as `1d20`.
- Keep-highest/lowest selectors: `4d6kh3` keeps the highest 3 of 4 dice,
  `4d6kl1` keeps the lowest 1. The dice term carries `keep_mode`
  (`"highest"`/`"lowest"`) and `keep_count` in JSON.
- Advantage and disadvantage as shorthand for a two-die keep-one roll:
  `d20adv` and `d20dis` are equivalent to `2d20kh1` and `2d20kl1`. Converting
  back to notation always produces the `kh`/`kl` form, since that's what the
  JSON actually stores.
- Exploding dice: `2d6!` marks a dice term so that each die rolling its
  maximum value adds another roll. The `!` goes right after the sides and
  before any keep selector, e.g. `4d6!kh3`. The dice term carries
  `"explode": true` in JSON; it's omitted when false.

## Install

No dependencies beyond the standard library. Run it straight from a
checkout with `python -m diceconv.cli`, or install locally:

```
$ pip install -e .
$ diceconv roll.txt
```

## License

MIT, see LICENSE.
