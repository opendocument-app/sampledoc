import io
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import pytest

import sampledoc
from fingerprint import fingerprint
from sampledoc import SAMPLES, document, file_name, languages
from sampledoc.cli import main
from sampledoc.names import FILLERS, manifest, query
from sampledoc.pdf import spellable

GOLDEN = json.loads((Path(__file__).parent / "golden.json").read_text(encoding="utf-8"))

EVERY = [(sample, language) for language in languages() for sample in SAMPLES]


@pytest.mark.parametrize(("sample", "language"), EVERY)
def test_matches_golden(sample, language):
    """What the original screenshot script wrote (see fingerprint.py). A change
    here is a change to every app's screenshots: regenerate golden.json on
    purpose, not to pass."""
    name = file_name(sample, language)
    assert name in GOLDEN, f"{name} has no golden fingerprint - new samples need one"
    assert fingerprint(document(sample, language)) == GOLDEN[name]


def test_reproducible():
    assert document("text", "de") == document("text", "de")


def test_every_language_file_has_the_same_shape():
    keys = None
    for language in languages():
        data = sampledoc._language.load(language)
        assert data["language"] == language
        shape = {key: sorted(value) if isinstance(value, dict) else None for key, value in data.items()}
        shape.pop("search", None)
        assert keys is None or shape == keys, language
        keys = shape


@pytest.mark.parametrize("language", languages())
@pytest.mark.parametrize("sample", ["text", "sheet", "slides"])
def test_odf_package(sample, language):
    with zipfile.ZipFile(io.BytesIO(document(sample, language))) as archive:
        first = archive.infolist()[0]
        assert first.filename == "mimetype"
        assert first.compress_type == zipfile.ZIP_STORED
        assert archive.read("mimetype").decode().startswith("application/vnd.oasis.opendocument.")
        for name in ("content.xml", "styles.xml", "META-INF/manifest.xml"):
            ElementTree.fromstring(archive.read(name))


@pytest.mark.parametrize("language", languages())
@pytest.mark.parametrize("sample", ["word", "cells", "deck"])
def test_ooxml_package(sample, language):
    with zipfile.ZipFile(io.BytesIO(document(sample, language))) as archive:
        assert "[Content_Types].xml" in archive.namelist()
        for name in archive.namelist():
            ElementTree.fromstring(archive.read(name))


@pytest.mark.parametrize("language", languages())
def test_pdf_cross_reference(language):
    data = document("paper", language)
    assert data.startswith(b"%PDF-1.4\n") and data.endswith(b"%%EOF\n")

    start = int(re.search(rb"startxref\n(\d+)\n", data).group(1))
    assert data[start:].startswith(b"xref\n")
    for number, offset in enumerate(re.findall(rb"(\d{10}) 00000 n ", data), start=1):
        assert data[int(offset) :].startswith(f"{number} 0 obj\n".encode())


def test_pdf_falls_back_to_english_where_helvetica_cannot_spell():
    assert not spellable(sampledoc._language.load("ja"))
    assert document("paper", "ja") == document("paper", "en")


@pytest.mark.parametrize("language", languages())
def test_query_is_in_the_report_more_than_once(language):
    word = query(language)
    text = document("notes", language).decode().lower()
    assert text.count(word.lower()) >= 2


def test_manifest():
    details = manifest({"de-DE": "de"})
    assert details["locales"] == {"de-DE": "de"}
    assert set(details["languages"]) == set(languages())
    for entry in details["languages"].values():
        assert set(FILLERS) | set(SAMPLES) == set(entry["files"])

    with pytest.raises(ValueError):
        manifest({"xx-XX": "xx"})


def test_unknown_names():
    with pytest.raises(KeyError):
        document("nope", "en")
    with pytest.raises(KeyError):
        document("text", "xx")


def test_cli(tmp_path):
    locales = tmp_path / "locales.json"
    locales.write_text('{"en-US": "en"}')
    out = tmp_path / "out"

    assert main(["-o", str(out), "-l", "en", "-s", "text", "-s", "paper", "--locales", str(locales)]) == 0

    assert sorted(path.name for path in out.iterdir()) == [
        "sample-paper-en.pdf",
        "sample-text-en.odt",
        "screenshot-names.json",
    ]
    assert json.loads((out / "screenshot-names.json").read_text(encoding="utf-8"))["locales"] == {
        "en-US": "en"
    }
