#!/usr/bin/env python3
"""Generate a wrapper for each chat tool from the one canonical prompt.

There is no universal skill format. Every tool has its own container, and the
only thing they share is that each container is instructions plus, sometimes,
files. So the prompt lives in exactly one place, `share/viewer.html`, and every
wrapper below is generated from it.

    python3 build_wrappers.py
    python3 build_wrappers.py --viewer-url https://example.com/viewer.html

Re-run it after editing the prompt. Never edit a generated file by hand; the
next run will overwrite it.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SHARE = HERE.parent
VIEWER = SHARE / "viewer.html"
DEFAULT_URL = "https://kunaldovedy.github.io/mygraph/share/viewer.html"

BANNER = "<!-- GENERATED from share/viewer.html by distribute/build_wrappers.py. Do not edit. -->"


def canonical_prompt() -> str:
    html = VIEWER.read_text()
    m = re.search(r'<script type="text/plain" id="prompt-src">\n(.*?)\n</script>', html, re.S)
    if not m:
        sys.exit("could not find the prompt block in viewer.html")
    return m.group(1).strip()


def where_to_send(url: str) -> str:
    return (
        f"When you hand over the JSON, tell them to open {url} and paste it "
        f"there. That page draws the graph, and its Save as one file button "
        f"gives them a single HTML file they can send to anyone."
    )


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")
    print(f"  {path.relative_to(SHARE.parent)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--viewer-url", default=DEFAULT_URL,
                    help="where the viewer is hosted, used in the hand-off line")
    args = ap.parse_args()
    prompt = canonical_prompt()
    handoff = where_to_send(args.viewer_url)

    print("generated:")

    # ------------------------------------------------- ChatGPT, a custom GPT
    write(HERE / "chatgpt-custom-gpt.md", f"""{BANNER}
# ChatGPT, as a custom GPT

A custom GPT gives you a link anyone can open, and it shows up in their
sidebar afterwards. Creating one needs a paid ChatGPT plan; using one does not.

In the GPT builder, switch to the **Configure** tab and fill in these fields.

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

{handoff}

You cannot draw the graph yourself, and you should not try. ASCII art and
mermaid diagrams are worse than the real thing. Hand over the JSON and the
link.
```

## Conversation starters

```
Map how I serve the world
I want to see who my work actually reaches
Help me find the gap between what I value and what I make
Start the interview
```

## Capabilities

Turn **Web Browsing** and **DALL-E** off. Neither helps, and both give it
chances to wander. Code Interpreter is optional; it changes nothing here.

## Sharing

Set visibility to **Anyone with the link**, then send the link. Publishing to
the GPT Store is a separate step and needs a verified builder profile.
""")

    # ------------------------------------------------------ Claude, a project
    write(HERE / "claude-project.md", f"""{BANNER}
# Claude, as a project

A project keeps the instructions attached to every conversation inside it. On
a paid plan you can share a project with your team; otherwise it is yours and
you send people the prompt instead.

Create a project, open **Set project instructions**, and paste this.

## Project instructions

```
{prompt}

{handoff}

You can also build the graph yourself. After you give them the JSON, offer to
render it as an interactive artifact in this conversation, so they see it
immediately without leaving Claude. If they say yes, build a single self
contained HTML artifact: a radial diagram with the person at the centre and
each stage on its own ring, reading outward. Give every kind of node a
distinct shape as well as a distinct colour, so it still reads for anyone who
cannot separate two hues. The JSON is still the thing they keep, because it
opens in the viewer and outlives this conversation.
```

## Also worth adding

Attach `share/PROMPT.md` to the project as a file. Claude reads it, and anyone
in the project can download it for use elsewhere.
""")

    # ----------------------------------------------------------- Gemini, a Gem
    write(HERE / "gemini-gem.md", f"""{BANNER}
# Gemini, as a Gem

A Gem is Gemini's saved instruction set. Gems can be shared by link on plans
that allow it.

Open Gems, create a new one, and fill in these two fields.

## Name

```
Service Graph
```

## Instructions

```
{prompt}

{handoff}

Do not try to draw the graph. Hand over the JSON and the link.
```
""")

    # ----------------------------------------------- Copilot, repo and chat
    write(HERE / "copilot-instructions.md", f"""{BANNER}
# GitHub Copilot

Copilot takes instructions two ways, and they suit different people.

## In a repository

Save the block below as `.github/copilot-instructions.md` in any repo. Copilot
Chat picks it up for everyone who works in that repo, with no setup on their
side. This is the only wrapper here that distributes itself.

## As personal custom instructions

Paste the same block into Copilot's custom instructions in your editor
settings, and it applies everywhere you work.

```
{prompt}

{handoff}

You are running inside an editor, so you can go one better: write the JSON
straight to a file called service-graph.json in the workspace, then tell them
where it is and what to do with it.
```
""")

    # --------------------------------------------- generic agents / rules file
    write(HERE / "AGENTS.md", f"""{BANNER}
# Any coding agent

Cursor, Windsurf, Zed, Aider, Continue and Copilot all read a plain
instructions file from the repository root. The names differ, the content does
not. Save this as whichever your tool wants: `AGENTS.md`, `.cursorrules`,
`.windsurfrules`, or `.github/copilot-instructions.md`.

```
{prompt}

{handoff}

You are running in an editor with file access, so write the JSON to
service-graph.json rather than printing it into the chat.
```
""")

    print(f"\nviewer url used: {args.viewer_url}")
    print("re-run with --viewer-url once the viewer is hosted somewhere else.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
