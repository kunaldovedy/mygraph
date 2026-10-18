PY ?= python3
export PYTHONPATH := src

.DEFAULT_GOAL := help

help:            ## Show this list
	@grep -hE '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | expand -t22

install:         ## Install the dependencies
	$(PY) -m pip install -r requirements.txt

check:           ## Validate the YAML without building anything
	$(PY) -m mygraph check

build:           ## Validate, write the database, the data file and the page
	$(PY) -m mygraph build

test:            ## Run the test suite
	$(PY) -m pytest tests -q

stats:           ## Print counts, provenance, leaders and gaps
	$(PY) -m mygraph stats

serve:           ## Serve the visualisation at http://127.0.0.1:8787/viz/
	$(PY) -m mygraph serve

exports:         ## Write Cypher, GraphML and Mermaid into build/
	$(PY) -m mygraph export cypher  --out build/mygraph.cypher
	$(PY) -m mygraph export graphml --out build/mygraph.graphml
	$(PY) -m mygraph export mermaid --out build/mygraph.mmd

clean:           ## Remove everything that is derived
	rm -rf build __pycache__ .pytest_cache src/mygraph/__pycache__ tests/__pycache__

all: check build test ## Check, build and test

.PHONY: help install check build test stats serve exports clean all

site-data:       ## Write the web payload into a site checkout (SITE=/path/to/site)
	@test -n "$(SITE)" || (echo "set SITE=/path/to/kunaldovedy.com" && exit 1)
	$(PY) -m mygraph export web --out "$(SITE)/src/app/graph/graph-data.json"
	$(PY) -m mygraph export web --out integrations/kunaldovedy.com/app/graph/graph-data.json

.PHONY: site-data
