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


# Compute shortest-path level (iteration) from initial compounds (roots)
incoming_edges = {v.id: [] for v in dg.vertices}
for e in dg.edges:
    for tgt in e.targets:
        incoming_edges[tgt.id].append(e)

# Identify roots: starting educts (GPP, FPP, H2O) or nodes with no incoming edges
educt_names = {m.name for m in eductMols} if 'eductMols' in globals() else {"GPP", "FPP", "H2O"}
roots = [v for v in dg.vertices if v.graph.name in educt_names]
if not roots:
    roots = [v for v in dg.vertices if not incoming_edges[v.id]]

vertex_iterations = {v.id: None for v in dg.vertices}
for r in roots:
    vertex_iterations[r.id] = 0

# BFS-style level propagation
changed = True
while changed:
    changed = False
    for e in dg.edges:
        if e.sources and all(vertex_iterations[src.id] is not None for src in e.sources):
            src_levels = [vertex_iterations[src.id] for src in e.sources]
            level = max(src_levels) + 1
            for tgt in e.targets:
                if vertex_iterations[tgt.id] is None or level < vertex_iterations[tgt.id]:
                    vertex_iterations[tgt.id] = level
                    changed = True

# Default any unreachable node to iteration 0
for v in dg.vertices:
    if vertex_iterations[v.id] is None:
        vertex_iterations[v.id] = 0

nodes = []

for v in progress_utils.progress_iter(dg.vertices, desc="Fase 3/4: Renderizando moleculas (LaTeX/PDF)"):
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
for e in progress_utils.progress_iter(dg.edges, desc="Fase 3/4: Exportando reacoes (hiperarestas)"):
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
