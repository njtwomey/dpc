# HTML fixtures

## Real captures

Fetched from dpchallenge and committed verbatim. Everything the tests assert
about them was read off the real page.

| File | What it is | Why it is here |
| --- | --- | --- |
| `challenge/results.html` | `CHALLENGE_ID=1303`, "Posthumous Ribbon" (Nov 2010) | a finished challenge: the stats block, the `<b>Description</b>` heading, `23,001` votes with a thousands separator, and 133 image links |
| `challenge/invalid.html` | `CHALLENGE_ID=75` | the site's "Invalid CHALLENGE_ID" response. Some low ids really do return this. |
| `challenge/unfinished.html` | `CHALLENGE_ID=3882`, captured mid-voting | a *Challenge Details* page. The old parser had no notion of this third page type: it produced garbage from it and then cached it permanently, so the challenge was never revisited once it finished. |
| `image/anonymous.html` | `IMAGE_ID=921974`, fetched without a session | 29 real comments, and a full statistics panel — these numbers are public, no login needed. Still carries `Avg (commenters)`, which newer pages omit. |
| `image/scored.html` | `IMAGE_ID=1287065`, trimmed | the **current** statistics markup: headed "Statistics", `Place: 1 out of 40`, and no vote histogram at all. Trimmed to the title, photographer link and stats table so the repository does not republish other members' comments. |
| `member/odriew.html` | `USER_ID=75618` | `Name:` and `Username:` are different fields; `Registered: Mar. 16th 2007` has an ordinal suffix and a dotted month |
| `history/page.html` | `challenge_history.php`, first 60 rows | the full page is 2.7 MB. Note it interleaves still-open challenges (4193–4197) among the finished ones, so the listing is **not** sorted. |

## Synthesised

Built to the markup contract, for cases a real capture cannot cover.

| File | What it exercises | Why not real |
| --- | --- | --- |
| `image/scored.html` | full stats, `1,234` views, an edited comment | the voting-breakdown panel needs a logged-in session |
| `image/disqualified.html` | panel present, averages absent | same |
| `image/no_comments.html` | no comment table at all | same |
| `member/cancelled.html` | the red-font cancellation notice | no cancelled account to hand |
| `encoding/cp1252.html` | raw `0x97` bytes | the source of the `\x97` mojibake |

## On the legacy image fixtures

`image/scored.html` and `image/disqualified.html` encode assumptions about a
panel none of these captures contains. Replace them with real pages on the first
authenticated scrape — they are the last guesses left in the fixture set.

A *missing* panel and a *disqualified* image are different things, and
`ImageStatsUnavailableError` keeps them apart. Confusing the two would mark the
entire archive disqualified.
