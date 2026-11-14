"""sampledoc [-o DIR] [-l LANG]... [-s SAMPLE]... [--locales FILE] [--no-names]"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import SAMPLES, __version__, file_name, generate, languages, manifest

NAMES_FILE = "screenshot-names.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sampledoc",
        description="Write small, localized, reproducible sample office documents.",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("."),
        metavar="DIR",
        help="where to write the samples (default: the current directory)",
    )
    parser.add_argument(
        "-l",
        "--language",
        action="append",
        choices=languages(),
        metavar="LANG",
        help="only this language; repeatable (default: all of them)",
    )
    parser.add_argument(
        "-s",
        "--sample",
        action="append",
        choices=list(SAMPLES),
        metavar="SAMPLE",
        help="only this kind of sample; repeatable (default: all of them)",
    )
    parser.add_argument(
        "--locales",
        type=Path,
        metavar="FILE",
        help='a JSON object mapping device locales to languages, e.g. {"de-DE": "de"}, '
        f'copied into {NAMES_FILE} under "locales"',
    )
    parser.add_argument(
        "--no-names",
        action="store_true",
        help=f"do not write {NAMES_FILE}",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list the languages and samples there are, and exit",
    )
    args = parser.parse_args(argv)

    if args.list:
        print("languages:", " ".join(languages()))
        print("samples:")
        for name, sample in SAMPLES.items():
            print(f"  {name:<7} {file_name(name, 'LANG'):<22} {sample.description}")
        return 0

    locales = None
    if args.locales:
        locales = json.loads(args.locales.read_text(encoding="utf-8"))
        if not isinstance(locales, dict):
            parser.error(f"{args.locales} does not hold a JSON object")

    written = generate(args.output, languages=args.language, samples=args.sample)

    if not args.no_names:
        try:
            details = manifest(locales)
        except ValueError as error:
            parser.error(str(error))
        (args.output / NAMES_FILE).write_text(
            json.dumps(details, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )

    count = len(args.language or languages())
    print(f"wrote {len(written)} documents in {count} languages to {args.output}")

    return 0
