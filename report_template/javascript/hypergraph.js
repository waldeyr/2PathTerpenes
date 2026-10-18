// Interactive "metro map" visualization of the chemical derivation hypergraph.
// Data is embedded inline in hypergraph.html (see #hg-data, filled in by
// organize_hypergraph_assets.py) so this page works standalone via file://.

(function () {
  const CATEGORY_COLORS = {
    mono: '#0284c7',
    sesqui: '#9333ea',
    common: '#059669',
    default: '#94a3b8'
  };

  const COL_WIDTH = 260;
  const LANE_HEIGHT = 140;
  const MARGIN_X = 80;
  const MARGIN_Y = 60;
  const NODE_RADIUS = 20;
  const PAGE_SIZE = 100;
  const MAX_VIEW_NODES = 500;
  const MAX_VIEW_EDGES = 500;
  const MAX_VIEW_LINKS = 2000;
  // Do not shrink a tall, bounded page until hundreds of stations become
  // sub-pixel dots. The SVG opens a readable window; pan/zoom reaches the
  // remaining rows and columns in that page.
  const INITIAL_VIEW_WIDTH = 1200;
  const INITIAL_VIEW_HEIGHT = 800;

  function indexGraph(data) {
    const nodesById = new Map(data.nodes.map(n => [n.id, n]));
    const edgesById = new Map(data.hyperedges.map(e => [e.id, e]));
    const incoming = new Map(data.nodes.map(n => [n.id, []]));
    const outgoing = new Map(data.nodes.map(n => [n.id, []]));
    for (const edge of data.hyperedges) {
      for (const id of new Set(edge.sources)) outgoing.get(id)?.push(edge);
      for (const id of new Set(edge.targets)) incoming.get(id)?.push(edge);
    }
    return { nodesById, edgesById, incoming, outgoing };
  }

  // Retain the complete dataset but bound the DOM, even for a high-degree
  // cofactor. Every displayed reaction includes ALL its reactants/products.
  function boundedView(data, index, seeds, allowedEdges = null) {
    const ids = new Set(seeds.slice(0, PAGE_SIZE).map(n => n.id));
    const edges = new Map();
    const examined = new Set();
    let links = 0;
    for (const seed of seeds.slice(0, PAGE_SIZE)) {
      const candidates = [...index.incoming.get(seed.id), ...index.outgoing.get(seed.id)];
      for (const edge of candidates) {
        if (edges.size >= MAX_VIEW_EDGES) break;
        if (examined.has(edge.id) || (allowedEdges && !allowedEdges.has(edge.id))) continue;
        examined.add(edge.id);
        const endpoints = [...edge.sources, ...edge.targets];
        if (links + endpoints.length > MAX_VIEW_LINKS) continue;
        const additional = new Set(endpoints.filter(id => !ids.has(id)));
        if (ids.size + additional.size > MAX_VIEW_NODES) continue;
        additional.forEach(id => ids.add(id));
        edges.set(edge.id, edge);
        links += endpoints.length;
      }
    }
    return { meta: data.meta, nodes: [...ids].map(id => index.nodesById.get(id)),
      hyperedges: [...edges.values()] };
  }

  const state = {
    data: null,
    index: null,
    view: null,
    large: false,
    page: 0,
    pageCount: 1,
    layout: null,
    selection: null,
    pathHighlight: null,
    activeCategories: new Set(['mono', 'sesqui', 'common', 'default']),
    searchTerm: '',
    svg: null,
    zoom: null
  };

  if (typeof document !== 'undefined') document.addEventListener('DOMContentLoaded', init);
  if (typeof module !== 'undefined') module.exports = { indexGraph, boundedView, computeLayout, computePathToTarget };

  function init() {
    state.data = normalizeData(loadData());

    if (state.data.nodes.length === 0) {
      showEmptyState();
      return;
    }

    state.index = indexGraph(state.data);
    const incidences = state.data.hyperedges.reduce((n, e) => n + e.sources.length + e.targets.length, 0);
    state.large = state.data.nodes.length > MAX_VIEW_NODES ||
      state.data.hyperedges.length > MAX_VIEW_EDGES || incidences > MAX_VIEW_LINKS;
    refreshView();
    bindControls();
    updateStatus();
  }

  function matchesSearch(node, term) {
    return [node.id, node.name, node.smiles, node.chemblName, node.chemblId,
      node.pubchemName, node.pubchemId].some(value => String(value || '').toLowerCase().includes(term));
  }

  function refreshView() {
    const term = state.searchTerm.trim().toLowerCase();
    const candidates = state.data.nodes.filter(n =>
      (!term || matchesSearch(n, term)) && (!state.pathHighlight || state.pathHighlight.nodes.has(n.id)));
    state.pageCount = Math.max(1, Math.ceil(candidates.length / PAGE_SIZE));
    state.page = Math.min(state.page, state.pageCount - 1);
    state.view = state.large
      ? boundedView(state.data, state.index, candidates.slice(state.page * PAGE_SIZE, (state.page + 1) * PAGE_SIZE),
          state.pathHighlight?.edges)
      : state.data;
    state.layout = computeLayout(state.view);
    render();
    populatePathwaySelect();
    d3.select('#hg-paging').property('hidden', !state.large);
    d3.select('#hg-page').text(`Page ${state.page + 1} / ${state.pageCount}`);
    d3.select('#hg-prev').property('disabled', state.page === 0);
    d3.select('#hg-next').property('disabled', state.page + 1 >= state.pageCount);
  }

  function loadData() {
    const el = document.getElementById('hg-data');
    try {
      return JSON.parse(el.textContent);
    } catch (err) {
      return { meta: {}, nodes: [], hyperedges: [] };
    }
  }

  function showEmptyState() {
    d3.select('#hg-status').text('No hypergraph data available.');
    d3.select('#hg-details').html(
      '<div class="hg-details-placeholder">' +
      'No hypergraph data is embedded in this page. Run the export pipeline ' +
      '(<code>run-pipeline.sh</code>) to regenerate it.' +
      '</div>'
    );
  }

  function normalizeData(raw) {
    const nodes = (raw.nodes || []).map(n => ({ ...n, name: n.name || '(unnamed)' }));
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
    const rootNames = new Set(['gpp', 'fpp', 'npp', 'h2o', 'water']);
    data.nodes.forEach(n => {
      const nameLower = n.name.toLowerCase();
      const isH2O = nameLower === 'h2o' || nameLower === 'water';
      if (typeof n.iteration !== 'number') {
        const isRoot = incoming.get(n.id).length === 0 || rootNames.has(nameLower);
        if (isRoot) {
          n.iteration = isH2O ? 1 : 0;
        } else {
          n.iteration = null;
        }
      } else if (isH2O) {
        n.iteration = 1;
      }
    });
    let changed = data.nodes.some(n => n.iteration == null);
    let guard = 0;
    while (changed && guard < 1000) {
      changed = false;
      guard++;
      data.hyperedges.forEach(e => {
        // Filter out H2O/water when propagating levels
        const sourcesToPropagate = e.sources.filter(id => {
          const name = nodesById.get(id).name.toLowerCase();
          return name !== 'h2o' && name !== 'water';
        });
        const activeSources = sourcesToPropagate.length ? sourcesToPropagate : e.sources;

        const srcIters = activeSources.map(id => nodesById.get(id).iteration);
        if (srcIters.length && srcIters.every(v => v != null)) {
          const level = Math.max(...srcIters) + 1;
          e.targets.forEach(tid => {
            const tNode = nodesById.get(tid);
            if (tNode.iteration == null || level < tNode.iteration) {
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
      let firstFree = 0;
      const ordered = [...col].sort((a, b) => {
        const pa = preferredLane(a);
        const pb = preferredLane(b);
        return (pa == null ? Infinity : pa) - (pb == null ? Infinity : pb);
      });
      ordered.forEach(n => {
        let lane = preferredLane(n);
        if (lane == null || occupied.has(lane)) {
          lane = firstFree;
        }
        occupied.add(lane);
        while (occupied.has(firstFree)) firstFree++;
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
      if (typeof e.iteration !== 'number') {
        e.iteration = connected.reduce((m, n) => Math.max(m, n.iteration), 0);
      }
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
    const data = state.view;
    const layout = state.layout;
    const svg = d3.select('#hg-canvas');
    svg.selectAll('*').remove();
    const viewWidth = state.large ? Math.min(layout.width, INITIAL_VIEW_WIDTH) : layout.width;
    const viewHeight = state.large ? Math.min(layout.height, INITIAL_VIEW_HEIGHT) : layout.height;
    svg.attr('viewBox', `0 0 ${viewWidth} ${viewHeight}`)
      .attr('preserveAspectRatio', 'xMinYMin meet');

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
    // Redraws replace the root group. Reset D3's retained zoom state too, so
    // a page/search change cannot make the next gesture jump unexpectedly.
    svg.call(zoom).call(zoom.transform, d3.zoomIdentity);
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

  function getRoundedPath(points, radius) {
    if (points.length < 2) return '';
    if (points.length === 2) {
      return `M${points[0][0]},${points[0][1]} L${points[1][0]},${points[1][1]}`;
    }

    let d = `M${points[0][0]},${points[0][1]}`;
    
    for (let i = 1; i < points.length - 1; i++) {
      const prev = points[i - 1];
      const curr = points[i];
      const next = points[i + 1];

      const dx1 = curr[0] - prev[0];
      const dy1 = curr[1] - prev[1];
      const len1 = Math.sqrt(dx1 * dx1 + dy1 * dy1);

      const dx2 = next[0] - curr[0];
      const dy2 = next[1] - curr[1];
      const len2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);

      if (len1 === 0 || len2 === 0) continue;

      const r = Math.min(radius, len1 / 2, len2 / 2);

      const p1x = curr[0] - (dx1 / len1) * r;
      const p1y = curr[1] - (dy1 / len1) * r;
      const p2x = curr[0] + (dx2 / len2) * r;
      const p2y = curr[1] + (dy2 / len2) * r;

      d += ` L${p1x},${p1y} Q${curr[0]},${curr[1]} ${p2x},${p2y}`;
    }

    d += ` L${points[points.length - 1][0]},${points[points.length - 1][1]}`;
    return d;
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

    const dx = Math.abs(x1 - x0);
    const dy = y1 - y0;
    const absDy = Math.abs(dy);

    let points = [];
    if (absDy === 0) {
      points = [[x0, y0], [x1, y1]];
    } else if (dx >= absDy) {
      const x_mid1 = x0 + (x1 > x0 ? 1 : -1) * (dx - absDy) / 2;
      const x_mid2 = x1 - (x1 > x0 ? 1 : -1) * (dx - absDy) / 2;
      points = [[x0, y0], [x_mid1, y0], [x_mid2, y1], [x1, y1]];
    } else {
      const x_mid = (x0 + x1) / 2;
      points = [[x0, y0], [x_mid, y0], [x_mid, y1], [x1, y1]];
    }

    return getRoundedPath(points, 8);
  }

  // ---------------------------------------------------------------------
  // Pathway highlighting: trace a route from a root molecule (e.g. GPP/FPP)
  // to a chosen target through the hyperedges that were actually reachable.
  // ---------------------------------------------------------------------
  function computePathToTarget(targetId, data = state.data, index = state.index) {
    const { incoming, outgoing } = index;

    const knownRoots = new Set(data.meta.rootIds || []);
    const roots = data.nodes
      .filter(n => knownRoots.has(n.id) || ['gpp', 'fpp', 'h2o', 'water'].includes(n.name.toLowerCase()) ||
        (incoming.get(n.id) || []).length === 0)
      .map(n => n.id);

    // Multi-source BFS: a hyperedge "fires" once all of its sources have
    // been reached, recording the hyperedge that first reached each target.
    const predEdge = new Map();
    const reached = new Set(roots);
    const pending = new Map(data.hyperedges.map(e => [e.id, new Set(e.sources).size]));
    const frontier = [...roots];
    for (let cursor = 0; cursor < frontier.length; cursor++) {
      (outgoing.get(frontier[cursor]) || []).forEach(e => {
        pending.set(e.id, pending.get(e.id) - 1);
        if (pending.get(e.id) === 0) {
          e.targets.forEach(t => {
            if (!reached.has(t)) {
              reached.add(t);
              predEdge.set(t, e);
              frontier.push(t);
            }
          });
        }
      });
    }

    if (!reached.has(targetId)) return null;

    // Walk the predecessor forest backwards from the target. Each non-root
    // node has exactly one predEdge (the hyperedge that first produced it),
    // so following all of its sources keeps the highlighted set connected
    // (e.g. a merge step also highlights the edge that produced each educt).
    const nodes = new Set();
    const visited = new Set();
    const edges = new Set();
    const stack = [targetId];
    while (stack.length) {
      const current = stack.pop();
      if (visited.has(current)) continue;
      visited.add(current);
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
    const leaves = state.view.nodes
      .filter(n => state.large || (state.index.outgoing.get(n.id) || []).length === 0)
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
      ? new Set(data.nodes.filter(n => matchesSearch(n, search)).map(n => n.id))
      : null;

    const highlightNodes = new Set();
    const highlightEdges = new Set();
    if (state.selection) {
      if (state.selection.type === 'node') {
        highlightNodes.add(state.selection.id);
        [...state.index.incoming.get(state.selection.id), ...state.index.outgoing.get(state.selection.id)].forEach(e => {
          if (e.sources.includes(state.selection.id) || e.targets.includes(state.selection.id)) {
            highlightEdges.add(e.id);
            e.sources.forEach(s => highlightNodes.add(s));
            e.targets.forEach(t => highlightNodes.add(t));
          }
        });
      } else if (state.selection.type === 'edge') {
        const edge = state.index.edgesById.get(state.selection.id);
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
    const incomingEdges = state.index.incoming.get(node.id) || [];
    const outgoingEdges = state.index.outgoing.get(node.id) || [];

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
    if (node.pubchemId) {
      const pubchemUrl = `https://pubchem.ncbi.nlm.nih.gov/compound/${encodeURIComponent(node.pubchemId)}`;
      html += `<dt>PubChem</dt><dd><a href="${escapeHtml(pubchemUrl)}" target="_blank" rel="noopener">CID ${escapeHtml(node.pubchemId)}</a>`;
      if (node.pubchemName) html += ` &mdash; ${escapeHtml(node.pubchemName)}`;
      html += '</dd>';
    }
    html += '</dl>';

    if (incomingEdges.length) {
      html += '<p class="hg-label">Produced by</p><ul class="hg-rule-list">';
      incomingEdges.slice(0, 100).forEach(e => {
        html += `<li>${escapeHtml((e.rules || []).join(', ') || e.id)}</li>`;
      });
      html += '</ul>';
      if (incomingEdges.length > 100) html += `<p>Showing 100 of ${incomingEdges.length} incoming reactions.</p>`;
    }
    if (outgoingEdges.length) {
      html += '<p class="hg-label">Reacts via</p><ul class="hg-rule-list">';
      outgoingEdges.slice(0, 100).forEach(e => {
        html += `<li>${escapeHtml((e.rules || []).join(', ') || e.id)}</li>`;
      });
      html += '</ul>';
      if (outgoingEdges.length > 100) html += `<p>Showing 100 of ${outgoingEdges.length} outgoing reactions.</p>`;
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
    if (state.large) text += ` · View: ${state.view.nodes.length} molecules / ${state.view.hyperedges.length} reactions. Search all molecules or use pages; each view includes a limited set of complete reactions.`;
    if (searchNodes) text += ` · ${searchNodes.size} match${searchNodes.size === 1 ? '' : 'es'}`;
    d3.select('#hg-status').text(text);
  }

  function bindControls() {
    populatePathwaySelect();

    let searchTimer;
    d3.select('#hg-search').on('input', event => {
      state.searchTerm = event.target.value;
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        state.page = 0;
        state.pathHighlight = null;
        state.selection = null;
        if (state.large) refreshView();
        else applyFilters();
      }, 180);
    });

    for (const [selector, delta] of [['#hg-prev', -1], ['#hg-next', 1]]) {
      d3.select(selector).on('click', () => {
        state.page += delta;
        state.selection = null;
        refreshView();
        renderPlaceholder();
      });
    }


    d3.select('#hg-pathway').on('change', event => {
      const targetId = event.target.value;
      if (!targetId) {
        state.pathHighlight = null;
        if (state.large) refreshView();
        else applyFilters();
        renderPlaceholder();
        return;
      }
      const path = computePathToTarget(targetId);
      state.pathHighlight = path;
      if (state.large && path) {
        state.searchTerm = '';
        state.page = 0;
        d3.select('#hg-search').property('value', '');
        refreshView();
      } else applyFilters();
      if (path) {
        renderPathwayDetails(state.index.nodesById.get(targetId), path);
      } else {
        d3.select('#hg-details').html(
          '<div class="hg-details-placeholder">No reachable pathway found to this molecule.</div>'
        );
      }
    });

    d3.select('#hg-reset').on('click', () => {
      clearTimeout(searchTimer);
      state.selection = null;
      state.pathHighlight = null;
      state.searchTerm = '';
      state.page = 0;
      d3.select('#hg-search').property('value', '');
      d3.select('#hg-pathway').property('value', '');
      if (state.large) refreshView();
      else {
        state.svg.transition().duration(300).call(state.zoom.transform, d3.zoomIdentity);
        applyFilters();
      }
      renderPlaceholder();
    });
  }

  function renderPathwayDetails(target, path) {
    const steps = [...path.edges]
      .map(id => state.index.edgesById.get(id))
      .sort((a, b) => a.iteration - b.iteration);

    let html = `<h3>Pathway to ${escapeHtml(target.name)}</h3>`;
    html += `<p class="hg-label">${steps.length} reaction step(s)</p>`;
    html += '<ul class="hg-rule-list">';
    if (steps.length > 100) html += '<li>Showing the first 100 steps; use pages to explore the pathway.</li>';
    steps.slice(0, 100).forEach(e => {
      const sources = e.sources.map(id => state.index.nodesById.get(id)?.name || id).join(' + ');
      const targets = e.targets.map(id => state.index.nodesById.get(id)?.name || id).join(' + ');
      const rules = e.rules.length ? e.rules.join(', ') : '(unnamed rule)';
      html += `<li>${escapeHtml(sources)} &rarr; ${escapeHtml(targets)}<br><em>${escapeHtml(rules)}</em></li>`;
    });
    html += '</ul>';
    d3.select('#hg-details').html(html);
  }
})();
