# Adding a bling to the gallery

The gallery finds awards by looking at the **image embedded in a comment**, not
at the words around it. So adding an award means telling the catalogue which
image to watch for, and then re-running the matcher over the comment corpus.

## What to ask the awarder for

Paste this at them:

> - **Name of the bling** — as you'd like it to appear
> - **A line or two describing it** — what it's for, how you decide who gets it
> - **A link to the image you use when awarding it** — right-click the bling in
>   one of your own comments and copy the image address
> - **Any older versions** — if the file has changed over the years, send every
>   one you've used and I'll cover them all
> - **A link to your DPC profile** — so I can pick up your user id

The only thing that really matters technically is the third: **the same image
file every time**. A bling awarded with a different upload each time cannot be
found automatically.

## Finding what they already have

Before adding anything, see what is actually in the archive. This lists every
bling-shaped comment a member has written — a comment of theirs embedding an
image from their own portfolio — grouped by graphic:

```bash
uv run python - <<'PY'
import re
from collections import Counter
from sqlalchemy import text
from dpc.db.session import create_db_engine
from dpc.config import Settings

USER_ID = 30049          # <- the awarder
BUCKET = f"{USER_ID // 5000 * 5000}-{USER_ID // 5000 * 5000 + 4999}"

e = create_db_engine(Settings().database_url)
with e.connect() as c:
    rows = c.execute(text("""
        SELECT id, image_id, date, raw_comment FROM comments
        WHERE commenter_id = :u AND raw_comment LIKE :pat ORDER BY date
    """), {"u": USER_ID, "pat": f"%images_portfolio/{BUCKET}/{USER_ID}%"}).all()

    seen = Counter()
    for _, image_id, _, raw in rows:
        for gid in re.findall(r"Copyrighted_Image_Reuse_Prohibited_(\d+)", raw):
            if gid != str(image_id):
                seen[gid] += 1
    print(f"{len(rows)} comments embedding their own images")
    for gid, n in seen.most_common():
        print(f"  {gid:>9}  used {n:>4}x")
e.dispose()
PY
```

A graphic used many times across many images is a bling. One used once or twice
is usually a photo edit they made for someone — check a few of the comments
before assuming.

## Adding it

Append to `config/awards.yaml`. If the awarder is already listed, add to their
`awards:`; otherwise start a new block.

```yaml
- name: glad2badad          # their DPC username
  user_id: 30049            # the USER_ID from their profile URL
  awards:
  - name: Story Teller
    description: >
      Whatever they told you it is for. One or two sentences, written the way
      they would describe it.
    image: https://images.dpchallenge.com/images_portfolio/30000-34999/30049/120/Copyrighted_Image_Reuse_Prohibited_1200689.jpg
    markers:
    - Copyrighted_Image_Reuse_Prohibited_1200689
    - '1200689'
```

**Markers** are plain substrings tested against the comment's HTML. The image id
on its own is the reliable one; the full filename is a safety net. If the bling
has had several images over the years, list a marker for each — see `Kali`,
which was awarded with two different files.

Quote numeric markers. Unquoted, YAML hands back an int, and while the loader
coerces it, the file reads better consistent.

Two rules the loader enforces, both of which will fail loudly at `dpc check`:

- slugs must be unique across every awarder
- one awarder may not have two awards whose markers contain one another

That second rule exists because `vlado`'s MUAIMHO marker is the bare
`Copyrighted_Image_Reuse_Prohibited_` prefix, which matches any embedded image
at all. It is only safe while it stays their only award.

## Running it

**Run the matcher locally.** This is the step that matters, and it is easy to
get wrong:

```bash
dpc check                # validates the catalogue, touches no database
dpc awards               # scans the full comment corpus for the new markers
dpc export               # regenerate site/data/dpc
make backup              # fold the new grants into backups/sql
```

Then commit `config/awards.yaml`, `site/data/dpc` and `backups/sql` together.

**Committing `awards.yaml` alone is not enough**, even though the weekly refresh
runs `dpc awards` itself. The runner rebuilds its database from `backups/sql`,
which holds only the ~7,000 comments that already granted an award — the other
3.6 million are on your machine and nowhere else. So the runner would find the
new bling in challenges scraped from that day onward, and would silently miss
every historical award. Only a local `dpc awards` sees the whole corpus.

## Awards that were never given in a comment

Some blings are handed out in a forum thread rather than on the image page.
Nothing in the pipeline can find those: it reads image comments only, and a
thread post leaves no trace on the image.

`award_grants.comment_id` is nullable precisely for this — `Asigmatic` is
computed from vote variance and has no comment behind it — so such a grant is
representable, it just has to be inserted by hand. `find_grants` is additive and
skips any `(award_id, image_id)` pair that already exists, so a manual grant
survives every later run and will not be duplicated.

The better answer, where the awarder is still active, is to ask them to drop the
bling on the image itself in future. Then it is picked up for free.
