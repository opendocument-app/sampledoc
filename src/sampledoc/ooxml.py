"""Office Open XML samples: the contract (.docx), sales figures (.xlsx) and a slide (.pptx).

Written to be read by odrcore rather than by Word, so they carry the least markup
that is still a valid package.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from ._table import ACCENT, table, zipped

OOXML_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="{type}" Target="{target}"/>
</Relationships>
"""

OFFICE_DOCUMENT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"


# How many lines the contract's appendix lists, and the half-points the whole of it
# is set in. Between them they are what carries it past the foot of a phone screen,
# the clauses above being fourteen short sentences - and they are the only length
# there is to give it, the renderer honouring neither `w:spacing` on a paragraph nor
# `w:trHeight` on a row.
ANNEX_ROWS = 40
CONTRACT_TEXT = 28


def _package(parts: dict) -> bytes:
    return zipped([(name, text, False) for name, text in parts.items()])


def cell_rows(lines: list) -> str:
    """A Word table of two columns, the first line of it the head."""
    out = [
        '<w:tbl><w:tblPr><w:tblW w:w="9070" w:type="dxa"/>'
        '<w:tblBorders><w:insideH w:val="single" w:sz="4" w:color="D4D9E0"/></w:tblBorders>'
        "</w:tblPr>"
        '<w:tblGrid><w:gridCol w:w="6350"/><w:gridCol w:w="2720"/></w:tblGrid>'
    ]
    for number, (name, value) in enumerate(lines):
        marks = "<w:b/>" if number == 0 else ""
        cells = "".join(
            f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>'
            f'<w:p><w:r><w:rPr>{marks}<w:sz w:val="{CONTRACT_TEXT}"/></w:rPr>'
            f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p></w:tc>'
            for text, width in ((name, 6350), (value, 2720))
        )
        out.append(f"<w:tr>{cells}</w:tr>")
    out.append("</w:tbl>")

    return "".join(out)


def docx_parts(language: dict) -> dict:
    """The Word file is the contract, not another copy of the report."""
    words = language["report"]
    contract = language["contract"]

    def run(text: str, *, size: int, bold: bool = False, colour: str = "") -> str:
        marks = ("<w:b/>" if bold else "") + (f'<w:color w:val="{colour}"/>' if colour else "")

        return (
            f'<w:r><w:rPr>{marks}<w:sz w:val="{size}"/></w:rPr>'
            f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'
        )

    def para(runs: str, after: int) -> str:
        return f'<w:p><w:pPr><w:spacing w:after="{after}"/></w:pPr>{runs}</w:p>'

    # A clause a paragraph, numbered in line with its first word. A number on a
    # line of its own above the sentence reads as a list of scraps rather than as
    # a contract.
    paragraphs = [
        para(run(contract["title"], size=72, bold=True), 640),
        para(run(contract["lead"], size=CONTRACT_TEXT), 420),
    ]
    for number, clause in enumerate(contract["clauses"], start=1):
        paragraphs.append(
            para(
                run(f"{number}.  ", size=CONTRACT_TEXT, bold=True, colour=ACCENT[1:])
                + run(clause, size=CONTRACT_TEXT),
                300,
            )
        )

    # An empty paragraph between them, rather than trusting w:spacing: the
    # renderer sets the clauses flush against each other whatever `w:after`
    # says, and a contract whose clauses touch reads as one block of text.
    body = "<w:p/>".join(paragraphs)

    # The appendix the last clauses promise, and the length that carries the
    # contract past the foot of the screen. Its two columns are words the report
    # already has in every language, so it costs no translation.
    _, rows, _ = table(words, columns=1, rows=ANNEX_ROWS)
    body += cell_rows([[words["item"], words["total"]]] + [[line[0], str(line[-1])] for line in rows])

    return {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-'
        'officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-'
        'officedocument.wordprocessingml.styles+xml"/></Types>',
        "_rels/.rels": OOXML_RELS.format(type=OFFICE_DOCUMENT, target="word/document.xml"),
        # Not optional. odrcore opens /word/styles.xml whether or not the
        # document has a style in it, and a package without one is not read as a
        # Word file at all: it falls through to the web view, which draws the
        # text with no page around it and offers neither search nor editing.
        "word/_rels/document.xml.rels": OOXML_RELS.format(
            type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles",
            target="styles.xml",
        ),
        "word/styles.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:docDefaults><w:rPrDefault><w:rPr>"
        '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/>'
        "</w:rPr></w:rPrDefault>"
        '<w:pPrDefault><w:pPr><w:spacing w:after="160"/></w:pPr></w:pPrDefault>'
        "</w:docDefaults>"
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
        '<w:name w:val="Normal"/></w:style>'
        "</w:styles>",
        "word/document.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        # A4 with 2cm margins, in twentieths of a point. Without it there is no
        # page for odrcore to lay the text on, and the document is drawn as a
        # bare column of text rather than as a sheet of paper.
        f"<w:body>{body}"
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/>'
        "</w:sectPr></w:body></w:document>",
    }


def xlsx_parts(language: dict) -> dict:
    """A workbook of its own figures, so it is not the .ods twice."""
    words = language["report"]
    head, body, foot = table(words, columns=2, rows=8, scale=3)
    rows_of = [head] + body + [foot]

    def cell(column: int, row: int, value) -> str:
        reference = f"{chr(ord('A') + column)}{row}"
        if isinstance(value, int):
            return f'<c r="{reference}"><v>{value}</v></c>'

        return f'<c r="{reference}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'

    rows = "".join(
        f'<row r="{index + 1}">'
        + "".join(cell(column, index + 1, value) for column, value in enumerate(line))
        + "</row>"
        for index, line in enumerate(rows_of)
    )

    return {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.worksheet+xml"/></Types>',
        "_rels/.rels": OOXML_RELS.format(type=OFFICE_DOCUMENT, target="xl/workbook.xml"),
        "xl/_rels/workbook.xml.rels": OOXML_RELS.format(
            type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet",
            target="worksheets/sheet1.xml",
        ),
        "xl/workbook.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets><sheet name="{escape(words["sheets"][0])}" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/worksheets/sheet1.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{rows}</sheetData></worksheet>",
    }


def pptx_parts(language: dict) -> dict:
    """One slide, titled and bulleted, so a deck opens on something."""
    words = language["report"]
    drawing = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
    presentation = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'

    def shape(identifier: int, name: str, box: str, lines: list, size: int) -> str:
        paragraphs = "".join(
            f'<a:p><a:r><a:rPr lang="en" sz="{size}" b="{1 if size > 2000 else 0}"/>'
            f"<a:t>{escape(line)}</a:t></a:r></a:p>"
            for line in lines
        )

        return (
            f'<p:sp><p:nvSpPr><p:cNvPr id="{identifier}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f"<p:spPr><a:xfrm>{box}</a:xfrm>"
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
            f"<p:txBody><a:bodyPr/><a:lstStyle/>{paragraphs}</p:txBody></p:sp>"
        )

    slide = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld {presentation} {drawing}>'
        "<p:cSld><p:spTree>"
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
        + shape(
            2,
            "Title",
            '<a:off x="685800" y="838200"/><a:ext cx="7772400" cy="1143000"/>',
            [words["slides"][0][0]],
            4000,
        )
        + shape(
            3,
            "Body",
            '<a:off x="685800" y="2286000"/><a:ext cx="7772400" cy="2743200"/>',
            words["slides"][0][1],
            2000,
        )
        + "</p:spTree></p:cSld></p:sld>"
    )

    return {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-'
        'officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-'
        'officedocument.presentationml.slide+xml"/></Types>',
        "_rels/.rels": OOXML_RELS.format(type=OFFICE_DOCUMENT, target="ppt/presentation.xml"),
        "ppt/_rels/presentation.xml.rels": OOXML_RELS.format(
            type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide",
            target="slides/slide1.xml",
        ),
        "ppt/presentation.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:presentation {presentation} xmlns:r="http://schemas.openxmlformats.org/'
        f'officeDocument/2006/relationships">'
        '<p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst>'
        '<p:sldSz cx="9144000" cy="5143500"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>',
        "ppt/slides/slide1.xml": slide,
    }


def docx(language: dict) -> bytes:
    return _package(docx_parts(language))


def xlsx(language: dict) -> bytes:
    return _package(xlsx_parts(language))


def pptx(language: dict) -> bytes:
    return _package(pptx_parts(language))
