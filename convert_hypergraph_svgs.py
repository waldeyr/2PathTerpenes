#!/usr/bin/env python3
"""Convert exactly the molecule depictions referenced by hypergraph.json."""

import argparse
import json
import os
import subprocess
import sys
import tempfile

import progress_utils
from validate_pipeline import images, validate_graph, validate_svg


def expected_images(out_dir):
    path = os.path.join(out_dir, "hypergraph.json")
    with open(path, encoding="utf-8") as handle:
        hypergraph = json.load(handle)

    validate_graph(hypergraph)
    return images(hypergraph)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="out")
    args = parser.parse_args()

    images = expected_images(args.out_dir)
    missing_pdfs = []
    converted = 0
    skipped = 0

    for image in progress_utils.progress_iter(images, desc="Phase 3/4: Converting PDF depictions to SVG"):
        svg_path = os.path.join(args.out_dir, image)
        pdf_path = f"{svg_path[:-4]}.pdf"
        if os.path.isfile(svg_path):
            try:
                validate_svg(svg_path)
            except ValueError:
                pass  # An interrupted/invalid conversion must be regenerated.
            else:
                skipped += 1
                continue
        if not os.path.isfile(pdf_path) or os.path.getsize(pdf_path) == 0:
            missing_pdfs.append(pdf_path)
            continue
        base = pdf_path[:-4]
        # Publish only after a successful, parsed conversion. A failed command
        # must never leave a non-empty partial SVG that a retry would reuse.
        with tempfile.TemporaryDirectory(prefix=".svg-", dir=args.out_dir) as temporary:
            target = os.path.join(temporary, "molecule")
            subprocess.run(["mod_post", "--mode", "pdfToSvg", base, target], check=True)
            validate_svg(f"{target}.svg")
            os.replace(f"{target}.svg", svg_path)
        converted += 1

    if missing_pdfs:
        preview = ", ".join(missing_pdfs[:5])
        raise RuntimeError(f"Missing {len(missing_pdfs)} expected PDF depictions: {preview}")

    print(f"SVG conversion completed: {converted} converted, {skipped} already present, {len(images)} expected.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"SVG conversion failed: {error}", file=sys.stderr)
        raise SystemExit(1)
