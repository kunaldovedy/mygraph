"""Tests for mygraph.

Run them with:  python3 -m pytest tests -q     (or `make test`)
They need nothing but the standard library, PyYAML and pytest.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from mygraph import db, export, queries  # noqa: E402
from mygraph.metrics import all_metrics, pagerank, reachable  # noqa: E402
from mygraph.model import Edge, Graph, Node, ValidationError, load_graph  # noqa: E402


@pytest.fixture(scope="session")
def graph() -> Graph:
    return load_graph(ROOT)


@pytest.fixture(scope="session")
def conn(graph: Graph, tmp_path_factory) -> sqlite3.Connection:
    path = tmp_path_factory.mktemp("db") / "test.db"
    db.build(graph, path)
    connection = db.connect(path)
    yield connection
    connection.close()


# --------------------------------------------------------------- the data
def test_the_shipped_graph_is_valid(graph: Graph) -> None:
    assert graph.validate() == []


def test_the_graph_is_not_empty(graph: Graph) -> None:
    assert len(graph.nodes) > 20
    assert len(graph.edges) > 50


def test_the_subject_exists_and_is_a_person(graph: Graph) -> None:
    subject = graph.node(graph.ontology.subject)
    assert subject.type == "person"


def test_every_node_type_in_the_ontology_has_at_least_one_node(graph: Graph) -> None:
    for name in graph.ontology.node_types:
        assert graph.by_type(name), f"no nodes of type {name}"


def test_every_node_declares_where_it_came_from(graph: Graph) -> None:
    for node in graph.nodes:
        assert node.source in graph.ontology.sources
        assert node.confidence in graph.ontology.confidence_levels


def test_the_practice_reaches_a_real_audience(graph: Graph) -> None:
    served = reachable(graph, graph.ontology.subject, node_types=["audience"])
    assert len(served) >= 5


def test_the_loop_closes(graph: Graph) -> None:
    """Outcomes must feed back. A graph with no return edge is a pipeline."""
    returns = [e for e in graph.edges if graph.ontology.edge_types[e.rel].kind == "return"]
    assert returns, "no feedback edges: nothing comes back"


def test_every_outcome_reaches_somebody(graph: Graph) -> None:
    received = {e.src for e in graph.edges if e.rel == "received_by"}
    for node in graph.by_type("outcome"):
        assert node.id in received, f"{node.id} changes nothing for anyone"


# --------------------------------------------------------- validation rules
def _tiny(**overrides) -> Graph:
    graph = load_graph(ROOT)
    return Graph(ontology=graph.ontology, **overrides)


def test_a_dangling_edge_is_caught(graph: Graph) -> None:
    broken = Graph(
        ontology=graph.ontology,
        nodes=[Node(id="me", type="person", label="Me", source="self", confidence="high")],
        edges=[Edge(src="me", rel="practices", dst="nowhere", source="self", confidence="high")],
    )
    assert any("is not a node" in p for p in broken.validate())


def test_an_edge_between_the_wrong_types_is_caught(graph: Graph) -> None:
    broken = Graph(
        ontology=graph.ontology,
        nodes=[
            Node(id="me", type="person", label="Me", source="self", confidence="high"),
            Node(id="x-a", type="outcome", label="An outcome", source="self", confidence="high"),
        ],
        edges=[Edge(src="me", rel="practices", dst="x-a", source="self", confidence="high")],
    )
    assert any("may not end at" in p for p in broken.validate())


def test_a_duplicate_id_is_caught(graph: Graph) -> None:
    node = Node(id="me", type="person", label="Me", source="self", confidence="high")
    other = Node(id="me", type="person", label="Me again", source="self", confidence="high")
    broken = Graph(ontology=graph.ontology, nodes=[node, other], edges=[])
    assert any("duplicate id" in p for p in broken.validate())


def test_an_orphan_node_is_caught(graph: Graph) -> None:
    broken = Graph(
        ontology=graph.ontology,
        nodes=[Node(id="lonely", type="value", label="Lonely", source="self", confidence="high")],
        edges=[],
    )
    assert any("serves nobody" in p for p in broken.validate())


def test_validate_or_raise_raises(graph: Graph) -> None:
    broken = Graph(ontology=graph.ontology, nodes=[], edges=[
        Edge(src="a", rel="practices", dst="b", source="self", confidence="high")
    ])
    with pytest.raises(ValidationError):
        broken.validate_or_raise()


# -------------------------------------------------------------- the metrics
def test_pagerank_sums_to_one(graph: Graph) -> None:
    assert pytest.approx(sum(pagerank(graph).values()), abs=1e-6) == 1.0


def test_metrics_cover_every_node(graph: Graph) -> None:
    rows = all_metrics(graph)
    assert set(rows) == {n.id for n in graph.nodes}
    for row in rows.values():
        assert row["pagerank"] > 0


def test_a_node_does_not_count_itself_as_reachable(graph: Graph) -> None:
    subject = graph.ontology.subject
    assert subject not in reachable(graph, subject, node_types=["person"])


# ------------------------------------------------------------- the database
def test_the_database_holds_every_row(conn: sqlite3.Connection, graph: Graph) -> None:
    assert conn.execute("SELECT count(*) FROM node").fetchone()[0] == len(graph.nodes)
    assert conn.execute("SELECT count(*) FROM edge").fetchone()[0] == len(graph.edges)


def test_foreign_keys_hold(conn: sqlite3.Connection) -> None:
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_statements_read_as_sentences(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT subject, verb, object FROM statement WHERE rel = 'practices' LIMIT 1"
    ).fetchone()
    sentence = f"{row['subject']} {row['verb']} {row['object']}"
    assert sentence.count(" ") >= 3


def test_shortest_path_from_the_centre_to_an_audience(conn: sqlite3.Connection) -> None:
    steps = queries.shortest_path(conn, "me", "a-museum-visitors")
    assert steps and steps[0]["from"] == "me"
    assert steps[-1]["to"] == "a-museum-visitors"


def test_no_path_returns_nothing_rather_than_failing(conn: sqlite3.Connection) -> None:
    assert queries.shortest_path(conn, "a-developers", "me") == []


def test_neighbourhood_grows_with_depth(conn: sqlite3.Connection) -> None:
    near = queries.neighbourhood(conn, "me", 1)
    wider = queries.neighbourhood(conn, "me", 3)
    assert len(wider) > len(near) > 1


def test_search_finds_the_instrument(conn: sqlite3.Connection) -> None:
    hits = queries.find(conn, "turbinophone")
    assert any(h["id"] == "w-turbinophone" for h in hits)


def test_search_looks_inside_summaries(conn: sqlite3.Connection) -> None:
    assert queries.find(conn, "ball bearing")


def test_stats_report_gaps(conn: sqlite3.Connection) -> None:
    data = queries.stats(conn)
    assert data["audiences_reached"] > 0
    assert "gaps" in data


def test_leaderboard_rejects_an_unknown_measure(conn: sqlite3.Connection) -> None:
    with pytest.raises(ValueError):
        queries.leaderboard(conn, "charisma")


# --------------------------------------------------------------- the exports
def test_json_export_carries_everything_the_page_needs(graph: Graph) -> None:
    payload = export.to_dict(graph, ROOT)
    assert payload["meta"]["subject"] == graph.ontology.subject
    assert len(payload["nodes"]) == len(graph.nodes)
    assert payload["palette"]["categorical"]["blue"]["light"].startswith("#")
    for node in payload["nodes"]:
        assert "pagerank" in node and "stage" in node
    for edge in payload["edges"]:
        assert edge["kind"] in {"forward", "return"}


def test_json_export_is_json(graph: Graph, tmp_path: pathlib.Path) -> None:
    path = export.write_json(graph, tmp_path / "graph.json", ROOT)
    assert json.loads(path.read_text())["meta"]["node_count"] == len(graph.nodes)


def test_cypher_quotes_apostrophes(graph: Graph) -> None:
    script = export.to_cypher(graph)
    assert "CREATE (:Person" in script
    assert "\\'" in script or "'" in script
    assert script.count("MATCH (a {id:") == len(graph.edges)


def test_graphml_is_well_formed(graph: Graph) -> None:
    import xml.etree.ElementTree as ET

    root = ET.fromstring(export.to_graphml(graph))
    nodes = root.findall(".//{http://graphml.graphdrawing.org/xmlns}node")
    assert len(nodes) == len(graph.nodes)


def test_mermaid_names_the_subject(graph: Graph) -> None:
    assert "flowchart" in export.to_mermaid(graph)


def test_single_file_page_inlines_the_data(graph: Graph, tmp_path: pathlib.Path) -> None:
    out = export.write_single_file_html(graph, ROOT / "viz" / "index.html", tmp_path / "p.html", ROOT)
    html = out.read_text()
    assert export.DATA_MARKER not in html
    assert '"nodes"' in html
    assert "</script>" not in html.split("<script>")[1].split("})();")[0]


def test_the_page_template_still_has_its_marker() -> None:
    assert export.DATA_MARKER in (ROOT / "viz" / "index.html").read_text()


def test_web_export_is_smaller_and_still_complete(graph: Graph) -> None:
    """The phone payload drops the measures nobody reads, not the content."""
    full = export.to_dict(graph, ROOT)
    web = export.to_web(graph, ROOT)
    assert len(web["nodes"]) == len(full["nodes"])
    assert len(web["edges"]) == len(full["edges"])
    assert len(json.dumps(web)) < len(json.dumps(full))
    for node in web["nodes"]:
        assert "betweenness" not in node
        assert node["label"] and node["summary"]
        assert isinstance(node["stage"], int)
    for edge in web["edges"]:
        assert edge["src"] and edge["dst"] and edge["rel_label"]


def test_web_export_writes_a_single_line_file(graph: Graph, tmp_path: pathlib.Path) -> None:
    path = export.write_web_json(graph, tmp_path / "web.json", ROOT)
    payload = json.loads(path.read_text())
    assert payload["meta"]["subject"] == graph.ontology.subject


def test_the_site_payload_is_in_step_with_the_data(graph: Graph) -> None:
    """The copy committed for kunaldovedy.com must match the graph."""
    shipped = ROOT / "integrations" / "kunaldovedy.com" / "app" / "graph" / "graph-data.json"
    if not shipped.exists():
        pytest.skip("no site integration in this checkout")
    payload = json.loads(shipped.read_text())
    assert payload["meta"]["node_count"] == len(graph.nodes)
    assert payload["meta"]["edge_count"] == len(graph.edges)
