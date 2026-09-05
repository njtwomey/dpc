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

Every `dpc` command warns if `.env` is readable beyond its owner.

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

## Backups

The database holds other members' comments, so it is not ours to publish, and it
stays out of git entirely — git keeps every version forever, which is the
opposite of what a backup wants. `database-backup/` and `backups/` are ignored.

```bash
make backup          # one SQL file per table -> backups/sql
make backup-awards   # only rows an award touches -> backups/sql-awards
make restore         # rebuild a SQLite database from backups/sql
```

`backups/sql` is committed. The dumps are plain SQL, one file per table,
deliberately not compressed: the point is for git to diff and delta-compress the
actual values rather than store an opaque blob whole on every version. The
largest file, `images.sql`, is about 49 MB — under GitHub's 50 MB warning and
its 100 MB hard limit.

`comments` is filtered to those that granted an award — around 7,000 rows rather
than 3.6 million. The award scope goes further and keeps only rows an award
touches; it is about 6.5 MB of text, and rebuilding from it produces a
**byte-identical** `site/data/dpc` export to the one built from the full 1.2 GB
database. The archive itself — the other 380,000 images and 3.6M comments — is
not in either dump and lives only in `dpc.sqlite`.

> `database-backup/backup.sql.zip` — a 2020 dump — was tracked in git LFS until
> recently. It is untracked now, but the object is still in history and still in
> the LFS store. Since it contains other members' comments, purge it properly
> rather than leaving it:
>
> ```bash
> git filter-repo --path database-backup/backup.sql.zip --invert-paths
> ```
>
> then force-push and ask GitHub support to clear the orphaned LFS object; a
> plain delete commit reclaims neither the history nor the quota.

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

`make help` lists the developer tasks (tests, linting, the Hugo dev server). The pipeline itself lives in the CLI, not in the Makefile.

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
config/awards.yaml  the hand-maintained award catalogue
src/dpc/
  config.py     Settings (no secrets) and Credentials (secrets), kept apart so
                export and site builds never need a login
  parse/        pure functions: HTML string in, dataclass out. No network, no
                database — which is what makes them testable
  scrape/       HTTP client, HTML cache, and the crawler that composes the above
  db/           SQLAlchemy models and session handling
  awards/       the award catalogue and comment matching
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

`config/awards.yaml` lists each awarder and the marker substrings that identify their
award inside a comment's HTML. It is validated on load: markers may not be
blank, slugs must be unique across awarders, and no awarder may have two awards
whose markers contain one another — that last rule exists because `vlado`'s
MUAIMHO marker is the bare `Copyrighted_Image_Reuse_Prohibited_` prefix, which
matches every embedded image and is only safe while it is their only award.

Awards are only ever found in comments that actually gave them; nothing is
derived after the fact. Matching ignores anything a comment *quotes*, because
replying to an award copies its image into the reply and would otherwise award
it twice — see <https://www.dpchallenge.com/image.php?IMAGE_ID=1160121>.

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
`main` that touches `site/`. Set **Settings → Pages → Source** to
**GitHub Actions**.

Previously the built HTML was committed to a second repository,
`njtwomey/dpc`, and pushed by hand. That repo still serves the live site, so
archive it only once the first Actions deploy succeeds. Its local working copy
(`hugo-website/`) has been deleted; `git clone git@github.com:njtwomey/dpc.git`
brings it back if ever needed.
