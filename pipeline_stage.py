#!/usr/bin/env python3
"""Run a stage with durable logs, independent heartbeats and signal cleanup."""

import argparse
import math
import os
import selectors
import signal
import subprocess
import sys
import time

from progress_utils import update_progress


class Interrupted(Exception):
    def __init__(self, signum):
        self.signum = signum


def interrupt(signum, _frame):
    raise Interrupted(signum)


def stop_process_group(process):
    """Terminate only the command and descendants created for this stage."""
    for signum in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, signum)
        except ProcessLookupError:
            return
        if signum == signal.SIGTERM:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                continue
        else:
            process.wait()
    # A command may have exited before its children; the second signal above
    # still cleans up descendants that kept the process group alive.


def positive_seconds(value):
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("heartbeat interval must be positive and finite")
    return seconds


def write_all(stream, data):
    """Raw log files can return a short write, for example on a full disk."""
    remaining = memoryview(data)
    while remaining:
        written = stream.write(remaining)
        if written is None or written <= 0:
            raise OSError("Could not write all stage output")
        remaining = remaining[written:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--pipeline-log", required=True)
    parser.add_argument("--progress-file", required=True)
    parser.add_argument("--heartbeat-seconds", type=positive_seconds, default=30)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("a stage command is required")

    for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, interrupt)

    process = None
    started = time.monotonic()
    exit_code = 1
    try:
        update_progress(args.progress_file, stage=args.name, stageStatus="running", status="running",
                        description=args.name, current=None, total=None, stageElapsedSeconds=0,
                        exitCode=None, heartbeatAt=None, phaseUpdatedAt=None)
        with open(args.log, "ab", buffering=0) as stage_log, open(args.pipeline_log, "ab", buffering=0) as pipeline_log:
            def emit(data):
                # A logging or console error is a stage failure, not a success
                # with missing diagnostics. The shell's EXIT handler records it.
                write_all(stage_log, data)
                write_all(pipeline_log, data)
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()

            environment = dict(os.environ, PYTHONUNBUFFERED="1", PIPELINE_PROGRESS_FILE=args.progress_file)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       env=environment, start_new_session=True)
            next_heartbeat = time.monotonic() + args.heartbeat_seconds
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while selector.get_map() or process.poll() is None:
                    timeout = max(0, next_heartbeat - time.monotonic())
                    for key, _mask in selector.select(timeout):
                        data = os.read(key.fd, 65536)
                        if data:
                            emit(data)
                        else:
                            selector.unregister(key.fileobj)
                    if time.monotonic() >= next_heartbeat:
                        elapsed = round(time.monotonic() - started, 1)
                        progress = update_progress(args.progress_file, stageElapsedSeconds=elapsed,
                                                   heartbeatAt=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
                        description = progress.get("description", args.name)
                        emit(f"[heartbeat] {args.name}: {elapsed:.1f}s; {description}\n".encode())
                        next_heartbeat = time.monotonic() + args.heartbeat_seconds
            result = process.wait()
            exit_code = result if result >= 0 else 128 - result
    except Interrupted as error:
        exit_code = 128 + error.signum
        print(f"Stage {args.name} interrupted by {signal.Signals(error.signum).name}", file=sys.stderr, flush=True)
    except (OSError, ValueError) as error:
        print(f"Stage {args.name} failed: {error}", file=sys.stderr, flush=True)
    finally:
        # Ignore repeated signals while cleaning up our own child process group.
        for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            signal.signal(signum, signal.SIG_IGN)
        if process is not None:
            if exit_code != 0:
                stop_process_group(process)
            if process.stdout is not None:
                process.stdout.close()
        outcome = "completed" if exit_code == 0 else "failed"
        try:
            update_progress(args.progress_file, status=outcome, stageStatus=outcome,
                            stageElapsedSeconds=round(time.monotonic() - started, 1), exitCode=exit_code)
        except (OSError, ValueError) as error:
            print(f"Could not save final progress: {error}", file=sys.stderr, flush=True)
            if exit_code == 0:
                exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
