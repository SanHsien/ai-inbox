#!/usr/bin/env python3
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from audit_fullstack_security import (
    audit_fullstack_security,
    check_client_components,
    check_env_example,
    check_gitignore,
    check_sql_rls,
)


class TestAuditFullstackSecurity(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_audit_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

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


if __name__ == "__main__":
    unittest.main()
