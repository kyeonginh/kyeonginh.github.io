#!/usr/bin/env python3
"""Build a portable static academic website. Python 3.10+, standard library only."""
import argparse
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def esc(value):
    return html.escape(str(value), quote=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true', help='Include provisional presentation selections in an explicitly labelled local preview.')
    args = parser.parse_args()
    content = json.loads((ROOT / 'site/content.json').read_text())
    output = ROOT / ('preview' if args.preview else 'dist')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    (output / 'assets').mkdir()
    shutil.copyfile(ROOT / 'site/style.css', output / 'assets/style.css')
    shutil.copyfile(ROOT / 'site/favicon.svg', output / 'assets/favicon.svg')
    cv = content.get('cv')
    if cv:
        (output / 'assets/documents').mkdir()
        shutil.copyfile(ROOT / 'assets/documents' / cv, output / 'assets/documents' / cv)
    (output / '.nojekyll').touch()
    if args.preview:
        (output / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    notes = [n for n in content['notes'] if n['status'] == 'published' or args.preview]
    for note in notes:
        folder = ROOT / ('preview-materials' if note['status'] != 'published' else 'assets/documents')
        (output / 'assets/documents').mkdir(exist_ok=True)
        target = output / 'assets/documents' / note['pdf']
        source = folder / note['pdf']
        if source.resolve() != target.resolve():
            shutil.copyfile(source, target)
        image_dir = output / 'assets/images'
        image_dir.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / 'assets/images' / note['image'], image_dir / note['image'])

    def page(title, body, prefix='', active=''):
        nav = [('', 'About', 'home')]
        if notes:
            nav.append(('archive.html', 'Notes', 'notes'))
        if cv:
            nav.append((f'assets/documents/{cv}', 'CV', 'cv'))
        links = ''.join(f'<a href="{prefix}{href or "index.html"}"'+ (' aria-current="page"' if active == key else '') + f'>{label}</a>' for href,label,key in nav)
        banner = '<div class="preview-banner">Local preview <span>· Presentation selections are provisional</span></div>' if args.preview else ''
        robots = '<meta name="robots" content="noindex, nofollow">' if args.preview else ''
        return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {esc(content['name'])}</title>
<meta name="description" content="{esc(content['name'])} — combinatorial optimization, polyhedral methods, and mathematical expositions.">
<meta name="theme-color" content="#f8f7f3">{robots}
<link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg"><link rel="stylesheet" href="{prefix}assets/style.css"></head>
<body>{banner}<a class="skip-link" href="#main">Skip to content</a>
<header class="header"><a class="wordmark" href="{prefix}index.html">{esc(content['name'])}</a><nav aria-label="Main navigation">{links}</nav></header>
{body}
<footer class="footer"><span>© 2026 {esc(content['name'])}</span><a href="mailto:{esc(content['email'])}">{esc(content['email'])}</a></footer>
</body></html>'''

    def note_rows(items, prefix=''):
        return ''.join(f'''<article class="note-row">
<a class="note-thumb" href="{prefix}notes/{esc(n['slug'])}.html" tabindex="-1" aria-hidden="true"><img src="{prefix}assets/images/{esc(n['image'])}" alt="" width="960" height="540" loading="lazy"></a>
<div class="note-copy"><p class="eyebrow">{esc(n['field'])} <span> / {esc(n['year'])}</span></p>
<h3><a href="{prefix}notes/{esc(n['slug'])}.html">{esc(n['title'])}</a></h3><p>{esc(n['summary'])}</p>
<div class="note-links"><a href="{prefix}notes/{esc(n['slug'])}.html">Overview <span aria-hidden="true">→</span></a><a href="{prefix}assets/documents/{esc(n['pdf'])}" aria-label="Read slides for {esc(n['title'])}">Slides <span class="file-tag">PDF</span></a></div></div></article>''' for n in items)

    interests = ''.join(f'<li><strong>{esc(i["title"])}</strong><span>{esc(i["text"])}</span></li>' for i in content['interests'])
    selected = f'''<section id="expositions" class="section"><div class="section-heading"><div><p class="eyebrow">Reading seminar materials</p><h2>Mathematical expositions</h2></div><a class="text-link" href="archive.html">All notes <span aria-hidden="true">→</span></a></div><p class="section-intro">Selected presentations based on textbooks in combinatorics and matroid theory.</p><div class="notes">{note_rows(notes[:3])}</div></section>''' if notes else ''
    cv_button = f'<a class="cv-button" href="assets/documents/{esc(cv)}">Curriculum vitae <span class="file-tag">PDF</span><span aria-hidden="true">↗</span></a>' if cv else ''
    body = f'''<main id="main" class="home">
<section class="intro" aria-labelledby="name"><aside class="identity"><p class="eyebrow">Personal academic website</p><h1 id="name">Kyeongin<br> Hong<span class="name-dot">.</span></h1><p class="location">{esc(content['location'])}</p>{cv_button}<div class="contact-links"><a href="mailto:{esc(content['email'])}">Email</a><a href="{esc(content['github'])}">GitHub <span aria-hidden="true">↗</span></a></div></aside>
<div class="intro-copy"><p class="lead">{esc(content['intro'])}</p><p>{esc(content['about'])}</p><p>{esc(content['background'])}</p></div></section>
<section class="section interests" aria-labelledby="interests-heading"><div><p class="eyebrow">Research interests</p><h2 id="interests-heading">Structure, formulations,<br> and algorithms.</h2></div><ul class="interest-list">{interests}</ul></section>
{selected}
<section class="section contact-section"><div><p class="eyebrow">Get in touch</p><h2>Contact</h2></div><div><p>For correspondence, please reach me by email.</p><a class="contact-email" href="mailto:{esc(content['email'])}">{esc(content['email'])}<span aria-hidden="true"> ↗</span></a></div></section>
</main>'''
    (output / 'index.html').write_text(page('About', body, active='home'))
    groups = ''
    for field in ['Matroid theory','Combinatorics']:
        entries = [n for n in notes if n['field'] == field]
        if entries:
            groups += f'<section class="archive-group"><h2>{esc(field)}</h2>{note_rows(entries)}</section>'
    if not groups:
        groups = '<p class="empty-note">Seminar materials are being prepared for this archive.</p>'
    archive_body = f'''<main id="main" class="inner"><div class="page-title"><p class="eyebrow">Seminar archive</p><h1>Notes &amp; presentations</h1><p>Expository materials prepared while studying combinatorics and matroid theory in reading seminars with Professor Boram Park.</p><p class="source-note">These presentations explain established results from the sources listed with each item.</p></div>{groups}</main>'''
    if notes:
        (output / 'archive.html').write_text(page('Notes & presentations', archive_body, active='notes'))
    if notes:
        (output / 'notes').mkdir()
    for n in notes:
        topics = ''.join(f'<li>{esc(t)}</li>' for t in n['topics'])
        detail = f'''<main id="main" class="inner detail"><a class="back-link" href="../archive.html">← All presentations</a><div class="page-title"><p class="eyebrow">{esc(n['field'])} / {esc(n['year'])}</p><h1>{esc(n['title'])}</h1><p>{esc(n['summary'])}</p><a class="cv-button" href="../assets/documents/{esc(n['pdf'])}">Read the slides <span class="file-tag">PDF</span><span aria-hidden="true">↗</span></a></div><a class="slide-preview" href="../assets/documents/{esc(n['pdf'])}" aria-label="Open presentation PDF"><img src="../assets/images/{esc(n['image'])}" alt="An example slide from {esc(n['title'])}" width="960" height="540"></a><div class="detail-grid"><section><h2>In these slides</h2><ul>{topics}</ul></section><section><h2>Background</h2><p>{esc(n['prerequisites'])}</p><h2>Source</h2><p>{esc(n['book'])}</p></section></div></main>'''
        (output / 'notes' / f"{n['slug']}.html").write_text(page(n['title'], detail, prefix='../', active='notes'))
    (output / '404.html').write_text(page('Page not found', '<main id="main" class="inner"><div class="page-title"><p class="eyebrow">404</p><h1>Page not found</h1><p>This page may have moved. <a href="/">Return to the homepage.</a></p></div></main>', prefix='/'))
    print(f'Built {output}: {len(notes)} presentations; preview={args.preview}')

if __name__ == '__main__':
    main()
