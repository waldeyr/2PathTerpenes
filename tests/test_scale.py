"""Scale and integrity regressions independent of a Docker/MØD installation."""

import contextlib
import compile_molecule_pdfs
import io
import json
import os
from pathlib import Path
import random
import runpy
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hypergraph_levels import derivation_levels
from validate_pipeline import validate_svg
import convert_hypergraph_svgs as converter


class LevelTests(unittest.TestCase):
    def test_reverse_order_chain_of_50000_nodes(self):
        # The previous repeated scan took one full pass per node for this order.
        reactions = [([i], [i + 1]) for i in reversed(range(49_999))]
        levels = derivation_levels(range(50_000), reactions, {0: 0})
        self.assertEqual(levels[49_999], 49_999)
        self.assertEqual(list(levels.values()), list(range(50_000)))

    def test_and_sources_water_shortcuts_and_unreachable_cycle(self):
        reactions = [(['a', 'b', 'water'], ['c']), (['water'], ['d']),
                     (['a'], ['b']), (['c'], ['a']), (['x'], ['y']), (['y'], ['x'])]
        self.assertEqual(derivation_levels(['a', 'b', 'c', 'd', 'water', 'x', 'y'],
                         reactions, {'a': 0, 'water': 1}, {'water'}),
                         {'a': 0, 'b': 1, 'c': 2, 'd': 2, 'water': 1, 'x': None, 'y': None})

    def test_matches_reference_relaxation_on_random_hypergraphs(self):
        rng = random.Random(42)
        for _ in range(50):
            reactions = [(rng.sample(range(40), rng.randint(1, 4)),
                          rng.sample(range(40), rng.randint(1, 3))) for _ in range(100)]
            reference = dict.fromkeys(range(40))
            reference.update({0: 0, 1: 0, 2: 1})
            changed = True
            while changed:
                changed = False
                for sources, targets in reactions:
                    active = set(sources) - {2} or set(sources)
                    if all(reference[s] is not None for s in active):
                        level = max(reference[s] for s in active) + 1
                        for t in targets:
                            if reference[t] is None or level < reference[t]:
                                reference[t] = level
                                changed = True
            self.assertEqual(derivation_levels(range(40), reactions, {0: 0, 1: 0, 2: 1}, {2}), reference)


class PrinterIntegrationTests(unittest.TestCase):
    def execute_printer(self, size, environment):
        dg = types.SimpleNamespace(vertices=range(size), edges=range(size), print=mock.Mock())
        mod = types.ModuleType('mod')
        mod.DGPrinter = mock.Mock()
        mod.post = types.SimpleNamespace(summarySection=mock.Mock())
        with mock.patch.dict(sys.modules, mod=mod), mock.patch.dict(os.environ, environment, clear=True), \
             contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(ROOT / 'printer.py'), init_globals={'dg': dg})
        return dg

    def test_large_dg_never_queues_graphviz_layout(self):
        self.execute_printer(48_639, {}).print.assert_not_called()

    def test_small_dg_still_queues_pdf(self):
        self.execute_printer(5, {}).print.assert_called_once()

    def test_force_override_reaches_printer(self):
        self.execute_printer(48_639, {'FORCE_PDF_REPORT': '1'}).print.assert_called_once()


class ConversionIntegrityTests(unittest.TestCase):
    def test_partial_svg_is_rebuilt_atomically_and_failure_preserves_original(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            graph = {'nodes': [{'id': 'a', 'image': 'a.svg'}],
                     'hyperedges': [{'id': 'e', 'sources': ['a'], 'targets': ['a']}]}
            (out / 'hypergraph.json').write_text(json.dumps(graph))
            (out / 'a.pdf').write_bytes(b'%PDF-fixture')
            (out / 'a.svg').write_text('<svg><path')
            def fail(command, **kwargs):
                Path(command[-1] + '.svg').write_text('<svg>partial')
                raise subprocess.CalledProcessError(1, command)
            def success(command, **kwargs):
                self.assertEqual((out / 'a.svg').read_text(), '<svg><path')
                Path(command[-1] + '.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            with mock.patch.object(sys, 'argv', ['converter', '--out-dir', directory]), \
                 contextlib.redirect_stdout(io.StringIO()):
                with mock.patch.object(converter.subprocess, 'run', side_effect=fail):
                    with self.assertRaises(subprocess.CalledProcessError):
                        converter.main()
                self.assertEqual((out / 'a.svg').read_text(), '<svg><path')
                with mock.patch.object(converter.subprocess, 'run', side_effect=success):
                    converter.main()
                validate_svg(out / 'a.svg')
                with mock.patch.object(converter.subprocess, 'run') as run:
                    converter.main()
                    run.assert_not_called()
            self.assertEqual(list(out.glob('.svg-*')), [])


class MoleculePdfMakefileTests(unittest.TestCase):
    def test_post_makefiles_create_marker_before_mod_post(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out = root / "out"
            out.mkdir()
            (out / "post.sh").write_text("summarySection test\n")
            previous = os.getcwd()
            os.chdir(root)

            def fake_mod_post(command, **kwargs):
                self.assertEqual(command, ["mod_post"])
                self.assertTrue((out / "disableInvokeMake").is_file())
                summary = root / "summary"
                summary.mkdir()
                (summary / "MakefileImpl").write_text("")

            try:
                with mock.patch.object(compile_molecule_pdfs.shutil, "which", return_value="mod_post"), \
                     mock.patch.object(compile_molecule_pdfs.subprocess, "run", side_effect=fake_mod_post):
                    self.assertTrue(compile_molecule_pdfs._ensure_post_makefiles(out).is_file())
            finally:
                os.chdir(previous)

    def test_helper_compiles_only_requested_targets_from_impl(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out = root / "out"
            summary = root / "summary"
            out.mkdir()
            summary.mkdir()
            graph = {
                "meta": {},
                "nodes": [{"id": "v0", "image": "001.svg"}],
                "hyperedges": [{"id": "e0", "sources": ["v0"], "targets": ["v0"]}],
            }
            (out / "hypergraph.json").write_text(json.dumps(graph))
            (out / "001.tex").write_text("tex")
            (summary / "MakefileImpl").write_text(
                "out/001.pdf: out/001.tex\n\tprintf pdf > $@\n"
            )
            previous = os.getcwd()
            previous_argv = sys.argv
            os.chdir(root)
            sys.argv = ["compile_molecule_pdfs.py", "--out-dir", "out"]
            try:
                compile_molecule_pdfs.main()
            finally:
                sys.argv = previous_argv
                os.chdir(previous)
            self.assertEqual((out / "001.pdf").read_bytes(), b"pdf")

    def test_bounded_makefile_has_no_monolithic_recipe(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "compile.mk"
            targets = [f"out/{index:05d}.pdf" for index in range(70_000)]
            compile_molecule_pdfs._write_makefile(path, targets)
            text = path.read_text()
            self.assertIn("include summary/MakefileImpl", text)
            self.assertNotIn("\n\t", text)
            self.assertLessEqual(max(map(len, text.splitlines())), 8_000)

    def test_large_graph_with_existing_pdfs_skips_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out = root / "out"
            out.mkdir()
            graph = {
                "meta": {},
                "nodes": [{"id": "v0", "image": "001.svg"},
                          {"id": "v1", "image": "002.svg"}],
                "hyperedges": [{"id": "e0", "sources": ["v0"], "targets": ["v1"]}],
            }
            (out / "hypergraph.json").write_text(json.dumps(graph))
            (out / "001.pdf").write_bytes(b"pdf")
            (out / "002.pdf").write_bytes(b"pdf")
            with contextlib.redirect_stdout(io.StringIO()) as output:
                previous = os.getcwd()
                previous_argv = sys.argv
                previous_env = os.environ.copy()
                os.chdir(root)
                sys.argv = ["compile_molecule_pdfs.py", "--out-dir", "out"]
                os.environ["PDF_REPORT_MAX_VERTICES"] = "1"
                try:
                    compile_molecule_pdfs.main()
                finally:
                    os.environ.clear()
                    os.environ.update(previous_env)
                    sys.argv = previous_argv
                    os.chdir(previous)
            self.assertIn("Molecule PDF", output.getvalue())
            self.assertIn("skipped for large graph", output.getvalue())


if __name__ == '__main__':
    unittest.main()
