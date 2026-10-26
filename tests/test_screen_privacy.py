"""tools/screen_privacy.py 與 docs/multimodal-screen-privacy-spec.md 的單元測試。

假金鑰一律用字串拼接產生，避免整串出現在原始碼裡被 verify_inbox 的機密掃描擋下。
"""

import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import screen_privacy as sp  # noqa: E402

TOOL = ROOT / "tools" / "screen_privacy.py"
SPEC = ROOT / "docs" / "multimodal-screen-privacy-spec.md"


def fake(*parts: str) -> str:
    return "".join(parts)


class TitleNormalizationTest(unittest.TestCase):
    def test_normalize_strips_spinner_dirty_mark_and_notification_count(self):
        self.assertEqual(sp.normalize_title("◐ Claude Code"), "Claude Code")
        self.assertEqual(sp.normalize_title("● main.py - Code"), "main.py - Code")
        self.assertEqual(sp.normalize_title("(3) Inbox - Mail"), "Inbox - Mail")
        self.assertEqual(sp.normalize_title("(12+) ⠋ ● Build"), "Build")
        self.assertEqual(sp.normalize_title(None), "")

    def test_normalize_is_idempotent(self):
        once = sp.normalize_title("(3) ◐ ● Title")
        self.assertEqual(sp.normalize_title(once), once)

    def test_sanitize_removes_invisible_and_neutralises_urls_and_schemes(self):
        dirty = "Hi\u200b\u202e there\x00 https://evil.example/path?q=1 javascript:alert(1)"
        clean = sp.sanitize_title(dirty)
        for bad in ("\u200b", "\u202e", "\x00", "https://", "javascript:"):
            self.assertNotIn(bad, clean)
        self.assertIn("[網址:evil.example]", clean)
        self.assertIn("[連結]:", clean)

    def test_sanitize_url_keeps_only_the_host(self):
        # 標題裡的網址只該留主機名：帳密（userinfo）、沒有路徑時緊接在主機後的 ?query 與 #fragment 都是機密
        cases = {
            "Login https://alice:hunter2@example.com/inbox": ("hunter2", "[網址:example.com]"),
            "https://example.com?token=abc123secret": ("abc123secret", "[網址:example.com]"),
            "https://example.com#access_token=zzz999": ("zzz999", "[網址:example.com]"),
            "https://host.example:8443?key=k3y": ("k3y", "[網址:host.example:8443]"),
            "ftp://admin:pw0rd@files.example/x": ("pw0rd", "[網址:files.example]"),
        }
        for dirty, (leaked, expected) in cases.items():
            with self.subTest(dirty=dirty):
                clean = sp.sanitize_title(dirty)
                self.assertNotIn(leaked, clean)
                self.assertIn(expected, clean)

    def test_sanitize_strips_markup_and_truncates(self):
        self.assertEqual(sp.sanitize_title("a`b<c>d|e{f}g\\h"), "abcdefgh")
        self.assertEqual(len(sp.sanitize_title("x" * 500)), 160)
        self.assertEqual(len(sp.sanitize_title("x" * 500, limit=10)), 10)


class ClassifyWindowSpecTest(unittest.TestCase):
    """規範第 7 節的視窗分類案例。"""

    def test_blocked(self):
        cases = [
            ("chrome.exe", "病歷系統 - Google Chrome"),
            ("chrome.exe", "Patient chart - Chrome"),
            ("1Password.exe", "1Password"),
            ("chrome.exe", "Pornhub - Google Chrome"),
            ("chrome.exe", "某論壇 無碼專區 - Chrome"),
            ("chrome.exe", "新标签页 - 无痕模式"),
            ("chrome.exe", "新しいタブ (シークレット) - Google Chrome"),
            ("chrome.exe", "환자 진료 기록 - Chrome"),
            ("chrome.exe", "網路銀行 線上轉帳 - Edge"),
            ("Code.exe", ".env - Visual Studio Code"),
            ("Code.exe", "id_rsa - Visual Studio Code"),
        ]
        for app, title in cases:
            with self.subTest(title=title):
                self.assertEqual(sp.classify_window(app, title), "blocked")

    def test_nocap(self):
        cases = [
            ("LINE.exe", "LINE"),
            ("Slack.exe", "general - Slack"),
            ("chrome.exe", "收件匣 (5) - Gmail - Chrome"),
            ("League of Legends.exe", "LoL"),
        ]
        for app, title in cases:
            with self.subTest(title=title):
                self.assertEqual(sp.classify_window(app, title), "nocap")

    def test_self(self):
        for app, title in [("WindowsTerminal.exe", "◐ Claude Code"), ("WindowsTerminal.exe", "Antigravity CLI")]:
            with self.subTest(title=title):
                self.assertEqual(sp.classify_window(app, title), "self")

    def test_ok(self):
        cases = [
            ("chrome.exe", "建置過程中出現錯誤 - Terminal"),
            ("Code.exe", "javascript.ts - Visual Studio Code"),  # jav 不能誤判
            ("chrome.exe", "進出口交易系統 - Chrome"),
            ("Code.exe", "API 暴露點檢查清單.md - VS Code"),
            ("chrome.exe", "Amazon EMR - Console - Chrome"),
        ]
        for app, title in cases:
            with self.subTest(title=title):
                self.assertEqual(sp.classify_window(app, title), "ok")


class ClassifyWindowExtraTest(unittest.TestCase):
    def test_blocked_app_by_name_even_with_innocent_title(self):
        self.assertEqual(sp.classify_window("KeePassXC.exe", "Database"), "blocked")
        self.assertEqual(sp.classify_window(r"C:\Program Files\Bitwarden\Bitwarden.exe", "Vault"), "blocked")

    def test_blocked_has_priority_over_self_and_nocap(self):
        self.assertEqual(sp.classify_window("Slack.exe", "InPrivate - Slack"), "blocked")
        self.assertEqual(sp.classify_window("WindowsTerminal.exe", "Claude Code - 病歷"), "blocked")

    def test_zero_width_characters_cannot_bypass_title_rules(self):
        self.assertEqual(sp.classify_window("chrome.exe", "病\u200b歷系統 - Chrome"), "blocked")
        self.assertEqual(sp.classify_window("chrome.exe", "Incog\u2060nito - Chrome"), "blocked")

    def test_self_apps_and_terminal_titles(self):
        self.assertEqual(sp.classify_window("Antigravity.exe", "Antigravity - project"), "self")
        self.assertEqual(sp.classify_window("pwsh.exe", "✳ Claude Code"), "self")
        # 瀏覽器分頁剛好叫 Codex 文件，不是代理自己的終端
        self.assertEqual(sp.classify_window("chrome.exe", "Codex CLI docs - Chrome"), "ok")

    def test_nocap_service_name_must_be_a_title_segment(self):
        self.assertEqual(sp.classify_window("chrome.exe", "Gmail - Google Chrome"), "nocap")
        self.assertEqual(sp.classify_window("chrome.exe", "Slack API reference - Chrome"), "ok")
        self.assertEqual(sp.classify_window("Code.exe", "ai-inbox - Visual Studio Code"), "ok")

    def test_empty_and_none_inputs_are_ok(self):
        self.assertEqual(sp.classify_window("", ""), "ok")
        self.assertEqual(sp.classify_window(None, None), "ok")


class FalsePositiveRegressionTest(unittest.TestCase):
    """審查找到的誤殺：收斂後必須放行；仍該擋的要繼續擋。"""

    def test_clinic_as_brand_name_is_not_blocked(self):
        for title in (
            "Mayo Clinic researchers report new cancer therapy results - Google Chrome",
            "Mayo Clinic - Chrome",
            "Cleveland Clinic News - Edge",
        ):
            with self.subTest(title=title):
                self.assertEqual(sp.classify_window("chrome.exe", title), "ok")

    def test_clinic_records_are_still_blocked(self):
        self.assertEqual(sp.classify_window("chrome.exe", "Clinic records - Chrome"), "blocked")
        self.assertEqual(sp.classify_window("chrome.exe", "Clinic portal login - Chrome"), "blocked")

    def test_browser_reading_pem_docs_is_not_blocked(self):
        for title in (
            "How to convert a .pem file to .pfx - Stack Overflow - Google Chrome",
            "OpenSSL cookbook: .p12 and .pem formats - Firefox",
            "Understanding id_rsa and SSH keys - Chrome",
            "dotenv: how .env files work - Chrome",
        ):
            with self.subTest(title=title):
                self.assertEqual(sp.classify_window("chrome.exe", title), "ok")

    def test_secret_file_names_still_blocked_where_they_are_the_document(self):
        cases = [
            ("notepad.exe", "server.pem - Notepad"),
            ("Code.exe", "cert.p12 - project - Visual Studio Code"),
            ("explorer.exe", "backup.pfx"),
            ("Code.exe", "● .env.local - Visual Studio Code"),
            ("Code.exe", "credentials.json - Visual Studio Code"),
            ("chrome.exe", "server.pem"),  # 瀏覽器直接開原始檔：標題就是檔名
            ("chrome.exe", "raw.githubusercontent.com/me/repo/main/.env"),
            ("firefox.exe", "secrets.yaml - Mozilla Firefox"),
        ]
        for app, title in cases:
            with self.subTest(title=title):
                self.assertEqual(sp.classify_window(app, title), "blocked")

    def test_editor_viewing_unrelated_file_with_pem_like_name_is_ok(self):
        self.assertEqual(sp.classify_window("Code.exe", "pem-notes.md - Visual Studio Code"), "ok")

    def test_assignment_to_identifier_is_not_a_secret(self):
        for text in (
            "password = getpass_value_here",
            "password = get_password_from_user",
            "secret = load_secret_from_vault",
            "token = refresh_token_value",
            "auth_token = get_token_v2",
            "const password = getpassValueHere;",
        ):
            with self.subTest(text=text):
                self.assertEqual(sp.inspect_ocr_text(text), (False, "pass"))

    def test_ordinary_code_is_not_a_secret(self):
        for text in (
            "def add(a, b):\n    return a + b\n",
            "for i in range(10):\n    print(i)\n",
            "max_tokens = 4096",
            "password_field = document.getElementById('pw')",
            "const token = await getToken();",
            "SELECT id, name FROM users WHERE active = 1;",
        ):
            with self.subTest(text=text):
                self.assertEqual(sp.inspect_ocr_text(text), (False, "pass"))

    def test_real_looking_assignments_are_still_caught(self):
        for text in (
            "DB_PASSWORD=hunter2xyz9",
            "password = 'correcthorsebattery'",
            '"password": "hunter2xyz9"',
            "api_key: Zx81Qw99Lp20",
            "SECRET_TOKEN=Abcd1234Efgh",
        ):
            with self.subTest(text=text):
                self.assertEqual(sp.inspect_ocr_text(text), (True, "drop_image"))


class SecretRuleRegressionTest(unittest.TestCase):
    def test_github_fine_grained_pat_is_caught(self):
        token = fake("github_pat_", "11ABCDEFG0", "_", "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJ")
        self.assertEqual(sp.inspect_ocr_text("token " + token), (True, "drop_image"))
        self.assertIn("GitHub Fine-grained PAT", sp.scan_secrets(token))
        self.assertEqual(sp.redact_text(token), "[GitHub金鑰]")

    def test_anthropic_key_has_its_own_label(self):
        key = fake("sk-ant-", "api03-", "abcdefghijklmnopqrstuvwxyz0123456789ABCD")
        self.assertEqual(sp.scan_secrets(key), ["Anthropic API Key"])
        self.assertEqual(sp.redact_text("key=" + key), "key=[Anthropic金鑰]")

    def test_openai_key_keeps_openai_label(self):
        key = fake("sk-proj-", "abc1234567890abcdef1234567890abcdef12")
        self.assertEqual(sp.scan_secrets(key), ["OpenAI API Key"])
        self.assertEqual(sp.redact_text(key), "[OpenAI金鑰]")

    def test_anthropic_rule_precedes_openai_rule(self):
        labels = [label for label, _p, _r in sp.SECRET_RULES]
        self.assertLess(labels.index("Anthropic API Key"), labels.index("OpenAI API Key"))

    def test_connection_string_with_s_or_backslash_in_credentials(self):
        # 舊版 [^\\s:@/] 在原始字串裡等於「排除反斜線與字母 s」，帳號或密碼含 s 就漏抓
        for url in (
            "https://sam:p4ssw0rd@example.com/db",
            "postgres://admin:secret@db.internal:5432/app",
            "smb://CORP\\bob:pw123@fileserver/share",
        ):
            with self.subTest(url=url):
                self.assertEqual(sp.inspect_ocr_text("connect " + url), (True, "drop_image"))
                self.assertIn("://[連線字串]", sp.redact_text(url))
                self.assertNotIn("@", sp.redact_text(url))

    def test_bearer_class_does_not_swallow_backslash(self):
        out = sp.redact_text("Authorization: Bearer abcdefghijklmnop1234\\next-line")
        self.assertEqual(out, "Authorization: Bearer [遮蔽]\\next-line")

    def test_pii_patterns_use_plain_pipe_not_markdown_escape(self):
        for _label, pattern, _repl in sp.PII_RULES + sp.SECRET_RULES:
            self.assertNotIn("\\|", pattern, pattern)
        self.assertEqual(sp.redact_text("psql postgresql://user@host/db"), "psql postgresql://[連線字串]")
        self.assertEqual(sp.redact_text("tool --password hunter2 --x"), "tool --password [遮蔽] --x")
        self.assertEqual(sp.redact_text("tool --api-key=abc123"), "tool --api-key=[遮蔽]")


class OcrSpecTest(unittest.TestCase):
    """規範第 7 節的 OCR 案例。"""

    def test_secrets_are_dropped(self):
        secrets = [
            "DB_PASSWORD=hunter2xyz9",
            fake("sk-proj-", "abc1234567890abcdef1234567890abcdef12"),
            fake("ghp_", "123456789012345678901234567890123456"),
            fake("AKIA", "IOSFODNN7EXAMPLE"),
            "https://bob:s3cr3t@example.com/db",
            fake("npm_", "abcdefghijklmnopqrstuvwxyz0123456789"),
            fake("glpat-", "abcdefghijklmnopqrstuvwxyz"),
        ]
        for secret in secrets:
            with self.subTest(secret=secret[:12]):
                is_sensitive, action = sp.inspect_ocr_text(secret)
                self.assertTrue(is_sensitive)
                self.assertEqual(action, "drop_image")

    def test_normal_code_is_not_flagged(self):
        for code in (
            "const token = await getToken();",
            "apiKey = config.apiKey",
            "password: string",
            "tokenizer = AutoTokenizer.from_pretrained(name)",
            'token: "${TOKEN}"',
        ):
            with self.subTest(code=code):
                is_sensitive, _ = sp.inspect_ocr_text(code)
                self.assertFalse(is_sensitive)

    def test_other_token_formats(self):
        cases = {
            "Google Cloud Key": fake("AIza", "SyA1234567890abcdefghijklmnopqrstuv"),
            "Slack Token": fake("xoxb-", "1234567890-abcdefghij"),
            "Supabase Secret": fake("sbp_", "abcdefghijklmnopqrstuv"),
            "Resend API Key": fake("re_", "abcdEFGH12", "_", "abcdefghijklmnop1234"),
            "Hugging Face Token": fake("hf_", "a" * 34),
            "SendGrid API Key": fake("SG.", "a" * 20, ".", "b" * 20),
            "Webhook Secret": fake("whsec_", "a" * 28),
            "Discord Token": fake("M", "A" * 24, ".", "abcdef", ".", "b" * 27),
            "Telegram Bot Token": fake("123456789", ":", "A" * 35),
            "JSON Web Token (JWT)": fake("eyJ", "hbGciOiJI", ".", "eyJzdWIiOiIx", ".", "abcd1234"),
            "Bearer 授權標頭": fake("Bearer ", "abcdefghijklmnopqrstuvwxyz"),
        }
        for label, text in cases.items():
            with self.subTest(label=label):
                self.assertIn(label, sp.scan_secrets(text))
                self.assertEqual(sp.inspect_ocr_text(text), (True, "drop_image"))

    def test_keyword_threshold(self):
        self.assertEqual(sp.inspect_ocr_text("診斷證明已出"), (False, "pass"))  # 只有 1 個
        self.assertEqual(sp.inspect_ocr_text("診斷 與 處方 與 掛號"), (True, "drop_image"))
        self.assertEqual(sp.inspect_ocr_text("診斷 診斷 診斷"), (False, "pass"))  # 重複不算獨立命中

    def test_empty_text(self):
        self.assertEqual(sp.inspect_ocr_text(""), (False, "pass"))
        self.assertEqual(sp.inspect_ocr_text(None), (False, "pass"))
        self.assertEqual(sp.redact_text(""), "")


class RedactTextTest(unittest.TestCase):
    def test_pii(self):
        self.assertEqual(sp.redact_text("ID A123456789 ok"), "ID [身分證] ok")
        self.assertEqual(sp.redact_text("card 4111 1111 1111 1111."), "card [卡號].")
        self.assertEqual(sp.redact_text("call 0912-345-678 now"), "call [手機] now")
        self.assertEqual(sp.redact_text("mail bob.smith+x@example.co.uk!"), "mail [email]!")

    def test_id_and_card_numbers_drop_the_whole_image(self):
        # 截圖會帶著號碼送出去，只遮 OCR 文字沒有用
        for text in ("身分證 A123456789", "居留證 A812345678", "card 4111 1111 1111 1111"):
            with self.subTest(text=text):
                self.assertEqual(sp.inspect_ocr_text(text), (True, sp.ACTION_DROP))
        self.assertEqual(sp.inspect_ocr_text("聯絡 0912-345-678"), (False, sp.ACTION_PASS))  # 手機只遮不丟

    def test_pii_non_matches(self):
        self.assertEqual(sp.redact_text("order 12345678901234567"), "order 12345678901234567")
        self.assertEqual(sp.redact_text("version 1.2.3"), "version 1.2.3")

    def test_redact_masks_secrets_too(self):
        out = sp.redact_text(fake("key ", "AKIA", "IOSFODNN7EXAMPLE", " mail a@b.com"))
        self.assertEqual(out, "key [AWS金鑰] mail [email]")

    def test_redact_is_idempotent(self):
        text = "https://bob:s3cr3t@example.com/db a@b.com --token xyz"
        once = sp.redact_text(text)
        self.assertEqual(sp.redact_text(once), once)


class ReDoSTest(unittest.TestCase):
    def test_adversarial_inputs_finish_within_one_second(self):
        n = 40000
        samples = {
            "at-sign": "a" * n + "@",
            "keyword-repeat": "password" * (n // 8),
            "keyword-then-long-value": "password=" + "a" * n + "{",
            "unterminated-quote": 'password="' + "a" * n,
            "quote-repeat": "password='" * (n // 10),
            "jwt-prefix": "eyJ" + "a" * n,
            "sk-repeat": "sk-" * (n // 3),
            "bearer-spaces": "Bearer " + " " * n,
            "scheme-repeat": "http://" * (n // 7),
            "colon-repeat": "a:" * (n // 2),
            "card-repeat": "1234 " * (n // 5),
            "cli-param-repeat": "--password " * (n // 11),
            "digits": "0" * n,
            "keyword-then-spaces": "password" + " " * n + "x",
            "dotted-local": "a." * (n // 2) + "@",
            "dotted-domain": "a@" + "a." * (n // 2),
            "db-scheme-repeat": "postgres://" * (n // 11),
            "sendgrid-repeat": "SG." * (n // 3),
            "discord-prefix": "M" + "a" * n,
        }
        for name, text in samples.items():
            with self.subTest(name=name):
                start = time.perf_counter()
                sp.redact_text(text)
                sp.inspect_ocr_text(text)
                elapsed = time.perf_counter() - start
                self.assertLess(elapsed, 1.0, f"{name} 耗時 {elapsed:.2f}s，疑似 ReDoS")

    def test_long_title_classification_is_fast(self):
        for title in ("a " * 50000, "(1) " * 20000, "\u200b" * 100000):
            start = time.perf_counter()
            sp.classify_window("chrome.exe", title)
            self.assertLess(time.perf_counter() - start, 1.0)


class SpecDocConsistencyTest(unittest.TestCase):
    """文件只是正本的鏡像：每條正則都要能在文件找到（表格內 `|` 寫成 `\\|`）。"""

    @classmethod
    def setUpClass(cls):
        cls.doc = SPEC.read_text(encoding="utf-8")

    def test_secret_and_pii_patterns_appear_in_doc(self):
        for label, pattern, _repl in sp.SECRET_RULES + sp.PII_RULES:
            with self.subTest(label=label):
                self.assertIn(pattern.replace("|", "\\|"), self.doc)

    def test_title_patterns_appear_in_doc(self):
        for pattern in (
            sp.TITLE_MEDICAL, sp.TITLE_PRIVATE_BROWSING, sp.TITLE_PASSWORD_MANAGER, sp.TITLE_BANKING,
            sp.TITLE_ADULT, sp.TITLE_SECRET_FILE_ANYWHERE, sp.TITLE_SECRET_FILE_AT_END,
        ):
            with self.subTest(pattern=pattern[:30]):
                self.assertIn(pattern, self.doc)

    def test_doc_points_to_reference_implementation_and_tests(self):
        self.assertIn("tools/screen_privacy.py", self.doc)
        self.assertIn("tests/test_screen_privacy.py", self.doc)

    def test_doc_has_no_unrunnable_inline_test_matrix(self):
        self.assertNotIn("class TestScreenPrivacySpecification", self.doc)


class ReviewFindingRegressionTest(unittest.TestCase):
    """2026-10-26 覆核審查找到的漏抓與誤判，每一項都要維持修正。"""

    def assertDropped(self, text):
        self.assertEqual(sp.inspect_ocr_text(text), (True, sp.ACTION_DROP), text)

    def test_private_key_blocks(self):
        for kind in ("OPENSSH ", "RSA ", "EC ", ""):
            self.assertDropped(fake("-----BEGIN ", kind, "PRIVATE KEY-----\nMIIEvQ..."))

    def test_stripe_keys(self):
        self.assertDropped("key " + fake("sk_", "live_", "4eC39HqLyjWDarjtT1zdp7dc"))
        self.assertDropped("key " + fake("rk_", "test_", "4eC39HqLyjWDarjtT1zdp7dc"))

    def test_secrets_glued_to_chinese_text(self):
        # OCR 常把空白吃掉；Python 的 \b 把中文字也當成字元，緊貼中文時 \b 不成立
        self.assertDropped("金鑰" + fake("sk-ant-", "api03-", "a" * 40))
        self.assertDropped("權杖" + fake("ghp_", "A" * 36))
        self.assertDropped("金鑰" + fake("AKIA", "IOSFODNN7EXAMPLE"))
        self.assertDropped("身分證A123456789號")

    def test_slack_app_token_and_chinese_password_label(self):
        self.assertDropped(fake("xapp-", "1-A0123456789-0123456789-abcdef"))
        self.assertDropped("密碼：Hunter2!xyz9")

    def test_card_numbers_need_luhn(self):
        self.assertDropped("card 4111111111111111")           # 無分隔
        self.assertDropped("amex 3782 822463 10005")           # Amex 4-6-5
        self.assertEqual(sp.inspect_ocr_text("order id 1234-5678-9012-3456"), (False, sp.ACTION_PASS))
        self.assertEqual(sp.redact_text("order id 1234-5678-9012-3456"), "order id 1234-5678-9012-3456")
        self.assertEqual(sp.redact_text("card 4111-1111-1111-1111."), "card [卡號].")

    def test_card_followed_by_expiry_or_cvv_is_still_caught(self):
        # 候選正則是貪婪的：卡號後面接「空白＋數字」（有效期限、安全碼）會被一起吞進去，
        # 整串 18～19 位多半不過 Luhn，真正的卡號就漏掉、截圖照送出去。
        cases = {
            "卡號 4111 1111 1111 1111 12/25": "卡號 [卡號] 12/25",
            "4111111111111111 123": "[卡號] 123",
            "4111-1111-1111-1111 12 25": "[卡號] 12 25",
            "Amex 3782 822463 10005 123": "Amex [卡號] 123",
        }
        for text, redacted in cases.items():
            with self.subTest(text=text):
                self.assertDropped(text)
                self.assertEqual(sp.redact_text(text), redacted)

    def test_short_tail_never_changes_the_verdict_of_a_non_card_number(self):
        # 性質：16 位不過 Luhn 的編號後面接一小段數字，判定必須等同「把整串當一個號碼做 Luhn」。
        # 修正卡號被尾巴吃掉的漏報時不能放大誤報（舊版取任意連續片段，誤報約變三倍）。
        import random

        rng = random.Random(20261026)
        checked = 0
        while checked < 400:
            number = "".join(rng.choice("0123456789") for _ in range(16))
            if sp._luhn_ok(number):
                continue
            tail = "".join(rng.choice("0123456789") for _ in range(rng.randint(1, 3)))
            sep = rng.choice([" ", "-"])
            text = "id " + sep.join(number[i:i + 4] for i in range(0, 16, 4)) + " " + tail
            whole = number + tail
            expected = len(whole) in sp._CARD_LENGTHS and sp._luhn_ok(whole)
            with self.subTest(text=text):
                self.assertEqual(sp.inspect_ocr_text(text)[0], expected)
                if not expected:
                    self.assertEqual(sp.redact_text(text), text)
            checked += 1

    def test_card_is_never_cut_out_of_the_middle_of_a_longer_number(self):
        # 從第二組中間切出去的片段不是卡號：候選只從第一組起算、只切尾巴
        text = "order id 1234-5678-9012-3456 18"
        self.assertFalse(sp.inspect_ocr_text(text)[0])


    def test_digit_runs_beside_a_non_card_number_stay_untouched(self):
        # 修正後仍以數字群組為界、且要過 Luhn：訂單編號後面再接數字不能被誤判成卡號
        text = "order id 1234-5678-9012-3456 12"
        self.assertEqual(sp.inspect_ocr_text(text), (False, sp.ACTION_PASS))
        self.assertEqual(sp.redact_text(text), text)


class CliTest(unittest.TestCase):
    def test_drop_reason_names_the_pii_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ocr.txt"
            path.write_text("身分證：A123456789\n", encoding="utf-8")
            code, out, _ = self.run_cli("--ocr-file", str(path))
        self.assertIn("action: drop_image", out)
        self.assertIn("台灣身分證字號", out)
        self.assertNotIn("敏感關鍵字達門檻", out)
        self.assertNotIn("A123456789", out)

    def run_cli(self, *args):
        env = {**os.environ, "PYTHONIOENCODING": "cp950", "PYTHONUTF8": "0"}
        proc = subprocess.run(
            [sys.executable, str(TOOL), *args], capture_output=True, env=env, timeout=60
        )
        return proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8", "replace")

    def test_title_classification(self):
        code, out, _ = self.run_cli("--title", "病歷系統 - Google Chrome", "--app", "chrome.exe")
        self.assertEqual((code, out.strip()), (0, "classification: blocked"))
        code, out, _ = self.run_cli("--title", "Mayo Clinic - Chrome", "--app", "chrome.exe")
        self.assertEqual(out.strip(), "classification: ok")

    def test_ocr_file_with_secret_is_dropped_without_echoing_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ocr.txt"
            path.write_text("deploy with " + fake("AKIA", "IOSFODNN7EXAMPLE") + "\n", encoding="utf-8")
            code, out, _ = self.run_cli("--ocr-file", str(path))
        self.assertEqual(code, 0)
        self.assertIn("action: drop_image", out)
        self.assertIn("AWS Access Key", out)
        self.assertNotIn("IOSFODNN7EXAMPLE", out)

    def test_ocr_file_clean_text_is_redacted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ocr.txt"
            path.write_text("聯絡 bob@example.com 手機 0912345678\n", encoding="utf-8")
            code, out, _ = self.run_cli("--ocr-file", str(path))
        self.assertEqual(code, 0)
        self.assertIn("action: pass", out)
        self.assertIn("[email]", out)
        self.assertIn("[手機]", out)
        self.assertNotIn("bob@example.com", out)

    def test_missing_ocr_file_and_missing_arguments(self):
        code, _, err = self.run_cli("--ocr-file", str(ROOT / "no-such-file.txt"))
        self.assertEqual(code, 2)
        code, _, err = self.run_cli()
        self.assertNotEqual(code, 0)
        self.assertIn("--title", err)

    def test_help_is_utf8_under_cp950(self):
        code, out, _ = self.run_cli("--help")
        self.assertEqual(code, 0)
        self.assertIn("usage", out)
        self.assertIn("--ocr-file", out)


if __name__ == "__main__":
    unittest.main()
