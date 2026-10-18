"""Graph measures, in plain Python. The graph is small; clarity beats speed.

Four measures, each answering a different question:

    degree       How busy is this node?
    pagerank     How central is it to the whole structure?
    betweenness  How much of the traffic must pass through it?
    reach        How many audiences does it end up serving?
"""

from __future__ import annotations

from collections import deque
from typing import Iterable

from .model import Graph


def adjacency(graph: Graph, weighted: bool = True) -> dict[str, list[tuple[str, float]]]:
    out: dict[str, list[tuple[str, float]]] = {n.id: [] for n in graph.nodes}
    for edge in graph.edges:
        out[edge.src].append((edge.dst, edge.weight if weighted else 1.0))
    return out


def degrees(graph: Graph) -> dict[str, dict[str, float]]:
    result = {
        n.id: {"in_degree": 0.0, "out_degree": 0.0, "degree": 0.0} for n in graph.nodes
    }
    for edge in graph.edges:
        result[edge.src]["out_degree"] += edge.weight
        result[edge.dst]["in_degree"] += edge.weight
    for row in result.values():
        row["degree"] = row["in_degree"] + row["out_degree"]
    return result


def pagerank(
    graph: Graph, damping: float = 0.85, iterations: int = 100, tolerance: float = 1e-10
) -> dict[str, float]:
    """Weighted PageRank. Dangling nodes spread their rank over everyone."""
    ids = [n.id for n in graph.nodes]
    count = len(ids)
    if count == 0:
        return {}
    adj = adjacency(graph)
    totals = {nid: sum(w for _, w in edges) for nid, edges in adj.items()}
    rank = {nid: 1.0 / count for nid in ids}

    for _ in range(iterations):
        leaked = sum(rank[nid] for nid in ids if totals[nid] == 0.0)
        nxt = {nid: (1.0 - damping) / count + damping * leaked / count for nid in ids}
        for nid in ids:
            if totals[nid] == 0.0:
                continue
            share = damping * rank[nid] / totals[nid]
            for dst, weight in adj[nid]:
                nxt[dst] += share * weight
        delta = sum(abs(nxt[nid] - rank[nid]) for nid in ids)
        rank = nxt
        if delta < tolerance:
            break
    return rank


def betweenness(graph: Graph) -> dict[str, float]:
    """Brandes betweenness on the directed, unweighted graph, normalised to 0..1."""
    ids = [n.id for n in graph.nodes]
    adj = {nid: [dst for dst, _ in edges] for nid, edges in adjacency(graph).items()}
    score = {nid: 0.0 for nid in ids}

    for source in ids:
        stack: list[str] = []
        paths: dict[str, list[str]] = {nid: [] for nid in ids}
        sigma = {nid: 0.0 for nid in ids}
        dist = {nid: -1 for nid in ids}
        sigma[source] = 1.0
        dist[source] = 0
        queue = deque([source])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in adj[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    paths[w].append(v)
        delta = {nid: 0.0 for nid in ids}
        while stack:
            w = stack.pop()
            for v in paths[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w]) if sigma[w] else 0.0
            if w != source:
                score[w] += delta[w]

    count = len(ids)
    scale = 1.0 / ((count - 1) * (count - 2)) if count > 2 else 1.0
    return {nid: value * scale for nid, value in score.items()}


def reachable(graph: Graph, start: str, node_types: Iterable[str] | None = None) -> set[str]:
    """Every node reachable from start by following edges forward."""
    wanted = set(node_types) if node_types else None
    adj = {nid: [dst for dst, _ in edges] for nid, edges in adjacency(graph).items()}
    seen: set[str] = set()
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in adj.get(current, ()):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    index = graph.index
    if wanted is None:
        return seen
    return {nid for nid in seen if index[nid].type in wanted}


def all_metrics(graph: Graph) -> dict[str, dict[str, float]]:
    """One row of numbers per node, ready for the database and the page."""
    deg = degrees(graph)
    rank = pagerank(graph)
    between = betweenness(graph)
    ontology = graph.ontology
    rows: dict[str, dict[str, float]] = {}
    for node in graph.nodes:
        served = reachable(graph, node.id, node_types=["audience"])
        outcomes = reachable(graph, node.id, node_types=["outcome"])
        rows[node.id] = {
            **deg[node.id],
            "pagerank": rank[node.id],
            "betweenness": between[node.id],
            "audiences_reached": float(len(served)),
            "outcomes_produced": float(len(outcomes)),
            "stage": float(ontology.stage_of(node.type)),
        }
    return rows
