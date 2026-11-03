#!/usr/bin/env python3
"""Build everything downstream of the one prompt.

`share/prompt.md` is the source. It is also the file a chat model fetches and
follows, so it is written as pure instructions with no meta-commentary.

Two things are stitched together here.

    share/artifact-template.html -> the fenced block at the end of prompt.md

That block is what a model copies out verbatim to show the graph as a page
inside the conversation, so it has to live inside the fetchable prompt. Edit
the .html file, never the block.

Everything else is generated from the finished prompt and must not be
hand-edited either:

    share/viewer.html            the prompt behind its Copy button
    share/distribute/*.md        a wrapper per chat tool
    AGENTS.md                    at the repository root

    python3 share/build.py
    python3 share/build.py --viewer-url https://your-host/viewer.html
"""
from __future__ import annotations

import argparse
import base64
import pathlib
import re
import sys

SHARE = pathlib.Path(__file__).resolve().parent
ROOT = SHARE.parent
DIST = SHARE / "distribute"
PROMPT = SHARE / "prompt.md"
VIEWER = SHARE / "viewer.html"
TEMPLATE = SHARE / "artifact-template.html"

# Until the viewer is hosted somewhere, a link cannot open it. raw.github
# serves HTML as text/plain, so it will not do.
DEFAULT_URL = "https://kunaldovedy.github.io/mygraph/share/viewer.html"
PROMPT_RAW = "https://raw.githubusercontent.com/kunaldovedy/mygraph/main/share/prompt.md"

BANNER = "<!-- GENERATED from share/prompt.md by share/build.py. Do not edit. -->"
BLOCK = re.compile(r'(<script type="text/plain" id="prompt-src">\n).*?(\n</script>)', re.S)
TPL = re.compile(r'(<!--template-->\n```html\n).*?(\n```\n<!--/template-->)', re.S)

# The prompt now carries a whole HTML file, so every wrapper that quotes it
# needs an outer fence longer than any fence inside it.
FENCE = "`" * 6


def bootstrap(url: str) -> str:
    return (f"Build me a service graph of how I serve the world.\n"
            f"Follow the instructions at {url}")


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")
    print(f"  {path.relative_to(ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--viewer-url", default=DEFAULT_URL)
    ap.add_argument("--prompt-url", default=PROMPT_RAW)
    args = ap.parse_args()

    for required in (PROMPT, TEMPLATE, VIEWER):
        if not required.exists():
            sys.exit(f"missing {required}")

    print("generated:")

    # ------------------------------- the artifact template inside the prompt
    template = TEMPLATE.read_text().strip()
    if "__DATA__" not in template:
        sys.exit("artifact-template.html has no __DATA__ placeholder")
    if "```" in template:
        sys.exit("artifact-template.html contains a code fence; it cannot be quoted")
    raw = PROMPT.read_text()
    if not TPL.search(raw):
        sys.exit("template block not found in prompt.md")
    raw = TPL.sub(lambda m: m.group(1) + template + m.group(2), raw, count=1)
    PROMPT.write_text(raw)
    print(f"  {PROMPT.relative_to(ROOT)}  (template block)")

    prompt = raw.strip().replace("VIEWER_URL", args.viewer_url)
    one_liner = bootstrap(args.prompt_url)

    # ---------------------------------------- the prompt inside the viewer
    # Stored base64: the prompt contains </script>, which would otherwise end
    # the script element it sits in. The viewer decodes it before showing it.
    html = VIEWER.read_text()
    if not BLOCK.search(html):
        sys.exit("prompt block not found in viewer.html")
    packed = base64.b64encode(prompt.encode()).decode()
    packed = "\n".join(packed[i:i + 76] for i in range(0, len(packed), 76))
    html = BLOCK.sub(lambda m: m.group(1) + packed + m.group(2), html, count=1)
    # A closing script tag spelled out anywhere inside a script element ends it
    # there, which costs an afternoon to find. Count them instead.
    if html.count("<script") != html.count("</" + "script>"):
        sys.exit("viewer.html has an unbalanced script tag; a closing tag is "
                 "probably written out inside a script or a comment")
    VIEWER.write_text(html)
    print(f"  {VIEWER.relative_to(ROOT)}")

    # ------------------------------------------------------------- ChatGPT
    write(DIST / "chatgpt-custom-gpt.md", f"""{BANNER}
# ChatGPT, as a custom GPT

Creating one needs a paid plan; using one does not. In the GPT builder, open
the **Configure** tab.

## Name

```
Service Graph
```

## Description

```
Interviews you for fifteen minutes, then maps how your work actually reaches
people: from what you believe, through what you make, to who is different
afterwards.
```

## Instructions

{FENCE}
{prompt}
{FENCE}

## Conversation starters

```
Map how I serve the world
I want to see who my work actually reaches
Help me find the gap between what I value and what I make
Start the interview
```

## Capabilities

Turn **Canvas on** if your plan has it: a canvas renders HTML, which is what
lets the GPT put the graph itself in the conversation rather than a link to it.

Turn **Code Interpreter ON** as well. It is the fallback, and it writes the
page out as a file you can download, plus a single tappable link that carries
the whole graph.

Turn **Web Browsing** and **DALL-E** off. Neither helps and both give it room
to wander.

## Sharing

Set visibility to **Anyone with the link**.
""")

    # -------------------------------------------------------------- Claude
    write(DIST / "claude-project.md", f"""{BANNER}
# Claude, as a project

Create a project, open **Set project instructions**, and paste this. Claude
renders artifacts, so branch A of the instructions applies: the graph appears
as a page in the conversation, with the whole dataset inside it, and the
conversation is where it stays.

## Project instructions

{FENCE}
{prompt}
{FENCE}
""")

    # -------------------------------------------------------------- Gemini
    write(DIST / "gemini-gem.md", f"""{BANNER}
# Gemini, as a Gem

Open Gems, create a new one.

## Name

```
Service Graph
```

## Instructions

{FENCE}
{prompt}
{FENCE}
""")

    # ------------------------------------------------------------- Copilot
    write(DIST / "copilot-instructions.md", f"""{BANNER}
# GitHub Copilot

Save the block below as `.github/copilot-instructions.md` in any repository
and Copilot Chat picks it up for everyone who works there, with no setup on
their side. Or paste the same text into your editor's custom instructions to
have it everywhere.

{FENCE}
{prompt}

You are running in an editor with a filesystem and no way to render a page in
the chat, so take branch B: write the filled-in file to service-graph.html and
the JSON to service-graph.json in the workspace, and tell me to open the HTML
file. Do not print either one into the chat.
{FENCE}
""")

    # ------------------------------------------------- any coding agent
    agents = f"""{BANNER}
# Any coding agent

Cursor, Windsurf, Zed, Aider and Continue all read a plain instructions file
from the repository root. The filenames differ, the content does not: save
this as `AGENTS.md`, `.cursorrules`, `.windsurfrules`, or
`.github/copilot-instructions.md`.

{FENCE}
{prompt}

You are running in an editor with a filesystem and no way to render a page in
the chat, so take branch B: write the filled-in file to service-graph.html and
the JSON to service-graph.json, and tell me to open the HTML file. Do not
print either one into the chat.
{FENCE}
"""
    write(DIST / "AGENTS.md", agents)
    write(ROOT / "AGENTS.md", agents)

    # ----------------------------------------------------- the one-liner
    write(SHARE / "ONE-LINER.txt", one_liner)

    print(f"\nthe whole thing, for anyone, in two lines:\n")
    print("    " + one_liner.replace("\n", "\n    "))
    print(f"\nprompt: {len(prompt):,} chars, of which the page is {len(template):,}")
    print(f"viewer url baked in: {args.viewer_url}")
    if "github.io" in args.viewer_url:
        print("  ^ that only resolves once GitHub Pages is turned on for this repo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
