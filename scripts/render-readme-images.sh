#!/bin/sh
# Render the README's sample images with LibreOffice, from the current code.
#   scripts/render-readme-images.sh [path/to/soffice]
set -eu

SOFFICE=${1:-$(command -v soffice || echo /Applications/LibreOffice.app/Contents/MacOS/soffice)}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

uv run --project "$ROOT" sampledoc -o "$WORK" --no-names \
  -l en -l de -s text -s sheet -s word -s paper > /dev/null

cd "$WORK"
for file in sample-text-en.odt sample-sheet-en.ods sample-word-de.docx; do
  "$SOFFICE" --headless -env:UserInstallation="file://$WORK/profile" --convert-to png "$file" > /dev/null
done
"$SOFFICE" --headless -env:UserInstallation="file://$WORK/profile" \
  --infilter=draw_pdf_import --convert-to png sample-paper-en.pdf > /dev/null

for name in text-en sheet-en word-de paper-en; do
  cp "sample-$name.png" "$ROOT/docs/images/sample-$name.png"
done
echo "rendered into $ROOT/docs/images"
