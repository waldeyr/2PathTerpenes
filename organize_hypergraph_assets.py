import json
import os
import re
import shutil
import sys

# Ensure the script's directory is in the path to find local helper modules
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
except FileNotFoundError:
    sys.path.insert(0, '')

import progress_utils
from validate_pipeline import images, validate_graph, validate_svg


def main():
    # The pipeline provides isolated per-run directories through these
    # variables. Defaults retain compatibility with the documented manual use.
    out_dir = os.environ.get("OUTPUT_DIR", "out")
    report_dir = os.environ.get("REPORT_DIR", "report")
    source_dir = os.path.dirname(os.path.abspath(__file__))

    hypergraph_path = os.path.join(out_dir, "hypergraph.json")
    if not os.path.isfile(hypergraph_path):
        raise FileNotFoundError(f"No {hypergraph_path} found. Run export_hypergraph.py first.")

    with open(hypergraph_path) as f:
        hypergraph = json.load(f)

    validate_graph(hypergraph)
    for image in images(hypergraph):
        validate_svg(os.path.join(out_dir, image))
    build_report_package(report_dir, source_dir)

    img_dir = os.path.join(report_dir, "img", "molecules")
    os.makedirs(img_dir, exist_ok=True)
    copied = 0
    for node in progress_utils.progress_iter(hypergraph.get("nodes", []), desc="Copying SVG depictions to report/"):
        image = node.get("image")
        src_svg = os.path.join(out_dir, image)
        dest_svg = os.path.join(img_dir, image)
        shutil.copy2(src_svg, dest_svg)
        node["image"] = f"img/molecules/{image}"
        copied += 1

    embed_data_in_html(hypergraph, report_dir)

    print(f"Copied {copied} molecule depictions to {img_dir}.")
    print(f"Built standalone report in {report_dir}/hypergraph.html.")


def build_report_package(report_dir, source_dir=None):
    """Assemble a standalone report/ folder with everything hypergraph.html
    needs, so it can be zipped and shared and opened directly via file://
    without a server."""
    source_dir = source_dir or os.path.dirname(os.path.abspath(__file__))
    # Refuse to overwrite a prior package; a failed build remains inspectable.
    os.makedirs(report_dir, exist_ok=False)

    shutil.copy2(os.path.join(source_dir, "report_template", "hypergraph.html"), os.path.join(report_dir, "hypergraph.html"))

    for rel_file in [
        os.path.join("report_template", "css", "hypergraph.css"),
        os.path.join("report_template", "javascript", "d3.v7.min.js"),
        os.path.join("report_template", "javascript", "hypergraph.js"),
    ]:
        dest = os.path.join(report_dir, os.path.relpath(rel_file, "report_template"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(source_dir, rel_file), dest)

    for rel_file in [
        os.path.join("css", "style.css"),
        os.path.join("img", "2PathLogo.png"),
    ]:
        src = os.path.join(source_dir, "docs", rel_file)
        dest = os.path.join(report_dir, rel_file)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)


def embed_data_in_html(hypergraph, report_dir):
    """Embed the hypergraph data inline in report/hypergraph.html so the page
    works when opened directly via file:// (fetch() of a separate JSON file
    is blocked by the browser in that case)."""
    html_path = os.path.join(report_dir, "hypergraph.html")

    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    embedded = json.dumps(hypergraph).replace("<", "\\u003c")
    pattern = r'(<script type="application/json" id="hg-data">)(.*?)(</script>)'
    new_html, count = re.subn(pattern, lambda m: m.group(1) + embedded + m.group(3), html, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"Could not embed hypergraph data in {html_path}")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_html)


if __name__ == "__main__":
    main()
