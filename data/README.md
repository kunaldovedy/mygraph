# The graph data

These files are the example graph. They describe a real person, Kunal Dovedy,
and are built from public sources with each claim marked by where it came
from.

**They are not covered by the licence on the rest of this project, and are not
licensed for reuse.** Copyright 2026 Kunal Dovedy, all rights reserved.

This takes nothing away from you. The tool, the schema, the visualisation and
the agent skill are all licensed under
[PolyForm Small Business 1.0.0](../LICENSE.md), and you need none of this
biography to use any of them. The data is here because a real graph
demonstrates the tool far better than an empty one.

## Making it yours

Replace the contents of `nodes/` and `edges/` with your own, keeping the file
structure. `schema/ontology.yaml` defines what is allowed, and `make check`
will tell you when something does not hold together.

The fastest route is to open the project with Claude and say *build my service
graph*. The skill in `.claude/skills/service-graph/` will interview you and
write these files.

Anything you would rather not commit goes in `data/private/`, which is
git-ignored and loaded automatically.
