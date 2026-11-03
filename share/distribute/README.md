# Distributing this

**There is no universal skill format, and there is not going to be one soon.** Every tool has its own container, and they are not compatible:

| Tool | Its container | Can you hand someone a link? |
|---|---|---|
| ChatGPT | Custom GPT | Yes. Creating needs a paid plan; using does not. |
| Claude | Project, or a Skill | Project sharing needs a Team plan. A Skill is files. |
| Gemini | Gem | Yes, on plans that allow sharing. |
| Copilot | `.github/copilot-instructions.md`, or custom instructions | The repo file reaches everyone in that repo automatically. |
| Cursor, Windsurf, Zed, Aider | A rules file in the repo | Same: it ships with the code. |

So the thing you distribute is **not a skill**. It is a prompt, and a skill is one of several wrappers around it.

## The two artifacts

Everything reduces to these, and only one of them is per-tool.

**The prompt.** Plain text, and it carries the viewer inside it. The last thing in `share/prompt.md` is a complete 11.5 KB HTML page with a `__DATA__` hole in it; a model that can render HTML copies that out, drops the JSON in, and the graph appears in the conversation with no host, no link and no paste. This is the only part that has to be wrapped differently for each tool, and every wrapper here is generated from that one source so they cannot drift.

**The full viewer.** One larger HTML file, for the tools that cannot render a page: the AI hands someone JSON or a link, and this opens it. No tool needs to know it exists.

Both make the whole thing tool-agnostic the same way: the hard part never lives inside anybody's chat product, and the model's share is small enough that every model gets it right.

## How to actually distribute it

**Tier 1, the two lines.** Send someone the contents of `share/ONE-LINER.txt`: a sentence and a link to `share/prompt.md`. Their AI fetches the instructions itself. Nothing to install, nothing to configure, no wrapper needed. This is what goes in a post, an email signature, or a message to your coach, and it is the only tier that reaches people who will not set anything up, which is most people.

**Tier 2, the per-tool wrappers.** For people who will use it more than once. Each file here is ready to paste:

| File | Where it goes |
|---|---|
| `chatgpt-custom-gpt.md` | The GPT builder's Configure tab |
| `claude-project.md` | A Claude project's instructions |
| `gemini-gem.md` | A new Gem |
| `copilot-instructions.md` | `.github/copilot-instructions.md`, or editor settings |
| `AGENTS.md` | Any repo, for Cursor, Windsurf, Zed, Aider |

**Tier 3, discovery.** The repo README, a GitHub Pages site, and a link from kunaldovedy.com. This is where people find it at all.

## What only you can do

I cannot create a Custom GPT or a Gem for you. Those live inside OpenAI's and Google's products, behind their sign-in, and there is no API that creates one. The files here give you the exact text; the twenty minutes of clicking is yours.

Same for GitHub Pages: Settings, Pages, deploy from `main`. The proxy here blocks repository settings writes, so I cannot turn it on.

## Which wrappers are worth the effort

In order, if you only do some:

1. **Send the two lines** from `share/ONE-LINER.txt`. No wrapper required, nothing hosted, and in any tool that renders HTML it already works end to end: the graph comes back inside the conversation. This reaches everyone.
2. **Turn on GitHub Pages.** Settings, Pages, deploy from `main`. This is only for the tools that cannot render a page: without a hosted viewer, a model that writes a link has nowhere to point it.
3. **The ChatGPT custom GPT**, for people who will use it repeatedly and want it in their sidebar. Turn Code Interpreter on when you build it: that is what lets it hand back a tappable link.
4. **`AGENTS.md`** is already at the repo root and distributes itself to every coding agent, forever.
5. The rest, when someone asks.

## Two differences that are not cosmetic

The wrappers are not the same text with different headers.

**Some tools can show a page, and some cannot.** Claude artifacts render one, and so does a ChatGPT canvas on the plans that have it; those are the tools where the graph lands in the conversation. Where no page can be rendered the prompt falls back on its own, and every wrapper tells the model never to settle for ASCII art or a mermaid block, because people stop at the bad version and never see the good one.

**Editor agents have a filesystem.** The Copilot and `AGENTS.md` wrappers tell the model to write `service-graph.html` and `service-graph.json` to disk instead of printing them into a chat window.

## Keeping them in step

The prompt lives in exactly one place, `share/prompt.md`, which is also the file models fetch. The page it carries lives in `share/artifact-template.html` and is stitched into the end of it. Everything in this folder, the viewer's copy of the prompt, and the root `AGENTS.md`, is generated from the result:

```bash
python3 share/build.py
python3 share/build.py --viewer-url https://your-host/viewer.html
```

Do not hand-edit a generated file. The banner at the top of each says so, and the next run will overwrite it.

## What will go stale

Product menus move. The field names in these files, Configure, Set project instructions, Gems, were right when written and will drift. The *content* of each block stays correct regardless, because every one of these products is ultimately a box you paste instructions into.
