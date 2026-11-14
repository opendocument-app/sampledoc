"""The PDF sample: an invoice, written out by hand rather than through a library."""

from __future__ import annotations

import unicodedata

from ._language import FALLBACK, load
from ._table import table

# Helvetica's own character widths, in thousandths of the point size, so the pdf
# can be set the way a real one is: each word placed where it belongs rather
# than a whole line handed over as one run.
HELVETICA = {
    "regular": (
        "278 278 355 556 556 889 667 191 333 333 389 584 278 333 278 278 "
        "556 556 556 556 556 556 556 556 556 556 278 278 584 584 584 556 "
        "1015 667 667 722 722 667 611 778 722 278 500 667 556 833 722 778 "
        "667 778 722 667 611 722 667 944 667 667 611 278 278 278 469 556 "
        "333 556 556 500 556 556 278 556 556 222 222 500 222 833 556 556 "
        "556 556 333 500 278 556 500 722 500 500 500 334 260 334 584"
    ),
    "bold": (
        "278 333 474 556 556 889 722 238 333 333 389 584 278 333 278 278 "
        "556 556 556 556 556 556 556 556 556 556 333 333 584 584 584 611 "
        "975 722 722 722 722 667 611 778 722 278 556 722 611 833 722 778 "
        "667 778 722 667 611 722 667 944 667 667 611 333 278 333 584 556 "
        "333 556 611 556 611 556 333 611 611 278 278 556 278 889 611 611 "
        "611 611 389 556 333 611 556 778 556 556 500 389 280 389 584"
    ),
}

WIDTHS = {
    weight: {chr(32 + index): int(value) for index, value in enumerate(widths.split())}
    for weight, widths in HELVETICA.items()
}

WINANSI = set(bytes(range(32, 256)).decode("cp1252", errors="ignore"))

# A4 upright in points, with the same margin the ODF pages take.
PAGE = (595.0, 842.0)
MARGIN = 57.0

# How many lines the invoice bills for. Enough to run onto a second page: a page
# is two thirds of a phone's height, and what fills the rest is the top of the
# page after it.
INVOICE_ROWS = 40

# Who the invoice is addressed to. A made-up company, the same in every language.
ADDRESS = ("Muster GmbH", "Praterstrasse 12", "1020 Wien")

INVOICE_KEYS = (
    "number",
    "issued",
    "due",
    "billed_to",
    "subtotal",
    "vat",
    "amount_due",
    "thanks",
    "quantity",
    "unit_price",
)


def advance(text: str, weight: str, size: float) -> float:
    """How wide that text is set in Helvetica at that size.

    An accented letter is as wide as the letter it is built on - true across
    Helvetica's Latin range - so the table only has to hold the plain ones.
    """
    widths = WIDTHS[weight]
    total = 0
    for character in text:
        width = widths.get(character)
        if width is None:
            plain = unicodedata.normalize("NFD", character)[0]
            width = widths.get(plain, 556)
        total += width

    return total * size / 1000


def spellable(language: dict) -> bool:
    """Whether Helvetica's encoding can write everything the invoice puts on the page.

    Several languages fail this and take the English invoice: cs, pl and tr for a
    handful of letters, and hi, ja, ru and zh for their whole script. Fixing that
    means embedding a subset of a real font and writing the text as CIDs.
    """
    words = language["report"]
    spoken = [words["item"], words["total"], words["title"], words["closing"]]
    spoken += words["periods"] + words["rows"] + [language["invoice"][key] for key in INVOICE_KEYS]

    return all(character in WINANSI for line in spoken for character in line)


def pdf(language: dict) -> bytes:
    """A PDF invoice of one or two pages.

    An invoice, which is a page of placed labels and figures rather than of
    running prose: every cell is set where it belongs, so nothing has to be
    wrapped and `advance` is only asked how wide a number is.

    Helvetica and WinAnsi, so what it says is Latin text only - the languages
    this cannot spell get the English wording.
    """
    if not spellable(language):
        language = load(FALLBACK)
    words = language["report"]

    def literal(text: str) -> str:
        return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")

    number, issued, due, billed, subtotal, vat, due_label, thanks, quantity, unit = (
        language["invoice"][key] for key in INVOICE_KEYS
    )
    head, body, foot = table(words, columns=1, rows=INVOICE_ROWS)

    money = foot[-1]
    tax = round(money * 0.2)
    right = PAGE[0] - MARGIN

    pages: list[list[str]] = [[]]

    def put(text, x, y, weight="regular", size=10, align="left"):
        """One line, placed on whichever page is open. Numbers are hung off the
        right, which is what makes a column of figures a column rather than a
        ragged list."""
        name = "F2" if weight == "bold" else "F1"
        at = x - advance(text, weight, size) if align == "right" else x
        pages[-1].append(f"BT /{name} {size:g} Tf {at:.1f} {y:.1f} Td ({literal(text)}) Tj ET")

    # the head: who it is from and when, against who it is to
    y = PAGE[1] - MARGIN - 26
    put(number, MARGIN, y, "bold", 20)
    put(issued, right, y, "regular", 10, "right")
    put(due, right, y - 14, "regular", 10, "right")

    y -= 46
    put(billed, MARGIN, y, "bold", 11)
    for line in ADDRESS:
        y -= 14
        put(line, MARGIN, y)

    # the table, in four columns across the width
    columns = (MARGIN, MARGIN + 300, MARGIN + 390, right)

    def heads(y):
        put(head[0], columns[0], y, "bold", 10)
        put(quantity, columns[1], y, "bold", 10, "right")
        put(unit, columns[2], y, "bold", 10, "right")
        put(head[-1], columns[3], y, "bold", 10, "right")

    y -= 34
    heads(y)

    for index, line in enumerate(body):
        count = index % 4 + 1
        amount = line[-1]
        y -= 15

        # A line that would be set in the bottom margin opens the next page
        # instead, with the column heads written again above it - which is what a
        # producer does, and what makes the last page short rather than the first
        # page overfull.
        if y < MARGIN + 80:
            pages.append([])
            y = PAGE[1] - MARGIN - 26
            heads(y)
            y -= 15

        put(str(line[0]), columns[0], y)
        put(str(count), columns[1], y, align="right")
        put(f"{amount / count:.2f}", columns[2], y, align="right")
        put(str(amount), columns[3], y, align="right")

    y -= 24
    for label, value, weight in (
        (subtotal, money, "regular"),
        (vat, tax, "regular"),
        (due_label, money + tax, "bold"),
    ):
        put(label, columns[2], y, weight, 10 if weight == "regular" else 12, "right")
        put(str(value), columns[3], y, weight, 10 if weight == "regular" else 12, "right")
        y -= 17

    y -= 12
    put(thanks, MARGIN, y)

    # 1 catalog, 2 the page tree, 3 and 4 the two fonts, then a page each and a
    # content stream each - so a page is 4+n and the stream it points at 4+len+n.
    first_page = 5
    first_stream = first_page + len(pages)
    kids = " ".join(f"{first_page + n} 0 R" for n in range(len(pages)))

    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        f"<</Type/Pages/Kids[{kids}]/Count {len(pages)}>>".encode(),
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica/Encoding/WinAnsiEncoding>>",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica-Bold/Encoding/WinAnsiEncoding>>",
    ]
    objects += [
        f"<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]"
        f"/Resources<</Font<</F1 3 0 R/F2 4 0 R>>>>/Contents {first_stream + n} 0 R>>".encode()
        for n in range(len(pages))
    ]
    for drawn in pages:
        stream = ("\n".join(drawn) + "\n").encode("cp1252")
        objects.append(b"<</Length " + str(len(stream)).encode() + b">>\nstream\n" + stream + b"endstream")

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + obj + b"\nendobj\n"

    table_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += f"trailer\n<</Size {len(objects) + 1}/Root 1 0 R>>\nstartxref\n{table_at}\n%%EOF\n".encode()

    return bytes(out)
