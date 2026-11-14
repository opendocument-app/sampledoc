# sampledoc

[![CI](https://github.com/opendocument-app/sampledoc/actions/workflows/ci.yml/badge.svg)](https://github.com/opendocument-app/sampledoc/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/sampledoc.svg)](https://pypi.org/project/sampledoc/)
[![Python](https://img.shields.io/pypi/pyversions/sampledoc.svg)](https://pypi.org/project/sampledoc/)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](LICENSE)

Small, localized, byte-for-byte reproducible sample office documents.

`sampledoc` writes a believable folder of documents - a quarterly report, a
budget, a contract, an invoice, a contact list - in 15 languages and 9 file
formats. It has no dependencies: every file is written by hand, a few kilobytes
each, with no images and no third-party material.

It was built to give app-store screenshots of
[OpenDocument Reader](https://opendocument.app/) (Android and iOS) a document
in the language of each store listing, and is just as useful as test fixtures
for anything that opens office files.

## Install

```sh
pip install sampledoc
# or run it without installing
uvx sampledoc --list
pipx run sampledoc --list
```

Requires Python 3.10 or newer.

## Command line

```sh
sampledoc -o samples/                      # everything: 9 samples x 15 languages
sampledoc -o samples/ -l de -l fr          # only German and French
sampledoc -o samples/ -s text -s paper     # only the .odt report and the .pdf invoice
sampledoc -o samples/ --locales locales.json   # also map device locales to languages
sampledoc --list                           # what languages and samples there are
```

Files are named `sample-<sample>-<language>.<ext>`, e.g. `sample-text-de.odt`.

Next to them it writes `screenshot-names.json`, which holds, per language, a
realistic display name for every sample (plus a set of "filler" file names to
pad out a folder view) and a word to search the report for that is guaranteed
to appear in it several times:

```json
{
 "languages": {
  "de": {
   "files": {"text": "Quartalsbericht", "sheet": "Budget", "paper": "Rechnung", "...": "..."},
   "search": "version"
  }
 },
 "locales": {"de-DE": "de"}
}
```

`locales` is only present when `--locales FILE` is given; the file is a JSON
object mapping device/store locales to sample languages. Pass `--no-names` to
skip the file.

## Samples

| Sample   | Format | What it is                                         |
|----------|--------|----------------------------------------------------|
| `text`   | `.odt` | a quarterly report with headed sections and a table of costs, long enough to fill A4 |
| `sheet`  | `.ods` | a budget: 40 rows over six months, on two sheets    |
| `slides` | `.odp` | a three slide project plan, 16:9                   |
| `word`   | `.docx`| a service agreement with numbered clauses and an appendix |
| `cells`  | `.xlsx`| a small table of sales figures                     |
| `deck`   | `.pptx`| a single titled, bulleted slide                    |
| `paper`  | `.pdf` | a two page invoice (Helvetica/WinAnsi - languages it cannot spell get the English invoice) |
| `rows`   | `.csv` | a contact list                                     |
| `notes`  | `.txt` | the report and the slides as plain text            |

Languages: `en`, `cs`, `de`, `es`, `et`, `fr`, `hi`, `it`, `ja`, `pl`, `pt-BR`,
`ru`, `sv`, `tr`, `zh`.

## Python API

```python
import sampledoc

sampledoc.languages()  # ('en', 'cs', 'de', ...)
sampledoc.SAMPLES  # {'text': Sample(extension='odt', ...), ...}

data = sampledoc.document("text", "de")  # bytes of sample-text-de.odt
sampledoc.generate("out/", languages=["en"], samples=["text", "paper"])  # -> [Path, ...]

sampledoc.file_names("de")  # {'text': 'Quartalsbericht', ...}
sampledoc.query("de")  # the word to search the report for
sampledoc.manifest({"de-DE": "de"})  # what goes into screenshot-names.json
```

## Reproducibility

The same version of `sampledoc` always writes the same bytes: zip entries carry
a fixed 1980-01-01 timestamp and fixed permissions, and nothing depends on the
clock, the platform or the locale. The test suite pins a SHA-256 of every file,
so a change to the output is always a deliberate one - and is called out in the
[changelog](CHANGELOG.md), since it changes every screenshot taken of it.

If you need stable output across upgrades, pin the version.

## Contributing

Adding or fixing a language is a matter of editing one JSON file in
[`src/sampledoc/languages/`](src/sampledoc/languages). See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

[Mozilla Public License 2.0](LICENSE)
