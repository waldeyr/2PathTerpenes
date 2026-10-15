#!/usr/bin/env python3
"""Validate the hand-off artifacts produced by each pipeline stage."""

import argparse
import json
import os
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class ReportHTML(HTMLParser):
    """Read the embedded graph and the local assets required by the viewer."""

    def __init__(self):
        super().__init__()
        self.data_blocks = []
        self.assets = []
        self._data = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("id") == "hg-data":
            if attrs.get("type") != "application/json":
                raise ValueError("hg-data must be an application/json script")
            self._data = []
            self.data_blocks.append(self._data)
        if tag in ("script", "img") and attrs.get("src"):
            self.assets.append(attrs["src"])
        if tag == "link" and "stylesheet" in attrs.get("rel", "").split():
            if attrs.get("href"):
                self.assets.append(attrs["href"])

    def handle_data(self, data):
        if self._data is not None:
            self._data.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self._data = None


def require_file(path):
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        raise ValueError(f"Missing or empty file: {path}")


def validate_graph(hypergraph):
    if not isinstance(hypergraph, dict):
        raise ValueError("Hypergraph must be a JSON object")
    nodes = hypergraph.get("nodes")
    edges = hypergraph.get("hyperedges")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("Hypergraph has no nodes")
    if not isinstance(edges, list) or not edges:
        raise ValueError("Hypergraph has no hyperedges")
    for collection, name in ((nodes, "node"), (edges, "hyperedge")):
        ids = []
        for entry in collection:
            if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"]:
                raise ValueError(f"Invalid {name} ID")
            ids.append(entry["id"])
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate {name} IDs")
    node_ids = {node["id"] for node in nodes}
    for edge in edges:
        for side in ("sources", "targets"):
            refs = edge.get(side)
            if not isinstance(refs, list) or not refs:
                raise ValueError(f"Hyperedge {edge['id']} has no {side}")
            if any(not isinstance(ref, str) or ref not in node_ids for ref in refs):
                raise ValueError(f"Hyperedge {edge['id']} references an unknown node")


def load_hypergraph(run_dir):
    path = os.path.join(run_dir, "out", "hypergraph.json")
    if not os.path.isfile(path):
        raise ValueError(f"Missing hypergraph export: {path}")
    with open(path, encoding="utf-8") as handle:
        hypergraph = json.load(handle)
    validate_graph(hypergraph)
    return hypergraph


def images(hypergraph):
    result = []
    for node in hypergraph["nodes"]:
        image = node.get("image")
        if not image:
            raise ValueError(f"Node {node.get('id')} has no image reference")
        if not isinstance(image, str) or os.path.basename(image) != image or not image.endswith(".svg"):
            raise ValueError(f"Invalid image reference: {image!r}")
        result.append(image)
    if len(result) != len(set(result)):
        raise ValueError("Duplicate image references in hypergraph.json")
    return result


def validate_report(report_dir, hypergraph):
    html_path = os.path.join(report_dir, "hypergraph.html")
    require_file(html_path)
    parser = ReportHTML()
    with open(html_path, encoding="utf-8") as handle:
        parser.feed(handle.read())
    parser.close()
    if len(parser.data_blocks) != 1:
        raise ValueError("Report must contain exactly one hg-data script")
    embedded = json.loads("".join(parser.data_blocks[0]))
    validate_graph(embedded)

    # Packaging may rewrite only image paths, not the network or its metadata.
    expected = dict(hypergraph)
    expected["nodes"] = [dict(node, image=f"img/molecules/{node['image']}") for node in hypergraph["nodes"]]
    if embedded != expected:
        raise ValueError("Embedded hypergraph differs from out/hypergraph.json")

    required = {
        "css/style.css", "css/hypergraph.css", "javascript/d3.v7.min.js",
        "javascript/hypergraph.js", "img/2PathLogo.png",
    }
    if not required.issubset(parser.assets):
        raise ValueError("Report does not reference all required CSS, JavaScript and logo assets")

    for relative in parser.assets + [node["image"] for node in embedded["nodes"]]:
        url = urlsplit(relative)
        if url.scheme or url.netloc or url.path.startswith("/"):
            raise ValueError(f"Report asset is not a local relative path: {relative}")
        target = (Path(report_dir) / unquote(url.path)).resolve()
        if Path(report_dir).resolve() not in target.parents:
            raise ValueError(f"Report asset escapes the package: {relative}")
        require_file(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--stage", choices=("simulation", "assets", "report"), required=True)
    parser.add_argument("--report-dir", default="report")
    args = parser.parse_args()

    hypergraph = load_hypergraph(args.run_dir)
    referenced = images(hypergraph)
    print(f"Validated graph structure: {len(hypergraph['nodes'])} nodes, {len(hypergraph['hyperedges'])} hyperedges.")

    if args.stage == "simulation":
        return

    out_dir = os.path.join(args.run_dir, "out")
    for name in referenced:
        require_file(os.path.join(out_dir, name))
    print(f"Validated SVG assets: {len(referenced)} present.")

    if args.stage == "assets":
        return

    report_dir = os.path.join(args.run_dir, args.report_dir)
    validate_report(report_dir, hypergraph)
    print(f"Validated standalone report: {report_dir}/hypergraph.html with {len(referenced)} SVGs.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Pipeline validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
