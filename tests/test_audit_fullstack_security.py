#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from audit_fullstack_security import (
    audit_fullstack_security,
    check_client_components,
    check_env_example,
    check_gitignore,
    check_sql_rls,
    check_wrangler_config,
)


class TestAuditFullstackSecurity(unittest.TestCase):
    def setUp(self):
        # Wrangler 檢查以 git 的實際判定為準，所以稽核目標要是真的 git 工作樹。
        # 全域設定與全域忽略檔換成空檔，測試結果不受執行機器的 git 設定影響。
        self.base_dir = Path(tempfile.mkdtemp(prefix="test_audit_"))
        self.test_dir = self.base_dir / "repo"
        self.test_dir.mkdir()
        (self.base_dir / "empty_ignore").write_text("", encoding="utf-8")
        (self.base_dir / "gitconfig").write_text(
            "[core]\n\texcludesFile = " + (self.base_dir / "empty_ignore").as_posix() + "\n", encoding="utf-8")
        env = patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(self.base_dir / "gitconfig"),
                                      "GIT_CONFIG_NOSYSTEM": "1"})
        env.start()
        self.addCleanup(env.stop)
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            os.environ.pop(key, None)
        self._git("init", "-q")

    def tearDown(self):
        shutil.rmtree(self.base_dir, ignore_errors=True)

    def _git(self, *args, cwd=None):
        done = subprocess.run(["git", "-C", str(cwd or self.test_dir), *args],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def _git_would_commit(self, rel):
        """對照組：git 自己認為這個路徑不會被忽略（check-ignore 結束碼 1）。"""
        done = subprocess.run(["git", "-C", str(self.test_dir), "check-ignore", "-q", "--no-index", rel],
                              capture_output=True)
        return done.returncode == 1

    def test_clean_project_passes(self):
        # 1. 建立合格的 .gitignore
        (self.test_dir / ".gitignore").write_text(".env\n.env.local\nnode_modules\n", encoding="utf-8")

        # 2. 建立合格的 .env.example
        (self.test_dir / ".env.example").write_text(
            "NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co\nNEXT_PUBLIC_SUPABASE_ANON_KEY=anon-token\n",
            encoding="utf-8",
        )

        # 3. 建立合格的 Client Component
        src_dir = self.test_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "Button.tsx").write_text(
            '"use client";\nexport function Button() { return <button>Click</button>; }\n',
            encoding="utf-8",
        )

        # 4. 建立合格的 SQL Migration
        migrations_dir = self.test_dir / "supabase" / "migrations"
        migrations_dir.mkdir(parents=True, exist_ok=True)
        (migrations_dir / "001_init.sql").write_text(
            "CREATE TABLE public.orders (id UUID PRIMARY KEY);\nALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;\n",
            encoding="utf-8",
        )

        report = audit_fullstack_security(self.test_dir)
        self.assertTrue(report["passed"])
        self.assertEqual(report["total_issues"], 0)

    def test_missing_gitignore(self):
        issues = check_gitignore(self.test_dir)
        self.assertTrue(any("找不到 .gitignore" in i for i in issues))

    def test_incomplete_gitignore(self):
        (self.test_dir / ".gitignore").write_text("node_modules\n", encoding="utf-8")
        issues = check_gitignore(self.test_dir)
        self.assertTrue(any(".env" in i for i in issues))

    def test_env_example_leaking_key(self):
        fake_key = "sk_" + "live_" + "testdummy1234567890abcdef"
        (self.test_dir / ".env.example").write_text(
            f"STRIPE_SECRET_KEY={fake_key}\n",
            encoding="utf-8",
        )
        issues = check_env_example(self.test_dir)
        self.assertEqual(len(issues), 1)
        self.assertIn("Stripe Live Secret Key", issues[0])

    def test_client_component_leaking_secret(self):
        src_dir = self.test_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "LeakyComponent.tsx").write_text(
            '"use client";\nconst key = process.env.SUPABASE_SERVICE_ROLE_KEY;\n',
            encoding="utf-8",
        )
        issues = check_client_components(self.test_dir)
        self.assertEqual(len(issues), 1)
        self.assertIn("SUPABASE_SERVICE_ROLE_KEY", issues[0])

    def test_sql_missing_rls(self):
        sql_file = self.test_dir / "schema.sql"
        sql_file.write_text("CREATE TABLE public.secret_data (id INT);\n", encoding="utf-8")
        issues = check_sql_rls(self.test_dir)
        self.assertEqual(len(issues), 1)
        self.assertIn("ENABLE ROW LEVEL SECURITY", issues[0])

    def test_gitignore_substring_and_negation_do_not_count(self):
        # ".env.example" 不等於忽略 ".env"；否定規則也不算忽略
        (self.test_dir / ".gitignore").write_text(".env.example\n!.env\n!.env.local\n", encoding="utf-8")
        issues = check_gitignore(self.test_dir)
        self.assertEqual(len(issues), 2)

    def test_gitignore_with_utf8_bom_is_read_like_git_does(self):
        # Windows PowerShell 5 的 Out-File／Set-Content -Encoding UTF8 會在檔頭加 BOM；git 會略過它，
        # 稽核工具不能把第一行 ".env" 讀成 "﻿.env" 而誤報「未忽略」
        (self.test_dir / ".gitignore").write_bytes(b"\xef\xbb\xbf.env\n.env.local\n")
        self.assertEqual(check_gitignore(self.test_dir), [])

    def test_gitignore_negation_after_ignore_rule_un_ignores_the_file(self):
        # gitignore 以最後一條符合的規則為準：先忽略再用 "!" 放行，.env.local 就會被提交
        (self.test_dir / ".gitignore").write_text(".env*\n!.env.local\n", encoding="utf-8")
        issues = check_gitignore(self.test_dir)
        self.assertEqual(len(issues), 1)
        self.assertIn(".env.local", issues[0])
        # 放行的是範本檔就沒事；放行後又重新忽略也沒事
        (self.test_dir / ".gitignore").write_text(".env*\n!.env.example\n", encoding="utf-8")
        self.assertEqual(check_gitignore(self.test_dir), [])
        (self.test_dir / ".gitignore").write_text(".env*\n!.env.local\n.env.local\n", encoding="utf-8")
        self.assertEqual(check_gitignore(self.test_dir), [])

    def test_gitignore_glob_accepted(self):
        (self.test_dir / ".gitignore").write_text("# secrets\n.env*\n", encoding="utf-8")
        self.assertEqual(check_gitignore(self.test_dir), [])
        (self.test_dir / ".gitignore").write_text("/.env\n**/.env.local\n", encoding="utf-8")
        self.assertEqual(check_gitignore(self.test_dir), [])

    def test_env_example_detects_rsa_and_openssh_private_keys(self):
        for header in ("RSA PRIVATE KEY", "OPENSSH PRIVATE KEY", "PRIVATE KEY", "EC PRIVATE KEY"):
            (self.test_dir / ".env.example").write_text(f"KEY=-----BEGIN {header}-----\n", encoding="utf-8")
            self.assertEqual(len(check_env_example(self.test_dir)), 1, header)

    def test_client_component_scan_works_when_root_is_under_build_dir(self):
        # 專案根目錄的絕對路徑含 build/ 時，不可整個專案被略過
        root = self.test_dir / "build" / "app"
        (root / "src").mkdir(parents=True)
        (root / "src" / "Leak.tsx").write_text("'use client'\nconst k = SUPABASE_SERVICE_ROLE_KEY;\n", encoding="utf-8")
        (root / "node_modules" / "pkg").mkdir(parents=True)
        (root / "node_modules" / "pkg" / "x.js").write_text("'use client'\nJWT_SECRET\n", encoding="utf-8")
        issues = check_client_components(root)
        self.assertEqual(len(issues), 1)
        self.assertIn("SUPABASE_SERVICE_ROLE_KEY", issues[0])

    def test_client_component_mjs_extension_scanned(self):
        (self.test_dir / "a.mjs").write_text('"use client"\nconst k = STRIPE_SECRET_KEY;\n', encoding="utf-8")
        self.assertEqual(len(check_client_components(self.test_dir)), 1)

    def test_sql_rls_case_quoted_schema_and_comments(self):
        (self.test_dir / "a.sql").write_text(
            'CREATE TABLE "public"."Users" (id int);\nALTER TABLE public.users ENABLE ROW LEVEL SECURITY;\n',
            encoding="utf-8",
        )
        self.assertEqual(check_sql_rls(self.test_dir), [])
        (self.test_dir / "a.sql").write_text(
            'CREATE TABLE "Leaky" (id int);\n-- CREATE TABLE commented_out (id int);\n/* CREATE TABLE blk (id int); */\n',
            encoding="utf-8",
        )
        issues = check_sql_rls(self.test_dir)
        self.assertEqual(len(issues), 1)
        self.assertIn("leaky", issues[0])

    def test_wrangler_config_blocks_plaintext_secrets_and_missing_dev_vars_ignore(self):
        (self.test_dir / ".gitignore").write_text(".env\n.env.local\n", encoding="utf-8")
        (self.test_dir / "wrangler.toml").write_text(
            'name = "demo-worker"\ncompatibility_date = "2026-11-01"\n\n[vars]\nOPENAI_API_KEY = "real-secret-value-123"\n',
            encoding="utf-8",
        )
        issues = check_wrangler_config(self.test_dir)
        self.assertEqual(len(issues), 2)
        self.assertTrue(any(".dev.vars" in i for i in issues))
        self.assertTrue(any("OPENAI_API_KEY" in i for i in issues))

    def test_wrangler_config_passes_when_clean(self):
        (self.test_dir / ".gitignore").write_text(".env\n.env.local\n.dev.vars*\n", encoding="utf-8")
        (self.test_dir / "wrangler.toml").write_text(
            'name = "demo-worker"\ncompatibility_date = "2026-11-01"\n\n[vars]\nENVIRONMENT = "production"\n',
            encoding="utf-8",
        )
        self.assertEqual(check_wrangler_config(self.test_dir), [])

    def test_wrangler_inline_json_toml_and_numeric_password(self):
        (self.test_dir / '.gitignore').write_text('.dev.vars*\n', encoding='utf-8')
        for name, content in (
            ('wrangler.json', '{"name":"demo","vars":{"API_KEY":"synthetic-secret"}}'),
            ('wrangler.toml', 'name="demo"\nvars = { API_KEY = "synthetic-secret" }'),
            ('wrangler.toml', '[vars]\nPASSWORD=123456'),
        ):
            with self.subTest(name=name, content=content):
                p = self.test_dir / name
                p.write_text(content, encoding='utf-8')
                self.assertTrue(check_wrangler_config(self.test_dir))
                p.unlink()

    def test_wrangler_env_vars_all_types_and_nested_tokens(self):
        (self.test_dir / '.gitignore').write_text('.dev.vars*\n', encoding='utf-8')
        for value in (0, False, None, '', [], {}, ['safe'], {'nested': 'safe'}, 'static'):
            for scope in ('vars', 'env'):
                config = {'vars': {'PASSWORD': value}} if scope == 'vars' else {
                    'env': {'staging': {'vars': {'PASSWORD': value}}}}
                (self.test_dir / 'wrangler.json').write_text(json.dumps(config), encoding='utf-8')
                self.assertTrue(check_wrangler_config(self.test_dir), (scope, value))
        config = {'vars': {'PUBLIC': {'nested': ['ghp_' + 'a' * 24]}}}
        (self.test_dir / 'wrangler.json').write_text(json.dumps(config), encoding='utf-8')
        self.assertTrue(check_wrangler_config(self.test_dir))

    def test_wrangler_jsonc_strings_comments_and_trailing_commas(self):
        (self.test_dir / '.gitignore').write_text('.dev.vars*\n', encoding='utf-8')
        p = self.test_dir / 'wrangler.jsonc'
        p.write_text('''{// comment
          "vars": {"URL": "https://example.com/a//b/*c*/", "TEXT": "escaped\\\"quote",},
          /* comment */ "env": {"test": {"vars": {"ENVIRONMENT": "test"},},},
        }''', encoding='utf-8')
        self.assertEqual(check_wrangler_config(self.test_dir), [])
        p.write_text('{"env":{"x":{"vars":{"API_KEY":"secret"}}}}', encoding='utf-8')
        self.assertTrue(check_wrangler_config(self.test_dir))

    def test_wrangler_bad_schema_and_empty_config_fail_closed(self):
        (self.test_dir / '.gitignore').write_text('.dev.vars*\n', encoding='utf-8')
        for name, content in (('wrangler.json', ''), ('wrangler.json', '{}'),
                              ('wrangler.json', '[]'), ('wrangler.json', '{'),
                              ('wrangler.toml', ''), ('wrangler.toml', 'vars = ['),
                              ('wrangler.jsonc', '{/* unfinished'),
                              ('wrangler.json', '{"vars":[]}'),
                              ('wrangler.json', '{"env":{"x":[]}}'),
                              ('wrangler.json', '{"env":[]}'),
                              ('wrangler.json', '{"vars":{},"vars":{"PASSWORD":"x"}}')):
            with self.subTest(content=content):
                p = self.test_dir / name
                p.write_text(content, encoding='utf-8')
                self.assertTrue(check_wrangler_config(self.test_dir))
                p.unlink()

    def test_wrangler_missing_root_and_missing_ignore(self):
        self.assertTrue(check_wrangler_config(self.test_dir / 'absent'))
        (self.test_dir / 'wrangler.toml').write_text('name="demo"', encoding='utf-8')
        self.assertTrue(check_wrangler_config(self.test_dir))

    # ---- 第二輪：鍵名放寬、內嵌帳密、遞迴掃描、.dev.vars.* 與否定規則 ----
    def _wrangler(self, toml, ignore='.dev.vars*\n', where=''):
        (self.test_dir / '.gitignore').write_text(ignore, encoding='utf-8')
        d = self.test_dir / where if where else self.test_dir
        d.mkdir(parents=True, exist_ok=True)
        (d / 'wrangler.toml').write_text(toml, encoding='utf-8')
        return check_wrangler_config(self.test_dir)

    def test_wrangler_broadened_sensitive_key_names(self):
        for key in ('TOKEN', 'STRIPE_KEY', 'DB_SECRET', 'ADMIN_PASSWORD', 'SERVICE_CREDENTIAL'):
            with self.subTest(key=key):
                self.assertTrue(self._wrangler(f'name="d"\n[vars]\n{key}="x1"\n'))

    def test_wrangler_embedded_credentials_and_token_patterns(self):
        for value in ('postgres://admin:hunter2@db.example.com/x', 'rk' + '_live_' + 'a' * 24,
                      'sk' + '-ant-' + 'a' * 24, 'xox' + 'b-123456789012-abcdef', 'ya' + '29.' + 'a' * 20):
            with self.subTest(value=value[:12]):
                self.assertTrue(self._wrangler(f'name="d"\n[vars]\nPUBLIC_NOTE="{value}"\n'))
        self.assertEqual(self._wrangler('name="d"\n[vars]\nPUBLIC_URL="https://example.com/a"\n'), [])

    def test_wrangler_found_in_subdirectories_and_node_modules_skipped(self):
        bad = 'name="d"\n[vars]\nPASSWORD="x1"\n'
        self.assertTrue(self._wrangler(bad, where='apps/api'))
        (self.test_dir / 'apps' / 'api' / 'wrangler.toml').unlink()
        self.assertEqual(self._wrangler(bad, where='node_modules/pkg'), [])
        self.assertEqual(self._wrangler(bad, where='.git/x'), [])

    def test_wrangler_subdirectory_unparsable_fails_closed(self):
        self.assertTrue(self._wrangler('vars = [', where='apps/api'))

    def test_dev_vars_variants_must_be_ignored(self):
        clean = 'name="d"\n'
        self.assertEqual(self._wrangler(clean, ignore='.dev.vars\n.dev.vars.*\n'), [])
        issues = self._wrangler(clean, ignore='.dev.vars\n')
        self.assertTrue(any('.dev.vars.production' in i for i in issues), issues)
        (self.test_dir / '.dev.vars.staging').write_text('A=1', encoding='utf-8')
        issues = self._wrangler(clean, ignore='.dev.vars\n')
        self.assertTrue(any('.dev.vars.staging' in i for i in issues), issues)
        # .example 可以提交，不要求忽略
        (self.test_dir / '.dev.vars.staging').unlink()
        (self.test_dir / '.dev.vars.example').write_text('A=', encoding='utf-8')
        self.assertEqual(self._wrangler(clean, ignore='.dev.vars\n.dev.vars.*\n!.dev.vars.example\n'), [])

    def test_dev_vars_negation_rule_is_honoured(self):
        clean = 'name="d"\n'
        self.assertTrue(self._wrangler(clean, ignore='.dev.vars*\n!.dev.vars\n'))
        self.assertTrue(self._wrangler(clean, ignore='.dev.vars*\n!.dev.vars.*\n'))
        self.assertEqual(self._wrangler(clean, ignore='!.dev.vars\n.dev.vars*\n'), [])

    def test_wrangler_walk_error_fails_closed(self):
        import os
        from unittest.mock import patch

        def failing_walk(top, onerror=None, **kwargs):
            onerror(PermissionError(13, 'denied', str(Path(top) / 'locked')))
            return iter(())

        with patch.object(os, 'walk', failing_walk):
            issues = check_wrangler_config(self.test_dir)
        self.assertTrue(issues)
        self.assertTrue(any('未完成稽核' in i for i in issues))

    def test_dev_vars_only_project_without_wrangler_file(self):
        (self.test_dir / '.dev.vars').write_text('A=1', encoding='utf-8')
        self.assertTrue(check_wrangler_config(self.test_dir))

    def test_subdirectory_dev_vars_checked(self):
        d = self.test_dir / 'apps' / 'api'
        d.mkdir(parents=True)
        (d / '.dev.vars.staging').write_text('A=1', encoding='utf-8')
        (self.test_dir / '.gitignore').write_text('.dev.vars\n', encoding='utf-8')
        self.assertTrue(check_wrangler_config(self.test_dir))
        (d / '.gitignore').write_text('.dev.vars.*\n', encoding='utf-8')
        self.assertEqual(check_wrangler_config(self.test_dir), [])

    # ---- 第三輪（2026-11-21 稽核退回 T-20261108-05）：忽略判定以 git 為準 ----
    def _project(self, where, ignore_files, dev_vars=('.dev.vars',), toml='name="d"\n'):
        for rel, text in ignore_files.items():
            path = self.test_dir / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        d = self.test_dir / where
        d.mkdir(parents=True, exist_ok=True)
        (d / 'wrangler.toml').write_text(toml, encoding='utf-8')
        for name in dev_vars:
            (d / name).write_text('A=1\n', encoding='utf-8')
        return check_wrangler_config(self.test_dir)

    def test_root_anchored_rule_does_not_cover_subdirectory_project(self):
        # 重現 1：根目錄錨定規則只管根目錄那一層，app/.dev.vars 會被提交
        issues = self._project('app', {'.gitignore': '/.dev.vars\n/.dev.vars.*\n'})
        self.assertTrue(self._git_would_commit('app/.dev.vars'))
        self.assertTrue(any('app' in i and "'.dev.vars'" in i for i in issues), issues)
        # 同一份規則去掉錨點就真的忽略，不可誤報
        self.assertEqual(self._project('app', {'.gitignore': '.dev.vars\n.dev.vars.*\n'}), [])

    def test_intermediate_gitignore_negation_is_honoured(self):
        # 重現 2：中間層 a/.gitignore 的 "!" 把根目錄規則反轉，a/b/.dev.vars 會被提交
        issues = self._project('a/b', {'.gitignore': '.dev.vars*\n', 'a/.gitignore': '!.dev.vars\n'})
        self.assertTrue(self._git_would_commit('a/b/.dev.vars'))
        self.assertTrue(any('a/b' in i and "'.dev.vars'" in i for i in issues), issues)
        # 再往下一層重新忽略就沒事
        self.assertEqual(self._project('a/b', {'a/b/.gitignore': '.dev.vars\n'}), [])

    def test_wrangler_vars_short_secret_key_names(self):
        # 重現 3：DB_PASS、AUTH 這類鍵名的明文值要報，而且只報鍵名不輸出值
        marker = 'synthetic-value-do-not-print'
        keys = ('DB_PASS', 'AUTH', 'DBPASS', 'dbPass', 'MYSQL_PWD', 'BASIC_AUTH', 'Authorization',
                'SMTP_PASSWD', 'SENTRY_DSN', 'TLS_CERT', 'SIGNING_PRIVATE', 'UNLOCK_PASSPHRASE', 'oauth')
        issues = self._wrangler('name="d"\n[vars]\n' + ''.join(f'{key}="{marker}"\n' for key in keys))
        for key in keys:
            with self.subTest(key=key):
                self.assertTrue(any(i.endswith(f'vars.{key} 為敏感變數，所有值型別皆須移至 secrets') for i in issues), issues)
        self.assertEqual(len(issues), len(keys), issues)
        self.assertFalse(any(marker in i for i in issues), issues)
        # 最小重現：只有 DB_PASS 與 AUTH 兩個鍵，各報一項
        issues = self._wrangler(f'name="d"\n[vars]\nDB_PASS="{marker}"\nAUTH="Basic {marker}"\n')
        self.assertEqual(len(issues), 2, issues)
        # env.<名稱>.vars 一樣要報
        issues = self._wrangler(f'name="d"\n[env.prod.vars]\nDB_PASS="{marker}"\n')
        self.assertTrue(any('env.prod.vars.DB_PASS' in i for i in issues), issues)
        # 一般變數不可因為新增的鍵名而誤報
        clean = ('ENVIRONMENT', 'AUTHOR_NAME', 'COMPASS_URL', 'PUBLIC_URL', 'CERTAIN_MODE', 'PASSENGER_LIMIT')
        self.assertEqual(self._wrangler('name="d"\n[vars]\n' + ''.join(f'{key}="x1"\n' for key in clean)), [])

    def test_dev_vars_tracked_despite_ignore_rule_is_reported(self):
        # 攻擊者角度 4：.gitignore 有規則，但檔案早已被追蹤（或 git add -f），規則對它無效
        self._project('', {'.gitignore': '.dev.vars*\n'})
        self._git('add', '-f', '.dev.vars')
        self.assertIn('.dev.vars', self._git('ls-files'))
        issues = check_wrangler_config(self.test_dir)
        self.assertTrue(any("'.dev.vars'" in i and '追蹤' in i for i in issues), issues)

    def test_dev_vars_ignored_only_by_local_exclude_is_reported(self):
        # 攻擊者角度 5：只靠 .git/info/exclude 或個人全域忽略檔，規則不會跟著 repo 走，別人 clone 後照樣提交
        (self.test_dir / '.git' / 'info').mkdir(exist_ok=True)
        (self.test_dir / '.git' / 'info' / 'exclude').write_text('.dev.vars*\n', encoding='utf-8')
        issues = self._project('', {'.gitignore': 'node_modules\n'})
        self.assertFalse(self._git_would_commit('.dev.vars'))  # 本機 git 的確會忽略
        self.assertTrue(any('本機' in i and "'.dev.vars'" in i for i in issues), issues)
        (self.test_dir / '.git' / 'info' / 'exclude').write_text('', encoding='utf-8')
        (self.base_dir / 'empty_ignore').write_text('.dev.vars*\n', encoding='utf-8')
        self.assertFalse(self._git_would_commit('.dev.vars'))
        issues = check_wrangler_config(self.test_dir)
        self.assertTrue(any('本機' in i and "'.dev.vars'" in i for i in issues), issues)

    def test_dev_vars_case_variant_file_is_checked(self):
        # 攻擊者角度 6：檔名大小寫不同（Windows／macOS 上 Wrangler 照樣讀得到），
        # repo 設成分大小寫時小寫規則管不到它
        self._git('config', 'core.ignorecase', 'false')
        issues = self._project('', {'.gitignore': '.dev.vars*\n'}, dev_vars=('.DEV.VARS',))
        self.assertTrue(self._git_would_commit('.DEV.VARS'))
        self.assertTrue(any("'.DEV.VARS'" in i for i in issues), issues)

    def test_dev_vars_local_variant_with_anchored_rule(self):
        # 攻擊者角度 7：.dev.vars.local 這類變體放在子目錄，根目錄只寫錨定規則
        issues = self._project('svc', {'.gitignore': '.dev.vars\n/.dev.vars.*\n'},
                               dev_vars=('.dev.vars.local',))
        self.assertTrue(self._git_would_commit('svc/.dev.vars.local'))
        self.assertTrue(any("'.dev.vars.local'" in i for i in issues), issues)

    def test_ignored_parent_directory_counts_as_ignored(self):
        # 整個目錄被忽略時 git 不會提交裡面的檔，不可誤報
        self.assertEqual(self._project('local', {'.gitignore': '/local/\n'}), [])

    def test_outside_git_work_tree_is_reported_as_unknown(self):
        # 不在 git 工作樹內：無從得知會不會被提交，不可默認安全
        plain = self.base_dir / 'plain'
        plain.mkdir()
        (plain / '.gitignore').write_text('.dev.vars*\n', encoding='utf-8')
        (plain / 'wrangler.toml').write_text('name="d"\n', encoding='utf-8')
        with patch.dict(os.environ, {'GIT_CEILING_DIRECTORIES': str(self.base_dir)}):
            issues = check_wrangler_config(plain)
            report = audit_fullstack_security(plain)
        self.assertTrue(any('無法' in i and '未完成稽核' in i for i in issues), issues)
        self.assertFalse(report['passed'])

    def test_git_unavailable_is_reported_as_unknown(self):
        (self.test_dir / '.gitignore').write_text('.dev.vars*\n', encoding='utf-8')
        (self.test_dir / 'wrangler.toml').write_text('name="d"\n', encoding='utf-8')
        import audit_fullstack_security as tool
        for error in (FileNotFoundError('git'), subprocess.TimeoutExpired('git', 1)):
            with self.subTest(error=type(error).__name__):
                with patch.object(tool.subprocess, 'run', side_effect=error):
                    issues = check_wrangler_config(self.test_dir)
                self.assertTrue(any('無法' in i and '未完成稽核' in i for i in issues), issues)

    def test_nested_repository_uses_its_own_rules(self):
        # 外層 repo 的規則管不到內層獨立 repo；逐目錄問該目錄所屬的 repo
        inner = self.test_dir / 'vendor' / 'svc'
        inner.mkdir(parents=True)
        self._git('init', '-q', cwd=inner)
        issues = self._project('vendor/svc', {'.gitignore': '.dev.vars*\n'})
        self.assertTrue(any('vendor/svc' in i and "'.dev.vars'" in i for i in issues), issues)
        (inner / '.gitignore').write_text('.dev.vars*\n', encoding='utf-8')
        self.assertEqual(check_wrangler_config(self.test_dir), [])


if __name__ == "__main__":
    unittest.main()
