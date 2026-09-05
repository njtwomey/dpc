# Developer tasks. The data pipeline itself lives in the `dpc` CLI --
# `uv run dpc --help` -- so it is deliberately not mirrored here, where the
# targets could only ever hide the CLI's own options.
#
PY := uv run python
DPC := uv run dpc

.PHONY: help install check test fmt parse serve revision backup backup-awards restore clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install:  ## Sync the virtualenv from uv.lock
	uv sync --locked

check:  ## Everything CI runs: lint, format, types, tests
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .
	$(PY) -m mypy
	$(PY) -m pytest -q

test:  ## Run the test suite
	$(PY) -m pytest -q

fmt:  ## Format and apply safe lint fixes
	$(PY) -m ruff format .
	$(PY) -m ruff check --fix .

parse:  ## Fetch new challenges, rematch awards, refresh site/data/dpc
	$(DPC) scrape --from-history
	$(DPC) awards
	$(DPC) export

serve:  ## Hugo dev server against the committed data
	cd site && hugo server --disableFastRender

revision:  ## Autogenerate a migration after changing models (make revision m="add x")
	$(PY) -m alembic revision --autogenerate -m "$(m)"

# Plain SQL, not gzipped: the point is for git to diff and delta-compress the
# actual values. A gzipped dump is an opaque blob stored whole every version.
backup:  ## Dump one SQL file per table to backups/sql
	$(PY) scripts/dump_sql.py --out backups/sql

backup-awards:  ## Award-scoped dump: only rows an award touches
	$(PY) scripts/dump_sql.py --out backups/sql-awards --scope awards

restore:  ## Rebuild a SQLite database from a dump (make restore to=rebuilt.sqlite)
	$(PY) scripts/restore_sql.py --from backups/sql --to $(or $(to),rebuilt.sqlite)

clean:  ## Remove build output. Leaves .mypy_cache: rebuilding it is slow and it is gitignored.
	rm -rf site/public site/resources site/.hugo_build.lock
	rm -rf .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -not -path './.venv/*' -exec rm -rf {} +
