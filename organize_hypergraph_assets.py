import json
import os
import shutil


def main():
    out_dir = "out"
    data_dir = os.path.join("docs", "data")
    img_dir = os.path.join("docs", "img", "molecules")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    hypergraph_path = os.path.join(out_dir, "hypergraph.json")
    if not os.path.isfile(hypergraph_path):
        print(f"No {hypergraph_path} found. Run export_hypergraph.py first.")
        return

    with open(hypergraph_path) as f:
        hypergraph = json.load(f)

    copied = 0
    for node in hypergraph.get("nodes", []):
        image = node.get("image")
        if not image:
            continue
        src_svg = os.path.join(out_dir, image)
        if os.path.isfile(src_svg):
            dest_svg = os.path.join(img_dir, image)
            shutil.copy2(src_svg, dest_svg)
            node["image"] = f"img/molecules/{image}"
            copied += 1
        else:
            print(f"Missing depiction: {src_svg}")
            node["image"] = None

    dest_json = os.path.join(data_dir, "hypergraph.json")
    with open(dest_json, "w") as f:
        json.dump(hypergraph, f, indent=2)

    print(f"Copied {copied} molecule depictions to {img_dir}.")
    print(f"Wrote {dest_json} for docs/hypergraph.html.")


if __name__ == "__main__":
    main()
