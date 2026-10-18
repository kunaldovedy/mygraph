"""Questions you can ask the database.

Traversal runs inside SQLite with recursive common table expressions, so these
functions are thin and the work stays in the engine.
"""

from __future__ import annotations

import sqlite3
from typing import Any

MAX_DEPTH = 8


def _rows(conn: sqlite3.Connection, sql: str, params: Any = ()) -> list[dict[str, Any]]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def node(conn: sqlite3.Connection, node_id: str) -> dict[str, Any] | None:
    found = _rows(conn, "SELECT * FROM node_full WHERE id = ?", (node_id,))
    return found[0] if found else None


def find(conn: sqlite3.Connection, text: str, limit: int = 20) -> list[dict[str, Any]]:
    """Free-text search over id, label, subtitle and summary."""
    like = f"%{text.lower()}%"
    return _rows(
        conn,
        """
        SELECT id, type, label, subtitle, pagerank FROM node_full
        WHERE lower(id) LIKE ? OR lower(label) LIKE ?
           OR lower(subtitle) LIKE ? OR lower(summary) LIKE ?
        ORDER BY pagerank DESC LIMIT ?
        """,
        (like, like, like, like, limit),
    )


def statements(conn: sqlite3.Connection, node_id: str) -> dict[str, list[dict[str, Any]]]:
    """Everything this node says, and everything said about it."""
    return {
        "out": _rows(
            conn,
            "SELECT * FROM statement WHERE id IN (SELECT id FROM edge WHERE src = ?)"
            " ORDER BY weight DESC, object",
            (node_id,),
        ),
        "in": _rows(
            conn,
            "SELECT * FROM statement WHERE id IN (SELECT id FROM edge WHERE dst = ?)"
            " ORDER BY weight DESC, subject",
            (node_id,),
        ),
    }


def neighbourhood(
    conn: sqlite3.Connection, node_id: str, depth: int = 1, undirected: bool = True
) -> list[dict[str, Any]]:
    """Nodes within `depth` hops, with the hop count."""
    depth = max(1, min(depth, MAX_DEPTH))
    source = "arc" if undirected else "(SELECT src AS a, dst AS b FROM edge)"
    return _rows(
        conn,
        f"""
        WITH RECURSIVE walk(id, hops) AS (
            SELECT ?, 0
            UNION
            SELECT s.b, walk.hops + 1
            FROM {source} s JOIN walk ON s.a = walk.id
            WHERE walk.hops < ?
        )
        SELECT n.id, n.type, n.label, n.subtitle, min(w.hops) AS hops, n.pagerank
        FROM walk w JOIN node_full n ON n.id = w.id
        GROUP BY n.id ORDER BY hops, n.type, n.label
        """,
        (node_id, depth),
    )


def shortest_path(
    conn: sqlite3.Connection, start: str, end: str, undirected: bool = False
) -> list[dict[str, Any]]:
    """One shortest path from start to end, as a list of steps."""
    source = "arc" if undirected else "edge"
    a, b = ("a", "b") if undirected else ("src", "dst")
    row = conn.execute(
        f"""
        WITH RECURSIVE walk(id, hops, trail) AS (
            SELECT ?, 0, ?
            UNION ALL
            SELECT s.{b}, w.hops + 1, w.trail || '>' || s.rel || '>' || s.{b}
            FROM {source} s JOIN walk w ON s.{a} = w.id
            WHERE w.hops < ? AND instr(w.trail, s.{b}) = 0
        )
        SELECT trail, hops FROM walk WHERE id = ? ORDER BY hops LIMIT 1
        """,
        (start, start, MAX_DEPTH, end),
    ).fetchone()
    if row is None:
        return []

    parts = row["trail"].split(">")
    steps: list[dict[str, Any]] = []
    for i in range(0, len(parts) - 1, 2):
        src, rel, dst = parts[i], parts[i + 1], parts[i + 2]
        steps.append(
            {
                "from": src,
                "from_label": _label(conn, src),
                "rel": rel,
                "rel_label": _rel_label(conn, rel),
                "to": dst,
                "to_label": _label(conn, dst),
            }
        )
    return steps


def paths_to(
    conn: sqlite3.Connection, start: str, end: str, limit: int = 12
) -> list[list[str]]:
    """Up to `limit` distinct forward paths from start to end, shortest first."""
    rows = conn.execute(
        """
        WITH RECURSIVE walk(id, hops, trail) AS (
            SELECT ?, 0, ?
            UNION ALL
            SELECT e.dst, w.hops + 1, w.trail || '>' || e.rel || '>' || e.dst
            FROM edge e JOIN walk w ON e.src = w.id
            WHERE w.hops < ? AND instr(w.trail, e.dst) = 0
        )
        SELECT trail, hops FROM walk WHERE id = ? ORDER BY hops LIMIT ?
        """,
        (start, start, MAX_DEPTH, end, limit),
    ).fetchall()
    return [row["trail"].split(">") for row in rows]


def reach(conn: sqlite3.Connection, node_id: str, node_type: str = "audience") -> list[dict[str, Any]]:
    """Every node of a type that this node eventually reaches, with the distance."""
    return _rows(
        conn,
        """
        WITH RECURSIVE walk(id, hops) AS (
            SELECT ?, 0
            UNION
            SELECT e.dst, w.hops + 1 FROM edge e JOIN walk w ON e.src = w.id
            WHERE w.hops < ?
        )
        SELECT n.id, n.label, n.type, min(w.hops) AS hops
        FROM walk w JOIN node_full n ON n.id = w.id
        WHERE n.type = ? AND n.id != ?
        GROUP BY n.id ORDER BY hops, n.label
        """,
        (node_id, MAX_DEPTH, node_type, node_id),
    )


def leaderboard(conn: sqlite3.Connection, measure: str = "pagerank", limit: int = 10) -> list[dict[str, Any]]:
    allowed = {"pagerank", "betweenness", "degree", "audiences_reached", "outcomes_produced"}
    if measure not in allowed:
        raise ValueError(f"measure must be one of {sorted(allowed)}")
    return _rows(
        conn,
        f"SELECT id, type, label, {measure} AS value FROM node_full"
        f" ORDER BY value DESC, label LIMIT ?",
        (limit,),
    )


def stats(conn: sqlite3.Connection) -> dict[str, Any]:
    subject = conn.execute("SELECT value FROM meta WHERE key = 'subject'").fetchone()[0]
    by_type = _rows(
        conn,
        "SELECT t.name AS type, t.plural, t.stage, count(n.id) AS count"
        " FROM node_type t LEFT JOIN node n ON n.type = t.name"
        " GROUP BY t.name ORDER BY t.stage",
    )
    by_rel = _rows(
        conn,
        "SELECT rel, count(*) AS count FROM edge GROUP BY rel ORDER BY count DESC",
    )
    by_source = _rows(
        conn,
        "SELECT source, count(*) AS count FROM node GROUP BY source ORDER BY count DESC",
    )
    unreceived = _rows(
        conn,
        "SELECT id, label FROM node WHERE type = 'outcome' AND id NOT IN"
        " (SELECT src FROM edge WHERE rel = 'received_by') ORDER BY label",
    )
    unserved = _rows(
        conn,
        "SELECT id, label FROM node WHERE type = 'audience' AND id NOT IN"
        " (SELECT dst FROM edge WHERE rel IN ('reaches','serves','received_by'))"
        " ORDER BY label",
    )
    return {
        "subject": subject,
        "nodes": conn.execute("SELECT count(*) FROM node").fetchone()[0],
        "edges": conn.execute("SELECT count(*) FROM edge").fetchone()[0],
        "by_type": by_type,
        "by_rel": by_rel,
        "by_source": by_source,
        "audiences_reached": len(reach(conn, subject, "audience")),
        "outcomes_produced": len(reach(conn, subject, "outcome")),
        "gaps": {"outcomes_with_no_audience": unreceived, "audiences_with_no_channel": unserved},
    }


def _label(conn: sqlite3.Connection, node_id: str) -> str:
    row = conn.execute("SELECT label FROM node WHERE id = ?", (node_id,)).fetchone()
    return row["label"] if row else node_id


def _rel_label(conn: sqlite3.Connection, rel: str) -> str:
    row = conn.execute("SELECT label FROM edge_type WHERE name = ?", (rel,)).fetchone()
    return row["label"] if row else rel
