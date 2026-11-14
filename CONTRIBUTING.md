# Contributing

## Setup

```sh
git clone https://github.com/opendocument-app/sampledoc
cd sampledoc
uv sync            # or: python -m venv .venv && .venv/bin/pip install -e . pytest ruff
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## Layout

```
src/sampledoc/
  languages/<code>.json   all wording, one file per language
  _language.py            finds and loads the language files
  _table.py               the figures every table is built from; reproducible zips
  odf.py                  .odt .ods .odp
  ooxml.py                .docx .xlsx .pptx
  pdf.py                  .pdf
  plain.py                .csv .txt
  names.py                display names, search word, screenshot-names.json
  cli.py                  the `sampledoc` command
tests/
  golden.json             SHA-256 of every sample file
```

## Adding a language

1. Copy `src/sampledoc/languages/en.json` to `<code>.json` (a BCP 47 tag such
   as `sv` or `pt-BR`) and translate every string. Keep the keys and the
   number of entries in each list - `report.rows` must have 40 names,
   `report.periods` six months, `report.sections` five sections.
2. Languages that do not separate words with spaces (like `ja` and `zh`) need a
   `"search"` key naming a word that occurs at least twice in the report.
3. Run the tests. `test_matches_golden` will fail for the new files because
   they have no hash yet; add them by regenerating `golden.json` (below).

Keep the writing plain and short: it is a document seen over someone's
shoulder, not copy that has to sell anything. No real people or companies.

## Changing the output

Every sample's bytes are pinned in `tests/golden.json`. Apps take screenshots
of these files, so any change to them should be on purpose. When it is,
regenerate the hashes and mention the change in `CHANGELOG.md`:

```sh
uv run python -c "
import hashlib, json, sampledoc
golden = {sampledoc.file_name(s, l): hashlib.sha256(sampledoc.document(s, l)).hexdigest()
          for l in sampledoc.languages() for s in sampledoc.SAMPLES}
open('tests/golden.json', 'w').write(json.dumps(golden, indent=1, sort_keys=True))
"
```

## Releasing

1. Bump `__version__` in `src/sampledoc/__init__.py` and move the
   `Unreleased` section of `CHANGELOG.md` under the new version.
2. Commit, tag `vX.Y.Z`, push the tag, and publish a GitHub release for it.
   The `release` workflow builds and uploads to PyPI via trusted publishing.
