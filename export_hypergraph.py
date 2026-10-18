# EXPORT THE DERIVATION GRAPH AS A JSON HYPERGRAPH FOR THE INTERACTIVE HTML VIEWER
#
# This script must run after simulation.py has built `dg`. It walks the
# derivation graph (a hypergraph: vertices = molecules, hyperedges =
# reactions with possibly several educts/products) and writes
# `out/hypergraph.json`, plus one depiction (PDF) per molecule that
# `organize_hypergraph_assets.py` later converts to SVG and bundles into the
# standalone `report/hypergraph.html` viewer.
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

import progress_utils
from hypergraph_levels import derivation_levels

OUT_DIR = "out"
os.makedirs(OUT_DIR, exist_ok=True)


def build_rule_category_map():
    # Rule.name (used below) may reflect the GML "ruleID" (e.g. "2,6 closure")
    # or the GML filename (e.g. "mono_2_6_Cyc.gml" / "mono_2_6_Cyc"). Build a
    # lookup mapping all of these to their respective category.
    mapping = {}
    for category, prefix in (("mono", "mono_"), ("sesqui", "sesqui_")):
        for path in glob.glob(os.path.join("rules", f"{prefix}*.gml")):
            base = os.path.basename(path)
            mapping[base] = category
            if base.endswith(".gml"):
                mapping[base[:-4]] = category
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
    categories = {RULE_CATEGORY_BY_ID.get(name) for name in rule_names if name in RULE_CATEGORY_BY_ID}
    categories = {c for c in categories if c is not None}
    
    # Fallback to substring matching on rule name
    if not categories:
        for name in rule_names:
            name_lower = name.lower()
            if "mono" in name_lower:
                categories.add("mono")
            elif "sesqui" in name_lower:
                categories.add("sesqui")
            elif "common" in name_lower:
                categories.add("common")
                
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


# Identify roots: starting educts (GPP, FPP, H2O) or nodes with no incoming edges
educt_names = {m.name for m in eductMols} if 'eductMols' in globals() else {"GPP", "FPP", "H2O"}
roots = [v for v in dg.vertices if v.graph.name in educt_names]
if not roots:
    targets_with_incoming = {t.id for e in dg.edges for t in e.targets}
    roots = [v for v in dg.vertices if v.id not in targets_with_incoming]

root_levels = {v.id: 1 if v.graph.name.upper() in ("H2O", "WATER") else 0 for v in roots}
with progress_utils.phase("Computing derivation levels"):
    vertex_iterations = derivation_levels(
        (v.id for v in dg.vertices),
        (([s.id for s in e.sources], [t.id for t in e.targets]) for e in dg.edges),
        root_levels,
        (v.id for v in dg.vertices if v.graph.name.upper() in ("H2O", "WATER")),
    )

# Default any unreachable node to iteration 0
for v in dg.vertices:
    if vertex_iterations[v.id] is None:
        vertex_iterations[v.id] = 0

nodes = []

for v in progress_utils.progress_iter(dg.vertices, desc="Phase 3/4: Rendering molecules (LaTeX/PDF)"):
    g = v.graph
    file_prefix = print_graph(g)
    nodes.append({
        "id": f"v{v.id}",
        "name": g.name,
        "smiles": graph_smiles(g),
        "charge": graph_charge(g),
        "cycles": graph_cycles(g),
        "image": f"{file_prefix}.svg" if file_prefix else None,
        "iteration": vertex_iterations[v.id],
    })

hyperedges = []
for e in progress_utils.progress_iter(dg.edges, desc="Phase 3/4: Exporting reactions (hyperedges)"):
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
        "rootIds": [f"v{v.id}" for v in roots],
    },
    "nodes": nodes,
    "hyperedges": hyperedges,
}

with open(os.path.join(OUT_DIR, "hypergraph.json"), "w") as f:
    json.dump(hypergraph, f, indent=2)

post.summarySection("Interactive Hypergraph Export")
print(f"Wrote {len(nodes)} molecules and {len(hyperedges)} reactions to "
      f"{os.path.join(OUT_DIR, 'hypergraph.json')}")
