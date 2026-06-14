#!/usr/bin/env bash
# Pipeline completo: simulacao (Docker) -> conversao PDF->SVG -> report/hypergraph.html
set -euo pipefail

IMAGE=2path-terpenes-mod:latest

echo "==> Step 1/3: Simulation + hypergraph export + PDF report (Docker)"
docker run --rm --volume "$(pwd):/home/shared/" --workdir /home/shared/ "$IMAGE" \
  -f /home/shared/molecules.py \
  -f /home/shared/simulation.py \
  -f /home/shared/export_hypergraph.py \
  -f /home/shared/printer.py

echo "==> Step 2/3: Converting molecule depictions (PDF -> SVG)"
docker run --rm --entrypoint /bin/bash --volume "$(pwd):/home/shared" --workdir /home/shared "$IMAGE" \
  -c 'for f in out/*_g_*.pdf; do mod_post --mode pdfToSvg "${f%.pdf}" "${f%.pdf}"; done'

echo "==> Step 3/3: Generating standalone report/ package (interactive viewer)"
cd "$(pwd)"
python organize_hypergraph_assets.py

echo "Done. Open report/hypergraph.html (double-click, works without a server) to see the result."
