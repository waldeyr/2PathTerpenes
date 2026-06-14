# EXPORT THE DERIVATION GRAPH AS A JSON HYPERGRAPH FOR THE INTERACTIVE HTML VIEWER
#
# This script must run after simulation.py has built `dg`. It walks the
# derivation graph (a hypergraph: vertices = molecules, hyperedges =
# reactions with possibly several educts/products) and writes
# `out/hypergraph.json`, plus one depiction (PDF) per molecule that
# `organize_hypergraph_assets.py` later converts to SVG and copies into
# `docs/data/` and `docs/img/molecules/` for the interactive viewer
# (docs/hypergraph.html).
#
# Helper for MØD compatibility (mirrors molecules.py / simulation.py / printer.py)
try:
    from mod import post
    if not hasattr(post, 'summarySection'):
        raise ImportError
except ImportError:
    class PostDummy:
        @staticmethod
        def summarySection(heading):
            pass
    post = PostDummy

import json
import os

OUT_DIR = "out"
os.makedirs(OUT_DIR, exist_ok=True)


def rule_category(rule_name):
    name = rule_name.lower()
    if name.startswith("mono"):
        return "mono"
    if name.startswith("sesqui"):
        return "sesqui"
    return "common"


def graph_smiles(g):
    # `Graph.smiles` is available on most MOD versions; fall back gracefully.
    try:
        return g.smiles
    except Exception:
        return None


def graph_charge(g):
    try:
        return sum(int(v.charge) for v in g.vertices)
    except Exception:
        return None


def graph_cycles(g):
    try:
        return g.numEdges - g.numVertices + 1
    except Exception:
        return None


def print_graph(g, vertex_id):
    # Render the molecule depiction to PDF; organize_hypergraph_assets.py
    # converts these to SVG (same pdfToSvg approach used for rule previews).
    try:
        result = g.print()
        if isinstance(result, str) and result:
            return result
        if isinstance(result, (list, tuple)) and result:
            return result[0]
    except Exception:
        pass
    return None


nodes = []
node_index = {}

for v in dg.vertices:
    g = v.graph
    file_prefix = print_graph(g, v.id)
    node = {
        "id": f"v{v.id}",
        "name": g.name,
        "smiles": graph_smiles(g),
        "charge": graph_charge(g),
        "cycles": graph_cycles(g),
        "image": f"{file_prefix}.svg" if file_prefix else None,
    }
    nodes.append(node)
    node_index[v.id] = node

hyperedges = []
for e in dg.edges:
    rule_names = []
    try:
        for r in e.rules:
            rule_names.append(r.name)
    except Exception:
        pass

    sources = [f"v{src.id}" for src in e.sources]
    targets = [f"v{tgt.id}" for tgt in e.targets]
    category = rule_category(rule_names[0]) if rule_names else "common"

    hyperedges.append({
        "id": f"e{len(hyperedges)}",
        "sources": sources,
        "targets": targets,
        "rules": rule_names,
        "category": category,
    })

hypergraph = {
    "meta": {
        "title": "Plant Terpenes Biosynthesis - Derivation Hypergraph",
    },
    "nodes": nodes,
    "hyperedges": hyperedges,
}

with open(os.path.join(OUT_DIR, "hypergraph.json"), "w") as f:
    json.dump(hypergraph, f, indent=2)

post.summarySection("Interactive Hypergraph Export")
print(f"Wrote {len(nodes)} molecules and {len(hyperedges)} reactions to "
      f"{os.path.join(OUT_DIR, 'hypergraph.json')}")
