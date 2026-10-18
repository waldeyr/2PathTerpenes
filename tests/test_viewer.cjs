// Run with: node --test tests/test_viewer.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { indexGraph, boundedView, computeLayout, computePathToTarget } = require('../report_template/javascript/hypergraph.js');

test('50k molecules / 125k reactions remain complete with a bounded view', () => {
  const nodes = Array.from({ length: 50000 }, (_, i) => ({ id: `v${i}`, name: `M${i}`, iteration: i % 8 }));
  const hyperedges = Array.from({ length: 125000 }, (_, i) => ({
    id: `e${i}`, sources: ['v0', `v${i % 49999 + 1}`], targets: [`v${(i + 1) % 49999 + 1}`]
  }));
  const data = { nodes, hyperedges };
  const index = indexGraph(data);
  for (const seeds of [nodes.slice(0, 100), nodes.slice(-100), [nodes[49999]]]) {
    const view = boundedView(data, index, seeds);
    const ids = new Set(view.nodes.map(n => n.id));
    seeds.forEach(n => assert.ok(ids.has(n.id)));
    assert.ok(view.nodes.length <= 500);
    assert.ok(view.hyperedges.length <= 500);
    assert.ok(view.hyperedges.reduce((n, e) => n + e.sources.length + e.targets.length, 0) <= 2000);
    view.hyperedges.forEach(e => [...e.sources, ...e.targets].forEach(id => assert.ok(ids.has(id))));
    const layout = computeLayout(view);
    assert.ok(Number.isFinite(layout.height));
  }
  assert.equal(data.nodes.length, 50000);
  assert.equal(data.hyperedges.length, 125000);
});

test('same-column layout assigns distinct lanes to 50k vertices', () => {
  const nodes = Array.from({ length: 50000 }, (_, i) => ({ id: `v${i}`, name: `M${i}`, iteration: 0 }));
  computeLayout({ nodes, hyperedges: [] });
  assert.equal(new Set(nodes.map(n => n.lane)).size, 50000);
});

test('oversized hyperedge is omitted whole instead of clipping its endpoints', () => {
  const nodes = Array.from({ length: 600 }, (_, i) => ({ id: `v${i}`, name: `M${i}`, iteration: 0 }));
  const data = { nodes, hyperedges: [{ id: 'huge', sources: ['v0'], targets: nodes.slice(1).map(n => n.id) }] };
  assert.equal(boundedView(data, indexGraph(data), [nodes[0]]).hyperedges.length, 0);
});

test('pathways respect AND reactants, coproducts, cycles and explicit roots', () => {
  const data = { meta: { rootIds: ['a'] },
    nodes: ['a', 'b', 'c', 'd', 'x', 'y'].map(id => ({ id, name: id })),
    hyperedges: [
      { id: 'split', sources: ['a', 'a'], targets: ['b', 'c'] },
      { id: 'merge', sources: ['b', 'c'], targets: ['d'] },
      { id: 'back', sources: ['d'], targets: ['a'] },
      { id: 'xy', sources: ['x'], targets: ['y'] },
      { id: 'yx', sources: ['y'], targets: ['x'] },
      { id: 'blocked', sources: ['x', 'a'], targets: ['d'] }
    ] };
  const index = indexGraph(data);
  const path = computePathToTarget('d', data, index);
  assert.deepEqual(path.edges, new Set(['merge', 'split']));
  assert.deepEqual(path.nodes, new Set(['a', 'b', 'c', 'd']));
  assert.equal(computePathToTarget('x', data, index), null);
});

test('pathway traversal handles 50k steps without recursive stack overflow', () => {
  const data = { meta: { rootIds: ['v0'] },
    nodes: Array.from({ length: 50000 }, (_, i) => ({ id: `v${i}`, name: `M${i}` })),
    hyperedges: Array.from({ length: 49999 }, (_, i) => ({ id: `e${i}`, sources: [`v${i}`], targets: [`v${i + 1}`] })) };
  const path = computePathToTarget('v49999', data, indexGraph(data));
  assert.equal(path.nodes.size, 50000);
  assert.equal(path.edges.size, 49999);
});
