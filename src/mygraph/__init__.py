"""mygraph — a service graph: how one person serves the world.

The package has four parts:

    model    load the YAML source of truth and validate it
    db       write it into a SQLite property graph
    metrics  degree, PageRank, betweenness, reach
    export   graph.json, Cypher, GraphML, Mermaid, single-file HTML
"""

__version__ = "1.0.0"

from .model import Graph, Node, Edge, Ontology, load_graph  # noqa: F401
