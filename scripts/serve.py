#!/usr/bin/env python3
"""로컬 편집용 서버. 파일을 저장한 뒤 브라우저를 새로고침하면 다시 빌드합니다."""
import argparse
import subprocess
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source_stamp():
    """사이트 소스가 마지막 빌드 이후 바뀌었는지 확인합니다."""
    files = [path for path in (ROOT / 'site').rglob('*') if path.is_file()]
    files.append(ROOT / 'scripts/build.py')
    # 첨부파일을 나중에 추가하거나 교체했을 때도 새로 빌드합니다.
    for folder in ['assets/documents', 'assets/images']:
        if (ROOT / folder).exists():
            files.extend(path for path in (ROOT / folder).rglob('*') if path.is_file())
    return tuple(sorted((str(path), path.stat().st_mtime_ns) for path in files))


def build_site():
    subprocess.run([sys.executable, str(ROOT / 'scripts/build.py')], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    build_site()
    last_build = source_stamp()

    class PreviewHandler(SimpleHTTPRequestHandler):
        def __init__(self, *handler_args, **kwargs):
            super().__init__(*handler_args, directory=str(ROOT / 'dist'), **kwargs)

        def do_GET(self):
            nonlocal last_build
            current = source_stamp()
            if current != last_build:
                try:
                    build_site()
                except subprocess.CalledProcessError:
                    self.send_error(500, 'Build failed. Check the terminal for details.')
                    return
                last_build = current
            super().do_GET()

    # localhost에서만 열립니다. 이 명령으로 인터넷에 공개되지는 않습니다.
    with HTTPServer(('127.0.0.1', args.port), PreviewHandler) as server:
        print(f'Preview: http://127.0.0.1:{args.port}', flush=True)
        print('파일 저장 → 브라우저 새로고침. 종료: Ctrl+C', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nPreview stopped.')


if __name__ == '__main__':
    main()
