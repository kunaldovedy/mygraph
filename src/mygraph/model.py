"""Load and validate the YAML source of truth.

The data files are the graph. Everything else in this package is derived and can
be deleted and rebuilt.
"""

from __future__ import annotations

import dataclasses
import pathlib
import re
from typing import Any, Iterable

import yaml

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ValidationError(Exception):
    """Raised when the data files do not describe a usable graph."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        super().__init__(
            "%d problem(s) in the graph data:\n  - %s"
            % (len(problems), "\n  - ".join(problems))
        )


@dataclasses.dataclass(frozen=True)
class NodeType:
    name: str
    label: str
    plural: str
    stage: int
    glyph: str
    palette: str
    question: str = ""


@dataclasses.dataclass(frozen=True)
class EdgeType:
    name: str
    label: str
    kind: str  # forward | return
    from_types: tuple[str, ...]
    to_types: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class Ontology:
    meta: dict[str, Any]
    node_types: dict[str, NodeType]
    edge_types: dict[str, EdgeType]
    sources: dict[str, str]
    confidence_levels: tuple[str, ...]

    @property
    def subject(self) -> str:
        return str(self.meta.get("subject", "me"))

    def stage_of(self, node_type: str) -> int:
        return self.node_types[node_type].stage

    @property
    def stage_count(self) -> int:
        return max(t.stage for t in self.node_types.values()) + 1

    @classmethod
    def load(cls, path: pathlib.Path) -> "Ontology":
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        node_types = {
            name: NodeType(
                name=name,
                label=spec.get("label", name.title()),
                plural=spec.get("plural", name.title() + "s"),
                stage=int(spec["stage"]),
                glyph=spec.get("glyph", "circle"),
                palette=spec.get("palette", "blue"),
                question=spec.get("question", ""),
            )
            for name, spec in (raw.get("node_types") or {}).items()
        }
        edge_types = {
            name: EdgeType(
                name=name,
                label=spec.get("label", name.replace("_", " ")),
                kind=spec.get("kind", "forward"),
                from_types=tuple(spec.get("from") or ()),
                to_types=tuple(spec.get("to") or ()),
            )
            for name, spec in (raw.get("edge_types") or {}).items()
        }
        return cls(
            meta=raw.get("meta") or {},
            node_types=node_types,
            edge_types=edge_types,
            sources=raw.get("sources") or {},
            confidence_levels=tuple(raw.get("confidence_levels") or ()),
        )


@dataclasses.dataclass
class Node:
    id: str
    type: str
    label: str
    subtitle: str = ""
    summary: str = ""
    source: str = "self"
    confidence: str = "medium"
    refs: list[str] = dataclasses.field(default_factory=list)
    props: dict[str, Any] = dataclasses.field(default_factory=dict)
    origin: str = ""  # file the node was read from

    def as_row(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "subtitle": self.subtitle,
            "summary": " ".join(self.summary.split()),
            "source": self.source,
            "confidence": self.confidence,
            "refs": list(self.refs),
            "props": dict(self.props),
        }


@dataclasses.dataclass
class Edge:
    src: str
    rel: str
    dst: str
    weight: float = 1.0
    note: str = ""
    source: str = "self"
    confidence: str = "medium"
    origin: str = ""

    @property
    def id(self) -> str:
        return f"{self.src}|{self.rel}|{self.dst}"

    def as_row(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "src": self.src,
            "rel": self.rel,
            "dst": self.dst,
            "weight": float(self.weight),
            "note": " ".join(self.note.split()),
            "source": self.source,
            "confidence": self.confidence,
        }


@dataclasses.dataclass
class Graph:
    ontology: Ontology
    nodes: list[Node]
    edges: list[Edge]

    # ---------------------------------------------------------------- lookups
    def node(self, node_id: str) -> Node:
        return self.index[node_id]

    @property
    def index(self) -> dict[str, Node]:
        if not hasattr(self, "_index") or len(self._index) != len(self.nodes):
            self._index = {n.id: n for n in self.nodes}
        return self._index

    def out_edges(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges if e.src == node_id]

    def in_edges(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges if e.dst == node_id]

    def by_type(self, node_type: str) -> list[Node]:
        return [n for n in self.nodes if n.type == node_type]

    def stage_of(self, node_id: str) -> int:
        return self.ontology.stage_of(self.index[node_id].type)

    # ------------------------------------------------------------- validation
    def validate(self) -> list[str]:
        problems: list[str] = []
        ont = self.ontology
        seen: dict[str, str] = {}

        for node in self.nodes:
            where = f"{node.origin or '<memory>'}:{node.id}"
            if not ID_RE.match(node.id):
                problems.append(f"{where}: id must be lower-case-kebab-case")
            if node.id in seen:
                problems.append(f"{where}: duplicate id, already defined in {seen[node.id]}")
            seen[node.id] = node.origin or "<memory>"
            if node.type not in ont.node_types:
                problems.append(f"{where}: unknown node type {node.type!r}")
            if not node.label:
                problems.append(f"{where}: label is required")
            if ont.sources and node.source not in ont.sources:
                problems.append(f"{where}: unknown source {node.source!r}")
            if ont.confidence_levels and node.confidence not in ont.confidence_levels:
                problems.append(f"{where}: unknown confidence {node.confidence!r}")

        ids = set(seen)
        edge_ids: set[str] = set()
        for edge in self.edges:
            where = f"{edge.origin or '<memory>'}:{edge.id}"
            if edge.rel not in ont.edge_types:
                problems.append(f"{where}: unknown relation {edge.rel!r}")
            if edge.src not in ids:
                problems.append(f"{where}: src {edge.src!r} is not a node")
            if edge.dst not in ids:
                problems.append(f"{where}: dst {edge.dst!r} is not a node")
            if edge.src == edge.dst:
                problems.append(f"{where}: an edge must not loop onto its own node")
            if edge.id in edge_ids:
                problems.append(f"{where}: duplicate edge")
            edge_ids.add(edge.id)
            if edge.weight <= 0:
                problems.append(f"{where}: weight must be greater than zero")

            spec = ont.edge_types.get(edge.rel)
            if spec and edge.src in ids and edge.dst in ids:
                src_type = self.index[edge.src].type
                dst_type = self.index[edge.dst].type
                if spec.from_types and src_type not in spec.from_types:
                    problems.append(
                        f"{where}: {edge.rel!r} may not start at a {src_type}"
                        f" (allowed: {', '.join(spec.from_types)})"
                    )
                if spec.to_types and dst_type not in spec.to_types:
                    problems.append(
                        f"{where}: {edge.rel!r} may not end at a {dst_type}"
                        f" (allowed: {', '.join(spec.to_types)})"
                    )

        # A service graph with a node nobody can reach is usually a typo.
        connected = {e.src for e in self.edges} | {e.dst for e in self.edges}
        for node in self.nodes:
            if node.id not in connected:
                problems.append(
                    f"{node.origin or '<memory>'}:{node.id}: no edges — it serves nobody"
                )
        return problems

    def validate_or_raise(self) -> "Graph":
        problems = self.validate()
        if problems:
            raise ValidationError(problems)
        return self


def _read_yaml_list(path: pathlib.Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return []
    if not isinstance(data, list):
        raise ValidationError([f"{path}: expected a YAML list at the top level"])
    return data


def _yaml_files(*dirs: pathlib.Path) -> Iterable[pathlib.Path]:
    for directory in dirs:
        if directory.is_dir():
            yield from sorted(directory.rglob("*.yaml"))
            yield from sorted(directory.rglob("*.yml"))


def load_graph(root: pathlib.Path | str = ".") -> Graph:
    """Read schema/ontology.yaml plus every file under data/ into a Graph.

    data/private/ is read when it exists and is ignored by git, so private
    material never has to be committed to see it in the graph.
    """
    root = pathlib.Path(root)
    ontology = Ontology.load(root / "schema" / "ontology.yaml")

    nodes: list[Node] = []
    edges: list[Edge] = []
    known_node_fields = {f.name for f in dataclasses.fields(Node)} - {"origin"}
    known_edge_fields = {f.name for f in dataclasses.fields(Edge)} - {"origin"}

    for path in _yaml_files(root / "data" / "nodes", root / "data" / "private" / "nodes"):
        rel = path.relative_to(root).as_posix()
        for item in _read_yaml_list(path):
            extra = set(item) - known_node_fields
            if extra:
                raise ValidationError([f"{rel}: unknown node field(s) {sorted(extra)}"])
            nodes.append(Node(origin=rel, **item))

    for path in _yaml_files(root / "data" / "edges", root / "data" / "private" / "edges"):
        rel = path.relative_to(root).as_posix()
        for item in _read_yaml_list(path):
            extra = set(item) - known_edge_fields
            if extra:
                raise ValidationError([f"{rel}: unknown edge field(s) {sorted(extra)}"])
            edges.append(Edge(origin=rel, **item))

    return Graph(ontology=ontology, nodes=nodes, edges=edges)
