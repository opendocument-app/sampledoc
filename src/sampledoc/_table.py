"""The figures every sample that has a table takes its numbers from."""

from __future__ import annotations

import io
import zipfile

# 1980-01-01, what zip stores when it is given nothing: a rerun with the same
# words has to produce the same bytes, or every run is a commit
EPOCH = (1980, 1, 1, 0, 0, 0)

# One accent, used for the report's headings and the slide titles, so the
# documents read as one set.
ACCENT = "#1c6fd6"
RULE = "#d4d9e0"

# What the sheets add up: forty rows over six periods, so there is enough of it
# to look like a spreadsheet. The first twenty keep the first four figures they
# had, because the invoice and the .xlsx take slices off the front.
FIGURES = [
    [1200, 1450, 1310, 1600, 1380, 1520],
    [480, 620, 510, 470, 690, 540],
    [3600, 900, 1200, 750, 830, 1150],
    [820, 760, 930, 1010, 870, 940],
    [540, 560, 580, 600, 610, 630],
    [300, 450, 380, 520, 410, 470],
    [1100, 1150, 1180, 1240, 1260, 1290],
    [640, 640, 660, 680, 700, 700],
    [420, 980, 350, 610, 1240, 380],
    [260, 280, 270, 300, 290, 310],
    [890, 910, 940, 980, 1000, 1030],
    [1500, 400, 620, 350, 480, 390],
    [340, 360, 350, 370, 380, 390],
    [220, 220, 230, 230, 240, 240],
    [180, 620, 210, 240, 190, 660],
    [410, 430, 400, 450, 440, 460],
    [760, 820, 690, 900, 850, 780],
    [950, 480, 1100, 520, 560, 1180],
    [280, 290, 300, 310, 320, 330],
    [520, 540, 530, 560, 570, 590],
    [1340, 1290, 1410, 1360, 1440, 1480],
    [710, 730, 720, 750, 760, 780],
    [190, 200, 190, 210, 200, 220],
    [330, 330, 340, 340, 350, 350],
    [860, 890, 1240, 910, 930, 960],
    [240, 250, 260, 260, 270, 280],
    [120, 130, 120, 140, 130, 150],
    [460, 170, 180, 490, 180, 190],
    [580, 610, 550, 640, 600, 670],
    [150, 160, 170, 160, 180, 170],
    [210, 230, 220, 250, 240, 260],
    [390, 390, 400, 410, 410, 420],
    [270, 1080, 310, 340, 290, 360],
    [1620, 350, 380, 360, 400, 370],
    [620, 650, 630, 680, 660, 700],
    [110, 120, 110, 130, 120, 140],
    [440, 450, 460, 470, 480, 490],
    [980, 1020, 640, 1060, 1090, 720],
    [560, 500, 590, 530, 610, 570],
    [740, 770, 800, 790, 830, 860],
]


def table(words: dict, columns: int = 4, rows: int = 0, scale: int = 1) -> tuple:
    """The figures as rows of cells: a header, the items across as many periods
    as are asked for with their totals, and a totals row under them.

    Narrowed and shortened for the files that are not the budget, so the .xlsx
    and the invoice hold their own figures rather than the .ods twice.

    As wide as the header a language has words for, so one translated ahead of
    the others comes out short rather than out of step.
    """
    periods = words["periods"][:columns]
    columns = len(periods)
    taken = FIGURES[:rows] if rows else FIGURES
    names = words["rows"][: len(taken)]

    head = [words["item"]] + periods + [words["total"]]
    body = [
        [name] + [value * scale for value in figures[:columns]] + [sum(figures[:columns]) * scale]
        for name, figures in zip(names, taken, strict=False)
    ]
    foot = (
        [words["total"]]
        + [sum(line[column + 1] for line in body) for column in range(len(periods))]
        + [sum(line[-1] for line in body)]
    )

    return head, body, foot


def zipped(parts: list[tuple[str, str, bool]]) -> bytes:
    """A zip of (name, text, stored) parts in the order given, reproducibly.

    Every entry carries the same date, permissions and creating system, so the
    archive depends on nothing but its contents - not the clock, not the platform.
    """
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, text, stored in parts:
            info = zipfile.ZipInfo(name, date_time=EPOCH)
            info.external_attr = 0o644 << 16
            # ZipInfo records the OS it was made on (0 on Windows, 3 elsewhere),
            # and that byte would make the same samples differ by platform
            info.create_system = 3
            archive.writestr(info, text, compress_type=zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED)

    return out.getvalue()
