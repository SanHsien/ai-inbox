"""templates/github-app-s2s-agent-workflow.md 內嵌的腳本與工作流實測。

測試從範本的程式碼區塊現場取出腳本與 YAML，實際執行：
- Python 腳本：用現場產生的假 RSA 金鑰簽 JWT，對本機模擬伺服器換 token（伺服器用公鑰驗簽，所以簽章錯誤會失敗）。
- 工作流內的 bash 步驟（產生 patch、爆破半徑關卡、停用 hook 的 commit）：在暫存 git repo 實跑，含 Agent 寫 .git/hooks 偷權杖的攻擊重現；沒有 bash 或 git 就明確 skipTest。
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

AGENT_RUN = "Run agent (Copilot token only; no repo write credentials here)"
MINT_COPILOT = "Mint Copilot-only installation token"
MINT_REPO = "Mint repo-scoped installation token"
MAKE_PATCH = "Create patch (worktree changes only)"
GATE = "Apply patch and blast radius gate"
COMMIT = "Commit with hooks disabled"
PUSH = "Push branch and open draft PR"


def split_jobs(yml):
    """回傳 {job 名稱: 該 job 的文字}。只認 jobs: 底下縮排兩格的鍵。"""
    body = yml.split("\njobs:\n", 1)[1]
    parts = re.split(r"(?m)^  ([a-z][\w-]*):\n", body)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


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


def steps_of(yml, job):
    return {step_name(s): s for s in split_steps(split_jobs(yml)[job])}


def step_order(yml, job):
    return [step_name(s) for s in split_steps(split_jobs(yml)[job])]


class WorkflowTests(TemplateCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.yml = cls.blocks["nightly-maintenance-agent.yml"]
        cls.jobs = split_jobs(cls.yml)
        cls.agent = steps_of(cls.yml, "agent")
        cls.publish = steps_of(cls.yml, "publish")

    def test_all_actions_are_pinned_to_full_sha_with_version_comment(self):
        self.assertEqual(unpinned_actions(self.yml), [])
        self.assertEqual(len(re.findall(r"uses:", self.yml)), 5)

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

    def test_top_level_permissions_empty_and_jobs_are_least_privilege(self):
        self.assertRegex(self.yml, r"(?m)^permissions: \{\}$")
        for job in ("agent", "publish"):
            perms = re.search(r"(?m)^    permissions:\n((?:      .*\n)+)", self.jobs[job]).group(1)
            self.assertNotIn("write", perms, job)
        self.assertNotIn("pull_request_target", self.yml)
        self.assertNotIn("pull_request:", self.yml)

    def test_agent_and_publish_are_separate_jobs(self):
        self.assertEqual(sorted(self.jobs), ["agent", "publish"])
        self.assertIn("needs: agent", self.jobs["publish"])
        self.assertIn(AGENT_RUN, self.agent)
        self.assertNotIn(AGENT_RUN, self.publish)
        self.assertIn(PUSH, self.publish)
        self.assertNotIn(PUSH, self.agent)
        for forbidden in ("git push", "gh pr create", "create-github-app-token", "repo-token", "permission-"):
            self.assertNotIn(forbidden, self.jobs["agent"], forbidden)
        for forbidden in ("Run agent", "INSTALLATION_TOKEN", "app_installation_token.py", "copilot_token"):
            self.assertNotIn(forbidden, self.jobs["publish"], forbidden)

    def test_agent_job_has_no_write_token_and_private_key_only_before_the_agent_runs(self):
        keyed = [n for n, s in self.agent.items() if "APP_PRIVATE_KEY" in s]
        self.assertEqual(keyed, [MINT_COPILOT])
        order = step_order(self.yml, "agent")
        self.assertLess(order.index(MINT_COPILOT), order.index(AGENT_RUN))
        agent_step = self.agent[AGENT_RUN]
        self.assertIn("INSTALLATION_TOKEN", agent_step)
        for forbidden in ("APP_PRIVATE_KEY", "GH_TOKEN", "github.token", "secrets."):
            self.assertNotIn(forbidden, agent_step)
        # 領 Copilot 權杖只要求 organization_copilot_requests: read，不含任何 repo 寫入權限
        script = run_script(self.agent[MINT_COPILOT])
        self.assertEqual(re.findall(r'"(\w+)":"(\w+)"', script), [("organization_copilot_requests", "read")])

    def test_publish_job_private_key_only_in_the_mint_step_after_gate_and_commit(self):
        keyed = [n for n, s in self.publish.items() if "APP_PRIVATE_KEY" in s]
        self.assertEqual(keyed, [MINT_REPO])
        order = step_order(self.yml, "publish")
        self.assertLess(order.index(GATE), order.index(COMMIT))
        self.assertLess(order.index(COMMIT), order.index(MINT_REPO))
        self.assertLess(order.index(MINT_REPO), order.index(PUSH))
        for name in order[:order.index(MINT_REPO)]:
            for secretish in ("secrets.", "GH_TOKEN", "repo-token", "x-access-token"):
                self.assertNotIn(secretish, self.publish[name], (name, secretish))

    def test_publish_job_runs_no_repo_code(self):
        runners = r"(?m)(^|[;&|]\s*)(python3?|node|npm|npx|pip|pytest|make|\./|bash\s+\S|sh\s+\S|source\s|\.\s+\S)"
        for name, step in self.publish.items():
            script = run_script(step) or ""
            self.assertIsNone(re.search(runners, script), name)
        self.assertNotIn(".github/scripts", self.jobs["publish"])

    def test_commit_disables_hooks_and_push_sets_hookspath(self):
        script = run_script(self.publish[COMMIT])
        self.assertIn("-c core.hooksPath=/dev/null commit --no-verify", script)
        push = run_script(self.publish[PUSH])
        self.assertIn('GIT_CONFIG_KEY_1="core.hooksPath"', push)
        self.assertIn('GIT_CONFIG_VALUE_1="/dev/null"', push)
        self.assertIn("GIT_CONFIG_COUNT=2", push)

    def test_checkouts_do_not_persist_credentials(self):
        for job in ("agent", "publish"):
            self.assertIn("persist-credentials: false", list(steps_of(self.yml, job).values())[0])

    def test_placeholder_agent_step_fails_closed(self):
        self.assertRegex(run_script(self.agent[AGENT_RUN]), r"(?m)^exit 1$")

    def test_repo_token_is_least_privilege(self):
        grants = re.findall(r"permission-([a-z-]+): (\w+)", self.publish[MINT_REPO])
        self.assertEqual(sorted(grants), [("contents", "write"), ("issues", "write"), ("pull-requests", "write")])

    def test_copilot_mint_arguments_pass_the_scripts_own_validation(self):
        mod = load_module(self.py_path)
        script = run_script(self.agent[MINT_COPILOT])
        raw = re.search(r"--permissions '(\{.*?\})'", script).group(1)
        self.assertEqual(mod.parse_permissions(raw), {"organization_copilot_requests": "read"})
        self.assertIn("--github-output copilot_token", script)
        self.assertIn(".github/scripts/app_installation_token.py", script)

    def test_pr_is_created_as_draft(self):
        self.assertIn("gh pr create --draft", run_script(self.publish[PUSH]))

    def test_structure_checks_catch_a_merged_job_and_leaked_secrets(self):
        # 反例：把 push 步驟搬回 agent job，或讓 agent job 帶著私鑰與寫入權杖，前述斷言用的條件必須成立
        merged = self.yml.replace("  publish:\n", "  agent_tail:\n", 1)
        self.assertNotEqual(sorted(split_jobs(merged)), ["agent", "publish"])
        leaky = self.yml.replace('INSTALLATION_TOKEN: ${{ steps.copilot.outputs.copilot_token }}',
                                 'INSTALLATION_TOKEN: ${{ steps.copilot.outputs.copilot_token }}\n          GH_TOKEN: ${{ secrets.APP_PRIVATE_KEY }}', 1)
        self.assertNotEqual(leaky, self.yml)
        agent_step = steps_of(leaky, "agent")[AGENT_RUN]
        self.assertIn("APP_PRIVATE_KEY", agent_step)
        self.assertEqual([n for n, s in steps_of(leaky, "agent").items() if "APP_PRIVATE_KEY" in s],
                         [MINT_COPILOT, AGENT_RUN])


HOOK = "#!/bin/sh\nprintf 'STOLEN=%s' \"$GH_TOKEN\" > \"$STOLEN_FILE\"\n"


@unittest.skipUnless(find_bash() and shutil.which("git"), "需要 bash 與 git 才能實跑 patch 產生、關卡與 commit 步驟")
class PublishPipelineTests(TemplateCase):
    """在暫存目錄裡模擬 agent job（會被 Agent 動手腳的 clone）與 publish job（新的 clone），實跑範本裡的步驟腳本。"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        steps = {n: s for job in ("agent", "publish") for n, s in steps_of(cls.blocks["nightly-maintenance-agent.yml"], job).items()}
        cls.patch_script = run_script(steps[MAKE_PATCH])
        cls.gate_script = run_script(steps[GATE])
        cls.gate_env = {k: v for k, v in step_env(steps[GATE]).items() if "${{" not in v}
        cls.commit_script = run_script(steps[COMMIT])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.origin = self.root / "origin"
        self.git(self.root, "init", "-q", str(self.origin))
        self.config(self.origin)
        (self.origin / "keep.txt").write_text("base\n", encoding="utf-8")
        self.git(self.origin, "add", "-A")
        self.git(self.origin, "commit", "-q", "-m", "base")

    def git(self, cwd, *args, check=True):
        return subprocess.run(["git", *args], cwd=str(cwd), check=check, capture_output=True, text=True,
                              encoding="utf-8")

    def config(self, repo):
        for key, value in (("user.email", "t@example.com"), ("user.name", "t"), ("core.autocrlf", "false"),
                           ("commit.gpgsign", "false")):
            self.git(repo, "config", key, value)

    def clone(self, name):
        self.clones = getattr(self, "clones", 0) + 1
        path = self.root / ("%s_%d" % (name, self.clones))
        self.git(self.root, "clone", "-q", str(self.origin), str(path))
        self.config(path)
        return path

    def bash(self, script, cwd, **env):
        return subprocess.run([find_bash(), "-c", script], cwd=str(cwd), env=clean_env(**env),
                              capture_output=True, text=True, encoding="utf-8", timeout=60)

    def make_patch(self, agent, changes):
        for rel, content in changes.items():
            target = agent / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        out = self.root / "gh_output"
        out.write_text("", encoding="utf-8")
        result = self.bash(self.patch_script, agent, RUNNER_TEMP=str(self.root), GITHUB_OUTPUT=str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.root / "agent.patch", out.read_text(encoding="utf-8")

    def run_gate(self, publish, patch_file, max_files=None):
        env = dict(self.gate_env, PATCH_FILE=str(patch_file))
        if max_files is not None:
            env["MAX_FILES"] = str(max_files)
        return self.bash(self.gate_script, publish, **env)

    def pipeline(self, changes, max_files=None):
        agent = self.clone("agent")
        patch, outputs = self.make_patch(agent, changes)
        publish = self.clone("publish")
        return self.run_gate(publish, patch, max_files), outputs, publish

    # ----- 爆破半徑關卡 -----
    def test_ordinary_changes_pass(self):
        for changes in ({"src/a.py": "x\n"}, {"keep.txt": "changed\n", "docs/n.md": "n\n"}):
            result, outputs, publish = self.pipeline(changes)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("has_patch=true", outputs)
            self.assertTrue((publish / list(changes)[0]).exists())

    def test_forbidden_paths_fail(self):
        for rel in (".github/workflows/x.yml", ".github/scripts/app_installation_token.py", "Dockerfile",
                    "services/api/Dockerfile", "docker-compose.yml", "deploy/docker-compose.prod.yaml",
                    "infra/main.tf", "prod.tfvars", ".gitattributes", "sub/.gitattributes", ".gitmodules"):
            with self.subTest(rel):
                result, _outputs, _publish = self.pipeline({"src/ok.py": "x\n", rel: "x\n"})
                self.assertEqual(result.returncode, 1, (rel, result.stderr))

    def test_no_changes_means_no_patch_and_gate_refuses_empty_patch(self):
        agent = self.clone("agent")
        patch, outputs = self.make_patch(agent, {})
        self.assertIn("has_patch=false", outputs)
        result = self.run_gate(self.clone("publish"), patch)
        self.assertEqual(result.returncode, 1)

    def test_too_many_files_and_oversized_patch_fail(self):
        self.assertEqual(self.pipeline({"f%d.txt" % i: "x\n" for i in range(10)})[0].returncode, 0)
        self.assertEqual(self.pipeline({"f%d.txt" % i: "x\n" for i in range(11)})[0].returncode, 1)
        agent = self.clone("agent")
        patch, _ = self.make_patch(agent, {"big.txt": "x" * 2000 + "\n"})
        result = self.run_gate(self.clone("publish"), patch, max_files=10)
        self.assertEqual(result.returncode, 0)
        env = dict(self.gate_env, PATCH_FILE=str(patch), MAX_PATCH_BYTES="100")
        self.assertEqual(self.bash(self.gate_script, self.clone("publish2"), **env).returncode, 1)

    def test_lookalike_names_are_not_false_positives(self):
        result, _o, _p = self.pipeline({"src/github_notes.md": "x\n", "docs/Dockerfile.md": "x\n"})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_handwritten_patch_touching_dot_git_is_refused_and_nothing_lands(self):
        template = ("diff --git a/{p} b/{p}\nnew file mode 100755\nindex 0000000..e69de29\n"
                    "--- /dev/null\n+++ b/{p}\n@@ -0,0 +1 @@\n+#!/bin/sh\n")
        for rel in (".git/hooks/pre-commit", "sub/.git/config", ".git/config"):
            with self.subTest(rel):
                publish = self.clone("publish_" + rel.replace("/", "_").replace(".", ""))
                patch = self.root / "evil.patch"
                patch.write_text(template.format(p=rel), encoding="utf-8", newline="\n")
                result = self.run_gate(publish, patch)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertFalse((publish / ".git" / "hooks" / "pre-commit").exists())

    @unittest.skipIf(sys.platform == "win32", "Windows 預設無法建立符號連結，無法驗證模式 120000")
    def test_symlink_patch_is_refused(self):
        patch = self.root / "link.patch"
        patch.write_text("diff --git a/link b/link\nnew file mode 120000\nindex 0000000..d6d8c3c\n"
                         "--- /dev/null\n+++ b/link\n@@ -0,0 +1 @@\n+/etc/passwd\n\\ No newline at end of file\n",
                         encoding="utf-8", newline="\n")
        self.assertEqual(self.run_gate(self.clone("publish"), patch).returncode, 1)

    # ----- 審查員重現的攻擊：Agent 寫 .git/hooks/pre-commit 偷 repo 權杖 -----
    def attack(self, agent):
        hook = agent / ".git" / "hooks" / "pre-commit"
        hook.write_text(HOOK, encoding="utf-8", newline="\n")
        hook.chmod(0o755)

    def test_hook_attack_is_real_in_the_old_single_job_flow(self):
        """對照組：舊流程（同一個 clone 先讓 Agent 動手，再用 git add／diff 做關卡，再帶 token commit）確實會洩漏。"""
        agent = self.clone("agent")
        (agent / "src").mkdir()
        (agent / "src" / "a.py").write_text("x\n", encoding="utf-8")
        self.attack(agent)
        self.git(agent, "add", "-A")
        names = self.git(agent, "diff", "--cached", "--name-only").stdout.split()
        self.assertEqual(names, ["src/a.py"])  # 關卡看不到 .git/ 裡的 hook
        stolen = self.root / "stolen_old"
        env = clean_env(GH_TOKEN="ghs_FAKE_REPO_TOKEN", STOLEN_FILE=str(stolen))
        subprocess.run(["git", "commit", "-q", "-m", "x"], cwd=str(agent), env=env, check=True,
                       capture_output=True)
        self.assertEqual(stolen.read_text(encoding="utf-8"), "STOLEN=ghs_FAKE_REPO_TOKEN")

    def test_hook_attack_gets_no_token_in_the_two_job_flow(self):
        agent = self.clone("agent")
        self.attack(agent)
        patch, outputs = self.make_patch(agent, {"src/a.py": "x\n"})
        self.assertIn("has_patch=true", outputs)
        text = patch.read_text(encoding="utf-8")
        self.assertIn("src/a.py", text)
        self.assertNotIn("hooks", text)  # patch 只含工作樹變更，.git/ 不會跟過去
        publish = self.clone("publish")
        self.assertEqual(self.run_gate(publish, patch).returncode, 0)
        self.assertFalse((publish / ".git" / "hooks" / "pre-commit").exists())
        stolen = self.root / "stolen_new"
        # 連 commit 步驟的環境變數裡放 token 都拿不到：此步驟在真實流程中本來就沒有 token，這裡刻意加上以加強對照
        result = self.bash(self.commit_script, publish, ISSUE_NUMBER="7", RUN_ID="9", RUN_URL="http://x",
                           GH_TOKEN="ghs_FAKE_REPO_TOKEN", STOLEN_FILE=str(stolen))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(stolen.exists())
        shown = self.git(publish, "show", "--name-only", "--pretty=format:%s", "HEAD").stdout.split("\n")
        self.assertEqual(shown[0], "fix: automated change for issue #7")
        self.assertEqual([x for x in shown[1:] if x], ["src/a.py"])
        self.assertEqual(self.git(publish, "branch", "--show-current").stdout.strip(), "ai-agent/issue-7-9")

    def test_commit_step_alone_neutralizes_an_installed_hook(self):
        """即使 publish 這邊的 .git/hooks 被裝了 hook（假設有別的漏洞），停用 hook 的 commit 也不會執行它。"""
        publish = self.clone("publish")
        self.attack(publish)
        (publish / "src").mkdir()
        (publish / "src" / "a.py").write_text("x\n", encoding="utf-8")
        self.git(publish, "add", "-A")
        stolen = self.root / "stolen_commit"
        result = self.bash(self.commit_script, publish, ISSUE_NUMBER="7", RUN_ID="9", RUN_URL="http://x",
                           GH_TOKEN="ghs_FAKE_REPO_TOKEN", STOLEN_FILE=str(stolen))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(stolen.exists())

    def test_commit_step_rejects_non_numeric_issue(self):
        publish = self.clone("publish")
        result = self.bash(self.commit_script, publish, ISSUE_NUMBER="7; echo pwned", RUN_ID="9", RUN_URL="x")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("pwned", result.stdout)


if __name__ == "__main__":
    unittest.main()
