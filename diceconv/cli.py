"""Command-line entry point: reads from a file or stdin, writes to stdout."""

import argparse
import json
import sys

from . import notation


def read_input(path):
    if path is None or path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def detect_format(text):
    stripped = text.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        return "json"
    return "notation"


def build_parser():
    parser = argparse.ArgumentParser(
        prog="diceconv",
        description="Convert dice notation between compact text and structured JSON.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="input file, or omit / pass '-' to read from stdin",
    )
    parser.add_argument(
        "--from",
        dest="from_format",
        choices=["notation", "json"],
        default=None,
        help="input format (default: auto-detect from content)",
    )
    parser.add_argument(
        "--to",
        dest="to_format",
        choices=["notation", "json"],
        default=None,
        help="output format (default: the format --from isn't)",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    text = read_input(args.file)

    from_format = args.from_format or detect_format(text)
    to_format = args.to_format or ("json" if from_format == "notation" else "notation")
    if to_format == from_format:
        raise SystemExit("input and output format are the same, nothing to convert")

    try:
        if from_format == "notation":
            terms = notation.parse_notation(text.strip())
        else:
            terms = notation.spec_from_dict(json.loads(text))
    except (notation.NotationError, json.JSONDecodeError) as exc:
        raise SystemExit(f"diceconv: {exc}")

    if to_format == "notation":
        print(notation.format_notation(terms))
    else:
        print(json.dumps(notation.spec_to_dict(terms), indent=2))


if __name__ == "__main__":
    main()
