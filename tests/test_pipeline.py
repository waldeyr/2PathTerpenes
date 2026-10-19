"""Regression tests for validation, logging, heartbeats, signals and run paths."""

import contextlib
import copy
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import organize_hypergraph_assets as package
import progress_utils
from report_policy import should_render_pdf_report
from validate_pipeline import validate_report
from pipeline_stage import write_all


class LogWriteTests(unittest.TestCase):
    def test_short_writes_are_completed(self):
        data = bytearray()

        def short_write(chunk):
            data.extend(chunk[:2])
            return len(chunk[:2])

        stream = mock.Mock()
        stream.write.side_effect = short_write
        write_all(stream, b"complete log")
        self.assertEqual(data, b"complete log")

    def test_zero_write_is_a_failure(self):
        stream = mock.Mock()
        stream.write.return_value = 0
        with self.assertRaises(OSError):
            write_all(stream, b"must not be lost")


class PdfReportPolicyTests(unittest.TestCase):
    def test_small_graph_keeps_pdf_report(self):
        allowed, message = should_render_pdf_report(5_000, 10_000, {})
        self.assertTrue(allowed)
        self.assertIn("Generating", message)

    def test_oversized_graph_skips_only_monolithic_pdf(self):
        allowed, message = should_render_pdf_report(48_639, 122_770, {})
        self.assertFalse(allowed)
        self.assertIn("interactive hypergraph export remains enabled", message)

    def test_force_flag_requires_deliberate_opt_in(self):
        allowed, message = should_render_pdf_report(
            48_639, 122_770, {"FORCE_PDF_REPORT": "1"})
        self.assertTrue(allowed)
        self.assertIn("FORCE_PDF_REPORT", message)

    def test_invalid_limit_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "PDF_REPORT_MAX_EDGES"):
            should_render_pdf_report(1, 1, {"PDF_REPORT_MAX_EDGES": "0"})

    def test_invalid_force_flag_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "FORCE_PDF_REPORT"):
            should_render_pdf_report(1, 1, {"FORCE_PDF_REPORT": "maybe"})


class ReportValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="2path-report-test-")
        self.addCleanup(self.temporary.cleanup)
        self.run_dir = Path(self.temporary.name)
        self.out = self.run_dir / "out"
        self.report = self.run_dir / "report"
        self.out.mkdir()
        self.graph = {
            "meta": {"title": "Fixture"},
            "nodes": [{"id": "v0", "name": "</script>", "image": "001_g_0.svg"}],
            "hyperedges": [{"id": "e0", "sources": ["v0"], "targets": ["v0"]}],
        }
        (self.out / "hypergraph.json").write_text(json.dumps(self.graph))
        (self.out / "001_g_0.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        with mock.patch.dict(os.environ, OUTPUT_DIR=str(self.out), REPORT_DIR=str(self.report)), \
             mock.patch.object(progress_utils, "tqdm", None), contextlib.redirect_stdout(io.StringIO()):
            package.main()

    def replace_embedded(self, data):
        html_path = self.report / "hypergraph.html"
        html = html_path.read_text()
        html = re.sub(r'(<script type="application/json" id="hg-data">).*?(</script>)',
                      lambda match: match[1] + json.dumps(data) + match[2], html, flags=re.S)
        html_path.write_text(html)

    def test_valid_offline_package_and_escaped_script_content(self):
        validate_report(self.report, self.graph)
        self.assertNotIn('"name": "</script>"', (self.report / "hypergraph.html").read_text())

    def test_empty_embedded_graph_is_rejected(self):
        self.replace_embedded({"nodes": [], "hyperedges": []})
        with self.assertRaisesRegex(ValueError, "no nodes"):
            validate_report(self.report, self.graph)

    def test_changed_data_is_rejected_even_with_same_counts(self):
        changed = copy.deepcopy(self.graph)
        changed["nodes"][0].update(name="wrong graph", image="img/molecules/001_g_0.svg")
        self.replace_embedded(changed)
        with self.assertRaisesRegex(ValueError, "differs"):
            validate_report(self.report, self.graph)

    def test_invalid_embedded_json_is_rejected(self):
        html = self.report / "hypergraph.html"
        html.write_text(html.read_text().replace('"meta":', '"meta":invalid,'))
        with self.assertRaises(ValueError):
            validate_report(self.report, self.graph)

    def test_missing_or_empty_runtime_assets_are_rejected(self):
        for name in ("css/style.css", "css/hypergraph.css", "javascript/d3.v7.min.js",
                     "javascript/hypergraph.js", "img/2PathLogo.png", "img/molecules/001_g_0.svg"):
            with self.subTest(name=name):
                path = self.report / name
                content = path.read_bytes()
                path.write_bytes(b"")
                with self.assertRaisesRegex(ValueError, "Missing or empty"):
                    validate_report(self.report, self.graph)
                path.unlink()
                with self.assertRaisesRegex(ValueError, "Missing or empty"):
                    validate_report(self.report, self.graph)
                path.write_bytes(content)

    def test_truncated_packaged_svg_is_rejected(self):
        image = self.report / "img" / "molecules" / "001_g_0.svg"
        image.write_text("<svg><path")
        with self.assertRaisesRegex(ValueError, "Invalid or truncated SVG"):
            validate_report(self.report, self.graph)

    def test_unlinked_runtime_script_is_rejected(self):
        html = self.report / "hypergraph.html"
        html.write_text(html.read_text().replace('src="javascript/hypergraph.js"', 'src="other.js"'))
        with self.assertRaisesRegex(ValueError, "does not reference"):
            validate_report(self.report, self.graph)

    def test_external_dependency_is_rejected(self):
        html = self.report / "hypergraph.html"
        html.write_text(html.read_text().replace('</body>', '<script src="https://example.org/x.js"></script></body>'))
        with self.assertRaisesRegex(ValueError, "not a local relative"):
            validate_report(self.report, self.graph)

    def test_duplicate_data_block_is_rejected(self):
        html = self.report / "hypergraph.html"
        html.write_text(html.read_text() + '<script id="hg-data" type="application/json">{}</script>')
        with self.assertRaisesRegex(ValueError, "exactly one"):
            validate_report(self.report, self.graph)

    def test_builder_preserves_existing_package(self):
        sentinel = self.report / "keep.txt"
        sentinel.write_text("preserve")
        with self.assertRaises(FileExistsError):
            package.build_report_package(self.report)
        self.assertEqual(sentinel.read_text(), "preserve")


class PipelineExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="2path-run-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = self.base / "project"
        self.project.mkdir()
        for name in ("run-pipeline.sh", "pipeline_stage.py", "pipeline_status.py", "progress_utils.py",
                     "validate_pipeline.py", "convert_hypergraph_svgs.py", "compile_molecule_pdfs.py",
                     "organize_hypergraph_assets.py",
                     "simulation.py", "simulation-full.py", "report_policy.py", "lmodern.sty"):
            shutil.copy2(ROOT / name, self.project / name)
        for name in ("docs", "rules", "report_template"):
            shutil.copytree(ROOT / name, self.project / name)
        self.binaries = self.base / "bin"
        self.binaries.mkdir()
        fake = self.binaries / "docker"
        fake.write_text(f'#!{sys.executable}\nimport runpy\nrunpy.run_path({str(ROOT / "tests" / "fake_docker.py")!r}, run_name="__main__")\n')
        fake.chmod(0o755)
        mod_post = self.binaries / "mod_post"
        mod_post.write_text(f'#!{sys.executable}\nimport sys\nfrom pathlib import Path\nPath(sys.argv[-1] + ".svg").write_text(\'<svg xmlns="http://www.w3.org/2000/svg"/>\')\n')
        mod_post.chmod(0o755)
        self.runs = self.base / "external runs"
        self.calls = self.base / "docker-calls.jsonl"
        self.marker = self.base / "started"
        self.env = dict(os.environ, PATH=str(self.binaries) + os.pathsep + os.environ["PATH"],
                        RUNS_DIR=str(self.runs), MIN_FREE_GIB="0", HEARTBEAT_SECONDS="0.1",
                        FAKE_RUN_ID="regression", FAKE_DOCKER_CALLS=str(self.calls),
                        FAKE_DOCKER_MARKER=str(self.marker))
        self.env.pop("FAKE_DOCKER_MODE", None)
        for name in ('PDF_REPORT_MAX_VERTICES', 'PDF_REPORT_MAX_EDGES', 'FORCE_PDF_REPORT'):
            self.env.pop(name, None)

    @property
    def run_dir(self):
        return self.runs / "regression"

    def command(self):
        return ["bash", str(self.project / "run-pipeline.sh"), "--smoke", "--run-id", "regression"]

    def execute(self, mode="success"):
        return subprocess.run(self.command(), env=dict(self.env, FAKE_DOCKER_MODE=mode),
                              cwd=self.base, capture_output=True, text=True, timeout=15)

    def status(self):
        return json.loads((self.run_dir / "status.json").read_text())

    def test_full_orchestration_with_external_run_directory(self):
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.status()["status"], "completed")
        self.assertTrue(all(stage["status"] == "completed" for stage in self.status()["stages"].values()))
        self.assertFalse((self.run_dir / "report.tmp").exists())
        self.assertTrue((self.run_dir / "report" / "hypergraph.html").is_file())
        self.assertEqual(len(list((self.run_dir / "report" / "img" / "molecules").glob("*.svg"))), 2)
        self.assertFalse((self.run_dir / "out" / "unreferenced.svg").exists())
        calls = [json.loads(line) for line in self.calls.read_text().splitlines()]
        self.assertEqual(len(calls), 3)
        for call in calls:
            self.assertEqual(call["mounts"]["/run"], str(self.run_dir.resolve()))
            self.assertEqual(call["workdir"], "/run")
            self.assertEqual(call["env"]["HOME"], "/tmp")
            self.assertEqual(call["env"]["XDG_CACHE_HOME"], "/tmp/.cache")
            self.assertEqual(call["env"]["PDF_REPORT_MAX_VERTICES"], "5000")
            self.assertEqual(call["env"]["PDF_REPORT_MAX_EDGES"], "10000")
            self.assertEqual(call["env"]["MOD_NUM_POST_THREADS"], "2")
        validate_report(self.run_dir / "report", json.loads((self.run_dir / "out" / "hypergraph.json").read_text()))

    def test_relative_runs_directory_from_another_working_directory(self):
        self.env["RUNS_DIR"] = "external runs"
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.status()["status"], "completed")

    def test_nonzero_command_exit_is_recorded(self):
        result = self.execute("failure")
        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        self.assertEqual(self.status()["status"], "failed")
        self.assertEqual(self.status()["failedStage"], "simulation")
        self.assertEqual(self.status()["exitCode"], 7)
        self.assertFalse((self.run_dir / "report").exists())

    def test_invalid_pdf_limit_fails_before_simulation(self):
        self.env['PDF_REPORT_MAX_VERTICES'] = 'oops'
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.status()['failedStage'], 'preflight')
        self.assertFalse(self.calls.exists())

    def test_invalid_force_flag_fails_before_simulation(self):
        self.env['FORCE_PDF_REPORT'] = 'maybe'
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.status()['failedStage'], 'preflight')
        self.assertFalse(self.calls.exists())

    def test_custom_pdf_limits_reach_container(self):
        self.env.update(PDF_REPORT_MAX_VERTICES='123', PDF_REPORT_MAX_EDGES='456', FORCE_PDF_REPORT='1')
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = [json.loads(line) for line in self.calls.read_text().splitlines()]
        for call in calls:
            self.assertEqual(call['env']['PDF_REPORT_MAX_VERTICES'], '123')
            self.assertEqual(call['env']['PDF_REPORT_MAX_EDGES'], '456')
            self.assertEqual(call['env']['FORCE_PDF_REPORT'], '1')

    def test_stage_log_open_failure_is_recorded(self):
        result = self.execute("break-log")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.status()["status"], "failed")
        self.assertEqual(self.status()["failedStage"], "simulation")
        self.assertEqual(json.loads((self.run_dir / "progress.json").read_text())["stage"], "simulation")

    def test_logging_failure_outside_stage_is_recorded(self):
        result = self.execute("break-pipeline-log")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.status()["status"], "failed")
        self.assertEqual(self.status()["failedStage"], "preflight")

    def test_signals_record_failure_and_stop_stage_process(self):
        for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=signum):
                # Separate run IDs preserve each failure record.
                identifier = f"signal-{signum}"
                command = self.command()
                command[-1] = identifier
                run = self.runs / identifier
                self.marker.unlink(missing_ok=True)
                process = subprocess.Popen(command, env=dict(self.env, FAKE_DOCKER_MODE="block"),
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                try:
                    deadline = time.monotonic() + 8
                    while not self.marker.exists():
                        self.assertIsNone(process.poll(), "pipeline exited before the blocking command")
                        self.assertLess(time.monotonic(), deadline)
                        time.sleep(0.02)
                    child_pid = int(self.marker.read_text())
                    progress_path = run / "progress.json"
                    while True:
                        progress = json.loads(progress_path.read_text())
                        if progress.get("heartbeatAt") and progress.get("stageElapsedSeconds", 0) > 0:
                            break
                        self.assertLess(time.monotonic(), deadline)
                        time.sleep(0.02)
                    self.assertEqual(progress["stage"], "simulation")
                    self.assertEqual(progress["description"], "Native kernel fixture")
                    self.assertEqual(progress["current"], 3)
                    self.assertEqual(progress["total"], 100)
                    process.send_signal(signum)
                    stdout, stderr = process.communicate(timeout=8)
                    self.assertEqual(process.returncode, 128 + signum, stdout + stderr)
                    status = json.loads((run / "status.json").read_text())
                    self.assertEqual(status["status"], "failed")
                    self.assertEqual(status["failedStage"], "simulation")
                    self.assertIn(signal.Signals(signum).name.removeprefix("SIG"), status["message"])
                    self.assertIn("[heartbeat] simulation:", (run / "logs" / "simulation.log").read_text())
                    self.assertEqual(json.loads(progress_path.read_text())["stageStatus"], "failed")
                    with self.assertRaises(ProcessLookupError):
                        os.kill(child_pid, 0)
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.communicate(timeout=8)

    def test_unexpected_status_helper_failure_runs_exit_cleanup(self):
        wrapper = self.binaries / "python3"
        wrapper.write_text(f'#!{sys.executable}\nimport os, sys\n'
                           'args = sys.argv[1:]\n'
                           'if "--name" in args and "--stage-status" in args:\n'
                           '    if args[args.index("--name") + 1] == "simulation" and args[args.index("--stage-status") + 1] == "running":\n'
                           '        sys.exit(42)\n'
                           f'os.execv({sys.executable!r}, [{sys.executable!r}] + args)\n')
        wrapper.chmod(0o755)
        result = self.execute()
        self.assertEqual(result.returncode, 42, result.stdout + result.stderr)
        self.assertEqual(self.status()["status"], "failed")
        self.assertEqual(self.status()["failedStage"], "simulation")


if __name__ == "__main__":
    unittest.main()
