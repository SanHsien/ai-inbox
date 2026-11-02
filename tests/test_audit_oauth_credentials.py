"""tools/audit_oauth_credentials.py 的單元測試。

只用暫存資料夾裡的假憑證（哨兵字串），不讀真實家目錄，也不碰真實憑證。
重點是兩件事：每條規則都有「會報」與「不該報」的案例；任何輸出（文字、JSON、錯誤）都不含憑證值。
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOL = Path(__file__).resolve().parent.parent / "tools" / "audit_oauth_credentials.py"
sys.path.insert(0, str(TOOL.parent))
import audit_oauth_credentials as a  # noqa: E402

HAS_GIT = shutil.which("git") is not None
IS_WIN = sys.platform == "win32"

# 哨兵：假的憑證值。輸出裡出現其中任何一個（或前 10 字元）就代表洩漏。
S_ACCESS = "SENTINEL-ACCESS-7f3a91c2d4e65b08"
S_REFRESH = "SENTINEL-REFRESH-b81d03aa5c9e7f42"
S_ID = "SENTINEL-IDTOKEN-0e5c77d1a3b94f68"
S_SECRET = "SENTINEL-CLIENTSECRET-4a6b8c0d2e1f"
S_KEYNAME = "SENTINEL-KEYNAME-c3d4e5f6a7b8c9d0"
S_HOSTVAL = "SENTINEL-HOSTVAL-1122334455667788"
S_SCOPE = "SENTINEL-SCOPE-99aabbccddeeff00"
SENTINELS = [S_ACCESS, S_REFRESH, S_ID, S_SECRET, S_KEYNAME, S_HOSTVAL, S_SCOPE]

CODEX_AUTH = json.dumps({"auth_mode": "chatgpt", "tokens": {"id_token": S_ID, "access_token": S_ACCESS, "refresh_token": S_REFRESH}})


class FakeHome:
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()

    def write(self, rel, text, mode=None):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
        if mode is not None and not IS_WIN:
            os.chmod(p, mode)
        return p

    def write_bytes(self, rel, data):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p

    def close(self):
        self._tmp.cleanup()


def codes(findings, level=None):
    return sorted(f.code for f in findings if level is None or f.level == level)


def run_audit(home, repos=None, **kw):
    kw.setdefault("git_check", lambda p: "no-repo")
    return a.audit(home.root, a.candidate_dirs(home.root, None), repos, **kw)


class TokenKindsTest(unittest.TestCase):
    def test_nested_json_snake_case(self):
        self.assertEqual(a.token_kinds(CODEX_AUTH), ["access_token", "id_token", "refresh_token"])

    def test_camel_case_and_toml_and_env_styles(self):
        text = f'{{"claudeAiOauth": {{"accessToken": "{S_ACCESS}", "refreshToken": "{S_REFRESH}"}}}}'
        self.assertEqual(a.token_kinds(text), ["access_token", "refresh_token"])
        self.assertEqual(a.token_kinds(f'api_key = "{S_ACCESS}"'), ["api_key"])
        self.assertEqual(a.token_kinds(f"XAI_API_KEY={S_ACCESS}"), ["api_key"])
        self.assertEqual(a.token_kinds(f'client_secret: "{S_SECRET}"'), ["client_secret"])

    def test_bare_token_key(self):
        self.assertEqual(a.token_kinds(f'{{"token": "{S_ACCESS}"}}'), ["token"])

    def test_empty_null_short_and_placeholder_values_do_not_count(self):
        for text in (
            '{"refresh_token": ""}',
            '{"refresh_token": null}',
            '{"refresh_token": "short"}',
            'api_key = "${OPENAI_API_KEY}"',
            'api_key = "$OPENAI_API_KEY"',
            'api_key = "env:OPENAI_API_KEY"',
            'api_key = "<your-api-key-here>"',
            "OPENAI_API_KEY=",
        ):
            with self.subTest(text=text):
                self.assertEqual(a.token_kinds(text), [])

    def test_unrelated_keys_do_not_count(self):
        self.assertEqual(a.token_kinds('{"max_tokens": "1234567890123456", "model": "grok-something-long-name"}'), [])

    def test_commented_out_token_still_counts_because_it_is_still_on_disk(self):
        self.assertEqual(a.token_kinds(f'# api_key = "{S_ACCESS}"'), ["api_key"])

    def test_very_long_value_is_still_detected(self):
        self.assertEqual(a.token_kinds('{"access_token": "' + "A" * 5000 + '"}'), ["access_token"])

    def test_return_values_never_contain_the_secret(self):
        kinds = a.token_kinds(CODEX_AUTH + f'\n{{"{S_KEYNAME}_api_key": "{S_SECRET}"}}')
        for s in SENTINELS:
            self.assertNotIn(s, " ".join(kinds))
        self.assertEqual(kinds, ["access_token", "api_key", "id_token", "refresh_token"])


class DecodeTextTest(unittest.TestCase):
    TEXT = json.dumps({"tokens": {"refresh_token": S_REFRESH}}, ensure_ascii=False) + "\n# 備註：帳號"

    def test_encodings_all_round_trip(self):
        for name, raw in (
            ("utf-8", self.TEXT.encode("utf-8")),
            ("utf-8-bom", b"\xef\xbb\xbf" + self.TEXT.encode("utf-8")),
            ("utf-16-bom-le", b"\xff\xfe" + self.TEXT.encode("utf-16-le")),
            ("utf-16-bom-be", b"\xfe\xff" + self.TEXT.encode("utf-16-be")),
            ("utf-32-bom", self.TEXT.encode("utf-32")),
        ):
            with self.subTest(enc=name):
                self.assertEqual(a.decode_text(raw), self.TEXT)
                self.assertEqual(a.token_kinds(a.decode_text(raw)), ["refresh_token"])

    def test_utf16_without_bom_is_still_scanned_when_ascii_dominates(self):
        for name, raw in (("le", self.TEXT.encode("utf-16-le")), ("be", self.TEXT.encode("utf-16-be"))):
            with self.subTest(enc=name):
                self.assertEqual(a.token_kinds(a.decode_text(raw)), ["refresh_token"])

    PAYLOAD = b'{"refresh_token":"FAKEVALSENT1NEL1122334455", "bind": "0.0.0.0"}'

    def test_utf8_content_with_many_nul_bytes_is_not_mistaken_for_utf16(self):
        # 預先配置或寫入中斷的檔案：內容後面（或前面）是一大段 NUL，之前整份被當成 UTF-16 而漏報
        for name, raw in (
            ("trailing-nuls", self.PAYLOAD + b"\0" * 5000),
            ("leading-nuls", b"\0" * 5000 + self.PAYLOAD),
            ("leading-junk-pairs", b"\x00\xff" * 2000 + self.PAYLOAD),
            ("trailing-junk-pairs", self.PAYLOAD + b"\xff\x00" * 2000),
            ("middle-nuls", self.PAYLOAD[:20] + b"\0" * 300 + self.PAYLOAD[20:]),
            ("nuls-both-sides", b"\0" * 3000 + self.PAYLOAD + b"\0" * 3000),
        ):
            with self.subTest(case=name):
                text = a.decode_text(raw)
                self.assertEqual(a.token_kinds(text), ["refresh_token"])
                self.assertEqual([i[:2] for i in a.listen_issues(text)], [("ERROR", "listen-exposed")])

    def test_nul_padded_file_is_reported_by_the_audit(self):
        h = FakeHome()
        self.addCleanup(h.close)
        h.write_bytes(".codex/auth.json", self.PAYLOAD + b"\0" * 5000)
        findings, _ = run_audit(h)
        self.assertIn("plaintext-token", codes(findings))

    def test_invalid_bytes_do_not_raise(self):
        self.assertIsInstance(a.decode_text(b'{"access_token": "' + b"\xff\xfe\x80" * 10), str)
        self.assertEqual(a.decode_text(b""), "")
        self.assertEqual(a.decode_text(b"ab"), "ab")

    def test_plain_ascii_with_few_nulls_stays_utf8(self):
        self.assertEqual(a.decode_text(b"hello\x00world, plain text file"), "hello\x00world, plain text file")


class ListenTest(unittest.TestCase):
    def levels(self, text):
        return [(lv, code) for lv, code, _ in a.listen_issues(text)]

    def test_wildcard_and_lan_addresses_are_errors(self):
        for text in (
            'bind = "0.0.0.0:10541"',
            '{"host": "0.0.0.0", "port": 10541}',
            "host = '::'",
            'listen = ":8080"',
            '{"bind_address": "192.168.1.20"}',
            'listen_addr: "http://10.0.0.5:8080/v1"',
            'bind = "[::]:8080"',
        ):
            with self.subTest(text=text):
                self.assertEqual(self.levels(text), [("ERROR", "listen-exposed")])

    def test_loopback_is_fine(self):
        for text in (
            'bind = "127.0.0.1:10541"',
            '{"host": "127.0.0.1"}',
            'listen = "[::1]:8080"',
            'bind = "localhost:8080"',
            '{"host": "localhost"}',
        ):
            with self.subTest(text=text):
                self.assertEqual(self.levels(text), [])

    def test_plain_host_key_pointing_at_remote_server_is_ignored(self):
        self.assertEqual(self.levels('{"host": "api.example.com"}'), [])
        self.assertEqual(self.levels('{"host": "10.0.0.5"}'), [])  # host 只在萬用位址時才算

    def test_bind_hostname_that_is_not_localhost_is_a_warning(self):
        self.assertEqual(self.levels('bind = "myproxy.lan:80"'), [("WARN", "listen-unknown-host")])

    def test_ipv6_zone_id_is_never_echoed(self):
        for text in (f'listen = "fe80::1%{S_SCOPE}"', f'bind = "[fe80::1%{S_SCOPE}]:8080"', f'{{"bind": "http://[fe80::1%{S_SCOPE}]:80/v1"}}'):
            with self.subTest(text=text[:20]):
                issues = a.listen_issues(text)
                self.assertEqual([i[:2] for i in issues], [("ERROR", "listen-exposed")])
                self.assertIn("fe80::1", issues[0][2])
                self.assertNotIn("SENTINEL", issues[0][2])
                self.assertNotIn("%", issues[0][2])

    def test_zone_id_on_loopback_and_empty_address(self):
        self.assertEqual(self.levels('bind = "::1%lo"'), [])
        self.assertEqual(self.levels('bind = "%lo"'), [])

    def test_port_only_is_not_described_as_a_hostname(self):
        for text in ('{"listen": 8080}', "bind = 8080", 'listen = "8080"'):
            with self.subTest(text=text):
                issues = a.listen_issues(text)
                self.assertEqual([i[:2] for i in issues], [("WARN", "listen-port-only")])
                self.assertNotIn("名稱", issues[0][2])
        self.assertEqual(self.levels("host = 8080"), [], "host 欄位的純數字不當成監聽設定")

    def test_commented_out_listen_lines_are_not_current_settings(self):
        for text in ('# bind = "0.0.0.0"', '  // "bind": "0.0.0.0"', '; listen = ":8080"', '#bind=0.0.0.0'):
            with self.subTest(text=text):
                self.assertEqual(self.levels(text), [])
        self.assertEqual(self.levels('# bind = "0.0.0.0"\nbind = "127.0.0.1"'), [])
        self.assertEqual(self.levels('# bind = "127.0.0.1"\nbind = "0.0.0.0"'), [("ERROR", "listen-exposed")])
        self.assertEqual(self.levels('bind = "0.0.0.0"  # all interfaces'), [("ERROR", "listen-exposed")])

    def test_message_never_echoes_non_ip_values(self):
        issues = a.listen_issues(f'bind = "{S_HOSTVAL}"')
        self.assertEqual([i[:2] for i in issues], [("WARN", "listen-unknown-host")])
        self.assertNotIn(S_HOSTVAL, issues[0][2])


class IcaclsParseTest(unittest.TestCase):
    PATH = r"C:\Users\someone\.codex\auth.json"
    OWNER_ONLY = (
        PATH + r" NT AUTHORITY\SYSTEM:(I)(F)" + "\n"
        r"                                       BUILTIN\Administrators:(I)(F)" + "\n"
        r"                                       DESKTOP\someone:(I)(F)" + "\n\n"
    )

    def broad(self, extra=""):
        return a.broad_principals_in_icacls(self.OWNER_ONLY + extra, self.PATH)

    def test_owner_only_is_clean(self):
        self.assertEqual(self.broad(), [])

    def test_everyone_users_and_authenticated_users_are_flagged(self):
        self.assertEqual(self.broad(r"   Everyone:(R)" + "\n"), ["Everyone"])
        self.assertEqual(self.broad(r"   BUILTIN\Users:(I)(RX)" + "\n"), ["BUILTIN\\Users"])
        self.assertEqual(self.broad(r"   NT AUTHORITY\Authenticated Users:(I)(M)" + "\n"), ["NT AUTHORITY\\Authenticated Users"])

    def test_well_known_sids_are_flagged(self):
        self.assertEqual(self.broad("   S-1-1-0:(R)\n"), ["S-1-1-0"])
        self.assertEqual(self.broad("   S-1-5-32-545:(RX)\n"), ["S-1-5-32-545"])

    def test_guests_domain_users_and_anonymous_are_flagged(self):
        for line, expected in (
            (r"   BUILTIN\Guests:(R)", r"BUILTIN\Guests"),
            (r"   CORP\Domain Users:(I)(M)", r"CORP\Domain Users"),
            (r"   CORP\Domain Guests:(R)", r"CORP\Domain Guests"),
            (r"   NT AUTHORITY\ANONYMOUS LOGON:(R)", r"NT AUTHORITY\ANONYMOUS LOGON"),
            ("   S-1-5-32-546:(R)", "S-1-5-32-546"),
            ("   S-1-5-21-111-222-333-513:(R)", "S-1-5-21-111-222-333-513"),
            ("   S-1-5-7:(R)", "S-1-5-7"),
            (r"   everyone:(r)", "everyone"),
        ):
            with self.subTest(line=line):
                self.assertEqual(self.broad(line + "\n"), [expected])

    def test_domain_admins_and_ordinary_groups_are_not_flagged(self):
        for line in (r"   CORP\Domain Admins:(F)", r"   BUILTIN\Power Users:(M)", r"   MYPC\SomeoneEveryone:(F)", "   S-1-5-21-111-222-333-512:(F)"):
            with self.subTest(line=line):
                self.assertEqual(self.broad(line + "\n"), [])

    def test_deny_on_guests_and_domain_users_is_not_exposure(self):
        self.assertEqual(self.broad(r"   BUILTIN\Guests:(DENY)(R)" + "\n"), [])
        self.assertEqual(self.broad(r"   CORP\Domain Users:(DENY)(RX)" + "\n"), [])

    def test_garbled_or_unstrippable_path_prefix_does_not_hide_the_first_entry(self):
        # 路徑含中文、icacls 輸出編碼沒解對時，第一行是「亂碼路徑 主體:(權限)」；之前會因此漏報
        garbled = "C:\\Users\\\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\\.codex\\auth.json"
        for first in ("Everyone:(R)", r"BUILTIN\Users:(I)(RX)", r"NT AUTHORITY\Authenticated Users:(M)"):
            with self.subTest(first=first):
                text = f"{garbled} {first}\n   BUILTIN\\Administrators:(I)(F)\n"
                self.assertEqual(len(a.broad_principals_in_icacls(text, r"C:\somewhere\else.json")), 1)
                self.assertEqual(len(a.broad_principals_in_icacls(text, "")), 1)
                self.assertEqual(len(a.broad_principals_in_icacls(text)), 1)

    def test_chinese_path_with_spaces_in_the_prefix(self):
        path = r"C:\Users\帳號王小明 測試\.codex\auth.json"
        self.assertEqual(a.broad_principals_in_icacls(f"{path} Everyone:(R)\n", path), ["Everyone"])
        self.assertEqual(a.broad_principals_in_icacls(f"{path} NT AUTHORITY\\SYSTEM:(F)\n", path), [])

    def test_read_icacls_decodes_with_the_oem_code_page(self):
        path = r"C:\Users\帳號王小明\.codex\auth.json"
        raw = (path + " Everyone:(R)\r\n").encode("cp950")
        fake = subprocess.CompletedProcess([], 0, stdout=raw, stderr=b"")
        with mock.patch.object(a.subprocess, "run", return_value=fake), mock.patch.object(a, "oem_encoding", return_value="cp950"):
            text = a._read_icacls(Path(path))
        self.assertIn("帳號王小明", text)
        self.assertEqual(a.broad_principals_in_icacls(text, path), ["Everyone"])

    def test_oem_encoding_returns_a_codec_python_knows(self):
        import codecs

        codecs.lookup(a.oem_encoding())

    def test_deny_entry_is_not_exposure(self):
        self.assertEqual(self.broad(r"   Everyone:(DENY)(R)" + "\n"), [])

    def test_unrelated_user_sid_is_not_flagged(self):
        self.assertEqual(self.broad("   S-1-5-21-111-222-333-1001:(I)(F)\n"), [])

    def test_path_on_first_line_does_not_confuse_the_parser(self):
        text = self.PATH + r" Everyone:(R)" + "\n"
        self.assertEqual(a.broad_principals_in_icacls(text, self.PATH), ["Everyone"])


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.h = FakeHome()
        self.addCleanup(self.h.close)

    # ---- 基本

    def test_no_directories_means_no_findings(self):
        findings, stats = run_audit(self.h)
        self.assertEqual(findings, [])
        self.assertEqual(stats, {"dirs_found": 0, "files_scanned": 0, "files_with_token_fields": 0})

    def test_keyring_style_file_without_tokens_is_clean(self):
        self.h.write(".codex/config.toml", 'cli_auth_credentials_store = "keyring"\n', 0o600)
        findings, stats = run_audit(self.h)
        self.assertEqual(findings, [])
        self.assertEqual(stats["files_scanned"], 1)

    def test_plaintext_token_is_a_warning_and_lists_only_categories(self):
        self.h.write(".codex/auth.json", CODEX_AUTH, 0o600)
        findings, stats = run_audit(self.h)
        self.assertEqual(codes(findings), ["plaintext-token"])
        self.assertEqual(findings[0].level, "WARN")
        self.assertIn("access_token", findings[0].msg)
        self.assertEqual(findings[0].file, "~/.codex/auth.json")
        self.assertEqual(stats["files_with_token_fields"], 1)

    def test_directories_not_scanned_recursively(self):
        self.h.write(".claude/projects/x/auth.json", CODEX_AUTH, 0o600)
        self.h.write(".claude/sessions/state.json", '{"host": "0.0.0.0"}')
        findings, stats = run_audit(self.h)
        self.assertEqual(findings, [])
        self.assertEqual(stats["files_scanned"], 0)

    def test_oauth_proxy_subdirectory_is_scanned(self):
        self.h.write(".grok/oauth-proxy/state.json", '{"host": "0.0.0.0", "port": 10541}')
        findings, _ = run_audit(self.h)
        self.assertEqual(codes(findings, "ERROR"), ["listen-exposed"])
        self.assertEqual(findings[0].file, "~/.grok/oauth-proxy/state.json")

    def test_oversized_file_is_skipped_not_read(self):
        self.h.write(".codex/auth.json", '{"access_token": "' + "A" * (a.MAX_BYTES + 10) + '"}', 0o600)
        findings, _ = run_audit(self.h)
        self.assertEqual(codes(findings), ["skipped-large"])

    def test_backup_copy_with_tokens_is_flagged(self):
        self.h.write(".codex/auth.json.bak", CODEX_AUTH, 0o600)
        findings, _ = run_audit(self.h)
        self.assertEqual(codes(findings), ["backup-copy", "plaintext-token"])

    # ---- POSIX 權限

    @unittest.skipIf(IS_WIN, "POSIX 權限位元在 Windows 沒有意義；Windows 走 ACL 檢查")
    def test_loose_permissions_are_errors_when_tokens_present(self):
        for mode in (0o644, 0o640, 0o604, 0o666, 0o660, 0o601, 0o610, 0o701, 0o710):
            with self.subTest(mode=oct(mode)):
                self.h.write(".codex/auth.json", CODEX_AUTH, mode)
                findings, _ = run_audit(self.h)
                self.assertEqual(codes(findings, "ERROR"), ["perm-loose"])

    @unittest.skipIf(IS_WIN, "POSIX 權限位元在 Windows 沒有意義")
    def test_strict_permissions_pass(self):
        for mode in (0o600, 0o400):
            with self.subTest(mode=oct(mode)):
                self.h.write(".codex/auth.json", CODEX_AUTH, 0o600)
                os.chmod(self.h.root / ".codex/auth.json", mode)
                findings, _ = run_audit(self.h)
                self.assertEqual(codes(findings, "ERROR"), [])

    @unittest.skipIf(IS_WIN, "POSIX 權限位元在 Windows 沒有意義")
    def test_loose_permissions_on_credential_named_file_without_tokens_is_only_a_warning(self):
        self.h.write(".grok/auth.json", '{"note": "empty"}', 0o644)
        findings, _ = run_audit(self.h)
        self.assertEqual([(f.level, f.code) for f in findings], [("WARN", "perm-loose")])

    def audit_with_fake_mode(self, mode, content=CODEX_AUTH, name=".codex/auth.json"):
        """不靠真的 chmod：假造 stat 回傳的權限位元，讓 Windows 開發機也能驗 POSIX 分支。"""
        p = self.h.write(name, content)
        real = p.stat()
        fake = os.stat_result((0o100000 | mode, real.st_ino, real.st_dev, 1, 0, 0, real.st_size, 0, 0, 0))
        with mock.patch.object(Path, "stat", return_value=fake):
            findings, _ = a.audit_file(p, self.h.root, is_windows=False, icacls=lambda x: None, git_check=lambda x: "no-repo")
        return findings

    def test_posix_mode_logic_with_faked_stat(self):
        for mode in (0o644, 0o640, 0o604, 0o666, 0o660, 0o777, 0o601, 0o610, 0o701, 0o710):
            with self.subTest(loose=oct(mode)):
                self.assertEqual(codes(self.audit_with_fake_mode(mode), "ERROR"), ["perm-loose"])
        for mode in (0o600, 0o400, 0o700):
            with self.subTest(strict=oct(mode)):
                self.assertEqual(codes(self.audit_with_fake_mode(mode), "ERROR"), [])

    def test_posix_mode_logic_warning_when_no_tokens(self):
        findings = self.audit_with_fake_mode(0o644, content='{"note": "empty"}', name=".grok/auth.json")
        self.assertEqual([(f.level, f.code) for f in findings], [("WARN", "perm-loose")])
        self.assertEqual(self.audit_with_fake_mode(0o600, content='{"note": "empty"}', name=".grok/auth.json"), [])

    # ---- Windows ACL（用注入的 icacls 輸出，兩個平台都跑得到分支邏輯）

    def test_acl_broad_is_error_with_tokens_and_warning_without(self):
        self.h.write(".codex/auth.json", CODEX_AUTH)
        self.h.write(".grok/auth.json", '{"note": "empty"}')
        findings, _ = run_audit(self.h, is_windows=True, icacls=lambda p: f"{p} Everyone:(R)\n   BUILTIN\\Administrators:(F)\n")
        got = sorted((f.file, f.level, f.code) for f in findings if f.code == "acl-broad")
        self.assertEqual(got, [("~/.codex/auth.json", "ERROR", "acl-broad"), ("~/.grok/auth.json", "WARN", "acl-broad")])

    def test_acl_owner_only_passes_and_never_checks_posix_mode_on_windows(self):
        self.h.write(".codex/auth.json", CODEX_AUTH, 0o666)
        findings, _ = run_audit(self.h, is_windows=True, icacls=lambda p: f"{p} NT AUTHORITY\\SYSTEM:(F)\n   BUILTIN\\Administrators:(F)\n")
        self.assertEqual(codes(findings), ["plaintext-token"])

    def test_acl_unreadable_is_info_not_a_pass_or_a_failure(self):
        self.h.write(".codex/auth.json", CODEX_AUTH)
        findings, _ = run_audit(self.h, is_windows=True, icacls=lambda p: None)
        self.assertEqual(codes(findings, "INFO"), ["acl-unreadable"])
        self.assertEqual(codes(findings, "ERROR"), [])

    @unittest.skipUnless(IS_WIN, "需要真的 icacls")
    def test_live_icacls_detects_everyone_grant_on_a_temp_file(self):
        p = self.h.write(".codex/auth.json", CODEX_AUTH)
        findings, _ = run_audit(self.h, is_windows=True)
        self.assertEqual(codes(findings, "ERROR"), [], "暫存檔預設應只有擁有者與系統帳號")
        subprocess.run(["icacls", str(p), "/grant", "Everyone:R"], capture_output=True, check=True)
        findings, _ = run_audit(self.h, is_windows=True)
        self.assertEqual(codes(findings, "ERROR"), ["acl-broad"])

    @unittest.skipUnless(IS_WIN, "需要真的 icacls")
    def test_live_icacls_with_chinese_path_and_spaces(self):
        p = self.h.write("帳號王小明 測試/.codex/auth.json", CODEX_AUTH)
        d = [self.h.root / "帳號王小明 測試" / ".codex"]
        findings, _ = a.audit(self.h.root, d, is_windows=True, git_check=lambda x: "no-repo")
        self.assertEqual(codes(findings, "ERROR"), [], "未授權前不該有 ERROR")
        subprocess.run(["icacls", str(p), "/grant", "Everyone:R"], capture_output=True, check=True)
        findings, _ = a.audit(self.h.root, d, is_windows=True, git_check=lambda x: "no-repo")
        self.assertEqual(codes(findings, "ERROR"), ["acl-broad"], "中文路徑下 Everyone 授權必須被抓到")

    @unittest.skipUnless(IS_WIN, "需要真的 icacls")
    def test_live_chinese_path_cli_exit_code(self):
        p = self.h.write("帳號王小明/.codex/auth.json", CODEX_AUTH)
        subprocess.run(["icacls", str(p), "/grant", "Everyone:R"], capture_output=True, check=True)
        proc = subprocess.run([sys.executable, str(TOOL), "--home", str(self.h.root / "帳號王小明")], capture_output=True)
        self.assertEqual(proc.returncode, 1, proc.stdout.decode("utf-8", "replace"))
        self.assertIn("acl-broad", proc.stdout.decode("utf-8"))

    # ---- UTF-16 檔案（PowerShell 5 的 > 預設）

    def test_utf16_files_are_scanned(self):
        self.h.write_bytes(".codex/auth.json", CODEX_AUTH.encode("utf-16"))  # 含 BOM
        self.h.write_bytes(".grok/oauth-proxy/state.json", b"\xff\xfe" + '{"host": "0.0.0.0"}'.encode("utf-16-le"))
        settings = '{"env": {"ANTHROPIC_AUTH_TOKEN": "%s"}}' % S_ACCESS
        self.h.write_bytes(".claude/settings.json", settings.encode("utf-16-be"))
        findings, stats = run_audit(self.h)
        self.assertEqual(stats["files_with_token_fields"], 2)
        got = sorted((f.file, f.code) for f in findings if f.code != "perm-loose")
        self.assertEqual(
            got,
            [
                ("~/.claude/settings.json", "plaintext-token"),
                ("~/.codex/auth.json", "plaintext-token"),
                ("~/.grok/oauth-proxy/state.json", "listen-exposed"),
            ],
        )

    def test_utf8_bom_file_is_scanned(self):
        self.h.write_bytes(".codex/auth.json", b"\xef\xbb\xbf" + CODEX_AUTH.encode("utf-8"))
        findings, _ = run_audit(self.h)
        self.assertIn("plaintext-token", codes(findings))

    @unittest.skipUnless(HAS_GIT, "需要 git")
    def test_repo_option_reads_utf16_tracked_credentials(self):
        repo = self.h.root / "proj"
        repo.mkdir()
        self.git("init", "-q", cwd=repo)
        (repo / "auth.json").write_bytes(CODEX_AUTH.encode("utf-16"))
        self.git("add", "-A", cwd=repo)
        with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(self.h.root.parent)}):
            findings = a.audit_repo(repo)
        self.assertEqual([(f.level, f.code) for f in findings], [("ERROR", "git-tracked-credential")])

    # ---- 監聽設定

    def test_listen_exposed_in_config_files(self):
        self.h.write(".codex/config.toml", 'bind = "0.0.0.0:10541"\n')
        self.h.write(".claude/settings.json", '{"proxy": {"listen": "127.0.0.1:10541"}}')
        findings, _ = run_audit(self.h)
        self.assertEqual([(f.file, f.code) for f in findings], [("~/.codex/config.toml", "listen-exposed")])

    # ---- git

    def git(self, *args, cwd=None):
        env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(self.h.root.parent)}
        subprocess.run(["git", *args], cwd=str(cwd or self.h.root), check=True, capture_output=True, env=env)

    def run_audit_real_git(self):
        with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(self.h.root.parent)}):
            return a.audit(self.h.root, a.candidate_dirs(self.h.root, None))

    @unittest.skipUnless(HAS_GIT, "需要 git")
    def test_git_states(self):
        self.h.write(".codex/auth.json", CODEX_AUTH, 0o600)
        findings, _ = self.run_audit_real_git()
        self.assertEqual(codes(findings), ["plaintext-token"], "不在 git 工作樹內，不該有 git 發現")

        self.git("init", "-q")
        findings, _ = self.run_audit_real_git()
        self.assertEqual(codes(findings), ["git-not-ignored", "plaintext-token"])
        self.assertEqual([f.level for f in findings if f.code == "git-not-ignored"], ["WARN"])

        self.h.write(".gitignore", ".codex/\n")
        findings, _ = self.run_audit_real_git()
        self.assertEqual(codes(findings), ["plaintext-token"], "被 .gitignore 忽略就不該報")

        self.git("add", "-f", ".codex/auth.json")
        findings, _ = self.run_audit_real_git()
        self.assertEqual(codes(findings, "ERROR"), ["git-tracked"], "即使被忽略，已 add 進索引仍是追蹤")

    @unittest.skipUnless(HAS_GIT, "需要 git")
    def test_repo_option_flags_tracked_credential_files(self):
        repo = self.h.root / "proj"
        repo.mkdir()
        self.git("init", "-q", cwd=repo)
        (repo / "auth.json").write_text(CODEX_AUTH, encoding="utf-8")
        (repo / "fixtures").mkdir()
        (repo / "fixtures" / "auth.json").write_text('{"note": "no secrets here"}', encoding="utf-8")
        (repo / "README.md").write_text("hello", encoding="utf-8")
        self.git("add", "-A", cwd=repo)
        with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(self.h.root.parent)}):
            findings = a.audit_repo(repo)
        self.assertEqual(sorted((f.level, f.file.split("::")[1]) for f in findings), [("ERROR", "auth.json"), ("WARN", "fixtures/auth.json")])

    @unittest.skipUnless(HAS_GIT, "需要 git")
    def test_repo_option_clean_repo_and_non_repo(self):
        repo = self.h.root / "proj"
        repo.mkdir()
        self.git("init", "-q", cwd=repo)
        (repo / "README.md").write_text("hello", encoding="utf-8")
        self.git("add", "-A", cwd=repo)
        with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(self.h.root.parent)}):
            self.assertEqual(a.audit_repo(repo), [])
            plain = self.h.root / "plain"
            plain.mkdir()
            self.assertEqual(codes(a.audit_repo(plain)), ["git-unknown"])

    def test_git_unavailable_is_info(self):
        self.h.write(".codex/auth.json", CODEX_AUTH, 0o600)
        findings, _ = run_audit(self.h, git_check=lambda p: "unknown")
        self.assertEqual(codes(findings, "INFO"), ["git-unknown"])

    def test_git_state_without_git_binary_is_unknown(self):
        p = self.h.write(".codex/auth.json", CODEX_AUTH)
        with mock.patch.object(a.subprocess, "run", side_effect=FileNotFoundError):
            self.assertEqual(a.git_state(p), "unknown")

    # ---- 目錄來源

    def test_candidate_dirs_adds_env_dirs_only_when_given(self):
        home = Path("/h")
        self.assertEqual(a.candidate_dirs(home, None), [home / ".grok", home / ".codex", home / ".claude"])
        env = {"CODEX_HOME": "/alt/codex", "CLAUDE_CONFIG_DIR": "/alt/claude"}
        dirs = a.candidate_dirs(home, env)
        self.assertIn(Path("/alt/codex"), dirs)
        self.assertIn(Path("/alt/claude"), dirs)
        self.assertEqual(len(dirs), 5)


class NoLeakCliTest(unittest.TestCase):
    """用 CLI 跑一遍，確認文字、JSON、--strict 的所有輸出都不含憑證值（哨兵）。"""

    def setUp(self):
        self.h = FakeHome()
        self.addCleanup(self.h.close)
        mode = 0o644  # 刻意放寬，確保 perm-loose 路徑也被走過
        self.h.write(".codex/auth.json", CODEX_AUTH, mode)
        self.h.write(".codex/auth.json.bak", CODEX_AUTH, mode)
        self.h.write(".claude/.credentials.json", json.dumps({"claudeAiOauth": {"accessToken": S_ACCESS, "refreshToken": S_REFRESH}}), mode)
        self.h.write(".claude/settings.json", json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": S_ACCESS}}), mode)
        self.h.write(".grok/auth.json", f'{{"{S_KEYNAME}_api_key": "{S_SECRET}", "refresh_token": "{S_REFRESH}"}}', mode)
        self.h.write(".grok/oauth-proxy/state.json", json.dumps({"host": "0.0.0.0", "bind": S_HOSTVAL, "access_token": S_ACCESS}), mode)
        self.h.write(".grok/config.toml", f'listen = "0.0.0.0:10541"\nclient_secret = "{S_SECRET}"\n', mode)
        broken = self.h.write(".grok/broken.json", "", mode)
        broken.write_bytes(b'{"access_token": "' + S_ACCESS.encode() + b'\xff\xfe\x00 not json')
        self.h.write(".codex/auth.yaml", f"refresh_token: {S_REFRESH}\n", mode)
        self.h.write_bytes(".codex/auth16.json", CODEX_AUTH.encode("utf-16"))
        self.h.write_bytes(".grok/proxy16.json", f'{{"listen": "fe80::1%{S_SCOPE}", "access_token": "{S_ACCESS}"}}'.encode("utf-16"))
        self.h.write(".grok/scope.toml", f'bind = "[fe80::2%{S_SCOPE}]:8080"\nlisten = 8080\n')

    def run_cli(self, *args):
        env = {**os.environ, "PYTHONIOENCODING": "cp950", "PYTHONUTF8": "0", "GIT_CEILING_DIRECTORIES": str(self.h.root.parent)}
        return subprocess.run([sys.executable, str(TOOL), "--home", str(self.h.root), *args], capture_output=True, env=env, timeout=120)

    def assert_no_sentinel(self, proc):
        blob = proc.stdout + proc.stderr
        for s in SENTINELS:
            for needle in (s, s[:10] + s[10:16]):  # 完整值，以及值的前一段
                self.assertNotIn(needle.encode(), blob, f"輸出洩漏了 {needle[:14]}…")

    def test_text_output_has_no_secret_values(self):
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 1, proc.stderr.decode("utf-8", "replace"))
        self.assertIn("plaintext-token", proc.stdout.decode("utf-8"))
        self.assert_no_sentinel(proc)

    def test_json_output_has_no_secret_values(self):
        proc = self.run_cli("--json")
        data = json.loads(proc.stdout.decode("utf-8"))
        self.assertGreater(data["stats"]["files_with_token_fields"], 5)
        self.assert_no_sentinel(proc)
        for f in data["findings"]:
            self.assertEqual(set(f), {"level", "code", "file", "message"})

    def test_strict_output_has_no_secret_values(self):
        self.assert_no_sentinel(self.run_cli("--strict"))

    def test_detects_what_was_planted(self):
        data = json.loads(self.run_cli("--json").stdout.decode("utf-8"))
        files_by_code = {}
        for f in data["findings"]:
            files_by_code.setdefault(f["code"], set()).add(f["file"])
        self.assertIn("~/.claude/settings.json", files_by_code["plaintext-token"])
        self.assertIn("~/.grok/config.toml", files_by_code["listen-exposed"])
        self.assertIn("~/.grok/oauth-proxy/state.json", files_by_code["listen-exposed"])
        self.assertIn("~/.grok/broken.json", files_by_code["plaintext-token"], "壞掉的檔案也要能偵測，且不洩漏")
        self.assertIn("~/.codex/auth.json.bak", files_by_code["backup-copy"])
        self.assertIn("~/.codex/auth16.json", files_by_code["plaintext-token"], "UTF-16 檔案也要掃到")
        self.assertIn("~/.grok/proxy16.json", files_by_code["listen-exposed"])
        self.assertIn("~/.grok/scope.toml", files_by_code["listen-exposed"])
        self.assertIn("~/.grok/scope.toml", files_by_code["listen-port-only"])
        if not IS_WIN:
            self.assertIn("~/.codex/auth.json", files_by_code["perm-loose"])


class CliTest(unittest.TestCase):
    def run_cli(self, *args, env=None):
        return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, env=env or os.environ, timeout=120)

    def test_exit_codes(self):
        h = FakeHome()
        self.addCleanup(h.close)
        proc = self.run_cli("--home", str(h.root))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("未發現", proc.stdout.decode("utf-8"))

        h.write(".codex/auth.json", CODEX_AUTH, 0o600)  # 只有 WARN（plaintext-token）
        if not IS_WIN:
            self.assertEqual(self.run_cli("--home", str(h.root)).returncode, 0)
            self.assertEqual(self.run_cli("--home", str(h.root), "--strict").returncode, 1)
            os.chmod(h.root / ".codex/auth.json", 0o644)  # 加上 ERROR
            self.assertEqual(self.run_cli("--home", str(h.root)).returncode, 1)
        h.write(".grok/oauth-proxy/state.json", '{"host": "0.0.0.0"}')
        self.assertEqual(self.run_cli("--home", str(h.root)).returncode, 1)

    def test_usage_errors_exit_2(self):
        h = FakeHome()
        self.addCleanup(h.close)
        self.assertEqual(self.run_cli("--home", str(h.root / "nope")).returncode, 2)
        self.assertEqual(self.run_cli("--home", str(h.root), "--repo", str(h.root / "nope")).returncode, 2)
        self.assertEqual(self.run_cli("--bogus").returncode, 2)

    def test_dir_typo_exits_2_instead_of_silently_passing(self):
        h = FakeHome()
        self.addCleanup(h.close)
        proc = self.run_cli("--home", str(h.root), "--dir", str(h.root / "typo-dir"))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--dir", proc.stderr.decode("utf-8", "replace"))
        (h.root / "a-file").write_text("x", encoding="utf-8")
        self.assertEqual(self.run_cli("--home", str(h.root), "--dir", str(h.root / "a-file")).returncode, 2, "檔案不是資料夾")
        (h.root / "real").mkdir()
        self.assertEqual(self.run_cli("--home", str(h.root), "--dir", str(h.root / "real")).returncode, 0)

    def test_extra_dir_option(self):
        h = FakeHome()
        self.addCleanup(h.close)
        h.write("custom/state.json", '{"bind": "0.0.0.0:1"}')
        proc = self.run_cli("--home", str(h.root), "--dir", str(h.root / "custom"))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("~/custom/state.json", proc.stdout.decode("utf-8"))

    def test_output_is_utf8_under_cp950(self):
        h = FakeHome()
        self.addCleanup(h.close)
        h.write(".codex/auth.json", CODEX_AUTH, 0o600)
        env = {**os.environ, "PYTHONIOENCODING": "cp950", "PYTHONUTF8": "0"}
        for args in (["--help"], ["--home", str(h.root)], ["--home", str(h.root), "--json"]):
            with self.subTest(args=args[:1]):
                proc = self.run_cli(*args, env=env)
                proc.stdout.decode("utf-8")  # 不是 UTF-8 會丟 UnicodeDecodeError


if __name__ == "__main__":
    unittest.main()
