# Chris Schor — Studies in Musical Perception

A minimal static portfolio and wearable interaction audio case study. No build or dependencies required.

## GitHub Pages

Create a public repository (use `<username>.github.io` for a root portfolio URL), upload this folder's contents, then select **Settings → Pages → Deploy from a branch → main → / (root)** and Save.

The application link should point directly to `/interaction-audio.html`.

## Editing

- `index.html`: portfolio homepage and contact links.
- `interaction-audio.html`: case study and cue players.
- `style.css`: shared responsive styles.
- WAV files: original reel and eight lossless extracts.

The original WAV is unchanged. Extracts preserve the source level, stereo channels, 44.1 kHz sample rate and 24-bit PCM format; only silence boundaries and metadata differ. Source cue order follows Chris's supplied list. Critical Error contains only the final three-hit burst. No normalization or synthesis was applied.

This is an independent concept study; no shipped product, hardware validation, or recognition test is claimed.


## Portfolio collections

`portfolio.json` is the canonical catalog. It defines a fixed vocabulary of 15 tags; reuse those tags when adding projects rather than inventing a synonym per entry. `philosophical` is reserved for work that warrants it and is hidden until used. Change the vocabulary only as a deliberate decision, keeping it at 20 tags or fewer.

For a new entry, add its HTML card inside the homepage Selected work section with a unique id, then add the same id to `projects` in `portfolio.json`. Assign existing tags and the next `addedOrder` integer. Put its card first in the saved HTML as well, so newest-first order works without JavaScript. Artwork and copy revisions retain the original order number.

`portfolio.js` validates ids and tags, orders the entries, and builds clickable tag collections. Collections have shareable links such as `/#tag=videogame`; browser Back/Forward restores them. Without JavaScript or a working catalog, all projects remain available in the HTML. `portfolio.css` styles only the homepage collections.

## A Musical Notepad

`/notepad/` is the continuous listening feed; `/notepad/<slug>/` is an entry's permanent page. The design and native audio behavior reuse the portfolio's existing styles and `player.js`. Generated pages work without JavaScript, a database, or a server-side runtime.

### Add recordings and images

1. Copy source files, leaving originals untouched, into `notepad/media/<entry-slug>/`. Use a distinct filename for each recording; never overwrite a previous version.
2. Copy the object in `notepad/ENTRY-TEMPLATE.json` into the `entries` array in `notepad/entries.json`. The template is an authoring example, not a live entry. Replace its filenames and image description with the actual supplied assets. Omit `images` and `feedImage` if there is no artwork.
3. Keep `draft: true` while preparing an entry. Fill in actual dates and labels rather than inferred production history. Dates use `YYYY-MM-DD`. Notes are optional plain-text paragraph arrays; summary and version notes are optional text. Image captions and descriptive alt text are supported. Set `feedImage` to the zero-based index of the image to show on the feed, or omit it for an audio-only feed entry.
4. Set `featuredVersion` to any recording ID. An additional recording does not automatically replace the featured recording. A published entry requires at least one recording.
5. When the entry is ready for review, set `draft: false` and run `python3 scripts/build_notepad.py`. This writes HTML locally; it never uploads or publishes. Commit/upload generated pages alongside the catalog and media only after Chris approves publication.

Select another representative recording with:

```sh
python3 scripts/build_notepad.py --feature i-want-you v2
```

This retains all recordings and dates. Set `updated` explicitly when appropriate; preserve `published`. The feed sorts by original publication date, newest first, with later-added catalog entries first when publication dates match; append new entries to the catalog and preserve its existing order. Individual pages list recordings by recording date, newest first. Drafts are omitted from generated HTML; draft catalog data and media are **not private** if uploaded to a public repository. Leave unapproved files local.

Run checks with `python3 -m unittest discover -s tests`. Preview with `python3 -m http.server 8000` and visit `/notepad/`. No build is required for visitors: the generator runs only when editing content.

### Download controls

Audio players use `controlslist="nodownload"`; visible download links have been removed from the portfolio. Browser support varies. This discourages casual downloading and is not access control: public playable audio and images remain retrievable, including from a public GitHub repository. Do not place confidential media in this site.

### Scope and generated files

The generator owns `notepad/index.html` and `notepad/<slug>/index.html`. It removes only its own stale generated detail pages when entries become drafts or leave the catalog. It never deletes media. Keep the catalog and generated HTML together when preparing a publication. No notepad examples or test recordings are included in the public feed.

For unusually wide text-based artwork, set `wide: true` on the image object. This places the image across the feed width instead of squeezing it into the side column; it does not crop or edit the source image.

## About page

`about.html` contains Chris's supplied photo and Discogs, SoundCloud, Instagram, LinkedIn and Resident Advisor profile links, with no visible photo caption or speculative date. `about.css` scopes the layout. `images/chris-schor-dj.jpg` is a byte-for-byte copy of the supplied photograph. The photo is not cropped or AI edited. About is linked from all pages, including the notepad generator so later entry builds preserve the link.
