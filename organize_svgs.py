import os
import shutil

def main():
    # Target folder
    dest_dir = os.path.join("docs", "img")
    os.makedirs(dest_dir, exist_ok=True)

    print(f"Locating and copying rule DPO SVGs to {dest_dir}...")
    copied_count = 0

    if os.path.isdir("out"):
        for file in os.listdir("out"):
            # Rules always have _L, _K, or _R suffixes
            if file.endswith(("_L.svg", "_K.svg", "_R.svg")):
                src_svg = os.path.join("out", file)
                dest_svg = os.path.join(dest_dir, file)
                shutil.copy2(src_svg, dest_svg)
                print(f"Copied: {src_svg} -> {dest_svg}")
                copied_count += 1

    print(f"\nDone! Successfully copied {copied_count} DPO SVG files to {dest_dir}.")

if __name__ == "__main__":
    main()

