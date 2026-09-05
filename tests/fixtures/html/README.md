# HTML fixtures

## Real captures

Taken verbatim from the scraper's on-disk cache (`downloaded/`).

| File | What it is |
| --- | --- |
| `challenge/invalid.html` | `CHALLENGE_ID=1` — the site's "Invalid CHALLENGE_ID" response |
| `challenge/unfinished.html` | `CHALLENGE_ID=3882` — a *Challenge Details* page for a challenge still open. The old parser had no notion of this page type: it would parse garbage out of it and then cache it permanently, so the challenge was never revisited once it finished. |

## Synthesised

Built to the markup contract the previous parser encoded (the selectors, labels
and inline styles it relied on), because the cache held no authenticated capture
of these pages.

| File | What it exercises |
| --- | --- |
| `challenge/results.html` | a finished challenge; em dash in the title; duplicate image links |
| `member/normal.html` | `Registered: Jan. 1st 2004` — ordinal suffix and `.`-separated month |
| `member/cancelled.html` | the red-font cancelled-membership notice |
| `image/scored.html` | full stats, `1,234` views, two comments, one of them edited |
| `image/disqualified.html` | no `Avg (all users)`, so averages and place are absent |
| `image/no_comments.html` | no comment table at all |
| `history/page.html` | challenge-id extraction with a duplicate and an unrelated link |
| `encoding/cp1252.html` | raw `0x97` bytes — the source of the `\x97` mojibake |

**Replace the synthesised ones with real captures on the first authenticated
scrape.** They encode assumptions about labels and markup that only a real page
can confirm. `dpc scrape --save-fixture` is the intended way to do that.
