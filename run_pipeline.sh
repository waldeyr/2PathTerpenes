#!/usr/bin/env bash
# Pipeline completo: simulacao (Docker) -> conversao PDF->SVG -> report/hypergraph.html
set -euo pipefail

IMAGE=2path-terpenes-mod:latest
HOST_UID_GID="$(id -u):$(id -g)"
SIMULATION_SCRIPT=simulation.py

usage() {
  echo "Usage: $0 [--full]" >&2
  echo "  --full  Run simulation-full.py (all rules, 7 iterations)." >&2
}

case "${1:-}" in
  --full)
    SIMULATION_SCRIPT=simulation-full.py
    shift
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  "")
    ;;
  *)
    usage
    exit 2
    ;;
esac

if (( $# > 0 )); then
  usage
  exit 2
fi

if [[ ! -f "$SIMULATION_SCRIPT" ]]; then
  echo "Simulation script not found: $SIMULATION_SCRIPT" >&2
  exit 1
fi

echo "==> Step 1/3: Simulation ($SIMULATION_SCRIPT) + hypergraph export + PDF report (Docker)"
docker run --rm --user "$HOST_UID_GID" --volume "$(pwd):/home/shared/" --workdir /home/shared/ "$IMAGE" \
  -f /home/shared/molecules.py \
  -f "/home/shared/$SIMULATION_SCRIPT" \
  -f /home/shared/export_hypergraph.py \
  -f /home/shared/printer.py

echo "==> Step 2/3: Converting molecule depictions (PDF -> SVG)"
docker run --rm --user "$HOST_UID_GID" --entrypoint /bin/bash --volume "$(pwd):/home/shared" --workdir /home/shared "$IMAGE" \
  -c 'for f in out/*_g_*.pdf; do mod_post --mode pdfToSvg "${f%.pdf}" "${f%.pdf}"; done'

echo "==> Step 3/3: Generating standalone report/ package (interactive viewer)"
cd "$(pwd)"
python organize_hypergraph_assets.py

echo "Done. Open report/hypergraph.html (double-click, works without a server) to see the result."
