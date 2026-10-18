# Private overlay

Everything in this directory except this file is ignored by git.

The loader reads `data/private/nodes/*.yaml` and `data/private/edges/*.yaml`
when they exist, using exactly the same format as `data/nodes/` and
`data/edges/`. Put client names, unlaunched work, private repositories or
anything else you would rather not publish here. It appears in your local
graph, the database and the page, and never in a commit.

```bash
mkdir -p data/private/nodes data/private/edges
```
