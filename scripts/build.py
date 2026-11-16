#!/usr/bin/env python3
"""content.json과 HTML 템플릿을 합쳐 dist/를 만드는 빌드 도구.

문구 편집: site/content.json
배치 편집: site/templates/*.html
디자인 편집: site/style.css
이 파일은 이 셋을 연결하며, 별도 Python 패키지는 필요하지 않습니다.
"""
import argparse
import html
import hashlib
import json
import re
import shutil
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'



def stylesheet_name():
    """디자인이 바뀌면 파일명도 바뀌어 브라우저의 이전 CSS 캐시를 피합니다."""
    digest = hashlib.sha256((SITE / 'style.css').read_bytes()).hexdigest()[:12]
    return f'style.{digest}.css'


def script_name():
    """동작이 바뀌면 파일명도 바꿔 이전 애니메이션 캐시를 피합니다."""
    digest = hashlib.sha256((SITE / 'interactions.js').read_bytes()).hexdigest()[:12]
    return f'interactions.{digest}.js'


def escape(value):
    """JSON의 글자를 HTML에서 안전하게 표시합니다. 예: & → &amp;"""
    return html.escape(str(value), quote=True)



def inline_links(text):
    """소개 문장의 [이름](https://주소)만 링크로 변환합니다. 나머지는 일반 텍스트입니다."""
    parts = []
    cursor = 0
    for match in re.finditer(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', text):
        parts.append(escape(text[cursor:match.start()]))
        parts.append(f'<a href="{escape(match.group(2))}">{escape(match.group(1))}</a>')
        cursor = match.end()
    parts.append(escape(text[cursor:]))
    return ''.join(parts)


def render(template_name, **values):
    """템플릿의 ${이름}을 전달한 값으로 채웁니다."""
    source = (SITE / 'templates' / f'{template_name}.html').read_text(encoding='utf-8')
    return Template(source).substitute(values)


def note_values(note):
    return {key: escape(value) for key, value in note.items() if key != 'topics'}


def note_rows(notes, prefix=''):
    return '\n'.join(render('note-row', prefix=prefix, **note_values(note)) for note in notes)


def navigation(content, notes, prefix, active):
    links = [
        ('index.html', 'About', 'home'),
    ]
    if notes:
        links.append(('slides.html', 'Slides', 'notes'))
    return '\n'.join(
        render('navigation-link', href=escape(prefix + href), label=escape(label),
               current=' aria-current="page"' if key == active else '')
        for href, label, key in links
    )


def page(content, notes, title, body, preview=False, prefix='', active=''):
    """모든 페이지의 공통 틀에 본문을 넣습니다. prefix는 하위 페이지의 상대 경로입니다."""
    banner = ('<div class="preview-banner">Local preview '
              '<span>· Presentation selections are provisional</span></div>') if preview else ''
    return render(
        'base', title=escape(title), name=escape(content['name']),
        email=escape(content['email']), prefix=prefix, body=body, stylesheet=stylesheet_name(), script=script_name(),
        navigation=navigation(content, notes, prefix, active),
        preview_banner=banner,
        robots='<meta name="robots" content="noindex, nofollow">' if preview else '',
    )


def home(content, notes):
    """홈페이지의 각 부분을 조립합니다. 문장은 content.json에서 읽습니다."""
    def background_rows(key):
        return '\n'.join(render('profile-entry', title=inline_links(entry['title']),
                                organization=inline_links(entry['organization']),
                                dates=escape(entry['dates'])) for entry in content.get(key, []))
    profile_background = render('profile-background', experience=background_rows('experience'),
                                education=background_rows('education'))
    portrait = content.get('portrait')
    portrait_html = render('portrait', file=escape(portrait['file']), alt=escape(portrait['alt'])) if portrait else ''
    cv_reference = ''
    if content.get('cv'):
        # PDF가 바뀌면 링크도 바뀌어 이전 CV 캐시를 재사용하지 않습니다.
        cv_path = ROOT / 'assets/documents' / content['cv']
        cv_version = hashlib.sha256(cv_path.read_bytes()).hexdigest()[:12]
        cv_reference = render('cv-link', href=escape(f"assets/documents/{content['cv']}?v={cv_version}"))
    values = {key: escape(content[key]) for key in
              ['location', 'email', 'github', 'linkedin', 'about', 'research_interests']}
    values['about'] = inline_links(content['about'])
    return render(
        'home', **values, profile_background=profile_background,
        portrait=portrait_html, portrait_class='has-portrait' if portrait else '',
        cv_reference=cv_reference,
        name_lines='<br>\n'.join(escape(line) for line in content['name_lines']),
    )


def copy_assets(output, content, notes):
    """공개 대상만 복사합니다. cv=null, notes=[]이면 첨부파일을 출력하지 않습니다."""
    assets = output / 'assets'
    assets.mkdir()
    shutil.copyfile(SITE / 'style.css', assets / stylesheet_name())
    shutil.copyfile(SITE / 'interactions.js', assets / script_name())
    shutil.copyfile(SITE / 'favicon.svg', assets / 'favicon.svg')
    if content.get('portrait'):
        (assets / 'profile').mkdir()
        filename = content['portrait']['file']
        shutil.copyfile(ROOT / 'assets/profile' / filename, assets / 'profile' / filename)
    if content.get('cv'):
        (assets / 'documents').mkdir(exist_ok=True)
        shutil.copyfile(ROOT / 'assets/documents' / content['cv'], assets / 'documents' / content['cv'])
    for note in notes:
        folder = ROOT / ('assets/documents' if note['status'] == 'published' else 'preview-materials')
        (assets / 'documents').mkdir(exist_ok=True)
        destination = assets / 'documents' / note['pdf']
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(folder / note['pdf'], destination)
        if note.get('image'):
            (assets / 'images').mkdir(exist_ok=True)
            shutil.copyfile(ROOT / 'assets/images' / note['image'], assets / 'images' / note['image'])


def build(preview=False):
    content = json.loads((SITE / 'content.json').read_text(encoding='utf-8'))
    notes = [note for note in content['notes'] if note['status'] == 'published' or preview]
    notes.sort(key=lambda note: note['date_iso'], reverse=True)
    output = ROOT / ('preview' if preview else 'dist')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    copy_assets(output, content, notes)
    (output / '.nojekyll').touch()
    if preview:
        (output / 'robots.txt').write_text('User-agent: *\nDisallow: /\n', encoding='utf-8')

    def write(filename, title, body, prefix='', active=''):
        destination = output / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page(content, notes, title, body, preview, prefix, active), encoding='utf-8')

    write('index.html', 'About', home(content, notes), active='home')
    if notes:
        body = render('slides', expositions=render('expositions', notes=note_rows(notes)))
        write('slides.html', 'Seminar Slides', body, active='notes')
    write('404.html', 'Page not found', render('not-found'), prefix='/')

    # 별도 아카이브가 필요해졌을 때만 활성화합니다.
    if notes and content.get('archive_enabled', False):
        fields = dict.fromkeys(note['field'] for note in notes)
        groups = '\n'.join(
            render('archive-group', field=escape(field), notes=note_rows([n for n in notes if n['field'] == field]))
            for field in fields
        )
        write('archive.html', 'Notes & presentations', render('archive', groups=groups), active='notes')
        for note in notes:
            topics = '\n'.join(f'<li>{escape(topic)}</li>' for topic in note['topics'])
            body = render('note', **note_values(note), topics=topics)
            write(f"notes/{note['slug']}.html", note['title'], body, prefix='../', active='notes')
    print(f'Built {output}: {len(notes)} presentations; preview={preview}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true', help='미공개 후보도 로컬 미리보기에 포함합니다.')
    build(preview=parser.parse_args().preview)
