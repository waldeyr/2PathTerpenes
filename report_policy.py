"""Guardrails for the optional MØD derivation-graph PDF report.

The interactive hypergraph export renders molecule depictions separately. The
monolithic ``DGPrinter`` report is optional, and its Graphviz layout must be
bounded: force-directed layout becomes impractical for very large networks.
"""

import os


DEFAULT_MAX_VERTICES = 5_000
DEFAULT_MAX_EDGES = 10_000


def _positive_int(value, name, default):
    if value is None or value == "":
        return default
    try:
        result = int(value)
    except ValueError as error:
        raise ValueError(f"{name} must be a positive integer") from error
    if result < 1:
        raise ValueError(f"{name} must be a positive integer")
    return result


def _enabled(value, name):
    normalized = str(value or "").strip().lower()
    if normalized in {"", "0", "false", "no", "off"}:
        return False
    if normalized in {"1", "true", "yes", "on"}:
        return True
    raise ValueError(f"{name} must be a boolean (0/1, false/true, no/yes, off/on)")


def pdf_report_limits(environment=None):
    """Return the configured vertex/edge limits and the explicit override."""
    environment = os.environ if environment is None else environment
    return (
        _positive_int(environment.get("PDF_REPORT_MAX_VERTICES"),
                      "PDF_REPORT_MAX_VERTICES", DEFAULT_MAX_VERTICES),
        _positive_int(environment.get("PDF_REPORT_MAX_EDGES"),
                      "PDF_REPORT_MAX_EDGES", DEFAULT_MAX_EDGES),
        _enabled(environment.get("FORCE_PDF_REPORT"), "FORCE_PDF_REPORT"),
    )


def should_render_pdf_report(vertex_count, edge_count, environment=None):
    """Decide whether ``DGPrinter`` may layout the complete graph.

    Returns ``(allowed, message)``. ``FORCE_PDF_REPORT=1`` is deliberately
    explicit because it can demand substantial CPU time and memory.
    """
    max_vertices, max_edges, force = pdf_report_limits(environment)
    if force:
        return True, "FORCE_PDF_REPORT is enabled"
    if vertex_count > max_vertices or edge_count > max_edges:
        return False, (
            "Skipping monolithic derivation-graph PDF: "
            f"{vertex_count} vertices and {edge_count} edges exceed the "
            f"configured limits ({max_vertices} vertices, {max_edges} edges). "
            "The interactive hypergraph export remains enabled. Set "
            "FORCE_PDF_REPORT=1 only for a deliberate, separately sized run."
        )
    return True, (
        f"Generating monolithic derivation-graph PDF for {vertex_count} "
        f"vertices and {edge_count} edges."
    )
