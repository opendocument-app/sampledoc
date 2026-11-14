# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/). Any change to the bytes of a
generated sample is listed, because it changes every screenshot taken of it.

## [Unreleased]

## [0.1.0] - 2026-11-14

First release, extracted from the `make-screenshot-documents.py` scripts of
OpenDocument.droid and OpenDocument.ios.

### Added

- Nine samples (`.odt`, `.ods`, `.odp`, `.docx`, `.xlsx`, `.pptx`, `.pdf`,
  `.csv`, `.txt`) in 15 languages: cs, de, en, es, et, fr, hi, it, ja, pl,
  pt-BR, ru, sv, tr, zh.
- `sampledoc` command line tool and Python API (`document`, `generate`,
  `file_names`, `query`, `manifest`).
- `screenshot-names.json` with display names and search words per language,
  plus an optional locale table via `--locales`.
- Wording moved into one JSON file per language.

### Output

- Byte-for-byte identical to what OpenDocument.droid's script wrote at
  `f8b0a37d`, and, for its nine languages, to OpenDocument.ios at `f7f7a33`.
- Zip entries record a fixed creating system, so Windows writes the same
  package contents as macOS and Linux. Compressed bytes still depend on the
  zlib Python is built with (zlib-ng on Python 3.14 for Windows).
- `screenshot-names.json` now always nests languages under `"languages"` (the
  Android layout). The iOS script wrote them at the top level.

[Unreleased]: https://github.com/opendocument-app/sampledoc/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/opendocument-app/sampledoc/releases/tag/v0.1.0
