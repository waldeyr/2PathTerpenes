# ANNOTATE THE HYPERGRAPH JSON WITH ChEMBL IDENTIFIERS / PREFERRED NAMES
#
# Plain Python (no MOD dependency) post-processing step: for each molecule
# in docs/data/hypergraph.json (or the path given as argv[1]), compute its
# InChIKey (via the Open Babel `obabel` CLI) and look up an exact match in
# the ChEMBL REST API (https://www.ebi.ac.uk/chembl/api/data/molecule).
# Matches add "chemblId" and "chemblName" fields to the node, which
# docs/javascript/hypergraph.js shows in the details panel and includes in
# the search index.
#
# Results are cached by InChIKey in chembl_cache.json next to the input
# file, so repeated runs only query ChEMBL for previously unseen structures.
#
# Usage:
#   python annotate_chembl.py [path/to/hypergraph.json]

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

CHEMBL_URL = "https://www.ebi.ac.uk/chembl/api/data/molecule.json"
REQUEST_DELAY_SECONDS = 0.34  # stay under ChEMBL's ~3 requests/second guidance


def smiles_to_inchikey(smiles):
    try:
        result = subprocess.run(
            ["obabel", f"-:{smiles}", "-oinchikey"],
            capture_output=True, text=True, timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    key = result.stdout.strip()
    return key or None


def lookup_chembl(inchikey):
    query = urllib.parse.urlencode({
        "molecule_structures__standard_inchi_key": inchikey,
        "format": "json",
    })
    url = f"{CHEMBL_URL}?{query}"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.load(response)
    except (urllib.error.URLError, OSError, ValueError):
        return None

    molecules = data.get("molecules") or []
    if not molecules:
        return None

    molecule = molecules[0]
    return {
        "chemblId": molecule.get("molecule_chembl_id"),
        "chemblName": molecule.get("pref_name"),
    }


def main():
    hypergraph_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("docs", "data", "hypergraph.json")
    cache_path = os.path.join(os.path.dirname(hypergraph_path) or ".", "chembl_cache.json")

    with open(hypergraph_path) as f:
        hypergraph = json.load(f)

    cache = {}
    if os.path.isfile(cache_path):
        with open(cache_path) as f:
            cache = json.load(f)

    annotated = 0
    for node in hypergraph.get("nodes", []):
        smiles = node.get("smiles")
        if not smiles:
            continue

        inchikey = smiles_to_inchikey(smiles)
        if not inchikey:
            continue

        if inchikey in cache:
            result = cache[inchikey]
        else:
            result = lookup_chembl(inchikey)
            cache[inchikey] = result
            time.sleep(REQUEST_DELAY_SECONDS)

        if result and result.get("chemblId"):
            node["chemblId"] = result["chemblId"]
            node["chemblName"] = result.get("chemblName")
            annotated += 1

    with open(hypergraph_path, "w") as f:
        json.dump(hypergraph, f, indent=2)

    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=2)

    print(f"Annotated {annotated}/{len(hypergraph.get('nodes', []))} molecules with ChEMBL data.")


if __name__ == "__main__":
    main()
