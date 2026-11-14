"""The wording of the samples, one JSON file per language under `languages/`.

Adding a language is adding a file: copy `en.json`, translate the strings, keep
the keys. Nothing else in the package lists the languages.
"""

from __future__ import annotations

import json
from functools import cache
from importlib import resources

FALLBACK = "en"


@cache
def languages() -> tuple[str, ...]:
    """Every language there is a file for, English first and the rest by code."""
    found = sorted(
        entry.name.removesuffix(".json")
        for entry in resources.files(__package__).joinpath("languages").iterdir()
        if entry.name.endswith(".json")
    )
    found.remove(FALLBACK)

    return (FALLBACK, *found)


@cache
def load(language: str) -> dict:
    """The wording for one language, as written in its file."""
    if language not in languages():
        raise KeyError(f"no samples written in {language!r}; there are {', '.join(languages())}")

    text = resources.files(__package__).joinpath("languages", f"{language}.json").read_text("utf-8")

    return json.loads(text)
