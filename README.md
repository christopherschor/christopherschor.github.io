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
