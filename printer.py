import progress_utils
from report_policy import should_render_pdf_report

# Helper para compatibilidade com versões antigas (0.8.0) e novas (1.0+) de MØD
try:
    from mod import DGPrinter
    try:
        from mod import post
        if not hasattr(post, 'summarySection'):
            raise ImportError
    except ImportError:
        try:
            from mod import postSection as legacyPostSection
            class PostCompat:
                @staticmethod
                def summarySection(heading):
                    legacyPostSection(heading)
            post = PostCompat
        except ImportError:
            class PostDummy:
                @staticmethod
                def summarySection(heading):
                    pass
            post = PostDummy
except ImportError:
    pass

######################################
# PDF PRINTER
######################################
p = DGPrinter()
# print molecule with all the hydrogenes attached
p.graphPrinter.collapseHydrogens = True
p.graphPrinter.withIndex = False

# Callback compatível com ambas as assinaturas:
# MØD v0.8.0: lambda g, dg: ...
# MØD v1.0.0+: lambda v: ...
def vertex_colour_cb(*args):
    g = args[0] if len(args) == 2 else args[0].graph
    return "red" if overallCharge(g) != 0 else "black" if countCycs(g) > 0 else "black"

p.pushVertexColour(vertex_colour_cb)

post.summarySection("Plant Monoterpenes Biosynthesis")

# ``dg.print`` asks Graphviz/neato to lay out the complete derivation graph.
# This is separate from the molecule depictions queued by export_hypergraph.py
# for the interactive report. Apply a configurable precautionary size limit.
# ``DG.vertices``/``DG.edges`` are iterable in both supported MØD APIs, while
# some older bindings do not expose ``len`` on their proxy collections.
vertex_count = sum(1 for _ in dg.vertices)
edge_count = sum(1 for _ in dg.edges)
render_pdf, message = should_render_pdf_report(vertex_count, edge_count)
print(message, flush=True)
if render_pdf:
    with progress_utils.phase("Phase 4/4: Generating PDF/LaTeX report (summary.pdf)"):
        dg.print(p)
else:
    # MØD compiles the queued per-molecule PDFs after Python exits. Keep the
    # heartbeat truthful while that potentially long post-processing runs.
    progress_utils.update_progress(
        progress_utils.PROGRESS_FILE,
        description="Compiling molecule depictions (monolithic graph PDF skipped)",
        status="running", current=None, total=None,
    )

