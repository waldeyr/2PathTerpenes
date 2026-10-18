"""Opt-in filesystem/package stress test; synthetic SVGs, no chemical simulation.

Usage: python3 tests/stress_pipeline.py --output-dir /tmp/2path-stress-new
Creates a new directory, never reuses/overwrites an existing run.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--nodes', type=int, default=50_000)
    parser.add_argument('--edges', type=int, default=125_000)
    parser.add_argument('--svg-bytes', type=int, default=10_240,
                        help='approximate bytes per synthetic SVG (default matches the production average)')
    args = parser.parse_args()
    if args.nodes < 3 or args.edges < args.nodes - 2:
        parser.error('need at least 3 nodes and nodes-2 reactions')
    svg_prefix = '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80"><desc>'
    svg_suffix = '</desc><text x="5" y="30">Fixture</text></svg>'
    minimum_svg_bytes = len(svg_prefix) + len(svg_suffix)
    if args.svg_bytes < minimum_svg_bytes:
        parser.error(f'--svg-bytes must be at least {minimum_svg_bytes}')
    run = args.output_dir.resolve()
    run.mkdir(parents=True, exist_ok=False)
    out = run / 'out'
    out.mkdir()
    graph = {'meta': {'title': 'Synthetic scale verification', 'rootIds': ['v0', 'v1']},
             'nodes': [{'id': f'v{i}', 'name': 'GPP' if i == 0 else 'H2O' if i == 1 else f'Molecule {i}',
                        # Long enough to make the embedded payload at least as
                        # demanding as the 25.48 MiB production export.
                        'smiles': 'C' * 128, 'charge': 0, 'cycles': i % 8,
                        'iteration': 0 if i == 0 else 1, 'image': f'm{i}.svg'} for i in range(args.nodes)],
             'hyperedges': [{'id': f'e{i}', 'sources': ['v0', 'v1'],
                             'targets': [f'v{i % (args.nodes - 2) + 2}'], 'category': 'common',
                             'rules': ['synthetic-rule']} for i in range(args.edges)]}
    (out / 'hypergraph.json').write_text(json.dumps(graph), encoding='utf-8')
    svg = svg_prefix + ('x' * (args.svg_bytes - minimum_svg_bytes)) + svg_suffix
    for node in graph['nodes']:
        (out / node['image']).write_text(svg, encoding='utf-8')
    metrics = {'nodes': args.nodes, 'hyperedges': args.edges, 'synthetic': True,
               'svgBytesEach': len(svg), 'sourceSvgBytes': len(svg) * args.nodes}
    commands = {
        'validate-simulation': ['validate_pipeline.py', '--run-dir', str(run), '--stage', 'simulation'],
        'svg-cache-validation': ['convert_hypergraph_svgs.py', '--out-dir', str(out)],
        'validate-assets': ['validate_pipeline.py', '--run-dir', str(run), '--stage', 'assets'],
        'report-build': ['organize_hypergraph_assets.py'],
        'validate-report': ['validate_pipeline.py', '--run-dir', str(run), '--stage', 'report'],
    }
    environment = dict(os.environ, OUTPUT_DIR=str(out), REPORT_DIR=str(run / 'report'))
    for name, command in commands.items():
        start = time.monotonic()
        with (run / f'{name}.log').open('w') as log:
            subprocess.run([sys.executable, str(ROOT / command[0]), *command[1:]], env=environment,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        metrics[name + 'Seconds'] = round(time.monotonic() - start, 3)
        print(f'{name}: {metrics[name + "Seconds"]}s', flush=True)
    metrics['htmlBytes'] = (run / 'report' / 'hypergraph.html').stat().st_size
    (run / 'metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    print(json.dumps(metrics, indent=2))
    print(run / 'report' / 'hypergraph.html')


if __name__ == '__main__':
    main()
