#!/usr/bin/env python3
"""Generate buildless GitHub Pages notepad HTML from a single entry catalog."""
import argparse
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'notepad/entries.json'
E = lambda value: html.escape(str(value), quote=True)
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')

def paragraphs(items):
    return ''.join('<p>' + E(item).replace('\n', '<br>') + '</p>' for item in items)

def asset(value):
    path = Path(value)
    if path.is_absolute() or '..' in path.parts or not value.startswith('notepad/media/'):
        raise ValueError('Assets must be inside notepad/media/: ' + value)
    if not (ROOT / path).is_file():
        raise ValueError('Missing asset: ' + value)
    return value

def validate(data):
    if data.get('schemaVersion') != 1:
        raise ValueError('Unsupported catalog version')
    seen = set()
    for entry in data['entries']:
        slug = entry['slug']
        if not SLUG.fullmatch(slug) or slug in seen:
            raise ValueError('Invalid or duplicate entry slug: ' + slug)
        seen.add(slug)
        if not isinstance(entry.get('draft', True), bool):
            raise ValueError('draft must be true or false')
        if not entry.get('title', '').strip():
            raise ValueError('Entry needs a title: ' + slug)
        date.fromisoformat(entry['published'])
        date.fromisoformat(entry.get('updated', entry['published']))
        if entry.get('updated', entry['published']) < entry['published']:
            raise ValueError('Updated date precedes publication: ' + slug)
        for key in ('notes',):
            if not isinstance(entry.get(key, []), list) or any(not isinstance(v, str) for v in entry.get(key, [])):
                raise ValueError(key + ' must be a list of paragraphs')
        versions = entry.get('versions', [])
        ids = set()
        for version in versions:
            if not SLUG.fullmatch(version['id']) or version['id'] in ids:
                raise ValueError('Invalid or duplicate version id: ' + slug)
            ids.add(version['id'])
            if not version.get('label', '').strip():
                raise ValueError('Version needs a label')
            date.fromisoformat(version['date'])
            asset(version['audio'])
            if Path(version['audio']).suffix.lower() not in ('.mp3', '.m4a', '.wav', '.ogg'):
                raise ValueError('Unsupported audio format')
        if versions and entry.get('featuredVersion') not in ids:
            raise ValueError('Featured version must match an existing version: ' + slug)
        if not entry.get('draft', True) and not versions:
            raise ValueError('Published entry needs at least one recording: ' + slug)
        for picture in entry.get('images', []):
            asset(picture['src'])
            if Path(picture['src']).suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.avif'):
                raise ValueError('Unsupported image format')
            if not picture.get('alt', '').strip():
                raise ValueError('Image needs descriptive alt text: ' + slug)
        if 'feedImage' in entry and not 0 <= entry['feedImage'] < len(entry.get('images', [])):
            raise ValueError('feedImage must be an image index')

def stamp(value):
    return f'<time datetime="{E(value)}">{date.fromisoformat(value).strftime("%B %d, %Y").replace(" 0", " ")}</time>'

def image(picture, prefix):
    caption = '<figcaption>' + E(picture['caption']) + '</figcaption>' if picture.get('caption') else ''
    figure_class = ' class="image-wide"' if picture.get('wide') else ''
    return f'<figure{figure_class}><img src="{E(prefix + picture["src"])}" alt="{E(picture["alt"])}" loading="lazy">{caption}</figure>'

def player(entry, version, prefix):
    mime = {'.mp3': 'audio/mpeg', '.m4a': 'audio/mp4', '.wav': 'audio/wav', '.ogg': 'audio/ogg'}[Path(version['audio']).suffix.lower()]
    return f'<audio controls controlslist="nodownload" preload="metadata" aria-label="{E(entry["title"] + " — " + version["label"])}"><source src="{E(prefix + version["audio"])}" type="{mime}">Your browser does not support audio playback.</audio>'

def shell(title, description, body, prefix):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="dark">
<title>{E(title)} — Chris Schor</title><meta name="description" content="{E(description)}">
<link rel="stylesheet" href="{prefix}style.css"><link rel="stylesheet" href="{prefix}notepad/notepad.css"><script src="{prefix}player.js" defer></script>
</head><body><a class="skip" href="#main">Skip to content</a>
<header class="wrap site-header"><a class="wordmark" href="{prefix}" aria-label="Chris Schor home">CHRIS SCHOR<span class="mark" aria-hidden="true"> / </span>SOUND</a>
<nav aria-label="Main navigation"><a href="{prefix}interaction-audio.html">Interaction audio</a><a href="{prefix}experiential-audio.html">Immersive narrative audio</a><a href="{prefix}notepad/" aria-current="page">Sketches, WIPs, Noises</a><a href="{prefix}about.html">About</a><a href="{prefix}#contact">Contact</a></nav></header>
<main id="main" class="wrap notepad">{body}</main>
<footer class="wrap"><span>Chris Schor · Sound design &amp; music</span><a href="{prefix}">Studies in Musical Perception</a></footer></body></html>\n'''

def render(data):
    entries = [entry for _, entry in sorted(
        ((index, entry) for index, entry in enumerate(data['entries']) if not entry.get('draft', True)),
        key=lambda item: (item[1]['published'], item[0]), reverse=True)]
    feed = '<section class="hero"><p class="eyebrow">Sketches, WIPs, Noises</p><h1>A Musical Notepad</h1><p class="intro notepad-intro">Musical sketches, unfinished productions, sonic experiments, and occasional finished pieces.</p></section><section aria-label="Musical entries">'
    for entry in entries:
        featured = next(v for v in entry['versions'] if v['id'] == entry['featuredVersion'])
        slug = entry['slug']
        meta = stamp(entry['published']) + (' · ' + E(entry['status']) if entry.get('status') else '')
        feed += f'<article class="notepad-entry" id="{slug}" aria-labelledby="{slug}-title"><div class="entry-copy"><p class="eyebrow">{meta}</p><h2 id="{slug}-title"><a href="{slug}/">{E(entry["title"])}</a></h2>'
        if entry.get('summary'):
            feed += paragraphs([entry['summary']])
        feed += f'<p class="recording-label">{E(featured["label"])} · Featured recording</p>' + player(entry, featured, '../')
        count = len(entry['versions'])
        feed += f'<a class="text-link" href="{slug}/">Explore entry · {count} recording{"s" if count != 1 else ""}</a></div>'
        if 'feedImage' in entry:
            feed += image(entry['images'][entry['feedImage']], '../')
        feed += '</article>'
        detail = f'<section class="case-hero"><a class="back" href="../#{slug}">A Musical Notepad</a><p class="eyebrow accent">{E(entry.get("status", "Musical entry"))}</p><h1>{E(entry["title"])}</h1><div class="project-meta"><span>Added {stamp(entry["published"])}</span>'
        if entry.get('updated') and entry['updated'] != entry['published']:
            detail += '<span>Updated ' + stamp(entry['updated']) + '</span>'
        detail += '</div></section>'
        if entry.get('summary'):
            detail += '<div class="entry-notes">' + paragraphs([entry['summary']]) + '</div>'
        detail += '<div class="entry-notes">' + paragraphs(entry.get('notes', [])) + '</div>'
        detail += '<div class="entry-images">' + ''.join(image(p, '../../') for p in entry.get('images', [])) + '</div>'
        detail += '<section class="recordings" aria-labelledby="recordings-title"><h2 id="recordings-title">Recordings</h2>'
        for version in sorted(entry['versions'], key=lambda v: v['date'], reverse=True):
            badge = '<span class="featured-badge">Featured on the notepad</span>' if version['id'] == entry['featuredVersion'] else ''
            detail += f'<article class="recording" id="{E(version["id"])}"><p class="eyebrow">{stamp(version["date"])}</p><h3>{E(version["label"])}</h3>{badge}'
            if version.get('notes'):
                detail += paragraphs([version['notes']])
            detail += player(entry, version, '../../') + '</article>'
        detail += '</section>'
        yield Path('notepad') / slug / 'index.html', shell(entry['title'], entry.get('summary', entry['title'] + ' — A Musical Notepad.'), detail, '../../')
    if not entries:
        feed += '<p class="empty-notepad">The first recordings are on their way.</p>'
    feed += '</section>'
    yield Path('notepad/index.html'), shell('A Musical Notepad', 'Sketches, WIPs, Noises — a musical notepad by Chris Schor.', feed, '../')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feature', nargs=2, metavar=('ENTRY', 'VERSION'), help='Select the feed recording, retaining every version')
    args = parser.parse_args()
    data = json.loads(CATALOG.read_text())
    validate(data)
    if args.feature:
        slug, version_id = args.feature
        entry = next((e for e in data['entries'] if e['slug'] == slug), None)
        if not entry or version_id not in [v['id'] for v in entry['versions']]:
            raise ValueError('Unknown entry or version')
        entry['featuredVersion'] = version_id
        validate(data)
    pages = list(render(data))  # Validate and render everything before writing any page.
    if args.feature:
        CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    for path, content in pages:
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    # Removed/drafted entries must not leave stale public pages. Touch only generator-owned HTML.
    expected = {ROOT / path for path, _ in pages}
    for stale in (ROOT / 'notepad').glob('*/index.html'):
        if stale not in expected and 'class="wrap notepad"' in stale.read_text():
            stale.unlink()
    print(f'Built {len(pages)} notepad page(s). No publication performed.')

if __name__ == '__main__':
    main()
