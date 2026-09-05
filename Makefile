# Developer tasks. The data pipeline itself lives in the `dpc` CLI --
# `uv run dpc --help` -- so it is deliberately not mirrored here, where the
# targets could only ever hide the CLI's own options.
#
# Tools are invoked through the venv directly rather than through `uv run`:
# uv revalidates the environment against uv.lock on every invocation, which
# costs far more than the checks themselves. `make install` builds that venv.

PY := .venv/bin/python

.PHONY: help install check test fmt serve revision backup clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install:  ## Sync the virtualenv from uv.lock
	uv sync --locked

$(PY):
	@echo "no virtualenv yet -- run 'make install'" >&2; exit 1

check: $(PY)  ## Everything CI runs: lint, format, types, tests
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .
	$(PY) -m mypy
	$(PY) -m pytest -q

test: $(PY)  ## Run the test suite
	$(PY) -m pytest -q

fmt: $(PY)  ## Format and apply safe lint fixes
	$(PY) -m ruff format .
	$(PY) -m ruff check --fix .

serve:  ## Hugo dev server against the committed data
	cd site && hugo server --disableFastRender

revision: $(PY)  ## Autogenerate a migration after changing models (make revision m="add x")
	$(PY) -m alembic revision --autogenerate -m "$(m)"

backup:  ## Snapshot the database to backups/ (local only, never committed)
	@mkdir -p backups
	@f=backups/dpc-$$(date +%F).sqlite; \
	 rm -f $$f $$f.xz; \
	 sqlite3 dpc.sqlite "VACUUM INTO '$$f'" && xz -6 $$f && ls -lh $$f.xz

clean:  ## Remove build output. Leaves .mypy_cache: rebuilding it is slow and it is gitignored.
	rm -rf site/public site/resources site/.hugo_build.lock
	rm -rf .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -not -path './.venv/*' -exec rm -rf {} +
