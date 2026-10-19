#!/usr/bin/env python3
"""Compile the molecule PDFs without MØD's monolithic summary recipe.

MØD writes one rule per depiction to ``summary/MakefileImpl`` and also writes
one enormous recipe for ``summary/all.tex``.  GNU make refuses that recipe
once it contains more than 65,535 lines, even though the individual molecule
targets are perfectly usable.  This helper requests only the molecule PDF
targets from the implementation makefile and, for small graphs, optionally
builds the ordinary summary PDF afterwards.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from report_policy import should_render_pdf_report
from validate_pipeline import images, validate_graph


MAKE_RECIPE_LINE_LIMIT = 65_535


def _threads():
    value = os.environ.get("MOD_NUM_POST_THREADS", "2")
    try:
        threads = int(value)
    except ValueError as error:
        raise ValueError("MOD_NUM_POST_THREADS must be a positive integer") from error
    if threads < 1:
        raise ValueError("MOD_NUM_POST_THREADS must be a positive integer")
    return threads


def _load_graph(out_dir):
    path = Path(out_dir) / "hypergraph.json"
    with path.open(encoding="utf-8") as handle:
        graph = json.load(handle)
    validate_graph(graph)
    return graph


def _write_makefile(path, targets):
    """Write short prerequisite lines so no shell/Make line is enormous."""
    with path.open("w", encoding="utf-8") as handle:
        handle.write(".PHONY: all\n")
        for start in range(0, len(targets), 200):
            handle.write("all: " + " ".join(targets[start:start + 200]) + "\n")
        handle.write("include summary/MakefileImpl\n")


def _run_make(makefile, threads, target="all"):
    make = shutil.which("make")
    if make is None:
        raise RuntimeError("GNU make is required to compile molecule depictions")
    subprocess.run([make, "-s", "-j", str(threads), "-f", str(makefile), target], check=True)


def _recipe_line_count(makefile):
    """Count tab-prefixed recipe lines without parsing the Makefile."""
    try:
        with makefile.open(encoding="utf-8") as handle:
            return sum(line.startswith("\t") for line in handle)
    except OSError:
        return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="out")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    graph = _load_graph(out_dir)
    expected = images(graph)
    targets = [str(out_dir / (image[:-4] + ".pdf")) for image in expected]
    missing = [target for target in targets if not Path(target).is_file() or Path(target).stat().st_size == 0]

    makefile_impl = Path("summary") / "MakefileImpl"
    if missing:
        if not makefile_impl.is_file():
            raise RuntimeError(f"Missing {len(missing)} molecule PDFs and {makefile_impl} was not generated")
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix=".molecule-pdfs-", suffix=".mk",
            dir=out_dir, delete=False,
        ) as handle:
            makefile = Path(handle.name)
        try:
            _write_makefile(makefile, targets)
            _run_make(makefile, _threads())
        finally:
            makefile.unlink(missing_ok=True)

    remaining = [target for target in targets if not Path(target).is_file() or Path(target).stat().st_size == 0]
    if remaining:
        raise RuntimeError(f"Missing {len(remaining)} molecule PDFs after compilation: {remaining[:5]}")

    # The summary PDF is useful for small runs, but its all.tex recipe is the
    # exact scalability hazard this stage avoids for large hypergraphs.
    render_summary, message = should_render_pdf_report(
        len(graph["nodes"]), len(graph["hyperedges"]), os.environ,
    )
    print(f"Molecule PDF compilation completed: {len(targets)} expected, {len(missing)} built.", flush=True)
    summary_makefile = Path("summary/Makefile")
    recipe_lines = _recipe_line_count(summary_makefile)
    if render_summary and summary_makefile.is_file() and recipe_lines <= MAKE_RECIPE_LINE_LIMIT:
        _run_make(summary_makefile, _threads(), "summary.pdf")
        print("Summary PDF compilation completed.", flush=True)
    elif render_summary:
        if not summary_makefile.is_file():
            print("Summary PDF makefile not present; molecule depictions are ready.", flush=True)
        else:
            print(
                f"Summary PDF skipped: its recipe has {recipe_lines} lines, "
                f"above GNU make's {MAKE_RECIPE_LINE_LIMIT}-line limit.",
                flush=True,
            )
    else:
        print("Summary PDF skipped for large graph; interactive report remains enabled.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Molecule PDF compilation failed: {error}", flush=True)
        raise SystemExit(1)
