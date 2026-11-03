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

**The prompt.** Plain text. It is the only part that has to be wrapped differently for each tool, and the wrappers in this folder are all generated from one source so they cannot drift.

**The viewer.** One HTML file. No tool needs to know it exists. The AI hands someone JSON, they paste it in, they get a graph. This is what makes the whole thing tool-agnostic: the hard part never lives inside anybody's chat product.

## How to actually distribute it

**Tier 1, the one link.** Host `share/viewer.html` and send that URL. Nothing to install, nothing to configure, works with whatever AI the person already has open. This is what goes in a post, an email signature, or a message to your coach. It is the only tier that reaches people who will not set anything up, which is most people.

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

1. **Host the viewer.** Turns the whole thing into one link. Biggest return for the least work.
2. **The ChatGPT custom GPT.** Most people, including your coach, are on ChatGPT. A link they can open and keep.
3. **`AGENTS.md` in this repo.** Distributes itself to every coding agent, for free, forever.
4. The rest, when someone asks.

## Two differences that are not cosmetic

The wrappers are not the same text with different headers.

**Claude can draw it; ChatGPT cannot.** The Claude wrapper offers to render the graph as an artifact right there, so someone sees it without leaving the conversation. The ChatGPT and Gemini wrappers explicitly tell the model *not* to attempt a diagram, because ASCII art and a mermaid block are worse than the real thing and people stop at the bad version.

**Editor agents have a filesystem.** The Copilot and `AGENTS.md` wrappers tell the model to write `service-graph.json` to disk instead of printing forty lines into a chat window.

## Keeping them in step

The prompt lives in exactly one place, inside `share/viewer.html`. Everything in this folder, and `share/PROMPT.md`, is generated from it:

```bash
cd share/distribute
python3 build_wrappers.py
python3 build_wrappers.py --viewer-url https://your-host/viewer.html
```

Do not hand-edit a generated file. The banner at the top of each says so, and the next run will overwrite it.

## What will go stale

Product menus move. The field names in these files, Configure, Set project instructions, Gems, were right when written and will drift. The *content* of each block stays correct regardless, because every one of these products is ultimately a box you paste instructions into.
