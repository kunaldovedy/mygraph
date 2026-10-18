---
name: service-graph
description: Build or extend a service graph — a map of how a person or an organisation actually serves the world, running outward through values, practices, capabilities, works, vehicles, audiences and outcomes. Use when someone wants to map their practice, portfolio, impact, theory of change or "what I actually do and who it reaches"; when they ask who their work serves or what changed for those people; or when they want to add to, audit or visualise an existing graph in this repository. Produces validated YAML, a SQLite graph database and an interactive page.
---

# Service graph

A list of projects cannot show the thing that matters: the path from what
someone believes, through what they can do, to the person on the other end who
is different afterwards. That is a graph. This skill builds one.

## Before you start

Read `schema/ontology.yaml`. It is the contract: the node kinds, which
relations may join which kinds, and the provenance vocabulary. Validation
enforces all of it, so a graph that passes `make check` is structurally sound.

Then run `make check` on the graph that is already there, to see it pass.

## The eight stages

Each ring answers one question. Work outward.

| Stage | Kind | The question |
|---|---|---|
| 0 | Person | Who is at the centre? |
| 1 | Values | What must stay true? |
| 2 | Practices | What do I actually do? |
| 3 | Capabilities | What can I do that is hard to buy? |
| 4 | Works | What did I make? |
| 5 | Vehicles | Through what does the work travel? |
| 6 | Audiences | Who is on the other end? |
| 7 | Outcomes | What changed for them? |

Then outcomes point back at values, and audiences point back at capabilities.
Those return edges are the loop. Without them the picture is a pipeline, not a
practice, and the drawing will look like one.

## How to interview someone for this

Do not start at stage 1. People cannot state their values cold, and whatever
they say first is usually borrowed language.

Start at **stage 4, works**. Everyone can list what they made. Then go
outward, because that is where the real information is, and only then come
back inward:

1. **Works.** What did you make? Keep going until they slow down.
2. **Vehicles.** Who published, funded, exhibited, employed or hosted each one?
3. **Audiences.** Who received it? Push here. "Users" is not an audience.
   Name the person: the dispatcher at 6am, the kid at the museum, the
   practitioner in another country. This is the stage everyone skips.
4. **Outcomes.** What was different for that person afterwards? If the answer
   is a feature or a deliverable, it is not an outcome. Ask again.
5. **Capabilities.** Looking back at the works, what can this person do that
   is hard to hire for? Name the capability, not the job title.
6. **Practices.** Group the capabilities into the few verbs they actually
   practise. Most people have three to six.
7. **Values.** Now ask. By this point the evidence is on the table and the
   answer is grounded rather than aspirational.

**Look for their own words first.** A personal site, an About page, a company
values page, a repository README. Quote those verbatim rather than
paraphrasing. A paraphrase is a guess wearing a suit.

## Provenance is the point

Every node and edge declares `source` and `confidence`. This is not
bookkeeping. A service graph that cannot tell you which parts are evidence and
which are flattery is a brochure.

| Source | Means |
|---|---|
| `public-web` | On a public page you read directly |
| `public-web-indexed` | A public page quoted through a search index, not read first-hand |
| `public-profile` | A public professional profile or org listing |
| `public-github` | A public repository |
| `self` | The subject told you or confirmed it |
| `inferred` | You read between the lines. It needs confirming. |
| `placeholder` | A slot waiting to be filled |

Rules that are not negotiable:

- **Never upgrade a source you did not check.** If you could not open the page,
  it is `public-web-indexed` or `inferred`, not `public-web`.
- **Never invent a `refs` URL.** Omit the field instead.
- **Mark your own framing as `inferred`,** even when it rests on a sourced
  fact. The fact and your reading of it are different claims.
- **When the subject confirms something, change it to `self`** and say so in
  the summary. That is the system doing its job.
- **Private material goes in `data/private/`,** which is git-ignored and loaded
  automatically. Client names and unreleased work never need to be committed.

## Writing nodes and edges

Node files live in `data/nodes/`, one per stage. Edges live in `data/edges/`,
one per movement. Both are plain YAML lists; the loader reads every file.

```yaml
# data/nodes/40-works.yaml
- id: w-my-thing              # lower-case-kebab-case, unique
  type: work
  label: The thing I made
  subtitle: One line that earns a second look
  summary: >-
    Two or three sentences. What it is, who it was for, what it cost.
  source: self
  confidence: high            # high | medium | low
  refs: [https://example.com/the-thing]
  props: { years: 2024 }
```

```yaml
# data/edges/30-work-to-vehicle.yaml
- { src: w-my-thing, rel: carried_by, dst: o-some-venue, weight: 1.6,
    source: self, confidence: high }
```

Weight runs about 1.0 to 2.0 and drives line thickness and node size. Use it
for emphasis, not precision.

A note on YAML: flow mappings break on unquoted commas. Quote any `note:` or
`label:` containing a comma.

## Commands

```bash
make check                      # validate only; run this constantly
make build                      # database, data file and page
make serve                      # the visualisation at 127.0.0.1:8787/viz/
make test                       # 36 tests, including tests of the graph itself

python3 -m mygraph stats        # counts, provenance, leaders and gaps
python3 -m mygraph node <id>    # one node and every statement about it
python3 -m mygraph path me <id> # how the service actually arrives
python3 -m mygraph reach --type outcome
python3 -m mygraph top betweenness
```

## What good looks like

Run `python3 -m mygraph stats` and read the **gaps** section. It names
outcomes that reach nobody and audiences with no channel. Both are real holes
in the practice, not data-entry mistakes, and they are worth raising with the
subject rather than quietly patching.

Then check these by eye:

- **Every stage has something in it.** An empty ring is a gap in the practice.
- **Every outcome reaches somebody.** A test enforces this.
- **The loop closes.** At least one `renews` edge, ideally several.
- **Values are expressed.** A value with no `expresses` edge pointing at it is
  a poster on a wall.
- **The inferred count is honest.** `stats` reports it by provenance. If
  nothing is inferred, you are probably overclaiming.

## Extending the ontology

Add node kinds or relations in `schema/ontology.yaml`. A new node kind needs a
stage, a glyph and a palette slot; a new relation needs the kinds it may join.
Validation picks both up with no code change. Keep glyphs distinct, because
the drawing uses shape as well as colour so it still reads for anyone who
cannot separate two hues.

## Publishing it

`integrations/kunaldovedy.com/` holds a mobile-first Next.js route built on
this data, as a worked example of putting a graph on a real site. `make build`
also writes `build/mygraph.html`, one self-contained file that needs no server.

---

Required Notice: Copyright 2026 Kunal Dovedy (https://kunaldovedy.com)

This skill is part of `mygraph`, licensed under the PolyForm Small Business
License 1.0.0. Free for individuals and companies under 100 people and 1M USD
revenue; larger companies need a paid licence. Keep this notice with the skill
if you copy it elsewhere. See https://github.com/kunaldovedy/mygraph.
