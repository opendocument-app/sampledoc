"""Small, localized, reproducible sample office documents.

>>> import sampledoc
>>> sampledoc.languages()
('en', 'cs', 'de', ...)
>>> data = sampledoc.document("text", "de")      # the German report, as .odt bytes
>>> sampledoc.generate("out/", languages=["en"])  # every sample, written to disk
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from os import PathLike
from pathlib import Path
from typing import NamedTuple

from . import _language, odf, ooxml, pdf, plain
from ._language import languages, load
from .names import file_names, manifest, query

__all__ = [
    "SAMPLES",
    "Sample",
    "document",
    "file_name",
    "file_names",
    "generate",
    "languages",
    "manifest",
    "query",
]

__version__ = "0.1.0"


class Sample(NamedTuple):
    extension: str
    build: Callable[[dict], bytes]
    description: str


# Every kind of sample, by the name it is written under. The first three are the
# documents the screenshots open; the rest fill the folder around them.
SAMPLES: dict[str, Sample] = {
    "text": Sample("odt", odf.odt, "a quarterly report with a table of costs"),
    "sheet": Sample("ods", odf.ods, "a budget over two sheets"),
    "slides": Sample("odp", odf.odp, "a three slide project plan"),
    "word": Sample("docx", ooxml.docx, "a service agreement with an appendix"),
    "cells": Sample("xlsx", ooxml.xlsx, "a small table of sales figures"),
    "deck": Sample("pptx", ooxml.pptx, "a single titled, bulleted slide"),
    "paper": Sample("pdf", pdf.pdf, "an invoice over two pages"),
    "rows": Sample("csv", plain.csv, "a contact list"),
    "notes": Sample("txt", plain.txt, "the report as plain text notes"),
}


def file_name(sample: str, language: str) -> str:
    """The name a sample is written under, e.g. ``sample-text-de.odt``."""
    return f"sample-{sample}-{language}.{SAMPLES[sample].extension}"


def document(sample: str, language: str = "en") -> bytes:
    """One sample, as the bytes of its file. The same arguments give the same bytes."""
    if sample not in SAMPLES:
        raise KeyError(f"no sample called {sample!r}; there are {', '.join(SAMPLES)}")

    return SAMPLES[sample].build(load(language))


def generate(
    directory: str | PathLike,
    languages: Iterable[str] | None = None,
    samples: Iterable[str] | None = None,
) -> list[Path]:
    """Write samples into `directory`, creating it if need be.

    Every sample in every language unless narrowed down. Returns the paths written.
    """
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)

    written = []
    for language in languages or _language.languages():
        for sample in samples or SAMPLES:
            path = target / file_name(sample, language)
            path.write_bytes(document(sample, language))
            written.append(path)

    return written
