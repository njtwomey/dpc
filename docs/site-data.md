# Exported site data

`site/data/dpc/*.json` are the build input for the Hugo site, and the only thing that
crosses from the local machine to CI. Produce them with:

```bash
dpc export
```

Then commit the result. The export is deterministic — an unchanged database
re-exports byte-identically — so a diff here means the underlying data really
changed, and the diff is worth reading.

Each record is minified onto its own line. That is within a few hundred bytes of
fully minified once git has compressed it, while keeping a changed challenge to
one changed line instead of turning the whole file into a single altered blob.

The database itself and the scraped HTML cache stay local and are gitignored.

| File | Contents |
| --- | --- |
| `meta.json` | schema version and row counts |
| `awarders.json` | who gives awards, and how many they have given |
| `awards.json` | each award, its tallies, and the images that won it |
| `challenges.json` | each challenge, newest first, with per-award counts |
| `recipients.json` | each photographer, most-awarded first |
| `images.json` | every awarded image, keyed by id as a string |

Files store **ids, not URLs**. Every dpchallenge asset URL is derivable from an
id, and spelling them out is what made the previous export 38 MB. The Go
templates in `site/layouts/partials/urls/` rebuild them, and
`tests/test_site.py` pins those against the Python implementation in
`src/dpc/export/urls.py`.
