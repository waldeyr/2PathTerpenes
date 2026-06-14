// Interactive "metro map" visualization of the chemical derivation hypergraph.
// Data format produced by export_hypergraph.py (see docs/data/hypergraph.json),
// with docs/data/hypergraph.sample.json used as a fallback/preview dataset.

(function () {
  const DATA_URL = 'data/hypergraph.json';
  const SAMPLE_DATA_URL = 'data/hypergraph.sample.json';

  const CATEGORY_COLORS = {
    mono: '#0284c7',
    sesqui: '#9333ea',
    common: '#059669',
    default: '#94a3b8'
  };

  const COL_WIDTH = 200;
  const LANE_HEIGHT = 80;
  const MARGIN_X = 80;
  const MARGIN_Y = 60;
  const NODE_RADIUS = 20;

  const state = {
    data: null,
    layout: null,
    selection: null,
    pathHighlight: null,
    activeCategories: new Set(['mono', 'sesqui', 'common', 'default']),
    searchTerm: '',
    svg: null,
    zoom: null
  };

  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    const raw = await loadData();
    state.data = normalizeData(raw);
    state.layout = computeLayout(state.data);
    render();
    bindControls();
    updateStatus();
  }

  async function loadData() {
    try {
      const res = await fetch(DATA_URL, { cache: 'no-store' });
      if (res.ok) return await res.json();
    } catch (err) {
      // fall through to sample data
    }
    const res = await fetch(SAMPLE_DATA_URL);
    return res.json();
  }

  function normalizeData(raw) {
    const nodes = (raw.nodes || []).map(n => ({ ...n }));
    const hyperedges = (raw.hyperedges || []).map((e, idx) => ({
      id: e.id || `e${idx}`,
      sources: e.sources || [],
      targets: e.targets || [],
      rules: e.rules || [],
      category: (e.category || 'default').toLowerCase(),
      iteration: e.iteration
    }));
    return { meta: raw.meta || {}, nodes, hyperedges };
  }

  function categoryColor(category) {
    return CATEGORY_COLORS[category] || CATEGORY_COLORS.default;
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  function truncate(text, max) {
    if (!text) return '';
    return text.length > max ? `${text.slice(0, max - 1)}…` : text;
  }

  // ---------------------------------------------------------------------
  // Layout: assign an "iteration" (column) and a "lane" (row) to each node,
  // similar to how a metro map keeps a line on the same row when possible.
  // ---------------------------------------------------------------------
  function computeLayout(data) {
    const nodesById = new Map(data.nodes.map(n => [n.id, n]));
    const incoming = new Map();
    const outgoing = new Map();
    data.nodes.forEach(n => {
      incoming.set(n.id, []);
      outgoing.set(n.id, []);
    });
    data.hyperedges.forEach(e => {
      e.sources.forEach(s => outgoing.get(s) && outgoing.get(s).push(e));
      e.targets.forEach(t => incoming.get(t) && incoming.get(t).push(e));
    });

    // Iterations: trust provided values, otherwise derive from the source
    // nodes (root nodes with no incoming hyperedge start at 0).
    data.nodes.forEach(n => {
      if (typeof n.iteration !== 'number') {
        n.iteration = incoming.get(n.id).length === 0 ? 0 : null;
      }
    });
    let changed = true;
    let guard = 0;
    while (changed && guard < 1000) {
      changed = false;
      guard++;
      data.hyperedges.forEach(e => {
        const srcIters = e.sources.map(id => nodesById.get(id).iteration);
        if (srcIters.every(v => v != null)) {
          const level = Math.max(...srcIters) + 1;
          e.targets.forEach(tid => {
            const tNode = nodesById.get(tid);
            if (tNode.iteration == null || tNode.iteration < level) {
              tNode.iteration = level;
              changed = true;
            }
          });
        }
      });
    }
    data.nodes.forEach(n => { if (n.iteration == null) n.iteration = 0; });

    // Group nodes into columns by iteration.
    const maxIter = data.nodes.reduce((m, n) => Math.max(m, n.iteration), 0);
    const columns = Array.from({ length: maxIter + 1 }, () => []);
    data.nodes.forEach(n => columns[n.iteration].push(n));

    // Lane assignment: a node prefers the (rounded) average lane of the
    // sources of its incoming hyperedge(s) - this keeps a simple chain on
    // the same row (straight metro line), while merge points (multiple
    // educts) land between the lanes of their sources instead of jumping
    // to whichever source happens to be listed first.
    const laneOf = new Map();
    function preferredLane(node) {
      const inc = incoming.get(node.id);
      if (inc.length === 0) return null;
      const srcLanes = [];
      inc.forEach(e => e.sources.forEach(srcId => {
        if (laneOf.has(srcId)) srcLanes.push(laneOf.get(srcId));
      }));
      if (!srcLanes.length) return null;
      const avg = srcLanes.reduce((s, v) => s + v, 0) / srcLanes.length;
      return Math.round(avg);
    }
    columns.forEach(col => {
      const occupied = new Set();
      const ordered = [...col].sort((a, b) => {
        const pa = preferredLane(a);
        const pb = preferredLane(b);
        return (pa == null ? Infinity : pa) - (pb == null ? Infinity : pb);
      });
      ordered.forEach(n => {
        let lane = preferredLane(n);
        if (lane == null || occupied.has(lane)) {
          lane = 0;
          while (occupied.has(lane)) lane++;
        }
        occupied.add(lane);
        laneOf.set(n.id, lane);
        n.lane = lane;
      });
    });

    // Pixel coordinates.
    data.nodes.forEach(n => {
      n.x = MARGIN_X + n.iteration * COL_WIDTH;
      n.y = MARGIN_Y + n.lane * LANE_HEIGHT;
    });

    const maxLane = data.nodes.reduce((m, n) => Math.max(m, n.lane), 0);

    // Hyperedge "stations" sit between the source and target columns.
    data.hyperedges.forEach(e => {
      const connected = [...e.sources, ...e.targets]
        .map(id => nodesById.get(id))
        .filter(Boolean);
      const avgY = connected.reduce((s, n) => s + n.y, 0) / (connected.length || 1);
      const sourceX = e.sources.length
        ? Math.max(...e.sources.map(id => nodesById.get(id).x))
        : MARGIN_X;
      const targetX = e.targets.length
        ? Math.min(...e.targets.map(id => nodesById.get(id).x))
        : sourceX + COL_WIDTH;
      e.x = (sourceX + targetX) / 2;
      e.y = avgY;
    });

    return {
      width: MARGIN_X * 2 + maxIter * COL_WIDTH,
      height: MARGIN_Y * 2 + maxLane * LANE_HEIGHT,
      nodesById,
      incoming,
      outgoing
    };
  }

  // ---------------------------------------------------------------------
  // Rendering
  // ---------------------------------------------------------------------
  function render() {
    const data = state.data;
    const layout = state.layout;
    const svg = d3.select('#hg-canvas');
    svg.selectAll('*').remove();
    svg.attr('viewBox', `0 0 ${layout.width} ${layout.height}`);

    const root = svg.append('g').attr('class', 'hg-root');

    // Background rect to capture clicks that clear the current selection.
    root.append('rect')
      .attr('class', 'hg-background')
      .attr('x', -COL_WIDTH).attr('y', -LANE_HEIGHT)
      .attr('width', layout.width + COL_WIDTH * 2)
      .attr('height', layout.height + LANE_HEIGHT * 2)
      .attr('fill', 'transparent')
      .on('click', () => {
        state.selection = null;
        applyFilters();
        renderPlaceholder();
      });

    const zoom = d3.zoom()
      .scaleExtent([0.3, 3])
      .on('zoom', event => root.attr('transform', event.transform));
    svg.call(zoom);
    state.svg = svg;
    state.zoom = zoom;

    // Links: one path per (hyperedge, connected node) pair.
    const links = [];
    data.hyperedges.forEach(e => {
      e.sources.forEach(sid => links.push({ hyperedge: e, node: layout.nodesById.get(sid), dir: 'in' }));
      e.targets.forEach(tid => links.push({ hyperedge: e, node: layout.nodesById.get(tid), dir: 'out' }));
    });

    root.append('g').attr('class', 'hg-links')
      .selectAll('path')
      .data(links)
      .join('path')
      .attr('class', d => `hg-link hg-link-${d.hyperedge.category}`)
      .attr('data-edge', d => d.hyperedge.id)
      .attr('stroke', d => categoryColor(d.hyperedge.category))
      .attr('d', linkPath)
      .on('click', (event, d) => { event.stopPropagation(); selectHyperedge(d.hyperedge); })
      .append('title')
      .text(d => (d.hyperedge.rules || []).join(', '));

    // Hyperedge "stations".
    root.append('g').attr('class', 'hg-hyperedges')
      .selectAll('circle')
      .data(data.hyperedges)
      .join('circle')
      .attr('class', d => `hg-hyperedge hg-hyperedge-${d.category}`)
      .attr('data-edge', d => d.id)
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', 5)
      .attr('fill', d => categoryColor(d.category))
      .on('click', (event, d) => { event.stopPropagation(); selectHyperedge(d); })
      .append('title')
      .text(d => (d.rules || []).join(', '));

    // Molecule "stations".
    const nodeGroup = root.append('g').attr('class', 'hg-nodes')
      .selectAll('g')
      .data(data.nodes)
      .join('g')
      .attr('class', d => {
        const classes = ['hg-node'];
        if ((layout.incoming.get(d.id) || []).length === 0) classes.push('is-root');
        if ((layout.outgoing.get(d.id) || []).length === 0) classes.push('is-leaf');
        return classes.join(' ');
      })
      .attr('data-node', d => d.id)
      .attr('transform', d => `translate(${d.x}, ${d.y})`)
      .on('click', (event, d) => { event.stopPropagation(); selectNode(d); });

    nodeGroup.append('circle').attr('r', NODE_RADIUS);
    nodeGroup.append('text').attr('dy', NODE_RADIUS + 14).text(d => truncate(d.name, 16));
    nodeGroup.append('title').text(d => `${d.name}${d.smiles ? `\n${d.smiles}` : ''}`);

    applyFilters();
  }

  function linkPath(d) {
    const n = d.node;
    const e = d.hyperedge;
    let x0, y0, x1, y1;
    if (d.dir === 'in') {
      x0 = n.x + NODE_RADIUS; y0 = n.y;
      x1 = e.x; y1 = e.y;
    } else {
      x0 = e.x; y0 = e.y;
      x1 = n.x - NODE_RADIUS; y1 = n.y;
    }
    const mx = (x0 + x1) / 2;
    return `M${x0},${y0} C${mx},${y0} ${mx},${y1} ${x1},${y1}`;
  }

  // ---------------------------------------------------------------------
  // Pathway highlighting: trace a route from a root molecule (e.g. GPP/FPP)
  // to a chosen target through the hyperedges that were actually reachable.
  // ---------------------------------------------------------------------
  function computePathToTarget(targetId) {
    const { incoming, outgoing, nodesById } = state.layout;

    const roots = state.data.nodes
      .filter(n => (incoming.get(n.id) || []).length === 0)
      .map(n => n.id);

    // Multi-source BFS: a hyperedge "fires" once all of its sources have
    // been reached, recording the hyperedge that first reached each target.
    const predEdge = new Map();
    const reached = new Set(roots);
    let frontier = [...roots];
    while (frontier.length) {
      const next = [];
      frontier.forEach(nodeId => {
        (outgoing.get(nodeId) || []).forEach(e => {
          if (e.sources.every(s => reached.has(s))) {
            e.targets.forEach(t => {
              if (!reached.has(t)) {
                reached.add(t);
                predEdge.set(t, e);
                next.push(t);
              }
            });
          }
        });
      });
      frontier = next;
    }

    if (!reached.has(targetId)) return null;

    // Walk the predecessor forest backwards from the target. Each non-root
    // node has exactly one predEdge (the hyperedge that first produced it),
    // so following all of its sources keeps the highlighted set connected
    // (e.g. a merge step also highlights the edge that produced each educt).
    const nodes = new Set();
    const edges = new Set();
    const stack = [targetId];
    while (stack.length) {
      const current = stack.pop();
      if (nodes.has(current)) continue;
      nodes.add(current);
      const edge = predEdge.get(current);
      if (!edge) continue;
      edges.add(edge.id);
      edge.sources.forEach(s => stack.push(s));
      edge.targets.forEach(t => nodes.add(t));
    }
    return { nodes, edges };
  }

  function populatePathwaySelect() {
    const select = d3.select('#hg-pathway');
    const leaves = state.data.nodes
      .filter(n => (state.layout.outgoing.get(n.id) || []).length === 0)
      .sort((a, b) => a.name.localeCompare(b.name));
    select.selectAll('option:not([value=""])').remove();
    select.selectAll('option.hg-pathway-option')
      .data(leaves)
      .join('option')
      .attr('class', 'hg-pathway-option')
      .attr('value', d => d.id)
      .text(d => d.name);
  }

  // ---------------------------------------------------------------------
  // Selection, search and category filters
  // ---------------------------------------------------------------------
  function selectNode(node) {
    state.selection = { type: 'node', id: node.id };
    applyFilters();
    renderNodeDetails(node);
  }

  function selectHyperedge(edge) {
    state.selection = { type: 'edge', id: edge.id };
    applyFilters();
    renderEdgeDetails(edge);
  }

  function applyFilters() {
    const svg = state.svg;
    const data = state.data;
    const layout = state.layout;
    const search = state.searchTerm.trim().toLowerCase();

    const searchNodes = search
      ? new Set(data.nodes.filter(n => {
          return n.name.toLowerCase().includes(search) ||
            (n.chemblName && n.chemblName.toLowerCase().includes(search)) ||
            (n.chemblId && n.chemblId.toLowerCase().includes(search));
        }).map(n => n.id))
      : null;

    const highlightNodes = new Set();
    const highlightEdges = new Set();
    if (state.selection) {
      if (state.selection.type === 'node') {
        highlightNodes.add(state.selection.id);
        data.hyperedges.forEach(e => {
          if (e.sources.includes(state.selection.id) || e.targets.includes(state.selection.id)) {
            highlightEdges.add(e.id);
            e.sources.forEach(s => highlightNodes.add(s));
            e.targets.forEach(t => highlightNodes.add(t));
          }
        });
      } else if (state.selection.type === 'edge') {
        const edge = data.hyperedges.find(e => e.id === state.selection.id);
        highlightEdges.add(edge.id);
        edge.sources.forEach(s => highlightNodes.add(s));
        edge.targets.forEach(t => highlightNodes.add(t));
      }
    }
    if (state.pathHighlight) {
      state.pathHighlight.nodes.forEach(id => highlightNodes.add(id));
      state.pathHighlight.edges.forEach(id => highlightEdges.add(id));
    }

    const hasSelection = highlightNodes.size > 0;

    svg.selectAll('.hg-node').each(function (d) {
      const el = d3.select(this);
      const matchesSearch = !searchNodes || searchNodes.has(d.id);
      const matchesSelection = !hasSelection || highlightNodes.has(d.id);
      const active = (searchNodes && searchNodes.has(d.id)) || (hasSelection && highlightNodes.has(d.id));
      const dimmed = !matchesSearch || !matchesSelection;
      el.classed('is-active', !!active);
      el.classed('is-dimmed', dimmed && !active);
    });

    svg.selectAll('.hg-hyperedge, .hg-link').each(function (d) {
      const edge = d.hyperedge || d;
      const el = d3.select(this);
      const categoryHidden = !state.activeCategories.has(edge.category);
      const active = hasSelection && highlightEdges.has(edge.id);
      const dimmed = categoryHidden || (hasSelection && !highlightEdges.has(edge.id));
      el.classed('is-active', active);
      el.classed('is-dimmed', dimmed && !active);
    });

    updateStatus(searchNodes);
    void layout; // layout kept for reference/debugging
  }

  function renderNodeDetails(node) {
    const incomingEdges = state.layout.incoming.get(node.id) || [];
    const outgoingEdges = state.layout.outgoing.get(node.id) || [];

    let html = `<h3>${escapeHtml(node.name)}</h3>`;
    if (node.image) {
      html += `<img class="hg-molecule-image" src="${escapeHtml(node.image)}" alt="${escapeHtml(node.name)} structure">`;
    }
    html += '<dl>';
    if (node.smiles) html += `<dt>SMILES</dt><dd>${escapeHtml(node.smiles)}</dd>`;
    if (typeof node.charge === 'number') html += `<dt>Charge</dt><dd>${node.charge}</dd>`;
    if (typeof node.cycles === 'number') html += `<dt>Rings</dt><dd>${node.cycles}</dd>`;
    html += `<dt>Step</dt><dd>${node.iteration}</dd>`;
    if (node.chemblId) {
      const chemblUrl = `https://www.ebi.ac.uk/chembl/explore/molecule/${encodeURIComponent(node.chemblId)}`;
      html += `<dt>ChEMBL</dt><dd><a href="${escapeHtml(chemblUrl)}" target="_blank" rel="noopener">${escapeHtml(node.chemblId)}</a>`;
      if (node.chemblName) html += ` &mdash; ${escapeHtml(node.chemblName)}`;
      html += '</dd>';
    }
    html += '</dl>';

    if (incomingEdges.length) {
      html += '<p class="hg-label">Produced by</p><ul class="hg-rule-list">';
      incomingEdges.forEach(e => {
        html += `<li>${escapeHtml((e.rules || []).join(', ') || e.id)}</li>`;
      });
      html += '</ul>';
    }
    if (outgoingEdges.length) {
      html += '<p class="hg-label">Reacts via</p><ul class="hg-rule-list">';
      outgoingEdges.forEach(e => {
        html += `<li>${escapeHtml((e.rules || []).join(', ') || e.id)}</li>`;
      });
      html += '</ul>';
    }
    d3.select('#hg-details').html(html);
  }

  function renderEdgeDetails(edge) {
    const sources = edge.sources.map(id => state.layout.nodesById.get(id)?.name || id);
    const targets = edge.targets.map(id => state.layout.nodesById.get(id)?.name || id);

    let html = '<h3>Reaction</h3><dl>';
    html += `<dt>Educts</dt><dd>${escapeHtml(sources.join(' + '))}</dd>`;
    html += `<dt>Products</dt><dd>${escapeHtml(targets.join(' + '))}</dd>`;
    html += `<dt>Category</dt><dd>${escapeHtml(edge.category)}</dd>`;
    html += '</dl>';
    html += '<p class="hg-label">Applied rule(s)</p><ul class="hg-rule-list">';
    (edge.rules.length ? edge.rules : ['(unnamed rule)']).forEach(r => {
      html += `<li>${escapeHtml(r)}</li>`;
    });
    html += '</ul>';
    d3.select('#hg-details').html(html);
  }

  function renderPlaceholder() {
    d3.select('#hg-details').html(
      '<div class="hg-details-placeholder">Select a molecule (station) or a reaction (connector) to see details here.</div>'
    );
  }

  function updateStatus(searchNodes) {
    const data = state.data;
    let text = `${data.nodes.length} molecules · ${data.hyperedges.length} reactions`;
    if (searchNodes) text += ` · ${searchNodes.size} match${searchNodes.size === 1 ? '' : 'es'}`;
    d3.select('#hg-status').text(text);
  }

  function bindControls() {
    populatePathwaySelect();

    d3.select('#hg-search').on('input', event => {
      state.searchTerm = event.target.value;
      applyFilters();
    });

    d3.selectAll('#hg-legend input[type=checkbox]').on('change', event => {
      const category = event.target.dataset.category;
      if (event.target.checked) state.activeCategories.add(category);
      else state.activeCategories.delete(category);
      applyFilters();
    });

    d3.select('#hg-pathway').on('change', event => {
      const targetId = event.target.value;
      if (!targetId) {
        state.pathHighlight = null;
        applyFilters();
        renderPlaceholder();
        return;
      }
      const path = computePathToTarget(targetId);
      state.pathHighlight = path;
      applyFilters();
      if (path) {
        renderPathwayDetails(state.layout.nodesById.get(targetId), path);
      } else {
        d3.select('#hg-details').html(
          '<div class="hg-details-placeholder">No reachable pathway found to this molecule.</div>'
        );
      }
    });

    d3.select('#hg-reset').on('click', () => {
      state.selection = null;
      state.pathHighlight = null;
      state.searchTerm = '';
      d3.select('#hg-search').property('value', '');
      d3.select('#hg-pathway').property('value', '');
      state.svg.transition().duration(300).call(state.zoom.transform, d3.zoomIdentity);
      applyFilters();
      renderPlaceholder();
    });
  }

  function renderPathwayDetails(target, path) {
    const steps = [...path.edges]
      .map(id => state.data.hyperedges.find(e => e.id === id))
      .sort((a, b) => a.iteration - b.iteration);

    let html = `<h3>Pathway to ${escapeHtml(target.name)}</h3>`;
    html += `<p class="hg-label">${steps.length} reaction step(s)</p>`;
    html += '<ul class="hg-rule-list">';
    steps.forEach(e => {
      const sources = e.sources.map(id => state.layout.nodesById.get(id)?.name || id).join(' + ');
      const targets = e.targets.map(id => state.layout.nodesById.get(id)?.name || id).join(' + ');
      const rules = e.rules.length ? e.rules.join(', ') : '(unnamed rule)';
      html += `<li>${escapeHtml(sources)} &rarr; ${escapeHtml(targets)}<br><em>${escapeHtml(rules)}</em></li>`;
    });
    html += '</ul>';
    d3.select('#hg-details').html(html);
  }
})();
