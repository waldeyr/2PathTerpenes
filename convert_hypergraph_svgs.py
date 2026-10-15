#!/usr/bin/env python3
"""Convert exactly the molecule depictions referenced by hypergraph.json."""

import argparse
import json
import os
import subprocess
import sys

import progress_utils


def expected_images(out_dir):
    path = os.path.join(out_dir, "hypergraph.json")
    with open(path, encoding="utf-8") as handle:
        hypergraph = json.load(handle)

    images = []
    for node in hypergraph.get("nodes", []):
        image = node.get("image")
        if not image:
            continue
        if os.path.basename(image) != image or not image.endswith(".svg"):
            raise ValueError(f"Unsafe or invalid image reference: {image!r}")
        images.append(image)

    if not images:
        raise ValueError("hypergraph.json has no molecule image references")
    if len(images) != len(set(images)):
        raise ValueError("hypergraph.json has duplicate molecule image references")
    return images


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
        if not os.path.isfile(pdf_path) or os.path.getsize(pdf_path) == 0:
            missing_pdfs.append(pdf_path)
            continue
        if os.path.isfile(svg_path) and os.path.getsize(svg_path) > 0:
            skipped += 1
            continue
        base = pdf_path[:-4]
        subprocess.run(["mod_post", "--mode", "pdfToSvg", base, base], check=True)
        if not os.path.isfile(svg_path) or os.path.getsize(svg_path) == 0:
            raise RuntimeError(f"mod_post did not create a usable SVG: {svg_path}")
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
