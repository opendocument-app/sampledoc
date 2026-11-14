"""What the samples are called in a file browser, and the word to search them for.

The screenshot tests that use these samples show a folder full of them, then
open one and search it. Both need words in the device's language, so they come
from here rather than being written a second time in the app.
"""

from __future__ import annotations

import re

from ._language import FALLBACK, languages, load

# The rest of the folder, so it does not read as a set of nine samples. Each is
# a copy of the sample named beside it, which only decides its icon: the browser
# shows a name and an icon, and none of them is ever opened.
FILLERS = {
    "meeting": "text",
    "letter": "text",
    "travel": "text",
    "reading": "text",
    "household": "sheet",
    "hours": "sheet",
    "stocktake": "sheet",
    "kickoff": "slides",
    "course": "slides",
    "lease": "word",
    "resume": "word",
    "application": "word",
    "expenses": "cells",
    "inventory": "cells",
    "review": "deck",
    "ticket": "paper",
    "warranty": "paper",
    "manual": "paper",
}

# What separates one word from the next - written as what breaks a word rather
# than as what a word is made of. `\w` is the other way round and is wrong for
# some scripts: a Devanagari vowel sign is not a letter, a digit or an
# underscore, so a Hindi word comes apart at every matra.
BREAK = re.compile(r"[\s.,;:!?()\[\]{}<>\"'«»„“”‘’—–\-/\\|…।]+")


def file_names(language: str) -> dict[str, str]:
    """The display name of every sample and filler; a filler a language has no
    name for takes the English one."""
    data = load(language)
    fallback = load(FALLBACK)["fillers"]

    return data["files"] | {key: data["fillers"].get(key, fallback[key]) for key in FILLERS}


def query(language: str) -> str:
    """The word a search of the report should look for.

    Counted out of the document rather than written down, so it is always a word
    that is really in there, and always one that is in there several times - a
    search that highlights a single hit does not look like a search. Short words
    are skipped because "the" and "and" say nothing about the document.

    Languages that do not put spaces between words (ja, zh) name their word in
    the `search` key of their file instead, and it is checked against the text.
    """
    data = load(language)
    words = data["report"]
    text = " ".join(
        [words["title"], words["lead"], words["closing"]]
        + [heading for heading, _ in words["sections"]]
        + [line for _, paragraphs in words["sections"] for line in paragraphs]
    )

    written = data.get("search")
    if written:
        if text.count(written) < 2:
            raise ValueError(
                f"{language}: the report says {written!r} {text.count(written)} times, so a "
                "search for it would find too little. Pick another `search` word."
            )
        return written

    counted: dict[str, int] = {}
    for word in BREAK.split(text.lower()):
        if len(word) >= 5 and not word.isdigit():
            counted[word] = counted.get(word, 0) + 1

    if not counted:
        raise ValueError(f"{language}: nothing in the report to search for")

    # the most repeated, and the longest of those, so the choice is not a coin toss
    return max(counted, key=lambda word: (counted[word], len(word)))


def manifest(locales: dict[str, str] | None = None) -> dict:
    """The contents of `screenshot-names.json`: per language, what each sample is
    called and what to search for; and, if given, which device locale reads
    which language's samples.
    """
    if locales is not None:
        unknown = sorted({language for language in locales.values() if language} - set(languages()))
        if unknown:
            raise ValueError(f"locales map to languages there are no samples in: {unknown}")

    details: dict = {
        "languages": {
            language: {"files": file_names(language), "search": query(language)} for language in languages()
        }
    }
    if locales is not None:
        details["locales"] = locales

    return details
