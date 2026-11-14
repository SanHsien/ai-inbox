"""External reference checks use injected responses, never the network."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

from tools import check_external_refs as refs


class ExternalRefsTest(unittest.TestCase):
    def setUp(self):
        (Path.cwd() / '.work-tmp').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=Path.cwd() / '.work-tmp')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.notes = self.root / 'notes'
        self.notes.mkdir()
        (self.notes / 'a.md').write_text(
            'https://github.com/owner/repo/tree/main\n', encoding='utf-8')

    def run_check(self, response, *extra):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = refs.main(['--notes', str(self.notes), *extra],
                             query=lambda url: response)
        return code, output.getvalue()

    def test_github_404_exit_one(self):
        self.assertEqual(self.run_check({'status': 404})[0], 1)

    def test_rename_warns_exit_zero(self):
        code, out = self.run_check(
            {'status': 200, 'full_name': 'new/name', 'archived': False})
        self.assertEqual(code, 0)
        self.assertIn('WARNING renamed', out)

    def test_archived_and_redirect_warn(self):
        code, out = self.run_check(
            {'status': 301, 'full_name': 'owner/repo', 'archived': True})
        self.assertEqual(code, 0)
        self.assertIn('WARNING redirected', out)
        self.assertIn('WARNING archived', out)

    def test_private_fences_dedup_and_arxiv_pdf(self):
        (self.notes / 'a.md').write_text(
            'https://github.com/private/repo （私有）\n'
            '```python\nhttps://github.com/fake/repo\n```\n'
            '~~~~\nhttps://arxiv.org/abs/9999.12345\n~~~~\n'
            'https://github.com/owner/repo/issues/1\n'
            'https://github.com/OWNER/REPO.git\n'
            '[paper](https://arxiv.org/pdf/2301.12345v2.pdf)\n',
            encoding='utf-8')
        self.assertEqual(list(refs.collect_refs(self.notes)), [
            'https://arxiv.org/abs/2301.12345v2',
            'https://github.com/owner/repo'])

    def test_arxiv_404_exit_one(self):
        (self.notes / 'a.md').write_text(
            'https://arxiv.org/abs/2301.12345', encoding='utf-8')
        self.assertEqual(self.run_check({'status': 404})[0], 1)

    def test_bad_schema_and_unknown_status_fail_closed(self):
        for response in [None, [], {}, {'status': True}, {'status': 200},
                         {'status': 403}, {'status': 429},
                         {'status': 200, 'full_name': 'x/y', 'archived': 'no'}]:
            with self.subTest(response=response):
                self.assertEqual(self.run_check(response)[0], 1)

    def test_empty_missing_and_non_directory_exit_two(self):
        (self.notes / 'a.md').unlink()
        for path in [self.notes, self.root / 'missing', Path(__file__)]:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(refs.main(['--notes', str(path)]), 2)

    def test_offline_never_queries(self):
        with patch.object(refs, 'query_ref', side_effect=AssertionError):
            code, out = self.run_check(None, '--offline')
        self.assertEqual(code, 0)
        self.assertIn('NOT CHECKED', out)

    def test_cache_roundtrip_and_invalid_cache(self):
        cache = self.root / 'cache.json'
        good = {'status': 200, 'full_name': 'owner/repo', 'archived': False}
        self.assertEqual(self.run_check(good, '--cache', str(cache))[0], 0)
        self.assertEqual(self.run_check(None, '--cache', str(cache))[0], 0)
        for invalid in [[], {'version': 1, 'results': {'bad': good}},
                        {'version': 1, 'results': {
                            'https://github.com/owner/repo': {'status': 200}}}]:
            cache.write_text(json.dumps(invalid), encoding='utf-8')
            self.assertEqual(self.run_check(good, '--cache', str(cache))[0], 2)

    def test_query_exception_is_failure(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(refs.main(['--notes', str(self.notes)],
                             query=lambda _: (_ for _ in ()).throw(
                                 TimeoutError('timeout'))), 1)

    def test_gh_response_and_404(self):
        with patch.object(refs.shutil, 'which', return_value='gh'), patch.object(
                refs.subprocess, 'run') as run:
            run.return_value.returncode = 0
            run.return_value.stdout = json.dumps({
                'full_name': 'new/name', 'archived': True})
            result = refs.query_ref('https://github.com/old/name')
            self.assertEqual(result['full_name'], 'new/name')
            run.return_value.returncode = 1
            run.return_value.stderr = 'gh: Not Found (HTTP 404)'
            self.assertEqual(refs.query_ref(
                'https://github.com/old/name')['status'], 404)
            run.return_value.stderr = 'config access denied'
            with self.assertRaises(OSError):
                refs.query_ref('https://github.com/old/name')

    def test_gh_output_decoded_as_utf8_not_locale(self):
        # gh 輸出含非 ASCII（repo 描述常見）；以系統編碼（cp950）解碼曾讓 stdout 變 None 而崩潰
        with patch.object(refs.shutil, 'which', return_value='gh'), patch.object(
                refs.subprocess, 'run') as run:
            run.return_value.returncode = 0
            run.return_value.stdout = json.dumps({'full_name': 'a/b', 'archived': False})
            refs.query_ref('https://github.com/a/b')
            kwargs = run.call_args.kwargs
            self.assertEqual(kwargs.get('encoding'), 'utf-8')
            run.return_value.stdout = None
            with self.assertRaises(ValueError):
                refs.query_ref('https://github.com/a/b')

    def test_urllib_fallback_token_and_head(self):
        with patch.object(refs.shutil, 'which', return_value=None), patch.object(
                refs, 'urlopen') as open_url, patch.dict(
                    refs.os.environ, {'GITHUB_TOKEN': 'test-value'}):
            response = open_url.return_value.__enter__.return_value
            response.status = 200
            response.read.return_value = b'{"full_name":"x/y","archived":false}'
            self.assertEqual(refs.query_ref(
                'https://github.com/x/y')['status'], 200)
            request = open_url.call_args.args[0]
            self.assertEqual(request.get_header('Authorization'), 'Bearer test-value')
            response.url = 'https://arxiv.org/abs/2301.12345'
            refs.query_ref(response.url)
            request = open_url.call_args.args[0]
            self.assertEqual(request.method, 'HEAD')
            self.assertIsNone(request.get_header('Authorization'))
            open_url.side_effect = HTTPError(response.url, 404, 'missing', {}, None)
            self.assertEqual(refs.query_ref(response.url)['status'], 404)


if __name__ == '__main__':
    unittest.main()
