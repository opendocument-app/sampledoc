"""What tests/golden.json pins for each sample, and how to regenerate it.

A zip is pinned by what it holds - each entry's name, order, date, permissions,
creating system, compression method and uncompressed bytes - rather than by its
own bytes, because the compressed bytes depend on the zlib Python was built
with (zlib-ng in Python 3.14 on Windows, and on some Linux distributions).
Anything else is pinned by its bytes.

    uv run python tests/fingerprint.py      # rewrite golden.json from the current code
"""

import hashlib
import io
import json
import zipfile
from pathlib import Path

GOLDEN = Path(__file__).parent / "golden.json"


def fingerprint(data: bytes) -> str:
    digest = hashlib.sha256()
    if not data.startswith(b"PK\x03\x04"):
        digest.update(data)
        return digest.hexdigest()

    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            header = [
                info.filename,
                list(info.date_time),
                info.external_attr,
                info.create_system,
                info.compress_type,
            ]
            digest.update(json.dumps(header).encode() + b"\0")
            digest.update(archive.read(info) + b"\0")

    return "zip:" + digest.hexdigest()


def main() -> None:
    import sampledoc

    golden = {
        sampledoc.file_name(sample, language): fingerprint(sampledoc.document(sample, language))
        for language in sampledoc.languages()
        for sample in sampledoc.SAMPLES
    }
    GOLDEN.write_text(json.dumps(golden, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(golden)} fingerprints to {GOLDEN}")


if __name__ == "__main__":
    main()
