# Share this with anyone

The rest of this repository is a developer's tool: Python, a clone, a terminal, a Makefile. Most people will not do that, and they should not have to.

## The short version

Send someone these two lines. That is the whole thing.

```
Build me a service graph of how I serve the world.
Follow the instructions at https://raw.githubusercontent.com/kunaldovedy/mygraph/main/share/prompt.md
```

Their AI fetches the instructions, interviews them for about fifteen minutes, and hands back their graph. No install, no account, no repo, nothing to configure. It is in `ONE-LINER.txt` so you can copy it without reading this.

## What they get back, by tool

The instructions tell the model to work out what it can do and take the best option available. It does not ask; it just does the best one.

| If the model can | It gives them | Works on a phone |
|---|---|---|
| Render interactive HTML (Claude artifacts) | The graph, drawn in the conversation | Yes |
| Run code (ChatGPT Code Interpreter, Claude analysis) | One tappable link with the whole graph packed inside it | Yes |
| Neither | The JSON, and a link to paste it into | Yes, with one paste |

The middle row is the one that matters most, because it covers ChatGPT, where most people are. Code Interpreter needs no network access for this: the model writes the JSON itself, gzips it, base64s it, and prints a URL.

**For that row and the last one, the viewer has to be hosted.** Until then only the Claude path works end to end. See below.

## The sizes, since a link has to survive being sent

| Graph | Uncompressed link | Compressed link |
|---|---|---|
| 25 nodes, a typical first run | ~13,000 chars | **3,686 chars** |
| 71 nodes, a full one | 36,513 chars | **8,200 chars** |

Uncompressed is unusable: chat apps and mail clients mangle URLs that long. Gzipped, both survive. The viewer reads `#z=` (gzipped) and `#d=` (plain, for any browser without `CompressionStream`), and generates `#z=` itself.

Verified both directions: a link made by Python opens the full 71-node graph on an iPhone viewport with zero horizontal overflow, and a link made in the browser decompresses in Python.

## Hosting, which is the one thing left

A link can only open the viewer if the viewer is at a URL. `raw.githubusercontent.com` serves HTML as `text/plain`, so it will not do.

Turn on GitHub Pages: **Settings, Pages, deploy from `main`**. The viewer then lives at `https://kunaldovedy.github.io/mygraph/share/viewer.html`, which is the URL already baked into the generated files. If you host it anywhere else:

```bash
python3 share/build.py --viewer-url https://your-host/viewer.html
```

## Why it works with any AI

The model never has to get the drawing right. It produces a list of nodes and a list of connections, perhaps forty lines of JSON. Stages, colours, shapes, layout, PageRank and reach are all computed in the page from a built-in ontology of seventeen node types.

That keeps the model's share small enough that every model does it reliably, so a graph made in ChatGPT and one made in Claude render identically.

## It forgives what models actually do

Chat models are sloppy in predictable ways. The viewer absorbs all of this rather than showing a parse error nobody can fix:

- Prose wrapped around the JSON, or a ```` ```json ```` fence. Stripped.
- A connection naming a node by label instead of id. Either resolves.
- An invented type like `project` or `skill`. Synonyms map to real types; anything unknown becomes a work.
- A connection pointing at a node that does not exist. Dropped and counted.
- `source`/`target` instead of `from`/`to`, or `links` instead of `edges`. All accepted.

Whatever it repaired is reported above the graph, so nobody mistakes a patched graph for the one they described.

## Files

| File | What it is |
|---|---|
| `prompt.md` | **The source.** What a model fetches and follows. Edit this one. |
| `viewer.html` | The whole viewer. One file, no dependencies. |
| `ONE-LINER.txt` | The two lines to send someone. Generated. |
| `build.py` | Regenerates the viewer's copy of the prompt and every wrapper. |
| `distribute/` | A ready-made wrapper per chat tool. Generated. |

Run `python3 share/build.py` or `make wrappers` after editing `prompt.md`. Never hand-edit a generated file.

## Privacy

Nothing is uploaded, because there is nowhere to upload it to. The graph lives in the page, in the link if one is made, and in the file if one is saved.

A link or a saved file carries the whole graph inside it, so both are as public as whoever you send them to. And whatever someone types into ChatGPT is subject to that company's terms, which is worth saying out loud before anybody maps their inner life into one.
