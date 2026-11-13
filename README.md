# Kyeongin Hong

Personal academic homepage: <https://kyeonginh.github.io/>

A small static site built with Python's standard library. No frontend dependencies or external fonts are required.

## Build locally

Requires Python 3.10 or newer on macOS or Linux.

```sh
python3 scripts/build.py
python3 scripts/check.py dist
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
```

Open <http://127.0.0.1:8765>. Edit the page content in `site/content.json` and the design in `site/style.css`.

## Deployment

GitHub Actions builds, validates, and deploys the site to GitHub Pages on pushes to `main`. The workflow can also be started manually.

CVs, presentation PDFs, slide images, and other attachments are intentionally not included in this initial release. The corresponding navigation and download links remain hidden until these materials are added explicitly.
