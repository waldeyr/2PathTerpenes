#!/usr/bin/env python3
"""Maintain the durable status record for a pipeline run.

The shell runner invokes this tiny standard-library-only helper before and
after every stage. Writes are atomic, so `status.json` is always readable by a
monitoring shell or another process.
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_status(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {"stages": {}}


def write_status(path, status):
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".status-", suffix=".json", dir=directory)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(status, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        os.unlink(temporary)
        raise


def init(args):
    status = {
        "runId": args.run_id,
        "mode": args.mode,
        "simulationScript": args.simulation_script,
        "image": args.image,
        "gitCommit": args.git_commit,
        "gitDirty": args.git_dirty == "true",
        "pid": args.pid,
        "startedAt": now(),
        "status": "running",
        "stages": {},
    }
    write_status(args.status_file, status)


def stage(args):
    status = read_status(args.status_file)
    entry = status.setdefault("stages", {}).setdefault(args.name, {})
    entry["status"] = args.stage_status
    entry["updatedAt"] = now()
    if args.log:
        entry["log"] = args.log
    if args.stage_status == "running":
        entry["startedAt"] = entry["updatedAt"]
    if args.stage_status in {"completed", "failed"}:
        entry["finishedAt"] = entry["updatedAt"]
    if args.message:
        entry["message"] = args.message
    if args.exit_code is not None:
        entry["exitCode"] = args.exit_code
    if args.stage_status == "failed":
        status["status"] = "failed"
        status["failedStage"] = args.name
        status["finishedAt"] = entry["updatedAt"]
    write_status(args.status_file, status)


def finish(args):
    status = read_status(args.status_file)
    status["status"] = args.run_status
    status["finishedAt"] = now()
    if args.message:
        status["message"] = args.message
    if args.exit_code is not None:
        status["exitCode"] = args.exit_code
    write_status(args.status_file, status)


def preflight(args):
    if not shutil.which("docker"):
        raise SystemExit("docker is not available")
    subprocess.run(["docker", "image", "inspect", args.image], check=True, stdout=subprocess.DEVNULL)
    if args.min_free_gib < 0:
        raise SystemExit("MIN_FREE_GIB must be a non-negative integer")
    available = shutil.disk_usage(args.run_dir).free
    if available < args.min_free_gib * 1024**3:
        raise SystemExit(f"Insufficient free space in {args.run_dir}: need {args.min_free_gib} GiB, have {available // 1024**3} GiB")
    probe = None
    try:
        with tempfile.NamedTemporaryFile(dir=args.run_dir, prefix=".preflight-", delete=False) as handle:
            probe = handle.name
            handle.write(b"write-check\n")
    finally:
        if probe is not None:
            os.unlink(probe)
    print(f"Preflight passed: image={args.image}, free-space={available // 1024**3} GiB at {args.run_dir}.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--status-file", required=True)
    init_parser.add_argument("--run-id", required=True)
    init_parser.add_argument("--mode", required=True)
    init_parser.add_argument("--simulation-script", required=True)
    init_parser.add_argument("--image", required=True)
    init_parser.add_argument("--git-commit", required=True)
    init_parser.add_argument("--git-dirty", choices=("true", "false"), required=True)
    init_parser.add_argument("--pid", type=int)
    init_parser.set_defaults(func=init)

    stage_parser = subparsers.add_parser("stage")
    stage_parser.add_argument("--status-file", required=True)
    stage_parser.add_argument("--name", required=True)
    stage_parser.add_argument("--stage-status", choices=("running", "completed", "failed"), required=True)
    stage_parser.add_argument("--log")
    stage_parser.add_argument("--message")
    stage_parser.add_argument("--exit-code", type=int)
    stage_parser.set_defaults(func=stage)

    finish_parser = subparsers.add_parser("finish")
    finish_parser.add_argument("--status-file", required=True)
    finish_parser.add_argument("--run-status", choices=("completed", "failed"), required=True)
    finish_parser.add_argument("--message")
    finish_parser.add_argument("--exit-code", type=int)
    finish_parser.set_defaults(func=finish)

    preflight_parser = subparsers.add_parser("preflight")
    preflight_parser.add_argument("--image", required=True)
    preflight_parser.add_argument("--run-dir", required=True)
    preflight_parser.add_argument("--min-free-gib", type=int, required=True)
    preflight_parser.set_defaults(func=preflight)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
