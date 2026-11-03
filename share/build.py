#!/usr/bin/env python3
"""Build everything downstream of the one prompt.

`share/prompt.md` is the source. It is also the file a chat model fetches and
follows, so it is written as pure instructions with no meta-commentary.

Everything else is generated from it and must not be hand-edited:

    share/viewer.html            the prompt behind its Copy button
    share/distribute/*.md        a wrapper per chat tool
    AGENTS.md                    at the repository root

    python3 share/build.py
    python3 share/build.py --viewer-url https://your-host/viewer.html
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

SHARE = pathlib.Path(__file__).resolve().parent
ROOT = SHARE.parent
DIST = SHARE / "distribute"
PROMPT = SHARE / "prompt.md"
VIEWER = SHARE / "viewer.html"

# Until the viewer is hosted somewhere, a link cannot open it. raw.github
# serves HTML as text/plain, so it will not do.
DEFAULT_URL = "https://kunaldovedy.github.io/mygraph/share/viewer.html"
PROMPT_RAW = "https://raw.githubusercontent.com/kunaldovedy/mygraph/main/share/prompt.md"

BANNER = "<!-- GENERATED from share/prompt.md by share/build.py. Do not edit. -->"
BLOCK = re.compile(r'(<script type="text/plain" id="prompt-src">\n).*?(\n</script>)', re.S)


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

    if not PROMPT.exists():
        sys.exit(f"missing {PROMPT}")
    prompt = PROMPT.read_text().strip().replace("VIEWER_URL", args.viewer_url)
    one_liner = bootstrap(args.prompt_url)

    print("generated:")

    # ---------------------------------------- the prompt inside the viewer
    html = VIEWER.read_text()
    if not BLOCK.search(html):
        sys.exit("prompt block not found in viewer.html")
    VIEWER.write_text(BLOCK.sub(lambda m: m.group(1) + prompt + m.group(2), html, count=1))
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

```
{prompt}
```

## Conversation starters

```
Map how I serve the world
I want to see who my work actually reaches
Help me find the gap between what I value and what I make
Start the interview
```

## Capabilities

Turn **Code Interpreter ON**. It is what lets the GPT hand back a single
tappable link containing the whole graph, which is the difference between
someone seeing their graph on their phone and someone copying JSON around.

Turn **Web Browsing** and **DALL-E** off. Neither helps and both give it room
to wander.

## Sharing

Set visibility to **Anyone with the link**.
""")

    # -------------------------------------------------------------- Claude
    write(DIST / "claude-project.md", f"""{BANNER}
# Claude, as a project

Create a project, open **Set project instructions**, and paste this. Claude
can render the graph directly, so branch A of the instructions applies and
people see it without leaving the conversation.

## Project instructions

```
{prompt}
```
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

```
{prompt}
```
""")

    # ------------------------------------------------------------- Copilot
    write(DIST / "copilot-instructions.md", f"""{BANNER}
# GitHub Copilot

Save the block below as `.github/copilot-instructions.md` in any repository
and Copilot Chat picks it up for everyone who works there, with no setup on
their side. Or paste the same text into your editor's custom instructions to
have it everywhere.

```
{prompt}

You are running in an editor with a filesystem, so write the JSON to
service-graph.json in the workspace rather than printing it into the chat.
```
""")

    # ------------------------------------------------- any coding agent
    agents = f"""{BANNER}
# Any coding agent

Cursor, Windsurf, Zed, Aider and Continue all read a plain instructions file
from the repository root. The filenames differ, the content does not: save
this as `AGENTS.md`, `.cursorrules`, `.windsurfrules`, or
`.github/copilot-instructions.md`.

```
{prompt}

You are running in an editor with a filesystem, so write the JSON to
service-graph.json rather than printing it into the chat.
```
"""
    write(DIST / "AGENTS.md", agents)
    write(ROOT / "AGENTS.md", agents)

    # ----------------------------------------------------- the one-liner
    write(SHARE / "ONE-LINER.txt", one_liner)

    print(f"\nthe whole thing, for anyone, in two lines:\n")
    print("    " + one_liner.replace("\n", "\n    "))
    print(f"\nviewer url baked in: {args.viewer_url}")
    if "github.io" in args.viewer_url:
        print("  ^ that only resolves once GitHub Pages is turned on for this repo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
