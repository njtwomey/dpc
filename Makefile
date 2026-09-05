.PHONY: help install migrate revision scrape awards export site serve build test lint fmt typecheck check clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Sync the virtualenv from uv.lock
	uv sync --locked

migrate:  ## Create or upgrade the database schema
	uv run dpc db-init

revision:  ## Autogenerate a migration after changing the models (make revision m="add x")
	uv run alembic revision --autogenerate -m "$(m)"

scrape:  ## Fetch new challenges from the site history
	uv run dpc scrape --from-history

awards:  ## Match comments against the award catalogue
	uv run dpc awards

export:  ## Write site/data/dpc/*.json
	uv run dpc export

site: awards export  ## Refresh awards then re-export the site data

serve:  ## Hugo dev server against the committed data
	cd site && hugo server --disableFastRender

build:  ## Production Hugo build
	cd site && hugo --minify

test:  ## Run the test suite
	uv run pytest -q

lint:  ## Lint
	uv run ruff check .

fmt:  ## Format
	uv run ruff format .

typecheck:  ## Type-check
	uv run mypy

check: lint typecheck test  ## Everything CI runs

clean:  ## Remove build output and caches
	rm -rf site/public site/resources site/.hugo_build.lock
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
