"""Manual GitHub/arXiv inspection. Exit 0: no errors (offline: not checked),
1: missing/unverifiable reference, 2: invalid input/cache or local I/O failure.
Only the standard library and optional installed gh are used.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen


GITHUB = re.compile(
    r'https://github\.com/([A-Za-z0-9_-]+)/([A-Za-z0-9_.-]+)', re.I)
ARXIV = re.compile(
    r'https?://arxiv\.org/(?:abs|pdf)/'
    r'(\d{4}\.\d{4,5}(?:v\d+)?|[a-z-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)')


def collect_refs(notes: Path) -> dict[str, list[str]]:
    """Collect canonical URLs with source locations, ignoring fenced code."""
    if not notes.is_dir():
        raise ValueError('notes must be an existing directory')
    found = {}
    for path in sorted(notes.glob('*.md')):
        fence = None
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
            if marker:
                token, tail = marker.groups()
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence) and not tail.strip():
                    fence = None
                continue
            if fence is not None:
                continue
            urls = []
            if '（私有）' not in line:
                for owner, repo in GITHUB.findall(line):
                    repo = repo.rstrip('.')
                    if repo.lower().endswith('.git'):
                        repo = repo[:-4]
                    if repo:
                        urls.append(f'https://github.com/{owner}/{repo}'.lower())
            urls.extend(f'https://arxiv.org/abs/{paper}'
                        for paper in ARXIV.findall(line))
            for url in urls:
                found.setdefault(url, []).append(f'{path.as_posix()}:{number}')
    if not found:
        raise ValueError('no supported references found')
    return dict(sorted(found.items()))


def query_ref(url: str, *, transport: str = 'auto') -> dict:
    """Query once per reference; no retry or provider switching on failure."""
    github = url.startswith('https://github.com/')
    if github and transport != 'urllib' and shutil.which('gh'):
        endpoint = 'repos/' + url.removeprefix('https://github.com/')
        result = subprocess.run(
            ['gh', 'api', endpoint], capture_output=True, text=True,
            encoding='utf-8', errors='replace', timeout=25)
        if result.returncode:
            match = re.search(r'HTTP (\d{3})', result.stderr)
            if not match:
                raise OSError('gh unavailable; use --transport urllib explicitly')
            return {'status': int(match[1])}
        data = json.loads(result.stdout or '')
        if not isinstance(data, dict):
            raise ValueError('invalid GitHub response')
        return {'status': 200, 'full_name': data.get('full_name'),
                'archived': data.get('archived')}
    target = ('https://api.github.com/repos/'
              + url.removeprefix('https://github.com/')) if github else url
    headers = {'User-Agent': 'ai-inbox-external-refs'}
    if github and os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    request = Request(target, headers=headers, method='GET' if github else 'HEAD')
    try:
        with urlopen(request, timeout=20) as response:
            if github:
                data = json.load(response)
                if not isinstance(data, dict):
                    raise ValueError('invalid GitHub response')
                return {'status': response.status,
                        'full_name': data.get('full_name'),
                        'archived': data.get('archived')}
            return {'status': response.status, 'final_url': response.url}
    except HTTPError as error:
        return {'status': error.code}


def validate_result(url: str, result: object) -> None:
    if not isinstance(result, dict) or type(result.get('status')) is not int:
        raise ValueError('invalid response schema')
    if result['status'] in (200, 301, 302, 307, 308) and 'github.com/' in url:
        name = result.get('full_name')
        if (not isinstance(name, str)
                or not re.fullmatch(r'[\w-]+/[\w.-]+', name)
                or type(result.get('archived')) is not bool):
            raise ValueError('invalid GitHub metadata')


def main(argv=None, *, query=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notes', type=Path, default=Path('notes'))
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--transport', choices=('auto', 'urllib'), default='auto',
                        help='Explicit urllib fallback when installed gh is unusable')
    parser.add_argument('--cache', type=Path,
                        help='Explicit snapshot; delete to refresh. No expiry.')
    args = parser.parse_args(argv)
    query = query or (lambda url: query_ref(url, transport=args.transport))
    try:
        refs = collect_refs(args.notes)
        cache = {}
        if args.cache and args.cache.exists():
            data = json.loads(args.cache.read_text(encoding='utf-8'))
            if (not isinstance(data, dict) or data.get('version') != 1
                    or not isinstance(data.get('results'), dict)):
                raise ValueError('invalid cache schema')
            cache = data['results']
            for url, result in cache.items():
                if not (GITHUB.fullmatch(url) or re.fullmatch(
                        r'https://arxiv\.org/abs/.+', url)):
                    raise ValueError('invalid cache URL')
                validate_result(url, result)
        errors = warnings = 0
        for url, sources in refs.items():
            if args.offline:
                print(f'NOT CHECKED {url}')
                continue
            try:
                result = cache[url] if url in cache else query(url)
                validate_result(url, result)
                status = result['status']
                if status not in (200, 301, 302, 307, 308):
                    errors += 1
                    print(f'ERROR HTTP {status} {url} [{", ".join(sources)}]')
                    continue
                messages = []
                if status != 200:
                    messages.append('redirected')
                if url.startswith('https://github.com/'):
                    if result['full_name'].lower() != url.split('github.com/')[1]:
                        messages.append('renamed -> ' + result['full_name'])
                    if result['archived']:
                        messages.append('archived')
                for message in messages:
                    warnings += 1
                    print(f'WARNING {message} {url}')
                print(f'OK HTTP {status} {url}')
                cache[url] = result
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                errors += 1
                # Do not print exception details: transports may include credentials.
                print(f'ERROR unverifiable ({type(error).__name__}) {url}')
        if args.cache and not args.offline:
            args.cache.write_text(json.dumps(
                {'version': 1, 'results': cache}, indent=2) + '\n', encoding='utf-8')
        mode = 'offline, NOT CHECKED' if args.offline else 'online'
        print(f'SUMMARY total={len(refs)} errors={errors} warnings={warnings} {mode}')
        return 1 if errors else 0
    except (OSError, ValueError) as error:
        print(f'INPUT ERROR ({type(error).__name__}): invalid notes or cache')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
