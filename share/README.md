# Share this with anyone

The rest of this repository is a developer's tool: Python, a clone, a terminal, a Makefile. Most people will not do that, and they should not have to.

This folder is the version you can send to anybody, whatever AI they use.

## Three steps, no install

1. **Open `viewer.html`.** Double-click it. It is one file, it runs offline, and it has no server, no analytics and no network calls.
2. **Copy the prompt** from the page and paste it into ChatGPT, Claude, Copilot, Gemini, whichever they use. It interviews them for about fifteen minutes.
3. **Paste the JSON back in.** The graph appears.

Then they can **Save as one file** and send that single HTML to anyone. It carries the data inside it, so the recipient needs nothing at all. Or **Copy link**, which packs the whole graph into the URL.

## Why it works with any AI

The AI never has to get the drawing right. It only produces a small block of JSON: a list of nodes and a list of connections. Stages, colours, shapes, layout, PageRank and reach are all computed in the page.

That keeps the part a language model has to do small enough that every model does it reliably, and it means a graph made in ChatGPT and a graph made in Claude render identically.

## It forgives what models actually do

Chat models are sloppy in predictable ways, so the viewer handles all of this without complaining to the user:

- Wraps the JSON in prose, or a ```` ```json ```` fence. Both are stripped.
- Refers to a node by its label instead of its id. Either resolves.
- Invents a type like `project` or `skill`. Common synonyms map to real types; anything unknown becomes a work, with a note.
- Points a connection at something that does not exist. That edge is dropped and counted, rather than breaking the page.
- Uses `source`/`target` instead of `from`/`to`, or `links` instead of `edges`. All accepted.

Whatever it had to repair is reported above the graph, so nobody is misled into thinking a mangled graph is their real one.

## The seventeen kinds of node

Eight cover a service graph and are all most people need: **person, value, practice, capability, work, organisation, audience, outcome**.

Nine more widen it to a life: **belief, question, tension, chapter, health, source, commitment, place, resource**. They are in the prompt, and the viewer lays them on the same eight rings.

## Files

| File | What it is |
|---|---|
| `viewer.html` | The whole thing. One file, no dependencies. |
| `PROMPT.md` | The same prompt as text, for reading or pasting without opening the viewer. Generated from `viewer.html`. |

## Hosting it, if you want a link to share

`viewer.html` is a static file. Put it anywhere that serves HTML and the URL becomes the thing you send. GitHub Pages works: Settings, Pages, deploy from `main`, and it appears under `/share/viewer.html`.

Hosting also makes **Copy link** more useful, because a shared graph then opens in a browser rather than needing the file first.

## Privacy

Nothing is uploaded, because there is nowhere to upload it to. The graph lives in the page, in the URL if you copy a link, and in the file if you save one. A graph in a link or a saved file is readable by whoever you send it to, so treat both as public.

The AI conversation is a different matter. Whatever someone types into ChatGPT or Claude is subject to that company's terms, which is worth saying out loud before anybody maps their inner life into one.
