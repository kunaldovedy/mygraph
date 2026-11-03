# Share this with anyone

The rest of this repository is a developer's tool: Python, a clone, a terminal, a Makefile. Most people will not do that, and they should not have to.

## The short version

Send someone these two lines. That is the whole thing.

```
Build me a service graph of how I serve the world.
Follow the instructions at https://raw.githubusercontent.com/kunaldovedy/mygraph/main/share/prompt.md
```

Their AI fetches the instructions, interviews them for about fifteen minutes, and hands back their graph. No install, no account, no repo, nothing to configure. It is in `ONE-LINER.txt` so you can copy it without reading this.

It asks first whether there is anything to read — a CV, a site, a chat export — and drafts from that before interviewing, so the questions are about the gaps rather than the record. What it will not do is claim to have read your past conversations. No chat product lets a fetched prompt sweep your history reliably, so anything drafted from material comes back marked as a guess until you confirm it in your own words.

## What they get back, by tool

The instructions tell the model to work out what it can do and take the best option available. It does not ask; it just does the best one.

| If the model can | It gives them | Needs a hosted viewer |
|---|---|---|
| Render HTML in the chat (a Claude artifact, a ChatGPT canvas) | **The graph itself, in the conversation**, with all the data inside it | No |
| Write files (Code Interpreter, a coding agent) | The same page as a file to download, plus one tappable link | Only for the link |
| Neither | The JSON, and a link to paste it into | Yes |

The first row is the one that matters, and it is the reason `prompt.md` is fetched rather than pasted: because the model reads the instructions from a URL, those instructions can carry **the whole viewer with them**. At the end of `prompt.md` sits a complete 11.5 KB HTML file with a `__DATA__` placeholder in it. The model copies it out unchanged and drops the JSON in. That is the entire mechanism.

### Where the data lives

Inside the page, and nowhere else. The page is part of the conversation, so the chat tool is what saves it, and the JSON sits beside it in plain text in the same conversation. There is no account, no server and no upload; ask for a change and you get a new version back in the same place.

The page also carries two buttons for getting out: **Copy the JSON**, to take the graph to another chat, and **Save this page**, which writes the whole thing to a single HTML file that works offline forever.

### What is verified, and what is not

Verified here, in a browser: the page renders a 29-node graph and a 71-node one, on a desktop viewport and an iPhone one, with no horizontal overflow and no console errors; tapping a node lights its connections; the legend hides a kind; the saved copy opens on its own and draws the same graph.

Not verified here, because it needs the actual products: that a given model reproduces 153 lines of HTML faithfully. The file is deliberately small for that reason, and the prompt is blunt about copying it exactly, but a model that paraphrases it will produce a broken page. If that happens, tell it to output the file again without changing anything. If it keeps happening, the fallback rows still work.

## The sizes

| | On disk | Gzipped |
|---|---|---|
| The page the model copies out (`artifact-template.html`) | 11.5 KB | 5.0 KB |
| The whole prompt a model fetches, page included | 16.8 KB | 7.5 KB |
| A finished 29-node graph | 15.7 KB | 6.0 KB |
| A finished 71-node graph | 39.1 KB | 11.3 KB |
| `viewer.html`, the full version for a paste | 103.3 KB | 34.1 KB |

A link, for the rows that make one:

| Graph | Uncompressed link | Compressed link |
|---|---|---|
| 25 nodes, a typical first run | ~13,000 chars | **3,686 chars** |
| 71 nodes, a full one | 36,513 chars | **8,200 chars** |

Uncompressed is unusable: chat apps and mail clients mangle URLs that long. Gzipped, both survive. The viewer reads `#z=` (gzipped) and `#d=` (plain, for any browser without `CompressionStream`), and generates `#z=` itself. Verified both directions: a link made by Python opens the full 71-node graph on an iPhone viewport, and a link made in the browser decompresses in Python.

## Hosting, and why it costs you nothing

The first row above needs no host at all. The other two do, because a link can only open the viewer if the viewer is at a URL, and `raw.githubusercontent.com` serves HTML as `text/plain`.

**It should never be your own server.** Nothing here touches kunaldovedy.com or your Vercel project, and it should not. This is one immutable static file with no backend: 34.1 KB served gzipped, which is **about 2.9 million page loads per 100 GB**, and that is the worst case, because the file is immutable and every CDN and browser caches it.

In order of least exposure:

1. **GitHub Pages.** GitHub's bandwidth on a `github.io` address. Not your website, no card attached: the documented limit is a soft one and GitHub emails you rather than billing you. *(Check the current figure yourself; I could not reach their docs from where this was built.)*

   **Settings → Pages → Source: Deploy from a branch → `main` / `/ (root)` → Save.** One choice, the default one. The repo is already set up for it:

   - `index.html` at the root redirects to the viewer and **carries the URL fragment across**, so the short form `https://kunaldovedy.github.io/mygraph/#z=...` works. Verified over HTTP on a phone viewport: a 71-node graph arrives intact.
   - `.nojekyll` stops Pages running Jekyll over the repo.

   Give it a minute after saving, then open `https://kunaldovedy.github.io/mygraph/`.
2. **Cloudflare Pages or Netlify.** Separate free accounts, nothing shared with your existing hosting. Deploy from the same repo.
3. **Somebody else's copy.** The viewer has no absolute self-references, so anyone can host it. The URL is a build flag, not a constant.

```bash
python3 share/build.py --viewer-url https://your-host/viewer.html
```

## Why it works with any AI

The model never has to get the drawing right. It produces a list of nodes and a list of connections, perhaps forty lines of JSON, and copies out a file it does not have to understand. Stages, colours, shapes, ring order, label collisions and the detail panel are all worked out in the page from a built-in ontology of seventeen node types, plus a short synonym table so an invented type like `vehicle` or `project` still lands on the right ring.

That keeps the model's share small enough that every model does it reliably, so a graph made in ChatGPT and one made in Claude render identically.

## It forgives what models actually do

Chat models are sloppy in predictable ways. Both the page and the viewer absorb this rather than showing a parse error nobody can fix:

- A connection naming a node by label instead of id. Either resolves.
- An invented type like `project` or `skill`. Synonyms map to real types; anything unknown becomes a work.
- A connection pointing at a node that does not exist. Dropped.
- `source`/`target` instead of `from`/`to`. Accepted.

The full viewer goes further still: it strips prose and a ```` ```json ```` fence from a paste, accepts `links` for `edges`, and reports every repair it made above the graph so nobody mistakes a patched graph for the one they described.

## Files

| File | What it is |
|---|---|
| `prompt.md` | **The source.** What a model fetches and follows. Edit this one — but not the fenced block at the end. |
| `artifact-template.html` | The page a model copies out. `build.py` stitches it into the block at the end of `prompt.md`. |
| `viewer.html` | The full viewer, for a paste or a link. One file, no dependencies. |
| `ONE-LINER.txt` | The two lines to send someone. Generated. |
| `build.py` | Stitches the two sources together and regenerates every wrapper. |
| `distribute/` | A ready-made wrapper per chat tool. Generated. |

Run `python3 share/build.py` or `make wrappers` after editing `prompt.md` or `artifact-template.html`. Never hand-edit a generated file.

## Privacy

Your graph is never uploaded, because there is nowhere to upload it to. It lives in the page, in the conversation that holds the page, in the link if one is made, and in the file if one is saved.

The page the model writes into the chat makes no network request of any kind. `viewer.html` makes exactly one: it requests its fonts from Google Fonts, so Google sees that it was loaded, though never what is in it. Every font has a real fallback, so it works fully offline and simply looks plainer. If that one request is unwelcome, delete the `<link rel="stylesheet">` on line 2 of `viewer.html`; nothing else changes.

A link or a saved file carries the whole graph inside it, so both are as public as whoever you send them to. And whatever someone types into ChatGPT is subject to that company's terms, which is worth saying out loud before anybody maps their inner life into one.
