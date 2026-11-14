"""Plain text samples: a contact list (.csv) and notes (.txt)."""

from __future__ import annotations

# Names are names in every language, so these are not translated.
PEOPLE = ["A. Bauer", "M. Rossi", "J. Novak", "L. Dubois", "S. Meyer", "K. Larsen"]


def csv(language: dict) -> bytes:
    """The contact list its name promises."""
    headers = language["contacts"]["headers"]
    roles = language["contacts"]["roles"]
    lines = [",".join(headers)]
    for index, person in enumerate(PEOPLE):
        handle = person.split(". ")[-1].lower()
        lines.append(
            ",".join([person, roles[index % len(roles)], f"{handle}@example.org", f"+43 1 234 56{index}0"])
        )

    return ("\n".join(lines) + "\n").encode("utf-8")


def txt(language: dict) -> bytes:
    """The notes: the report in plain text, with the deck's points under it."""
    words = language["report"]
    lines = [words["title"], "=" * len(words["title"]), "", words["lead"], ""]
    for heading, paragraphs in words["sections"]:
        lines += [heading, "-" * len(heading), ""]
        for text in paragraphs:
            lines += [text, ""]
    for title, bullets in words["slides"]:
        lines += [title, "-" * len(title), ""]
        lines += [f"* {point}" for point in bullets]
        lines.append("")
    lines.append(words["closing"])

    return ("\n".join(lines) + "\n").encode("utf-8")
