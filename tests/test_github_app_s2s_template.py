"""templates/github-app-s2s-agent-workflow.md 內嵌的腳本與工作流實測。

測試從範本的程式碼區塊現場取出腳本與 YAML，實際執行：
- Python 腳本：用現場產生的假 RSA 金鑰簽 JWT，對本機模擬伺服器換 token（伺服器用公鑰驗簽，所以簽章錯誤會失敗）。
- 爆破半徑關卡（工作流內的 bash 片段）：有 bash 與 git 才跑，否則明確 skipTest。
- 工作流 YAML：沒有 YAML 解析器可用，只做結構檢查（釘 SHA、run 區塊不含 ${{ }}、最小 permissions），
  並附反例證明檢查函式抓得到壞輸入。
不連真的 GitHub、不含任何真實金鑰；假金鑰的 PEM 標頭在執行時才組字串。
"""
import base64
import hashlib
import http.server
import importlib.util
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "github-app-s2s-agent-workflow.md"
FENCE = re.compile(r"^```(\w+) (\S+)\n(.*?)^```$", re.S | re.M)
# RFC 8017 的 SHA-256 DigestInfo 前綴；測試自己持有一份，不從被測腳本匯入
SHA256_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")


def template_blocks():
    text = TEMPLATE.read_text(encoding="utf-8")
    return {name: body for _lang, name, body in FENCE.findall(text)}


# ---------- 假金鑰：純 Python 產生，不依賴 openssl ----------

def _is_prime(n):
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _gen_prime(bits):
    while True:
        c = secrets.randbits(bits) | (1 << (bits - 1)) | (1 << (bits - 2)) | 1
        if _is_prime(c):
            return c


def _der_len(n):
    if n < 0x80:
        return bytes([n])
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(raw)]) + raw


def _der(tag, body):
    return bytes([tag]) + _der_len(len(body)) + body


def _der_int(v):
    raw = v.to_bytes(max(1, (v.bit_length() + 8) // 8), "big")
    return _der(0x02, raw)


def _pem(label, der):
    b64 = base64.b64encode(der).decode()
    lines = "\n".join(b64[i:i + 64] for i in range(0, len(b64), 64))
    return "-----BEGIN " + label + "-----\n" + lines + "\n-----END " + label + "-----\n"


class FakeKey:
    def __init__(self, bits):
        while True:
            p, q = _gen_prime(bits // 2), _gen_prime(bits // 2)
            e = 65537
            phi = (p - 1) * (q - 1)
            if p != q and phi % e != 0 and (p * q).bit_length() == bits:
                break
        self.n, self.e, self.p, self.q = p * q, e, p, q
        self.d = pow(e, -1, phi)
        ints = [0, self.n, e, self.d, p, q, self.d % (p - 1), self.d % (q - 1), pow(q, -1, p)]
        self.pkcs1_der = _der(0x30, b"".join(_der_int(i) for i in ints))
        rsa_alg = _der(0x30, _der(0x06, bytes.fromhex("2a864886f70d010101")) + b"\x05\x00")
        self.pkcs8_der = _der(0x30, _der_int(0) + rsa_alg + _der(0x04, self.pkcs1_der))

    @property
    def pkcs1_pem(self):
        return _pem("RSA PRIVATE KEY", self.pkcs1_der)

    @property
    def pkcs8_pem(self):
        return _pem("PRIVATE KEY", self.pkcs8_der)


@lru_cache(maxsize=None)
def fake_key(bits=2048, which=0):
    return FakeKey(bits)


def verify_rs256(jwt, key):
    """用公鑰獨立驗證 JWT；回傳 (header, payload)，驗不過就丟 AssertionError。"""
    head, payload, sig = jwt.split(".")
    pad = lambda s: s + "=" * (-len(s) % 4)
    signature = base64.urlsafe_b64decode(pad(sig))
    k = (key.n.bit_length() + 7) // 8
    assert len(signature) == k, "簽章長度不等於金鑰長度"
    em = pow(int.from_bytes(signature, "big"), key.e, key.n).to_bytes(k, "big")
    t = SHA256_PREFIX + hashlib.sha256((head + "." + payload).encode()).digest()
    expected = b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
    assert em == expected, "RS256 簽章驗證失敗"
    return (json.loads(base64.urlsafe_b64decode(pad(head))),
            json.loads(base64.urlsafe_b64decode(pad(payload))))


# ---------- 模擬 GitHub API ----------

class MockGitHub:
    """本機模擬伺服器：用公鑰驗 JWT，驗不過回 401，所以簽章錯誤的腳本拿不到 token。"""

    def __init__(self, key, mode="ok"):
        self.key, self.mode = key, mode
        self.token = "ghs_" + secrets.token_hex(20)
        self.requests = []
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _reply(self, code, obj):
                raw = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def _handle(self, method):
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(length) or b"{}") if length else {}
                auth = self.headers.get("Authorization", "")
                try:
                    assert auth.startswith("Bearer ")
                    header, claims = verify_rs256(auth[7:], outer.key)
                    assert header == {"alg": "RS256", "typ": "JWT"}
                except Exception:
                    return self._reply(401, {"message": "Bad credentials"})
                outer.requests.append((method, self.path, {k.lower(): v for k, v in self.headers.items()}, body, claims))
                if method == "GET" and self.path == "/orgs/acme/installation":
                    return self._reply(200, {"id": 4242})
                if method == "POST" and re.fullmatch(r"/app/installations/\d+/access_tokens", self.path):
                    if outer.mode == "no-token":
                        return self._reply(201, {"expires_at": "2099-01-01T00:00:00Z"})
                    if outer.mode == "pat-token":
                        return self._reply(201, {"token": "ghp_" + "a" * 36, "expires_at": "x"})
                    perms = dict(body.get("permissions", {}))
                    if outer.mode == "wrong-perms":
                        perms = {"administration": "write"}
                    perms.setdefault("metadata", "read")
                    return self._reply(201, {"token": outer.token, "expires_at": "2099-01-01T00:00:00Z",
                                             "permissions": perms})
                return self._reply(404, {"message": "Not Found"})

            def do_GET(self):
                self._handle("GET")

            def do_POST(self):
                self._handle("POST")

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = "http://127.0.0.1:%d" % self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


# ---------- 共用 ----------

def clean_env(**extra):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("GH_", "GITHUB_", "PERMISSIONS_", "DRY_RUN"))}
    env.update(extra)
    return env


def find_bash():
    if sys.platform == "win32":
        git = shutil.which("git")
        if git:
            for root in Path(git).resolve().parents[:3]:  # cmd\git.exe 或 mingw64\bin\git.exe 往上找 Git 安裝根目錄
                for rel in ("bin/bash.exe", "usr/bin/bash.exe"):
                    if (root / rel).exists():
                        return str(root / rel)
        return None
    return shutil.which("bash")


def load_module(path):
    spec = importlib.util.spec_from_file_location("app_installation_token_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TemplateCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blocks = template_blocks()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.py_path = Path(cls.tmp.name) / "app_installation_token.py"
        cls.py_path.write_text(cls.blocks["app_installation_token.py"], encoding="utf-8")

    def run_py(self, args=(), env=None, timeout=60):
        return subprocess.run([sys.executable, str(self.py_path), *args], env=env or clean_env(),
                              capture_output=True, text=True, encoding="utf-8", timeout=timeout)


class TemplateStructureTests(TemplateCase):
    def test_required_blocks_and_frontmatter(self):
        self.assertEqual(set(self.blocks), {"app_installation_token.py", "nightly-maintenance-agent.yml"})
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: github-app-s2s-agent-workflow\ndescription: "))
        self.assertIn("\n---\n", text[4:])

    def test_template_has_no_real_secret_shapes(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", text))
        self.assertIsNone(re.search(r"\bgh[pousr]_[A-Za-z0-9]{20,}", text))


class PythonScriptTests(TemplateCase):
    def good_env(self, key=None, **extra):
        key = key or fake_key(2048)
        values = {"GH_APP_CLIENT_ID": "Iv1.fakeclientid0000", "GH_APP_PRIVATE_KEY": key.pkcs1_pem}
        values.update(extra)
        return clean_env(**values)

    def test_jwt_signature_verifies_with_public_key_for_both_pem_formats(self):
        mod = load_module(self.py_path)
        key = fake_key(2048)
        for pem in (key.pkcs1_pem, key.pkcs8_pem):
            n, e, d = mod.load_rsa_private_key(pem)
            self.assertEqual((n, e, d), (key.n, key.e, key.d))
            jwt = mod.build_jwt("Iv1.fakeclientid0000", n, d, now=1_800_000_000)
            header, claims = verify_rs256(jwt, key)
            self.assertEqual(header, {"alg": "RS256", "typ": "JWT"})
            self.assertEqual(claims, {"iat": 1_800_000_000 - 60, "exp": 1_800_000_000 + 540,
                                      "iss": "Iv1.fakeclientid0000"})
            self.assertLessEqual(claims["exp"] - 1_800_000_000, 600)  # 官方：不得超過 10 分鐘

    def test_signature_is_rejected_by_a_different_public_key(self):
        mod = load_module(self.py_path)
        key, other = fake_key(2048), fake_key(2048, 1)
        jwt = mod.build_jwt("Iv1.fakeclientid0000", key.n, key.d, now=1_800_000_000)
        with self.assertRaises(AssertionError):
            verify_rs256(jwt, other)

    @unittest.skipUnless(shutil.which("openssl"), "沒有 openssl，跳過與 openssl 簽章逐位元比對")
    def test_signature_is_byte_identical_to_openssl(self):
        mod = load_module(self.py_path)
        with tempfile.TemporaryDirectory() as tmp:
            keyfile = Path(tmp) / "k.pem"
            generated = subprocess.run(["openssl", "genrsa", "2048"], capture_output=True, text=True, check=True).stdout
            keyfile.write_text(generated, encoding="ascii")
            pkcs1 = subprocess.run(["openssl", "rsa", "-traditional", "-in", str(keyfile)],
                                   capture_output=True, text=True, check=True).stdout
            pkcs8 = subprocess.run(["openssl", "pkcs8", "-topk8", "-nocrypt", "-in", str(keyfile)],
                                   capture_output=True, text=True, check=True).stdout
            message = b"header.payload"
            expected = subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(keyfile)],
                                      input=message, capture_output=True, check=True).stdout
            for pem in (generated, pkcs1, pkcs8):
                n, e, d = mod.load_rsa_private_key(pem)
                self.assertEqual(mod.rs256_sign(message, n, d), expected)

    def test_dry_run_signs_jwt_without_leaking_key_or_signature(self):
        key = fake_key(2048)
        result = self.run_py(["--dry-run"], self.good_env(key))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["key_bits"], 2048)
        self.assertEqual(report["claims"]["iss"], "Iv1.fakeclientid0000")
        self.assertEqual(report["claims"]["exp"] - report["claims"]["iat"], 600)
        body = "".join(key.pkcs1_pem.splitlines()[1:-1])
        for stream in (result.stdout, result.stderr):
            self.assertNotIn(body[:40], stream)
            self.assertNotIn("PRIVATE KEY", stream)

    def test_escaped_newline_key_is_accepted(self):
        key = fake_key(2048)
        env = self.good_env(key)
        env["GH_APP_PRIVATE_KEY"] = key.pkcs1_pem.strip().replace("\n", "\\n")
        self.assertEqual(self.run_py(["--dry-run"], env).returncode, 0)

    def test_bad_inputs_fail_with_exit_2_and_never_echo_the_key(self):
        key = fake_key(2048)
        lines = key.pkcs1_pem.splitlines()
        body = "".join(lines[1:-1])
        d_flipped = bytearray(key.pkcs1_der)
        idx = d_flipped.find(key.d.to_bytes((key.d.bit_length() + 7) // 8, "big")) + 10
        d_flipped[idx] ^= 0x01
        cases = {
            "空字串": "",
            "不是 PEM": "hello world",
            "截斷的金鑰": "\n".join(lines[:len(lines) // 2] + [lines[-1]]),
            "base64 損壞": lines[0] + "\n!!!!\n" + lines[-1],
            "完整金鑰中混入非法字元": "\n".join(lines[:-2] + [lines[-2] + "!!", lines[-1]]),
            "1024 位元金鑰": fake_key(1024).pkcs1_pem,
            "加密金鑰標頭": _pem("ENCRYPTED PRIVATE KEY", key.pkcs8_der),
            "EC 金鑰標頭": _pem("EC PRIVATE KEY", key.pkcs1_der),
            "d 被改壞": _pem("RSA PRIVATE KEY", bytes(d_flipped)),
            "只有公鑰內容": _pem("PUBLIC KEY", key.pkcs1_der),
        }
        for name, pem in cases.items():
            with self.subTest(name):
                env = self.good_env()
                env["GH_APP_PRIVATE_KEY"] = pem
                result = self.run_py(["--dry-run"], env)
                self.assertEqual(result.returncode, 2, (result.stdout, result.stderr))
                self.assertNotIn(body[:40], result.stderr + result.stdout)
        for client_id in ("", "has space", "a" * 80, 'x"y'):
            with self.subTest(client_id=client_id):
                result = self.run_py(["--dry-run"], self.good_env(GH_APP_CLIENT_ID=client_id))
                self.assertEqual(result.returncode, 2, result.stderr)

    def test_permissions_guard(self):
        mod = load_module(self.py_path)
        self.assertEqual(mod.parse_permissions('{"organization_copilot_requests":"read"}'),
                         {"organization_copilot_requests": "read"})
        self.assertEqual(mod.parse_permissions(""), {})
        self.assertEqual(mod.parse_permissions('{"administration":"read"}'), {"administration": "read"})
        for bad in ('{"administration":"write"}', '{"members":"write"}', '{"workflows":"write"}',
                    '{"contents":"admin"}', '{"contents":true}', "not json", "[]"):
            with self.subTest(bad), self.assertRaises(mod.InputError):
                mod.parse_permissions(bad)

    def test_non_https_api_url_is_rejected_before_any_network_call(self):
        for url in ("http://example.com", "ftp://example.com", "api.github.com"):
            with self.subTest(url):
                result = self.run_py(["--installation-id", "1", "--api-url", url], self.good_env())
                self.assertEqual(result.returncode, 2, result.stderr)

    def test_missing_installation_id_fails(self):
        result = self.run_py(["--api-url", "http://127.0.0.1:9"], self.good_env())
        self.assertEqual(result.returncode, 2)

    def test_exchange_against_mock_server_returns_token_only_on_stdout(self):
        key = fake_key(2048)
        with MockGitHub(key) as server:
            result = self.run_py(["--installation-id", "123", "--api-url", server.url,
                                  "--permissions", '{"organization_copilot_requests":"read"}',
                                  "--repositories", "repo-a, repo-b"], self.good_env(key))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, server.token + "\n")
        self.assertNotIn(server.token, result.stderr)
        method, path, headers, body, claims = server.requests[-1]
        self.assertEqual((method, path), ("POST", "/app/installations/123/access_tokens"))
        self.assertEqual(headers["x-github-api-version"], "2026-03-10")
        self.assertEqual(body, {"permissions": {"organization_copilot_requests": "read"},
                                "repositories": ["repo-a", "repo-b"]})

    def test_org_lookup_resolves_installation_id(self):
        key = fake_key(2048)
        with MockGitHub(key) as server:
            result = self.run_py(["--org", "acme", "--api-url", server.url], self.good_env(key))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([r[:2] for r in server.requests],
                         [("GET", "/orgs/acme/installation"), ("POST", "/app/installations/4242/access_tokens")])

    def test_github_output_masks_before_writing_and_keeps_token_off_stderr(self):
        key = fake_key(2048)
        with tempfile.TemporaryDirectory() as tmp, MockGitHub(key) as server:
            out = Path(tmp) / "github_output"
            result = self.run_py(["--installation-id", "1", "--api-url", server.url, "--github-output", "tok"],
                                 self.good_env(key, GITHUB_OUTPUT=str(out)))
            written = out.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "::add-mask::" + server.token + "\n")
        self.assertEqual(written, "tok=" + server.token + "\n")
        self.assertNotIn(server.token, result.stderr)

    def test_github_output_without_actions_env_fails(self):
        key = fake_key(2048)
        with MockGitHub(key) as server:
            result = self.run_py(["--installation-id", "1", "--api-url", server.url, "--github-output", "tok"],
                                 self.good_env(key))
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(server.token, result.stdout + result.stderr)

    def test_signing_with_the_wrong_key_gets_401_and_exit_3(self):
        with MockGitHub(fake_key(2048)) as server:
            result = self.run_py(["--installation-id", "1", "--api-url", server.url],
                                 self.good_env(fake_key(2048, 1)))
        self.assertEqual(result.returncode, 3)
        self.assertIn("HTTP 401", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_bad_server_responses_fail_with_exit_4_and_no_token_output(self):
        key = fake_key(2048)
        for mode, extra in (("no-token", []), ("pat-token", []), ("wrong-perms",
                            ["--permissions", '{"organization_copilot_requests":"read"}'])):
            with self.subTest(mode), MockGitHub(key, mode) as server:
                result = self.run_py(["--installation-id", "1", "--api-url", server.url, *extra], self.good_env(key))
            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertEqual(result.stdout, "")

    def test_connection_refused_exits_3(self):
        result = self.run_py(["--installation-id", "1", "--api-url", "http://127.0.0.1:9"], self.good_env())
        self.assertEqual(result.returncode, 3)

    def test_refuses_to_print_token_to_a_terminal(self):
        mod = load_module(self.py_path)

        class FakeTty:
            def isatty(self):
                return True

            def write(self, _):
                raise AssertionError("token 被寫到終端機")

        real, mod.sys.stdout = mod.sys.stdout, FakeTty()
        try:
            with self.assertRaises(mod.InputError):
                mod.emit("ghs_" + "x" * 30, None)
        finally:
            mod.sys.stdout = real


# ---------- 工作流 YAML ----------

def split_steps(yml):
    return re.split(r"(?m)^(?=      - name: )", yml)[1:]


def step_name(step):
    return re.match(r"      - name: (.*)", step).group(1).strip()


def run_script(step):
    lines = step.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^        run: \|\s*$", line):
            block = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt.startswith("          "):
                    break
                block.append(nxt[10:])
            return "\n".join(block) + "\n"
    return None


def step_env(step):
    env, inside = {}, False
    for line in step.splitlines():
        if re.match(r"^        env:\s*$", line):
            inside = True
            continue
        if inside:
            m = re.match(r"^          ([A-Z_]+): (.*)$", line)
            if not m:
                if line.strip() and not line.startswith("          "):
                    inside = False
                continue
            value = m.group(2).strip()
            if value[:1] in "\"'" and value[-1:] == value[:1]:
                value = value[1:-1]
            env[m.group(1)] = value
    return env


def unpinned_actions(yml):
    bad = []
    for m in re.finditer(r"(?m)^\s*(?:-\s*)?uses:\s*(\S+)(.*)$", yml):
        ref, rest = m.group(1), m.group(2)
        if not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", ref) or not re.search(r"#\s*v\d", rest):
            bad.append(ref)
    return bad


def expressions_in_run_blocks(yml):
    found = []
    for step in split_steps(yml):
        script = run_script(step)
        if script and "${{" in script:
            found.append(step_name(step))
    return found


class WorkflowTests(TemplateCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.yml = cls.blocks["nightly-maintenance-agent.yml"]
        cls.steps = {step_name(s): s for s in split_steps(cls.yml)}

    def test_all_actions_are_pinned_to_full_sha_with_version_comment(self):
        self.assertEqual(unpinned_actions(self.yml), [])
        self.assertEqual(len(re.findall(r"uses:", self.yml)), 2)

    def test_pin_checker_catches_bad_inputs(self):
        self.assertEqual(unpinned_actions("      - uses: actions/checkout@v4"), ["actions/checkout@v4"])
        self.assertEqual(unpinned_actions("      - uses: actions/checkout@" + "a" * 39 + " # v1"),
                         ["actions/checkout@" + "a" * 39])
        self.assertEqual(unpinned_actions("      - uses: actions/checkout@" + "a" * 40),
                         ["actions/checkout@" + "a" * 40])

    def test_no_expression_interpolation_inside_run_blocks(self):
        self.assertEqual(expressions_in_run_blocks(self.yml), [])
        evil = self.yml.replace('echo "found=true" >> "$GITHUB_OUTPUT"',
                                'echo "${{ github.event.issue.title }}"', 1)
        self.assertNotEqual(evil, self.yml)
        self.assertEqual(expressions_in_run_blocks(evil), ["Select issue"])

    def test_top_level_permissions_are_minimal_and_no_dangerous_trigger(self):
        top = re.search(r"(?m)^permissions:\n((?:  .*\n)+)", self.yml).group(1)
        self.assertEqual(top.split(), ["contents:", "read", "issues:", "read"])
        self.assertNotIn("pull_request_target", self.yml)
        self.assertNotIn("pull_request:", self.yml)

    def test_checkout_does_not_persist_credentials(self):
        self.assertIn("persist-credentials: false", self.steps["Check out (read-only, no persisted credentials)"])

    def test_agent_step_sees_only_the_copilot_token(self):
        agent = self.steps["Run agent (Copilot token only; no repo write credentials here)"]
        self.assertIn("INSTALLATION_TOKEN", agent)
        for forbidden in ("APP_PRIVATE_KEY", "repo-token", "GH_TOKEN", "github.token"):
            self.assertNotIn(forbidden, agent)
        keyed = [n for n, s in self.steps.items() if "APP_PRIVATE_KEY" in s]
        self.assertEqual(sorted(keyed), ["Mint Copilot-only installation token", "Mint repo-scoped installation token"])

    def test_placeholder_steps_fail_closed(self):
        for name in ("Run agent (Copilot token only; no repo write credentials here)",
                     "Quality gate (tests / lint / typecheck)"):
            self.assertRegex(run_script(self.steps[name]), r"(?m)^exit 1$", name)

    def test_repo_token_is_least_privilege_and_minted_after_the_gates(self):
        order = list(self.steps)
        self.assertLess(order.index("Blast radius gate"), order.index("Mint repo-scoped installation token"))
        self.assertLess(order.index("Quality gate (tests / lint / typecheck)"),
                        order.index("Mint repo-scoped installation token"))
        mint = self.steps["Mint repo-scoped installation token"]
        grants = re.findall(r"permission-([a-z-]+): (\w+)", mint)
        self.assertEqual(sorted(grants), [("contents", "write"), ("issues", "write"), ("pull-requests", "write")])

    def test_copilot_mint_arguments_pass_the_scripts_own_validation(self):
        mod = load_module(self.py_path)
        script = run_script(self.steps["Mint Copilot-only installation token"])
        raw = re.search(r"--permissions '(\{.*?\})'", script).group(1)
        self.assertEqual(mod.parse_permissions(raw), {"organization_copilot_requests": "read"})
        self.assertIn("--github-output copilot_token", script)
        self.assertIn(".github/scripts/app_installation_token.py", script)

    def test_pr_is_created_as_draft(self):
        self.assertIn("gh pr create --draft", run_script(self.steps["Push branch and open draft PR"]))


@unittest.skipUnless(find_bash() and shutil.which("git"), "需要 bash 與 git 才能實跑爆破半徑關卡")
class BlastRadiusGateTests(TemplateCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        step = {step_name(s): s for s in split_steps(cls.blocks["nightly-maintenance-agent.yml"])}["Blast radius gate"]
        cls.script = run_script(step)
        cls.gate_env = step_env(step)

    def run_gate(self, changes, max_files=None):
        """changes: {相對路徑: 內容}；先建立含一個檔案的 repo，再套用 changes，最後執行關卡腳本。"""
        with tempfile.TemporaryDirectory() as tmp:
            git = lambda *a: subprocess.run(["git", *a], cwd=tmp, check=True, capture_output=True, text=True)
            git("init", "-q")
            git("config", "user.email", "t@example.com")
            git("config", "user.name", "t")
            git("config", "core.autocrlf", "false")
            (Path(tmp) / "keep.txt").write_text("base\n", encoding="utf-8")
            git("add", "-A")
            git("commit", "-q", "-m", "base")
            for rel, content in changes.items():
                target = Path(tmp) / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            env = clean_env(**self.gate_env)
            if max_files is not None:
                env["MAX_FILES"] = str(max_files)
            return subprocess.run([find_bash(), "-c", self.script], cwd=tmp, env=env, capture_output=True,
                                  text=True, encoding="utf-8", timeout=60)

    def test_gate_env_was_parsed(self):
        self.assertEqual(self.gate_env["MAX_FILES"], "10")
        self.assertIn(r"\.github/", self.gate_env["DENY_REGEX"])

    def test_ordinary_changes_pass(self):
        self.assertEqual(self.run_gate({"src/a.py": "x\n"}).returncode, 0)
        self.assertEqual(self.run_gate({"keep.txt": "changed\n", "docs/n.md": "n\n"}).returncode, 0)

    def test_forbidden_paths_fail(self):
        for rel in (".github/workflows/x.yml", ".github/scripts/app_installation_token.py", "Dockerfile",
                    "services/api/Dockerfile", "docker-compose.yml", "deploy/docker-compose.prod.yaml",
                    "infra/main.tf", "prod.tfvars"):
            with self.subTest(rel):
                result = self.run_gate({"src/ok.py": "x\n", rel: "x\n"})
                self.assertEqual(result.returncode, 1, (rel, result.stderr))

    def test_no_changes_fails(self):
        self.assertEqual(self.run_gate({}).returncode, 1)

    def test_too_many_files_fails(self):
        self.assertEqual(self.run_gate({"f%d.txt" % i: "x\n" for i in range(10)}).returncode, 0)
        self.assertEqual(self.run_gate({"f%d.txt" % i: "x\n" for i in range(11)}).returncode, 1)

    def test_lookalike_names_are_not_false_positives(self):
        self.assertEqual(self.run_gate({"src/github_notes.md": "x\n", "docs/Dockerfile.md": "x\n"}).returncode, 0)


if __name__ == "__main__":
    unittest.main()
