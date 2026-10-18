"""The SQLite property graph.

SQLite is the whole database: no server, one file, and recursive common table
expressions do the traversal. The file is disposable — `mygraph build` writes it
again from the YAML in a fraction of a second.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3

from .metrics import all_metrics
from .model import Graph

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE node_type (
    name     TEXT PRIMARY KEY,
    label    TEXT NOT NULL,
    plural   TEXT NOT NULL,
    stage    INTEGER NOT NULL,
    glyph    TEXT NOT NULL,
    palette  TEXT NOT NULL,
    question TEXT NOT NULL DEFAULT ''
);

CREATE TABLE edge_type (
    name       TEXT PRIMARY KEY,
    label      TEXT NOT NULL,
    kind       TEXT NOT NULL CHECK (kind IN ('forward', 'return')),
    from_types TEXT NOT NULL,
    to_types   TEXT NOT NULL
);

CREATE TABLE node (
    id         TEXT PRIMARY KEY,
    type       TEXT NOT NULL REFERENCES node_type(name),
    label      TEXT NOT NULL,
    subtitle   TEXT NOT NULL DEFAULT '',
    summary    TEXT NOT NULL DEFAULT '',
    source     TEXT NOT NULL,
    confidence TEXT NOT NULL,
    refs       TEXT NOT NULL DEFAULT '[]',   -- JSON array
    props      TEXT NOT NULL DEFAULT '{}',   -- JSON object
    origin     TEXT NOT NULL DEFAULT ''
);

CREATE TABLE edge (
    id         TEXT PRIMARY KEY,
    src        TEXT NOT NULL REFERENCES node(id),
    rel        TEXT NOT NULL REFERENCES edge_type(name),
    dst        TEXT NOT NULL REFERENCES node(id),
    weight     REAL NOT NULL DEFAULT 1.0,
    note       TEXT NOT NULL DEFAULT '',
    source     TEXT NOT NULL,
    confidence TEXT NOT NULL,
    origin     TEXT NOT NULL DEFAULT ''
);

CREATE TABLE node_metric (
    node_id           TEXT PRIMARY KEY REFERENCES node(id),
    stage             INTEGER NOT NULL,
    in_degree         REAL NOT NULL,
    out_degree        REAL NOT NULL,
    degree            REAL NOT NULL,
    pagerank          REAL NOT NULL,
    betweenness       REAL NOT NULL,
    audiences_reached INTEGER NOT NULL,
    outcomes_produced INTEGER NOT NULL
);

CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);

CREATE INDEX edge_src_idx ON edge(src);
CREATE INDEX edge_dst_idx ON edge(dst);
CREATE INDEX edge_rel_idx ON edge(rel);
CREATE INDEX node_type_idx ON node(type);

-- Every edge in both directions, so a traversal can run either way.
CREATE VIEW arc AS
    SELECT id, src AS a, dst AS b, rel, weight, 'out' AS direction FROM edge
    UNION ALL
    SELECT id, dst AS a, src AS b, rel, weight, 'in'  AS direction FROM edge;

-- A node with its numbers and its type, which is what every report wants.
CREATE VIEW node_full AS
    SELECT n.*, t.stage, t.glyph, t.palette, t.label AS type_label,
           m.degree, m.pagerank, m.betweenness,
           m.audiences_reached, m.outcomes_produced
    FROM node n
    JOIN node_type t ON t.name = n.type
    LEFT JOIN node_metric m ON m.node_id = n.id;

-- Readable edges: "Kunal Dovedy practices Creating interactive art and music".
CREATE VIEW statement AS
    SELECT e.id, s.label AS subject, t.label AS verb, o.label AS object,
           e.rel, e.weight, e.note, e.source, e.confidence,
           s.type AS src_type, o.type AS dst_type, t.kind
    FROM edge e
    JOIN node s ON s.id = e.src
    JOIN node o ON o.id = e.dst
    JOIN edge_type t ON t.name = e.rel;
"""


def connect(path: pathlib.Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def build(graph: Graph, path: pathlib.Path | str) -> pathlib.Path:
    """Write the graph to a fresh SQLite file and return its path."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ("", "-wal", "-shm"):
        stale = path.with_name(path.name + suffix)
        if stale.exists():
            stale.unlink()

    conn = connect(path)
    with conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO node_type VALUES (:name,:label,:plural,:stage,:glyph,:palette,:question)",
            [vars(t) for t in graph.ontology.node_types.values()],
        )
        conn.executemany(
            "INSERT INTO edge_type VALUES (:name,:label,:kind,:from_types,:to_types)",
            [
                {
                    "name": t.name,
                    "label": t.label,
                    "kind": t.kind,
                    "from_types": json.dumps(list(t.from_types)),
                    "to_types": json.dumps(list(t.to_types)),
                }
                for t in graph.ontology.edge_types.values()
            ],
        )
        conn.executemany(
            "INSERT INTO node VALUES (:id,:type,:label,:subtitle,:summary,:source,"
            ":confidence,:refs,:props,:origin)",
            [
                {**n.as_row(), "refs": json.dumps(n.refs), "props": json.dumps(n.props),
                 "origin": n.origin}
                for n in graph.nodes
            ],
        )
        conn.executemany(
            "INSERT INTO edge VALUES (:id,:src,:rel,:dst,:weight,:note,:source,"
            ":confidence,:origin)",
            [{**e.as_row(), "origin": e.origin} for e in graph.edges],
        )
        metrics = all_metrics(graph)
        conn.executemany(
            "INSERT INTO node_metric VALUES (:node_id,:stage,:in_degree,:out_degree,"
            ":degree,:pagerank,:betweenness,:audiences_reached,:outcomes_produced)",
            [
                {
                    "node_id": nid,
                    "stage": int(row["stage"]),
                    "in_degree": row["in_degree"],
                    "out_degree": row["out_degree"],
                    "degree": row["degree"],
                    "pagerank": row["pagerank"],
                    "betweenness": row["betweenness"],
                    "audiences_reached": int(row["audiences_reached"]),
                    "outcomes_produced": int(row["outcomes_produced"]),
                }
                for nid, row in metrics.items()
            ],
        )
        conn.executemany(
            "INSERT INTO meta VALUES (?,?)",
            [
                ("name", str(graph.ontology.meta.get("name", "mygraph"))),
                ("subject", graph.ontology.subject),
                ("nodes", str(len(graph.nodes))),
                ("edges", str(len(graph.edges))),
            ],
        )
    conn.close()
    return path
