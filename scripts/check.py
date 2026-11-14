#!/usr/bin/env python3
"""Check generated HTML links, fragment targets, and document presence."""
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = []
        self.lang = False
        self.viewport = False
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'html':
            self.lang = bool(a.get('lang'))
        if tag == 'meta' and a.get('name') == 'viewport':
            self.viewport = True
        for key in ['href', 'src']:
            if key in a:
                self.links.append(a[key])
        if tag == 'img' and 'alt' not in a:
            raise ValueError('Image without alt attribute')

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'dist').resolve()
errors = []
files = list(root.rglob('*.html'))
if not files:
    errors.append('No generated HTML')
for file in files:
    parsed = Page(file.read_text())
    if not parsed.lang or not parsed.viewport:
        errors.append(f'{file}: missing language or viewport')
    if len(parsed.ids) != len(set(parsed.ids)):
        errors.append(f'{file}: duplicate IDs')
    for link in parsed.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        if url.path.startswith('/'):
            target = (root / unquote(url.path).lstrip('/')).resolve()
            if target.is_dir():
                target = target / 'index.html'
        else:
            target = (file.parent / unquote(url.path)).resolve() if url.path else file
        if not target.is_relative_to(root):
            errors.append(f'{file.name}: escapes site root: {link}')
        elif not target.is_file():
            errors.append(f'{file.name}: missing: {link}')
        elif url.fragment and target.suffix == '.html' and unquote(url.fragment) not in Page(target.read_text()).ids:
            errors.append(f'{file.name}: missing fragment: {link}')
for p in root.rglob('*.pdf'):
    if not p.read_bytes().startswith(b'%PDF-'):
        errors.append(f'Invalid PDF: {p}')
# Only explicitly configured documents can enter the built site.
import json
content = json.loads((Path(__file__).resolve().parents[1] / 'site/content.json').read_text())
approved = {n['pdf'] for n in content['notes'] if n['status'] == 'published'}
if content.get('cv'):
    approved.add(content['cv'])
for p in root.rglob('*.pdf'):
    if p.relative_to(root / 'assets/documents').as_posix() not in approved:
        errors.append(f'Unapproved document: {p.name}')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(files)} HTML pages; local links, fragments, metadata, and PDFs checked.')
