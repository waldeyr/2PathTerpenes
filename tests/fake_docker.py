"""Docker contract fixture: emit a small graph or run the real SVG converter.

No daemon, network or MØD installation is needed for orchestration regressions.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    args = sys.argv[1:]
    mode = os.environ.get("FAKE_DOCKER_MODE", "success")
    if args[:2] == ["image", "inspect"]:
        if mode == "break-log":
            run_dir = Path(os.environ["RUNS_DIR"]) / os.environ["FAKE_RUN_ID"]
            (run_dir / "logs" / "simulation.log").mkdir()
        if mode == "break-pipeline-log":
            run_dir = Path(os.environ["RUNS_DIR"]) / os.environ["FAKE_RUN_ID"]
            log = run_dir / "logs" / "pipeline.log"
            log.unlink()
            log.mkdir()
        return 0
    assert args.pop(0) == "run"
    mounts = {}
    container_env = {}
    entrypoint = None
    workdir = None
    while args and args[0].startswith("--"):
        option = args.pop(0)
        if option == "--rm":
            continue
        value = args.pop(0)
        if option == "--volume":
            host, target, *_permissions = value.split(":")
            mounts[target] = host
        elif option == "--env":
            name, value = value.split("=", 1)
            container_env[name] = value
        elif option == "--entrypoint":
            entrypoint = value
        elif option == "--workdir":
            workdir = value
    args.pop(0)  # image
    with open(os.environ["FAKE_DOCKER_CALLS"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"mounts": mounts, "workdir": workdir, "args": args}) + "\n")

    if mode == "failure":
        print("Simulated simulation failure", flush=True)
        return 7
    if mode == "block":
        sys.path.insert(0, mounts["/workspace"])
        from progress_utils import _write_progress
        _write_progress("Native kernel fixture", current=3, total=100)
        Path(os.environ["FAKE_DOCKER_MARKER"]).write_text(str(os.getpid()))
        print("Simulated native kernel is busy", flush=True)
        time.sleep(120)
        return 0

    run_dir = Path(mounts["/run"])
    if entrypoint:
        assert entrypoint == "python"
        script = args[0].replace("/workspace", mounts["/workspace"], 1)
        environment = dict(os.environ)
        for name, value in container_env.items():
            for target in sorted(mounts, key=len, reverse=True):
                if value == target or value.startswith(target + "/"):
                    value = mounts[target] + value[len(target):]
                    break
            environment[name] = value
        return subprocess.call([sys.executable, script] + args[1:], cwd=run_dir, env=environment)

    out = run_dir / "out"
    out.mkdir()
    graph = {
        "meta": {"title": "Fixture graph"},
        "nodes": [{"id": "v0", "name": "A", "image": "001_g_0.svg"},
                  {"id": "v1", "name": "B", "image": "002_g_1.svg"}],
        "hyperedges": [{"id": "e0", "sources": ["v0"], "targets": ["v1"]}],
    }
    (out / "hypergraph.json").write_text(json.dumps(graph))
    for node in graph["nodes"]:
        (out / node["image"].replace(".svg", ".pdf")).write_bytes(b"%PDF-fixture")
    (out / "unreferenced.pdf").write_bytes(b"%PDF-not-for-the-viewer")
    print("Exported fixture: 2 nodes and 1 reaction", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
