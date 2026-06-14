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

try:
    from mod import GraphPrinter
    moleculePrinter = GraphPrinter()
    moleculePrinter.collapseHydrogens = True
    moleculePrinter.withIndex = False
except ImportError:
    moleculePrinter = None

import glob
import json
import os

OUT_DIR = "out"
os.makedirs(OUT_DIR, exist_ok=True)


def build_rule_category_map():
    # Rule.name (used below) reflects the GML "ruleID" of each rule (e.g.
    # "2,6 closure"), not the GML filename (e.g. "mono_2_6_Cyc.gml"). Build a
    # ruleID -> category lookup from the filenames in rules/ so hyperedges can
    # still be classified as mono/sesqui/common for the viewer's legend filter.
    mapping = {}
    for category, prefix in (("mono", "mono_"), ("sesqui", "sesqui_")):
        for path in glob.glob(os.path.join("rules", f"{prefix}*.gml")):
            try:
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("ruleID"):
                            parts = line.split('"')
                            if len(parts) >= 2:
                                mapping[parts[1]] = category
                            break
            except OSError:
                continue
    return mapping


RULE_CATEGORY_BY_ID = build_rule_category_map()


def hyperedge_category(rule_names):
    categories = {RULE_CATEGORY_BY_ID.get(name, "common") for name in rule_names}
    for preferred in ("mono", "sesqui"):
        if preferred in categories:
            return preferred
    return "common"


def graph_smiles(g):
    # `Graph.smiles` is available on most MOD versions; fall back gracefully.
    try:
        return g.smiles
    except Exception:
        return None


def graph_charge(g):
    # Mirrors simulation.py's overallCharge(), reimplemented here so this
    # script can also run standalone.
    try:
        return sum(int(v.charge) for v in g.vertices)
    except Exception:
        return None


def graph_cycles(g):
    # Mirrors simulation.py's countCycs(), reimplemented here so this script
    # can also run standalone.
    try:
        return g.numEdges - g.numVertices + 1
    except Exception:
        return None


def print_graph(g):
    # Graph.print() returns a tuple of PDF file paths (e.g. "out/0003_g_5.pdf").
    # Render with collapsed hydrogens (matching printer.py) and return the file
    # basename without extension, so the corresponding "<base>.svg" (produced by
    # `mod_post --mode pdfToSvg`, see organize_hypergraph_assets.py / README) can
    # be referenced from the JSON.
    try:
        if moleculePrinter is not None:
            result = g.print(moleculePrinter)
        else:
            result = g.print()
    except Exception:
        try:
            result = g.print()
        except Exception:
            return None

    pdf_path = None
    if isinstance(result, str) and result:
        pdf_path = result
    elif isinstance(result, (list, tuple)) and result:
        pdf_path = result[0]
    if not pdf_path:
        return None

    base = os.path.basename(pdf_path)
    if base.endswith(".pdf"):
        base = base[:-4]
    return base


nodes = []

for v in dg.vertices:
    g = v.graph
    file_prefix = print_graph(g)
    nodes.append({
        "id": f"v{v.id}",
        "name": g.name,
        "smiles": graph_smiles(g),
        "charge": graph_charge(g),
        "cycles": graph_cycles(g),
        "image": f"{file_prefix}.svg" if file_prefix else None,
    })

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
    category = hyperedge_category(rule_names)

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
