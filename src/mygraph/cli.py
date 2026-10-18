"""The mygraph command line.

    mygraph build                 validate, write the database, write the page
    mygraph check                 validate only
    mygraph stats                 counts, gaps and leaders
    mygraph node <id>             one node and every statement about it
    mygraph find <text>           search
    mygraph path <a> <b>          shortest path
    mygraph reach [id]            audiences reached, and how far away they are
    mygraph top [measure]         leaderboard
    mygraph export <format>       json | web | cypher | graphml | mermaid | html
    mygraph serve                 open the visualisation on localhost
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import pathlib
import socketserver
import sys
import webbrowser

from . import db, export, queries
from .model import ValidationError, load_graph

DEFAULT_DB = pathlib.Path("build/mygraph.db")
DEFAULT_JSON = pathlib.Path("build/graph.json")
DEFAULT_HTML = pathlib.Path("build/mygraph.html")
TEMPLATE = pathlib.Path("viz/index.html")


def _root(args: argparse.Namespace) -> pathlib.Path:
    return pathlib.Path(args.root)


def _load(args: argparse.Namespace):
    graph = load_graph(_root(args))
    graph.validate_or_raise()
    return graph


def _conn(args: argparse.Namespace):
    path = _root(args) / DEFAULT_DB
    if not path.exists():
        raise SystemExit(f"{path} is missing. Run `mygraph build` first.")
    return db.connect(path)


# ----------------------------------------------------------------- commands
def cmd_check(args: argparse.Namespace) -> int:
    graph = load_graph(_root(args))
    problems = graph.validate()
    if problems:
        print(f"{len(problems)} problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"ok — {len(graph.nodes)} nodes, {len(graph.edges)} edges, no problems")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    root = _root(args)
    graph = _load(args)
    database = db.build(graph, root / DEFAULT_DB)
    payload = export.write_json(graph, root / DEFAULT_JSON, root)
    print(f"database  {database}")
    print(f"data      {payload}")
    template = root / TEMPLATE
    if template.exists():
        page = export.write_single_file_html(graph, template, root / DEFAULT_HTML, root)
        print(f"page      {page}")
    print(f"built     {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    with _conn(args) as conn:
        data = queries.stats(conn)
        if args.json:
            print(json.dumps(data, indent=2))
            return 0
        subject = queries.node(conn, data["subject"])
        print(f"{(subject or {}).get('label', data['subject'])} — service graph")
        print(f"  {data['nodes']} nodes, {data['edges']} edges")
        print(f"  {data['audiences_reached']} audiences reached,"
              f" {data['outcomes_produced']} outcomes produced")
        print("\nby stage")
        for row in data["by_type"]:
            print(f"  {row['stage']}  {row['plural']:<14} {row['count']:>3}")
        print("\nby provenance")
        for row in data["by_source"]:
            print(f"  {row['source']:<16} {row['count']:>3}")
        print("\nmost central")
        for row in queries.leaderboard(conn, "pagerank", 8):
            print(f"  {row['value']:.4f}  {row['label']}  ({row['type']})")
        gaps = data["gaps"]
        if gaps["outcomes_with_no_audience"] or gaps["audiences_with_no_channel"]:
            print("\ngaps to fill")
            for row in gaps["outcomes_with_no_audience"]:
                print(f"  outcome reaches nobody: {row['label']}")
            for row in gaps["audiences_with_no_channel"]:
                print(f"  audience has no channel: {row['label']}")
    return 0


def cmd_node(args: argparse.Namespace) -> int:
    with _conn(args) as conn:
        found = queries.node(conn, args.id)
        if not found:
            matches = queries.find(conn, args.id, 5)
            print(f"no node {args.id!r}." + (" Did you mean:" if matches else ""))
            for row in matches:
                print(f"  {row['id']}  {row['label']}")
            return 1
        if args.json:
            print(json.dumps({**found, "statements": queries.statements(conn, args.id)}, indent=2))
            return 0
        print(f"{found['label']}  [{found['type']}]")
        if found["subtitle"]:
            print(f"  {found['subtitle']}")
        if found["summary"]:
            print(f"\n  {found['summary']}")
        print(f"\n  source {found['source']} / confidence {found['confidence']}")
        print(f"  pagerank {found['pagerank']:.4f}   audiences reached"
              f" {found['audiences_reached']}")
        for ref in json.loads(found["refs"] or "[]"):
            print(f"  ref {ref}")
        for key, value in json.loads(found["props"] or "{}").items():
            print(f"  {key.replace('_', ' ')}: {value}")
        sides = queries.statements(conn, args.id)
        if sides["out"]:
            print("\n  outward")
            for row in sides["out"]:
                note = f"  — {row['note']}" if row["note"] else ""
                print(f"    {row['verb']} {row['object']}{note}")
        if sides["in"]:
            print("\n  inward")
            for row in sides["in"]:
                print(f"    {row['subject']} {row['verb']} this")
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    with _conn(args) as conn:
        rows = queries.find(conn, args.text, args.limit)
        if not rows:
            print("nothing found")
            return 1
        for row in rows:
            subtitle = f" — {row['subtitle']}" if row["subtitle"] else ""
            print(f"{row['id']:<28} {row['type']:<11} {row['label']}{subtitle}")
    return 0


def cmd_path(args: argparse.Namespace) -> int:
    with _conn(args) as conn:
        steps = queries.shortest_path(conn, args.start, args.end, undirected=args.undirected)
        if not steps:
            print(f"no path from {args.start} to {args.end}"
                  + ("" if args.undirected else " — try --undirected"))
            return 1
        print(steps[0]["from_label"])
        for step in steps:
            print(f"  {step['rel_label']} -> {step['to_label']}")
    return 0


def cmd_reach(args: argparse.Namespace) -> int:
    with _conn(args) as conn:
        start = args.id or queries.stats(conn)["subject"]
        rows = queries.reach(conn, start, args.type)
        label = (queries.node(conn, start) or {}).get("label", start)
        print(f"{label} reaches {len(rows)} {args.type}(s):")
        for row in rows:
            print(f"  {row['hops']} hops  {row['label']}")
    return 0


def cmd_top(args: argparse.Namespace) -> int:
    with _conn(args) as conn:
        for row in queries.leaderboard(conn, args.measure, args.limit):
            print(f"{row['value']:>10.4f}  {row['label']}  ({row['type']})")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    root = _root(args)
    graph = _load(args)
    if args.format == "json":
        text = json.dumps(export.to_dict(graph, root), indent=2, ensure_ascii=False)
    elif args.format == "web":
        text = json.dumps(export.to_web(graph, root), ensure_ascii=False, separators=(",", ":"))
    elif args.format == "cypher":
        text = export.to_cypher(graph)
    elif args.format == "graphml":
        text = export.to_graphml(graph)
    elif args.format == "mermaid":
        text = export.to_mermaid(graph)
    else:  # html
        out = pathlib.Path(args.out) if args.out else root / DEFAULT_HTML
        print(export.write_single_file_html(graph, root / TEMPLATE, out, root))
        return 0
    if args.out:
        pathlib.Path(args.out).write_text(text, encoding="utf-8")
        print(args.out)
    else:
        print(text)
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    root = _root(args)
    if not (root / DEFAULT_JSON).exists():
        cmd_build(args)
    handler = functools.partial(_QuietHandler, directory=str(root))
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as server:
        url = f"http://127.0.0.1:{args.port}/viz/"
        print(f"serving {url}   (ctrl+c to stop)")
        if args.open:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
    return 0


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args: object) -> None:  # noqa: D102
        pass


# -------------------------------------------------------------------- parser
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mygraph", description="A service graph: how one person serves the world."
    )
    parser.add_argument("--root", default=".", help="project root (default: .)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="validate the data files").set_defaults(func=cmd_check)
    sub.add_parser("build", help="write the database, the data file and the page").set_defaults(func=cmd_build)

    stats = sub.add_parser("stats", help="counts, provenance, leaders and gaps")
    stats.add_argument("--json", action="store_true")
    stats.set_defaults(func=cmd_stats)

    node = sub.add_parser("node", help="show one node")
    node.add_argument("id")
    node.add_argument("--json", action="store_true")
    node.set_defaults(func=cmd_node)

    find = sub.add_parser("find", help="search the graph")
    find.add_argument("text")
    find.add_argument("--limit", type=int, default=20)
    find.set_defaults(func=cmd_find)

    path = sub.add_parser("path", help="shortest path between two nodes")
    path.add_argument("start")
    path.add_argument("end")
    path.add_argument("--undirected", action="store_true", help="ignore edge direction")
    path.set_defaults(func=cmd_path)

    reach = sub.add_parser("reach", help="what a node eventually reaches")
    reach.add_argument("id", nargs="?")
    reach.add_argument("--type", default="audience")
    reach.set_defaults(func=cmd_reach)

    top = sub.add_parser("top", help="leaderboard by a measure")
    top.add_argument("measure", nargs="?", default="pagerank")
    top.add_argument("--limit", type=int, default=10)
    top.set_defaults(func=cmd_top)

    exp = sub.add_parser("export", help="export to another format")
    exp.add_argument("format", choices=["json", "web", "cypher", "graphml", "mermaid", "html"])
    exp.add_argument("--out", help="write to this file instead of standard output")
    exp.set_defaults(func=cmd_export)

    serve = sub.add_parser("serve", help="serve the visualisation on localhost")
    serve.add_argument("--port", type=int, default=8787)
    serve.add_argument("--open", action="store_true", help="open a browser window")
    serve.set_defaults(func=cmd_serve)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ValidationError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
