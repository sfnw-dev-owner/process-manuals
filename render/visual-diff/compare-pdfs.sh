#!/usr/bin/env bash
set -euo pipefail

# Visual diff of all PDFs in two .zip archives.
#
# Usage:
#   compare-pdfs.sh LEFT.zip RIGHT.zip /output
#
# Unzips both archives into temp dirs, reports PDFs that appear in only
# one side, and produces visual diff PDFs for every PDF present in both
# (byte-wise-identical files are skipped).

if [[ $# -ne 3 ]]; then
    echo "Usage: $0 LEFT.zip RIGHT.zip /output" >&2
    exit 2
fi

ZIP1="$1"
ZIP2="$2"
OUTPUT="$3"

for f in "$ZIP1" "$ZIP2"; do
    if [[ ! -f "$f" ]]; then
        echo "Error: file not found: $f" >&2
        exit 2
    fi
done

JOBS="$(nproc)"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

LEFT="$TMPDIR/left"
RIGHT="$TMPDIR/right"
mkdir -p "$LEFT" "$RIGHT" "$OUTPUT"

echo "Extracting left ZIP ($ZIP1)..."
unzip -q "$ZIP1" -d "$LEFT"

echo "Extracting right ZIP ($ZIP2)..."
unzip -q "$ZIP2" -d "$RIGHT"

# Find PDFs relative to extraction root (sorted, as comm requires).
(cd "$LEFT"  && find . -type f -iname '*.pdf' -printf '%P\n' | sort) > "$TMPDIR/left.txt"
(cd "$RIGHT" && find . -type f -iname '*.pdf' -printf '%P\n' | sort) > "$TMPDIR/right.txt"

echo
echo "=== PDFs only in left ZIP ==="
ONLY_LEFT="$(comm -23 "$TMPDIR/left.txt" "$TMPDIR/right.txt")"
if [[ -n "$ONLY_LEFT" ]]; then printf '%s\n' "$ONLY_LEFT"; else echo "(none)"; fi

echo
echo "=== PDFs only in right ZIP ==="
ONLY_RIGHT="$(comm -13 "$TMPDIR/left.txt" "$TMPDIR/right.txt")"
if [[ -n "$ONLY_RIGHT" ]]; then printf '%s\n' "$ONLY_RIGHT"; else echo "(none)"; fi

# PDFs present in both -> compare them.
MATCHES="$TMPDIR/matches.txt"
comm -12 "$TMPDIR/left.txt" "$TMPDIR/right.txt" > "$MATCHES"

MATCH_COUNT=$(wc -l < "$MATCHES")

echo
echo "=== Visual comparison ==="
echo "Matching PDFs: $MATCH_COUNT"
echo "Parallel jobs: $JOBS"
echo "Output:        $OUTPUT"
echo

if (( MATCH_COUNT == 0 )); then
    echo "No matching PDFs to compare."
    exit 0
fi

compare_one() {
    local rel="$1"
    local left="$LEFT/$rel"
    local right="$RIGHT/$rel"
    local base="${rel%.*}"
    local out="$OUTPUT/${base}-diff.pdf"

    if cmp -s "$left" "$right"; then
        printf 'SAME\t%s\n' "$rel"
        return 0
    fi

    mkdir -p "$(dirname "$out")"

    if xvfb-run -a diff-pdf \
        --skip-identical \
        --dpi=150 \
        --output-diff="$out" \
        "$left" "$right"
    then
        rm -f "$out"
        printf 'SAME\t%s\n' "$rel"
    else
        printf 'DIFF\t%s\n' "$rel"
    fi
}
export LEFT RIGHT OUTPUT
export -f compare_one

# Kick off parallel diffing.
xargs -d '\n' -r -n1 -P "$JOBS" bash -c 'compare_one "$1"' _ < "$MATCHES"

# Prune directories that had no diffs.
find "$OUTPUT" -mindepth 1 -depth -type d -empty -delete
