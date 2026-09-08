# Automated refresh

**Status: built, never run on a runner.** `.github/workflows/refresh.yml`
exists and the whole pipeline has been rehearsed locally against a scratch
database, including a deliberate drop-and-refetch. It has not yet executed on
GitHub.

Measurements below were taken on 2026-09-05 against the archive as it stood at
`e6182b7`.

## The short answer

It works, and two facts make it far less awkward than it sounds.

**The scrape does not need a login.** Every page the crawler reads parses
completely for an anonymous client. See [No login required](#no-login-required).

**The committed SQL backup restores to a complete archive in under three
seconds**, so a runner can start from a real database rather than an empty one.

## Restoring in CI

`backups/sql/` is committed (about 60 MB, ordered by rowid so git deltas it
well). Restoring it into a scratch file:

```bash
DPC_DATABASE_URL="sqlite+pysqlite:///$RUNNER_TEMP/dpc.sqlite"
uv run python scripts/restore_sql.py --from backups/sql --to "$RUNNER_TEMP/dpc.sqlite"
```

took **2.7 s** and produced a 73 MB database:

| table | rows |
| --- | --- |
| members | 35,046 |
| challenges | 4,148 |
| images | 399,485 |
| comments | 7,389 (award-granting only) |
| award_grants | 7,389 |
| challenge_probes | 469 |

Running `dpc verify`, `dpc awards` and `dpc export` against that scratch
database reproduced all six files in `site/data/dpc/` **byte-identically** to
what is committed, and `dpc awards` created nothing — it is idempotent.

`DPC_DATABASE_URL` redirects every command, because `Settings.database_url` is
an ordinary `pydantic-settings` field. Nothing about the database path needed
changing.

### Rehearsed end to end

Against a scratch restore, with challenge 4192 and everything hanging off it
deleted first (1 challenge, 20 images, 2 comments, 2 grants):

| step | result |
| --- | --- |
| `dpc scrape --anonymous --from-history` | "1 of 4147 challenges to fetch" — refetched it, 20 images, 50 comments |
| `dpc verify` | exit 0 |
| `dpc awards` | rediscovered exactly the 2 grants from the refetched comments |
| `dpc export` | all six files **byte-identical** to what is committed |

The scrape found only the hole, not 4,147 challenges, and the archive healed
itself with no credentials in the environment.

### Why a partial restore is enough

The dump keeps only the comments that granted an award — that is what holds it
to 60 MB instead of gigabytes — and the missing 3.6 M comments cost nothing:

- `Crawler.pending_challenge_ids` filters on stored challenge ids and on the
  `challenge_probes` "invalid" memo. Both survive the dump, so a run fetches
  only genuinely new challenges rather than re-crawling the site.
- `awards.service.find_grants` is purely additive. It skips any
  `(award_id, image_id)` already granted and never deletes, so absent comments
  cannot retract an existing grant.

## No login required

`DpcClient` was pointed at the live site with `credentials=None` and `login()`
never called. Every page type the crawler uses parsed in full:

| page | anonymous result |
| --- | --- |
| `challenge_history.php?show_all=1` | 4,147 ids, newest 4197 |
| `challenge_results.php?CHALLENGE_ID=…&show_full=1` | classified `results`; name, vote and submission counts, all 20 image ids |
| `image.php?IMAGE_ID=…` | name, photographer, position, averages, views, votes, and the comment thread |
| `profile.php?USER_ID=…` | name, join date, cancelled flag |

Comment threads come back complete. Five images with more than twelve stored
comments were refetched anonymously and every count matched exactly
(17/17, 17/17, 20/20, 72/72, 30/30). That matters more than anything else on
this page, because the award markers live in comment HTML.

`dpc scrape --anonymous` is the switch. It skips constructing `Credentials`
entirely, so CI needs no secrets; without the flag the scraper still logs in,
which stays the default for local runs.

The one field missing anonymously is the vote histogram (`images.votes`), and it
is missing when logged in too — the site stopped publishing it around 2024:

| voting year | images | with histogram |
| --- | --- | --- |
| 2023 | 5,518 | 5,518 |
| 2024 | 4,178 | 934 |
| 2025 | 5,333 | 83 |
| 2026 | 4,030 | 2 |

Those recent challenges were all scraped with a logged-in session. Nothing in
`src/dpc/export/` reads the histogram, so the site does not miss it either.

This has not been tested exhaustively — one challenge, one profile, five
comment threads — and it says nothing about how dpchallenge treats a datacentre
IP. But the login step looks optional rather than load-bearing.

## Shape of the workflow

`.github/workflows/refresh.yml`. One workflow doing everything, rather than a
scrape job that pushes and a deploy job that reacts to the push. **Pushes made
with the default `GITHUB_TOKEN` do not trigger other workflows**, so a split
design would commit new data and then quietly fail to publish it. Keeping it in
one workflow also keeps a refresh to a single Actions run.

`workflow_dispatch` takes a `publish` input; setting it false does everything
and reports the diff without committing, which is the safe way to try it.

```
schedule (weekly) + workflow_dispatch
  ├─ checkout, setup-uv, setup-node
  ├─ restore backups/sql  → $RUNNER_TEMP/dpc.sqlite
  ├─ dpc scrape --anonymous --from-history   (DPC_DATABASE_URL → scratch db)
  ├─ dpc verify
  ├─ dpc awards
  ├─ dpc export
  ├─ dump_sql.py → backups/sql
  ├─ stop here if nothing changed
  ├─ commit site/data/dpc + backups/sql
  └─ npm ci && npm run build && deploy-pages
```

Runtime: dpchallenge has run about 3.5 challenges a week since 2024 (2.4 so far
in 2026) at roughly 31 images each. At the measured ~19 s per challenge that is
well under two minutes of scraping for a weekly run, plus three seconds to
restore and a few for the site build.

No secrets are configured. If you ever want the runner to log in, set
`DPC_USERNAME` and `DPC_PASSWORD` as repository secrets, export them into the
job and drop `--anonymous`: `Credentials` is a `BaseSettings` with
`env_prefix="DPC_"` and tolerates the absent `.env`, so no file needs writing,
and `tests/test_log.py` already pins that the password never reaches a log line.

### A bug this found

Rehearsing the round trip turned up a real defect in `scripts/restore_sql.py`.
`Path.read_text()` uses universal newlines, so restoring rewrote every carriage
return in stored comment HTML to a newline — 21,806 characters of the archive,
silently, on every restore. Invisible while nobody restores in anger; fatal to a
design that restores weekly, because each run would mutate the archive and bury
the real diff. Both scripts now read and write with `newline=""`, and
`tests/test_backup.py` pins the round trip byte-for-byte. The real 60 MB archive
now restores and re-dumps to eight identical files.

## What it would cost

**The comment corpus stops growing.** This is the real objection. A scheduled
run fetches full comment threads for new challenges, matches awards against
them, and then throws them away: the dump filters comments down to
award-granting ones, and the scratch database evaporates with the runner. The
corpus kept for later ML work would freeze at whatever the last local
`make parse` captured. Keeping it means still running the scrape locally, at
which point the automation is only saving the export-and-publish half — or
committing the full comment corpus, which was ruled out deliberately as not
something to publish.

**Every run rewrites 60 MB of SQL.** `images.sql` alone is 52 MB. It is ordered
by rowid so new rows append and the delta is small, but each run still adds
objects to the pack. The workflow gates the commit on `git diff --quiet`, so a
week where dpchallenge ran nothing new costs nothing and publishes nothing.

Note that refetching an existing challenge does produce a genuine diff: view
counts move on the live site. The workflow only fetches challenges it does not
already have, so this does not cause churn in normal operation.

**`dpc verify` exits 1 on an integrity contradiction** and would abort the job
before it publishes. That is probably the right instinct — better a stale site
than a wrong one — but it is a decision to make on purpose rather than discover.

## Open questions

- How dpchallenge responds to a GitHub runner's IP, anonymous or otherwise.
- Whether to drop the login entirely, keep it as a fallback, or keep it because
  it is the polite thing to do when scraping a site you have permission to
  scrape.
- Scheduled workflows are best-effort on the free tier and can be delayed by
  hours. A weekly cadence absorbs that; a daily one mostly does too.
