"""OpenDocument samples: the report (.odt), the budget (.ods) and the deck (.odp)."""

from __future__ import annotations

from xml.sax.saxutils import escape

from ._table import ACCENT, RULE, table, zipped

NAMESPACES = " ".join(
    [
        'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"',
        'xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"',
        'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"',
        'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"',
        'xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"',
        'xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"',
        'xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"',
    ]
)

MANIFEST = """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">
 <manifest:file-entry manifest:full-path="/" manifest:media-type="{mimetype}"/>
 <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
</manifest:manifest>
"""

TEXT = "application/vnd.oasis.opendocument.text"
SPREADSHEET = "application/vnd.oasis.opendocument.spreadsheet"
PRESENTATION = "application/vnd.oasis.opendocument.presentation"

# A4 upright for the report and the sheet, 16:9 for the deck.
#
# A page is fitted to the width of the screen, so a page with little on it reads
# as a smudge in the top third of an empty sheet. The answer is words rather
# than smaller paper: these documents are written long enough to fill A4.
PAGE_LAYOUTS = {
    "document": '<style:page-layout-properties fo:page-width="21cm" fo:page-height="29.7cm"'
    ' fo:margin-top="2cm" fo:margin-bottom="2cm" fo:margin-left="2cm" fo:margin-right="2cm"/>',
    "slide": '<style:page-layout-properties fo:page-width="28cm" fo:page-height="15.75cm"/>',
}

# Which section of the report the figures sit under - the costs one, second of the
# five - and how many rows of them there are. The rows are what carry the report
# past the foot of a phone screen, so this is the number to turn if it stops.
COSTS_SECTION = 1
REPORT_ROWS = 26


def styles(kind: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles {NAMESPACES} office:version="1.2">
 <office:styles/>
 <office:automatic-styles>
  <style:page-layout style:name="PM1">
   {PAGE_LAYOUTS[kind]}
  </style:page-layout>
 </office:automatic-styles>
 <office:master-styles>
  <style:master-page style:name="Default" style:page-layout-name="PM1"/>
 </office:master-styles>
</office:document-styles>
"""


def content(body: str, automatic: str = "") -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content {NAMESPACES} office:version="1.2">
 <office:automatic-styles>
{automatic}
 </office:automatic-styles>
 <office:body>
{body}
 </office:body>
</office:document-content>
"""


def paragraph_style(
    name: str, *, size: str, weight: str = "normal", colour: str = "#1a1a1a", space: str = "0.4cm"
) -> str:
    return f"""  <style:style style:name="{name}" style:family="paragraph">
   <style:paragraph-properties fo:margin-bottom="{space}"/>
   <style:text-properties fo:font-size="{size}" fo:font-weight="{weight}" fo:color="{colour}"/>
  </style:style>"""


def odf_row(cells: list, style: str | None = None) -> str:
    """One row of an ODF table, as the report and the sheet both write it.

    A figure carries its value in the attribute as well as in the text, or the
    spreadsheet holds a column of text that happens to look like numbers.
    """
    marked = f' table:style-name="{style}"' if style else ""
    out = ["    <table:table-row>"]
    for cell in cells:
        if isinstance(cell, int):
            out.append(
                f'     <table:table-cell{marked} office:value-type="float" office:value="{cell}">'
                f"<text:p>{cell}</text:p></table:table-cell>"
            )
        else:
            out.append(
                f'     <table:table-cell{marked} office:value-type="string">'
                f"<text:p>{escape(cell)}</text:p></table:table-cell>"
            )
    out.append("    </table:table-row>")

    return "\n".join(out)


# The head and the totals row, which the report and the sheet mark the same way.
CELL_STYLES = f"""  <style:style style:name="ceHead" style:family="table-cell">
   <style:table-cell-properties fo:background-color="#eef3fa" fo:border-bottom="0.06pt solid {RULE}"/>
   <style:text-properties fo:font-weight="bold" fo:color="{ACCENT}"/>
  </style:style>
  <style:style style:name="ceTotal" style:family="table-cell">
   <style:table-cell-properties fo:border-top="0.06pt solid {RULE}"/>
   <style:text-properties fo:font-weight="bold"/>
  </style:style>"""


def report(words: dict) -> str:
    """content.xml of the report: a title, a lead, headed sections with the costs
    figures under theirs, and a closing line.

    Long on purpose. A page fitted to the width of a phone is about two thirds of
    its height, so a document that ends after one is photographed with a third of
    the screen showing the backdrop behind it. Which is why there is a table in
    here at all: the figures are the only length the report can be given that is
    already written in every language.
    """
    automatic = "\n".join(
        [
            paragraph_style("Title", size="26pt", weight="bold", space="0.8cm"),
            paragraph_style("Heading", size="16pt", weight="bold", colour=ACCENT, space="0.3cm"),
            paragraph_style("Body", size="12pt", space="0.5cm"),
            CELL_STYLES,
            """  <style:style style:name="coReportLabel" style:family="table-column">
   <style:table-column-properties style:column-width="5.4cm"/>
  </style:style>""",
            """  <style:style style:name="coReportFigure" style:family="table-column">
   <style:table-column-properties style:column-width="2.9cm"/>
  </style:style>""",
        ]
    )

    head, body, foot = table(words, columns=3, rows=REPORT_ROWS)
    marks = "\n".join(
        ['    <table:table-column table:style-name="coReportLabel"/>']
        + ['    <table:table-column table:style-name="coReportFigure"/>'] * (len(head) - 1)
    )
    figures = (
        f'   <table:table table:name="{escape(words["sheets"][0])}">\n{marks}\n'
        + "\n".join([odf_row(head, "ceHead")] + [odf_row(line) for line in body] + [odf_row(foot, "ceTotal")])
        + "\n   </table:table>"
    )

    lines = [
        f'   <text:p text:style-name="Title">{escape(words["title"])}</text:p>',
        f'   <text:p text:style-name="Body">{escape(words["lead"])}</text:p>',
    ]
    for index, (heading, paragraphs) in enumerate(words["sections"]):
        lines.append(
            f'   <text:h text:style-name="Heading" text:outline-level="1">{escape(heading)}</text:h>'
        )
        lines += [f'   <text:p text:style-name="Body">{escape(text)}</text:p>' for text in paragraphs]

        # under the costs section, which is the one it is the figures for. Its own
        # heading would be a word to translate in every language for nothing
        if index == COSTS_SECTION:
            lines.append(figures)
            lines.append('   <text:p text:style-name="Body"/>')

    lines.append(f'   <text:p text:style-name="Body">{escape(words["closing"])}</text:p>')

    return content("  <office:text>\n" + "\n".join(lines) + "\n  </office:text>", automatic)


def sheet(words: dict) -> str:
    """content.xml of the budget: two sheets, so a tab bar has something to show."""
    automatic = "\n".join(
        [
            # two widths: eight at the label's width put half the sheet off
            # the right edge, and a figure needs less room than its row's name
            """  <style:style style:name="coLabel" style:family="table-column">
   <style:table-column-properties style:column-width="3.2cm"/>
  </style:style>""",
            """  <style:style style:name="coFigure" style:family="table-column">
   <style:table-column-properties style:column-width="2.2cm"/>
  </style:style>""",
            CELL_STYLES,
        ]
    )

    head, body, foot = table(words, columns=6)

    overview = [odf_row(head, "ceHead")] + [odf_row(line) for line in body] + [odf_row(foot, "ceTotal")]
    costs = [odf_row([words["item"], words["total"]], "ceHead")]
    costs += [odf_row([line[0], line[-1]]) for line in body]

    tables = []
    for name, rows, columns in (
        (words["sheets"][0], overview, len(head)),
        (words["sheets"][1], costs, 2),
    ):
        # the label column, then a figure column for each of the rest
        marks = "\n".join(
            ['    <table:table-column table:style-name="coLabel"/>']
            + ['    <table:table-column table:style-name="coFigure"/>'] * (columns - 1)
        )
        tables.append(
            f'   <table:table table:name="{escape(name)}">\n{marks}\n'
            + "\n".join(rows)
            + "\n   </table:table>"
        )

    return content("  <office:spreadsheet>\n" + "\n".join(tables) + "\n  </office:spreadsheet>", automatic)


def deck(words: dict) -> str:
    """content.xml of the deck: three slides, each with a title and its bullets."""
    automatic = "\n".join(
        [
            paragraph_style("SlideTitle", size="32pt", weight="bold", colour=ACCENT, space="0.6cm"),
            paragraph_style("Bullet", size="18pt", space="0.35cm"),
        ]
    )

    pages = []
    for title, bullets in words["slides"]:
        lines = [f'     <text:p text:style-name="SlideTitle">{escape(title)}</text:p>']
        lines += [f'     <text:p text:style-name="Bullet">• {escape(point)}</text:p>' for point in bullets]
        pages.append(
            f'   <draw:page draw:name="{escape(title)}" draw:master-page-name="Default">\n'
            '    <draw:frame svg:width="24cm" svg:height="12cm" svg:x="2cm" svg:y="2cm">\n'
            "     <draw:text-box>\n" + "\n".join(lines) + "\n     </draw:text-box>\n"
            "    </draw:frame>\n   </draw:page>"
        )

    return content("  <office:presentation>\n" + "\n".join(pages) + "\n  </office:presentation>", automatic)


def package(mimetype: str, kind: str, content_xml: str) -> bytes:
    """An ODF package around the given content.xml."""
    return zipped(
        [
            # first and uncompressed, or the package is only recognised by sniffing
            ("mimetype", mimetype, True),
            ("META-INF/manifest.xml", MANIFEST.format(mimetype=mimetype), False),
            ("styles.xml", styles(kind), False),
            ("content.xml", content_xml, False),
        ]
    )


def odt(language: dict) -> bytes:
    return package(TEXT, "document", report(language["report"]))


def ods(language: dict) -> bytes:
    return package(SPREADSHEET, "document", sheet(language["report"]))


def odp(language: dict) -> bytes:
    return package(PRESENTATION, "slide", deck(language["report"]))
