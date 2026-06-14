#!/usr/bin/env bash
# Pipeline completo: simulacao (Docker) -> conversao PDF->SVG -> report/hypergraph.html
set -euo pipefail

IMAGE=2path-terpenes-mod:latest

echo "==> Passo 1/3: Simulacao + export do hypergraph + relatorio PDF (Docker)"
docker run --rm --volume "$(pwd):/home/shared/" --workdir /home/shared/ "$IMAGE" \
  -f /home/shared/molecules.py \
  -f /home/shared/simulation.py \
  -f /home/shared/export_hypergraph.py \
  -f /home/shared/printer.py

echo "==> Passo 2/3: Convertendo depictions de moleculas (PDF -> SVG)"
docker run --rm --entrypoint /bin/bash --volume "$(pwd):/home/shared" --workdir /home/shared "$IMAGE" \
  -c 'for f in out/*_g_*.pdf; do mod_post --mode pdfToSvg "${f%.pdf}" "${f%.pdf}"; done'

echo "==> Passo 3/3: Gerando pacote standalone report/ (viewer interativo)"
python organize_hypergraph_assets.py

echo "Pronto. Abra report/hypergraph.html (duplo-clique, funciona sem servidor) para ver o resultado."
