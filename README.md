# dpc-parser

Scrapes the user-invented awards ("bling") that members of
[DPChallenge](https://www.dpchallenge.com) give each other in image comments,
and builds a static gallery of the images that won them.

Scraping runs locally, because the database is local. The site is built and
deployed by GitHub Actions from a small JSON dataset committed to this repo.

```
 local machine                                    │  GitHub Actions
                                                  │
 dpc scrape   ──▶  dpc.sqlite  ──▶  dpc export  ──┼─▶  hugo  ──▶  Pages
 (needs login)     (gitignored)     site/data/dpc │
                                    (committed)   │
```

The only thing that crosses the line is `site/data/dpc/*.json`. CI needs no
database, no credentials and no network access to dpchallenge.

## Setup

```bash
uv sync
cp .env.example .env
chmod 600 .env            # it will hold a plaintext password
# then fill in DPC_USERNAME and DPC_PASSWORD
```

Every `dpc` command warns if `.env` is readable beyond its owner; `make secure`
fixes it.

Credentials live only in `.env`, which is gitignored. The password is held as a
`SecretStr`, so it cannot reach a log line, a repr or a traceback —
`tests/test_config.py` enforces that.

> **One piece of cleanup left.** `.env` was committed in `edea4e7` and stayed
> tracked, so the `.gitignore` entry never applied to it — gitignore does not
> affect files already in the index. It is untracked now, but the old Postgres
> credentials remain in that commit. The repo is private and Postgres is being
> retired in favour of SQLite, so the practical risk is low; still, rotate that
> password, and scrub history with `git filter-repo --path .env --invert-paths`
> if you would rather it were gone.

## Migrating the old Postgres database

The previous incarnation used Postgres. To bring it across:

```bash
createdb dpcdb
psql -d dpcdb -f database-backup/backup.sql

uv run python scripts/migrate_pg_to_sqlite.py \
    --source postgresql+psycopg://niall@localhost:5432/dpcdb \
    --target sqlite+pysqlite:///dpc.sqlite
```

Re-runnable; it recreates the target each time.

## Usage

```bash
dpc db-init                        # create or upgrade the schema (Alembic)
dpc scrape --from-history          # discover and fetch new challenges
dpc scrape --challenge '[3880,3881]'
dpc awards                         # match comments against the catalogue
dpc export                         # write site/data/dpc/*.json
dpc check                          # validate awards.yaml, no database needed
```

Then commit `site/data/dpc/` and push. The deploy workflow does the rest.

The dataset's shape is documented in [docs/site-data.md](docs/site-data.md).

`make help` lists the same steps as targets.

### Schema changes

The schema is versioned with Alembic, so changes have a history:

```bash
# edit src/dpc/db/models.py, then
make revision m="add whatever"
make migrate
```

`tests/db/test_migrations.py` runs `alembic check`, so a model change without a
matching migration fails CI.

## Layout

```
src/dpc/
  config.py     Settings (no secrets) and Credentials (secrets), kept apart so
                export and site builds never need a login
  parse/        pure functions: HTML string in, dataclass out. No network, no
                database — which is what makes them testable
  scrape/       HTTP client, HTML cache, and the crawler that composes the above
  db/           SQLAlchemy models and session handling
  awards/       the award catalogue, comment matching, and derived awards
  export/       database to deterministic JSON
site/
  content/*/_content.gotmpl   content adapters: every award, challenge and
                              recipient page is generated at build time from
                              the JSON, so nothing under content/ is written by
                              a machine
  layouts/                    templates (no theme indirection)
  data/dpc/                   the committed export
tests/                        mirrors src/dpc/
```

## The award catalogue

`awards.yaml` lists each awarder and the marker substrings that identify their
award inside a comment's HTML. It is validated on load: markers may not be
blank, slugs must be unique across awarders, and no awarder may have two awards
whose markers contain one another — that last rule exists because `vlado`'s
MUAIMHO marker is the bare `Copyrighted_Image_Reuse_Prohibited_` prefix, which
matches every embedded image and is only safe while it is their only award.

## Development

```bash
uv run pytest             # 170+ tests, no database or network required
uv run ruff check .
uv run ruff format .
uv run mypy
```

Parser tests run against real captured pages in `tests/fixtures/html/`; see the
README there for which fixtures are genuine captures and which are synthesised.
`tests/test_site.py` runs a real Hugo build and checks that the Go template URL
builders agree with the Python ones, since the export ships ids rather than URLs.

## Deployment

GitHub Pages, published by `.github/workflows/deploy.yml` on any push to
`master` that touches `site/`. Set **Settings → Pages → Source** to
**GitHub Actions**.

Previously the built HTML was committed to a second repository,
`njtwomey/dpc`, and pushed by hand. That repo still serves the live site, so
archive it only once the first Actions deploy succeeds. Its local working copy
(`hugo-website/`) has been deleted; `git clone git@github.com:njtwomey/dpc.git`
brings it back if ever needed.
