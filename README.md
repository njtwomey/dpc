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

### Everyday: pull in new challenges

```bash
make parse
```

That is `dpc scrape --from-history`, then `dpc verify`, then `dpc awards`, then
`dpc export`. It only fetches challenges not already stored, so it is safe to
re-run — and safe to interrupt, since each challenge commits as a unit and a
failed one rolls back whole.

`verify` sits before `awards` so nothing is derived from a database that
contradicts itself; it exits non-zero only on integrity problems, so missing
data and inherited artefacts are reported without stopping the run.

Then commit `site/data/dpc/` and push; the deploy workflow does the rest.

### Scraping specific things

```bash
dpc scrape --challenge '[3729]'          # one challenge
dpc scrape --challenge '[3729,3730]'     # several
dpc scrape --from-history                # every challenge not yet stored
dpc scrape --incomplete                  # challenges missing some of their images
dpc scrape --from-history --no-images    # challenge metadata only, much faster
dpc scrape --challenge '[3729]' --refresh  # ignore the HTML cache and refetch
```

Explicit `--challenge` ids and `--incomplete` both mean "do these", so they
bypass the already-stored check. `--from-history` does not.

### Going faster

Fetching is I/O-bound and parsing is CPU-bound, so they are separated and use
different kinds of concurrency: a challenge's image pages are fetched together
on threads, then parsed — optionally across processes.

```bash
DPC_FETCH_WORKERS=8 DPC_REQUEST_DELAY=0.1 make parse   # the defaults
DPC_FETCH_WORKERS=1 DPC_REQUEST_DELAY=1.0 make parse   # gentle
DPC_PARSE_WORKERS=8 make parse                          # parse across processes
```

The delay is **per worker**, so the aggregate rate is roughly
`fetch_workers / request_delay` per second. Measured on a 40-image challenge:
90s at one worker and a 1s delay, 19s at eight workers and 0.1s.

Parsing costs about 14 ms/page, so it only becomes worth spreading across
processes once fetching is quick — at which point it is the slower half.

### Checking the archive

```bash
make verify     # or: dpc verify
```

Reports three things separately, and only the first is a failure:

- **integrity** — the database contradicting itself. Should always be empty.
- **missing data** — things to go and fetch, e.g. challenges holding only some
  of their images. `dpc scrape --incomplete` repairs these.
- **inherited** — artefacts the old scraper left behind, carried across
  faithfully by the migration. `dpc refresh-members` repairs the member ones.

```bash
dpc refresh-members                  # members stored with no name
dpc refresh-members --fabricated-dates   # + members sharing a scrape date
dpc refresh-members --ids '[99687]'      # specific ids
dpc refresh-members --limit 50           # stop after 50, to try it out first
```

### Awards and the site

```bash
dpc awards        # match comments against config/awards.yaml
dpc export        # write site/data/dpc/*.json
dpc check         # validate the catalogue, no database needed
make dev          # Hugo dev server against the committed data
```

### Backup and restore

```bash
make backup          # one SQL file per table -> backups/sql (committed)
make backup-awards   # only rows an award touches -> backups/sql-awards
make restore         # rebuild a database from backups/sql
make restore to=scratch.sqlite   # ...somewhere else
```

`backups/sql` is committed. Plain SQL rather than compressed, so git diffs and
delta-compresses the actual values instead of storing an opaque blob whole on
every version. `comments` is filtered to those that granted an award — 7,000-odd
rows rather than 3.6 million — which is what keeps it to ~58 MB; the largest
file, `images.sql`, is about 49 MB, under GitHub's 50 MB warning and 100 MB
limit.

The award scope goes further and keeps only rows an award touches. Rebuilding
from it produces a **byte-identical** `site/data/dpc` export to one built from
the full database — so it is enough to reconstruct the site, though it is not a
backup of the archive. The database itself is gitignored and lives only on your
machine.

### Starting from nothing

```bash
uv sync
cp .env.example .env && chmod 600 .env   # then fill in DPC_USERNAME/DPC_PASSWORD
make restore to=dpc.sqlite               # rebuild from the committed SQL
dpc verify                               # confirm it came back clean
dpc export                               # regenerate site/data/dpc
cd site && hugo                          # build the site
```

`make restore` gets you a working archive without scraping anything. From there
`make parse` brings it up to date.

### Schema changes

The schema is versioned with Alembic, so changes have a history:

```bash
# edit src/dpc/db/models.py, then
make revision m="add whatever"   # autogenerate the migration
dpc db-init                      # apply it
```

`tests/db/test_migrations.py` runs `alembic check`, so a model change without a
matching migration fails CI.

### Development

```bash
make check     # lint, format, types, tests -- everything CI runs
make test      # just the tests
make fmt       # format and apply safe lint fixes
make clean     # remove build output
```

Parser tests run against real captured pages in `tests/fixtures/html/`; see the
README there for which fixtures are genuine captures and which are synthesised.
`tests/test_site.py` runs a real Hugo build and checks that the Go template URL
builders agree with the Python ones, since the export ships ids rather than URLs.

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

## Deployment

GitHub Pages, published by `.github/workflows/deploy.yml` on any push to
`main` that touches `site/`. Set **Settings → Pages → Source** to
**GitHub Actions**.

Previously the built HTML was committed to a second repository,
`njtwomey/dpc`, and pushed by hand. That repo still serves the live site, so
archive it only once the first Actions deploy succeeds. Its local working copy
(`hugo-website/`) has been deleted; `git clone git@github.com:njtwomey/dpc.git`
brings it back if ever needed.
