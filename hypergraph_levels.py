"""Shortest derivation levels with AND semantics for reaction reactants."""

import heapq
from itertools import count


def derivation_levels(node_ids, reactions, roots, water_ids=()):
    """Finalize each node once; visit each source/target incidence once.

    A reaction fires after all non-water reactants have a level. Water-only
    reactions still require water. Cycles without a reachable seed stay None.
    Reactions are (sources, targets) pairs; IDs need not be comparable.
    """
    levels = dict.fromkeys(node_ids)
    outgoing = {node_id: [] for node_id in levels}
    water_ids = set(water_ids)
    pending, maxima, products = [], [], []
    for sources, targets in reactions:
        sources = set(sources)
        active = sources - water_ids or sources
        index = len(pending)
        pending.append(len(active))
        maxima.append(0)
        products.append(targets)
        for source in active:
            outgoing[source].append(index)
    serial = count()
    queue = [(level, next(serial), node) for node, level in roots.items()]
    heapq.heapify(queue)
    while queue:
        level, _, node = heapq.heappop(queue)
        if levels[node] is not None:
            continue
        levels[node] = level
        for index in outgoing[node]:
            pending[index] -= 1
            maxima[index] = max(maxima[index], level)
            if pending[index] == 0:
                for target in products[index]:
                    if levels[target] is None:
                        heapq.heappush(queue, (maxima[index] + 1, next(serial), target))
    return levels
