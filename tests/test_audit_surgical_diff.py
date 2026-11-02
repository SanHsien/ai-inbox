"""tools/audit_surgical_diff.py 的測試。

全部用暫存 git repo 做真實 commit／真實工作樹變更，不 mock git 輸出。
涵蓋：新增、修改、刪除、改名、例外路徑、門檻、空白雜訊、註解抹除、工作樹模式、參數錯誤。
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import audit_surgical_diff as asd  # noqa: E402

_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.invalid",
}
_saved_env: dict[str, str | None] = {}
_template: dict[str, str] = {}


def _run_git(repo: str, *args: str) -> str:
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return proc.stdout.strip()


def setUpModule() -> None:
    for k, v in _ENV.items():
        _saved_env[k] = os.environ.get(k)
        os.environ[k] = v
    # 範本 repo 只建一次；每個測試複製它（含 .git，commit hash 相同），比每次重建快很多
    tmp = tempfile.TemporaryDirectory()
    _template["tmp"] = tmp
    repo = os.path.join(tmp.name, "tpl")
    os.makedirs(repo)
    _run_git(repo, "init", "-q")
    _run_git(repo, "config", "commit.gpgsign", "false")
    _run_git(repo, "config", "core.autocrlf", "false")
    files = {
        "tools/foo.py": PY_LINES,
        "tests/test_foo.py": "import unittest\n",
        "docs/a.md": "# A\n\ntext\n",
        "README.md": "# readme\n",
        "src/legacy.py": COMMENTED,
        "lib/old.py": "x = 1\n",
    }
    for rel, text in files.items():
        p = Path(repo, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    _run_git(repo, "add", "-A")
    _run_git(repo, "commit", "-q", "-m", "base")
    _template["repo"] = repo
    _template["base"] = _run_git(repo, "rev-parse", "HEAD")


def tearDownModule() -> None:
    _template["tmp"].cleanup()
    for k, v in _saved_env.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


PY_LINES = "\n".join(f"line_{i} = {i}" for i in range(30)) + "\n"
COMMENTED = (
    "# 說明一\n# 說明二\n# 說明三\n# 說明四\n# 說明五\n"
    "def f():\n    return 1\n"
)


class GitRepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = os.path.join(self._tmp.name, "r")
        shutil.copytree(_template["repo"], self.repo)
        self.base = _template["base"]

    # -- helpers
    def git(self, *args: str) -> str:
        proc = subprocess.run(["git", "-C", self.repo, *args], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout.strip()

    def write(self, rel: str, text: str, *, newline: str | None = "\n") -> None:
        p = Path(self.repo, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline=newline) as fh:
            fh.write(text)

    def commit(self, msg: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    def commit_id(self, msg: str) -> str:
        self.commit(msg)
        return self.git("rev-parse", "HEAD")

    def run_audit(self, *extra: str, base: str | None = None, head: str | None = "HEAD", scope=("tools/foo.py", "tests/test_foo.py")):
        argv = ["--repo", self.repo, "--base", base or self.base]
        if head:
            argv += ["--head", head]
        for s in scope:
            argv += ["--scope", s]
        argv += list(extra)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = asd.main(argv)
        return code, out.getvalue(), err.getvalue()

    def kinds(self, out: str) -> set[str]:
        return {line.split("]")[0].strip()[1:] for line in out.splitlines() if line.startswith("  [") and "] " in line}


class ScopeTests(GitRepoCase):
    def test_small_in_scope_change_passes(self) -> None:
        self.write("tools/foo.py", PY_LINES.replace("line_3 = 3", "line_3 = 33"))
        self.write("tests/test_foo.py", "import unittest\n\n\nclass T(unittest.TestCase):\n    pass\n")
        self.commit("small")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 0, out)
        self.assertIn("[PASS]", out)

    def test_modify_out_of_scope_file_fails(self) -> None:
        self.write("tools/foo.py", PY_LINES + "extra = 1\n")
        self.write("lib/old.py", "x = 2\n")
        self.commit("touch lib")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("[out-of-scope] lib/old.py", out)
        self.assertNotIn("[out-of-scope] tools/foo.py", out)

    def test_add_out_of_scope_file_fails(self) -> None:
        self.write("lib/brand_new.py", "y = 1\n")
        self.commit("add")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("[out-of-scope] lib/brand_new.py", out)
        self.assertIn("新增", out)

    def test_delete_out_of_scope_file_fails(self) -> None:
        os.remove(Path(self.repo, "lib/old.py"))
        self.commit("rm")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("[out-of-scope] lib/old.py", out)
        self.assertIn("刪除", out)

    def test_delete_in_scope_file_passes(self) -> None:
        os.remove(Path(self.repo, "tests/test_foo.py"))
        self.commit("rm in scope")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 0, out)

    def test_rename_within_scope_passes(self) -> None:
        self.git("mv", "tools/foo.py", "tests/test_foo2.py")
        self.commit("mv")
        code, out, _ = self.run_audit(scope=("tools/foo.py", "tests/"))
        self.assertEqual(code, 0, out)
        self.assertIn("tools/foo.py -> tests/test_foo2.py", out)

    def test_rename_into_out_of_scope_fails_on_destination(self) -> None:
        self.git("mv", "tools/foo.py", "lib/foo.py")
        self.commit("mv out")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("[out-of-scope] lib/foo.py", out)
        self.assertNotIn("[out-of-scope] tools/foo.py", out)

    def test_rename_from_out_of_scope_fails_on_source(self) -> None:
        self.git("mv", "lib/old.py", "tools/foo_moved.py")
        self.commit("mv in")
        code, out, _ = self.run_audit(scope=("tools/",))
        self.assertEqual(code, 1)
        self.assertIn("[out-of-scope] lib/old.py", out)

    def test_exempt_path_not_checked_not_counted(self) -> None:
        self.write("tools/foo.py", PY_LINES + "extra = 1\n")
        self.write("README.md", "\n".join(f"row {i}" for i in range(500)) + "\n")
        self.commit("readme regenerated")
        code, out, _ = self.run_audit("--exempt", "README.md", "--max-lines", "50")
        self.assertEqual(code, 0, out)
        self.assertIn("豁免", out)
        self.assertIn("README.md", out)
        # 沒豁免就該紅（確認豁免不是預設行為）
        code2, out2, _ = self.run_audit()
        self.assertEqual(code2, 1)
        self.assertIn("[out-of-scope] README.md", out2)

    def test_exempt_rename_only_when_both_paths_exempt(self) -> None:
        self.git("mv", "lib/old.py", "lib/older.py")
        self.commit("mv in lib")
        code, out, _ = self.run_audit("--exempt", "lib/older.py", scope=("tools/",))
        self.assertEqual(code, 1)
        self.assertIn("[out-of-scope] lib/old.py", out)
        code, out, _ = self.run_audit("--exempt", "lib/", scope=("tools/",))
        self.assertEqual(code, 0, out)

    def test_special_filenames(self) -> None:
        self.write("tools/含 空白.py", "a = 1\n")
        self.write("lib/-dash 檔.py", "b = 1\n")
        self.commit("odd names")
        code, out, _ = self.run_audit(scope=("tools/",))
        self.assertEqual(code, 1)
        self.assertIn("[out-of-scope] lib/-dash 檔.py", out)
        self.assertNotIn("[out-of-scope] tools/含 空白.py", out)


class ThresholdTests(GitRepoCase):
    def test_too_many_files(self) -> None:
        for i in range(6):
            self.write(f"tools/n{i}.py", "a = 1\n")
        self.commit("many")
        code, out, _ = self.run_audit("--max-files", "5", scope=("tools/",))
        self.assertEqual(code, 1)
        self.assertIn("[too-many-files]", out)
        code, out, _ = self.run_audit("--max-files", "6", scope=("tools/",))
        self.assertEqual(code, 0, out)

    def test_too_many_lines_counts_added_and_deleted(self) -> None:
        self.write("tools/foo.py", "\n".join(f"new_{i} = {i}" for i in range(120)) + "\n")  # +120 -30
        self.commit("rewrite")
        code, out, _ = self.run_audit("--max-lines", "149")
        self.assertEqual(code, 1)
        self.assertIn("[too-many-lines]", out)
        self.assertIn("150 行", out)
        code, out, _ = self.run_audit("--max-lines", "150")
        self.assertEqual(code, 0, out)

    def test_whitespace_only_reindent_fails(self) -> None:
        self.write("tools/foo.py", "".join("    " + l + "\n" for l in PY_LINES.splitlines()))
        self.commit("reindent")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("[whitespace-only] tools/foo.py", out)

    def test_whitespace_only_line_ending_flip_fails(self) -> None:
        self.write("tools/foo.py", PY_LINES, newline="\r\n")
        self.commit("crlf")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("[whitespace-only] tools/foo.py", out)

    def test_whitespace_noise_mixed_with_real_change(self) -> None:
        lines = PY_LINES.splitlines()
        lines = [l + "  " if i < 20 else l for i, l in enumerate(lines)]  # 20 行行尾空白 = 新增 20 + 刪除 20 = 40
        lines[25] = "line_25 = 'changed'"
        self.write("tools/foo.py", "\n".join(lines) + "\n")
        self.commit("noise")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("[whitespace-noise] tools/foo.py", out)
        self.assertNotIn("[whitespace-only]", out)
        code, out, _ = self.run_audit("--max-whitespace-lines", "40")
        self.assertEqual(code, 0, out)

    def test_pure_rename_is_not_whitespace_only(self) -> None:
        self.git("mv", "tools/foo.py", "tools/bar.py")
        self.commit("pure rename")
        code, out, _ = self.run_audit(scope=("tools/",))
        self.assertEqual(code, 0, out)

    def test_comment_erasure_fails(self) -> None:
        self.write("src/legacy.py", "def f():\n    return 2\n")
        self.commit("strip comments")
        code, out, _ = self.run_audit(scope=("src/",))
        self.assertEqual(code, 1)
        self.assertIn("[comment-erasure] src/legacy.py", out)
        self.assertIn("淨少 5", out)

    def test_reworded_comments_pass(self) -> None:
        self.write("src/legacy.py", COMMENTED.replace("說明一", "新說明一").replace("說明二", "新說明二"))
        self.commit("reword")
        code, out, _ = self.run_audit(scope=("src/",))
        self.assertEqual(code, 0, out)

    def test_deleting_whole_file_is_not_comment_erasure(self) -> None:
        os.remove(Path(self.repo, "src/legacy.py"))
        self.commit("rm legacy")
        code, out, _ = self.run_audit(scope=("src/",))
        self.assertEqual(code, 0, out)

    def test_markdown_headings_are_not_comments(self) -> None:
        self.write("docs/a.md", "text only\n")  # 刪掉 "# A" 標題
        self.commit("md")
        code, out, _ = self.run_audit(scope=("docs/",))
        self.assertEqual(code, 0, out)

    def test_c_preprocessor_lines_are_not_comments(self) -> None:
        self.write("lib/x.c", "#include <a.h>\n#include <b.h>\n#include <c.h>\n#include <d.h>\n#include <e.h>\nint f;\n")
        self.commit("c")
        self.write("lib/x.c", "int f;\n")
        self.commit("c strip")
        base = self.git("rev-parse", "HEAD~1")
        code, out, _ = self.run_audit(base=base, scope=("lib/",))
        self.assertEqual(code, 0, out)

    def test_binary_file_counts_as_file_not_lines(self) -> None:
        Path(self.repo, "tools").mkdir(exist_ok=True)
        Path(self.repo, "tools/blob.bin").write_bytes(b"\x00\x01\x02" * 1000)
        self.commit("bin")
        code, out, _ = self.run_audit("--max-files", "0", scope=("tools/",))
        self.assertEqual(code, 1)
        self.assertIn("[too-many-files]", out)
        code, out, _ = self.run_audit("--max-lines", "0", scope=("tools/",))
        self.assertEqual(code, 0, out)


class RegressionTests(GitRepoCase):
    """審查回報的漏洞：每條都要有會失敗的反例。"""

    def test_sql_double_dash_comments_removed_are_detected(self) -> None:
        self.write("lib/q.sql", "".join(f"-- note {i}\n" for i in range(8)) + "select 1;\n")
        before = self.commit_id("sql")
        self.write("lib/q.sql", "select 1;\n")
        self.commit("sql strip")
        code, out, _ = self.run_audit(base=before, scope=("lib/",))
        self.assertEqual(code, 1, out)
        self.assertIn("[comment-erasure] lib/q.sql", out)
        self.assertIn("淨少 8", out)

    def test_comment_threshold_boundary(self) -> None:
        # src/legacy.py 有 5 行註解；刪 3 行剛好等於門檻 -> 通過，刪 4 行 -> 違規
        three = "# 說明四\n# 說明五\ndef f():\n    return 1\n"
        self.write("src/legacy.py", three)
        self.commit("remove 3")
        code, out, _ = self.run_audit(scope=("src/",))
        self.assertEqual(code, 0, out)
        self.write("src/legacy.py", "# 說明五\ndef f():\n    return 1\n")
        self.commit("remove 4")
        code, out, _ = self.run_audit(scope=("src/",))
        self.assertEqual(code, 1, out)
        self.assertIn("淨少 4", out)

    def test_markdown_heading_removal_beyond_threshold_still_passes(self) -> None:
        self.write("docs/h.md", "".join(f"# h{i}\n" for i in range(6)) + "body\n")
        before = self.commit_id("md headings")
        self.write("docs/h.md", "body\n")
        self.commit("md strip")
        code, out, _ = self.run_audit(base=before, scope=("docs/",))
        self.assertEqual(code, 0, out)  # .md 不做註解檢查：若被誤查，6 行會超過門檻 3

    def test_blank_line_padding_is_whitespace_only(self) -> None:
        self.write("tools/foo.py", PY_LINES + "\n" * 40)
        self.commit("pad blanks")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 1, out)
        self.assertIn("[whitespace-only] tools/foo.py", out)

    def test_blank_lines_mixed_with_real_change_count_as_noise(self) -> None:
        self.write("tools/foo.py", PY_LINES.replace("line_1 = 1", "line_1 = 'x'") + "\n" * 20)
        self.commit("pad + edit")
        code, out, _ = self.run_audit()
        self.assertEqual(code, 1, out)
        self.assertIn("[whitespace-noise] tools/foo.py", out)

    def test_submodule_pointer_bump_out_of_scope_is_detected(self) -> None:
        sub_src = os.path.join(self._tmp.name, "subsrc")
        os.makedirs(sub_src)
        _run_git(sub_src, "init", "-q")
        Path(sub_src, "f.txt").write_text("1\n", encoding="utf-8")
        _run_git(sub_src, "add", "-A")
        _run_git(sub_src, "commit", "-q", "-m", "s1")
        self.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", sub_src, "vendor/sub")
        before = self.commit_id("add submodule")
        inner = os.path.join(self.repo, "vendor", "sub")
        Path(inner, "f.txt").write_text("2\n", encoding="utf-8")
        _run_git(inner, "add", "-A")
        _run_git(inner, "commit", "-q", "-m", "s2")
        self.git("add", "vendor/sub")
        self.commit("bump submodule")
        code, out, _ = self.run_audit(base=before, scope=("tools/",))
        self.assertEqual(code, 1, out)
        self.assertIn("[out-of-scope] vendor/sub", out)
        code, out, _ = self.run_audit(base=before, scope=("vendor/",))
        self.assertEqual(code, 0, out)

    def test_head_mode_uses_merge_base_not_two_dot_diff(self) -> None:
        trunk = self.git("rev-parse", "--abbrev-ref", "HEAD")
        self.git("checkout", "-q", "-b", "feat")
        self.write("tools/foo.py", PY_LINES + "feat = 1\n")
        self.commit("feat work")
        self.git("checkout", "-q", trunk)
        self.write("lib/old.py", "x = 'trunk moved on'\n")
        self.commit("trunk advances")
        code, out, _ = self.run_audit("--head", "feat", base=trunk, head=None, scope=("tools/",))
        self.assertEqual(code, 0, out)
        self.assertNotIn("lib/old.py", out)
        # feat 自己越界仍要抓得到
        self.git("checkout", "-q", "feat")
        self.write("README.md", "# touched on feat\n")
        self.commit("feat strays")
        code, out, _ = self.run_audit("--head", "feat", base=trunk, head=None, scope=("tools/",))
        self.assertEqual(code, 1, out)
        self.assertIn("[out-of-scope] README.md", out)
        self.assertNotIn("lib/old.py", out)

    def test_worktree_mode_also_uses_merge_base(self) -> None:
        trunk = self.git("rev-parse", "--abbrev-ref", "HEAD")
        self.git("checkout", "-q", "-b", "feat")
        self.write("tools/foo.py", PY_LINES + "feat = 1\n")
        self.commit("feat work")
        self.git("checkout", "-q", trunk)
        self.write("lib/old.py", "x = 'trunk moved on'\n")
        self.commit("trunk advances")
        self.git("checkout", "-q", "feat")
        self.write("tests/test_foo.py", "import unittest\n# edit\n")
        code, out, _ = self.run_audit(base=trunk, head=None, scope=("tools/", "tests/"))
        self.assertEqual(code, 0, out)
        self.assertNotIn("lib/old.py", out)


class AncestryTests(GitRepoCase):
    """head 是 base 祖先、無共同祖先、shallow clone：不能靜默通過。"""

    def two_commits(self) -> str:
        self.write("tools/foo.py", PY_LINES + "more = 1\n")
        return self.commit_id("second")

    def test_reversed_base_head_is_exit_2_not_a_green_light(self) -> None:
        self.two_commits()
        code, out, err = self.run_audit(base="HEAD", head="HEAD~1", scope=("a/",))
        self.assertEqual(code, 2, out)
        self.assertNotIn("[PASS]", out)
        self.assertIn("祖先", err)
        self.assertIn("寫反", err)

    def test_reversed_with_explicit_shas_is_exit_2(self) -> None:
        newer = self.two_commits()
        code, _, err = self.run_audit(base=newer, head=self.base, scope=("tools/",))
        self.assertEqual(code, 2)
        self.assertIn("寫反", err)

    def test_base_equals_head_still_passes(self) -> None:
        self.two_commits()
        code, out, _ = self.run_audit(base="HEAD", head="HEAD", scope=("a/",))
        self.assertEqual(code, 0, out)
        self.assertIn("[PASS]", out)

    def test_normal_forward_range_unaffected(self) -> None:
        self.two_commits()
        code, out, _ = self.run_audit(base="HEAD~1", head="HEAD", scope=("tools/",))
        self.assertEqual(code, 0, out)
        self.assertIn("tools/foo.py", out)

    def test_title_prints_merge_base_hash(self) -> None:
        trunk = self.git("rev-parse", "--abbrev-ref", "HEAD")
        self.git("checkout", "-q", "-b", "feat")
        self.write("tools/foo.py", PY_LINES + "feat = 1\n")
        self.commit("feat")
        self.git("checkout", "-q", trunk)
        self.write("lib/old.py", "x = 'moved'\n")
        self.commit("trunk moves")
        code, out, _ = self.run_audit(base=trunk, head="feat", scope=("tools/",))
        self.assertEqual(code, 0, out)
        title = out.splitlines()[0]
        self.assertIn(f"merge-base {self.base[:12]}", title)
        self.assertIn(f"{trunk}...feat", title)
        data = json.loads(self.run_audit("--json", base=trunk, head="feat", scope=("tools/",))[1])
        self.assertEqual(data["merge_base"], self.base)

    def test_unrelated_histories_give_a_useful_error(self) -> None:
        trunk = self.git("rev-parse", "--abbrev-ref", "HEAD")
        self.git("checkout", "-q", "--orphan", "other")
        self.git("rm", "-rq", "--cached", ".")
        self.write("solo.txt", "x\n")
        self.commit("orphan root")
        code, out, err = self.run_audit(base=trunk, head="other", scope=("solo.txt",))
        self.assertEqual(code, 2, out)
        self.assertIn("共同祖先", err)
        self.assertIn("fetch-depth: 0", err)
        self.assertNotIn("失敗（exit 1）：\n", err)

    def test_shallow_clone_gives_fetch_hint(self) -> None:
        trunk = self.git("rev-parse", "--abbrev-ref", "HEAD")
        self.git("checkout", "-q", "-b", "feat")
        self.write("tools/foo.py", PY_LINES + "feat = 1\n")
        self.commit("feat")
        self.git("checkout", "-q", trunk)
        self.write("lib/old.py", "x = 2\n")
        self.commit("trunk 1")
        self.write("lib/old.py", "x = 3\n")
        self.commit("trunk 2")
        shallow = os.path.join(self._tmp.name, "shallow")
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--no-single-branch", Path(self.repo).as_uri(), shallow],
                       check=True, capture_output=True)
        self.repo = shallow
        code, out, err = self.run_audit(base=f"origin/{trunk}", head="origin/feat", scope=("tools/",))
        self.assertEqual(code, 2, out)
        self.assertIn("shallow", err)
        self.assertIn("fetch-depth: 0", err)

    def test_bad_ref_keeps_gits_own_message(self) -> None:
        code, _, err = self.run_audit(base="no-such-rev", head="HEAD")
        self.assertEqual(code, 2)
        self.assertNotIn("共同祖先", err)
        self.assertIn("no-such-rev", err)


class WorktreeModeTests(GitRepoCase):
    def test_unstaged_staged_and_untracked(self) -> None:
        self.write("tools/foo.py", PY_LINES + "more = 1\n")  # 未暫存
        self.write("tests/test_new.py", "pass\n")
        self.git("add", "tests/test_new.py")  # 已暫存新增
        self.write("lib/untracked.py", "z = 1\n")  # 未追蹤
        code, out, _ = self.run_audit(head=None, scope=("tools/", "tests/"))
        self.assertEqual(code, 1)
        self.assertIn("[out-of-scope] lib/untracked.py", out)
        self.assertNotIn("[out-of-scope] tests/test_new.py", out)
        self.assertIn("工作樹", out)

    def test_clean_worktree_passes(self) -> None:
        code, out, _ = self.run_audit(head=None)
        self.assertEqual(code, 0, out)

    def test_gitignored_files_are_not_audited(self) -> None:
        self.write(".gitignore", "*.log\n")
        self.commit("ignore")
        self.write("lib/debug.log", "noise\n")
        code, out, _ = self.run_audit(head=None, base="HEAD")
        self.assertEqual(code, 0, out)

    def test_untracked_lines_count_toward_budget(self) -> None:
        self.write("tools/big_new.py", "\n".join(f"v{i} = {i}" for i in range(100)) + "\n")
        code, out, _ = self.run_audit("--max-lines", "99", head=None, scope=("tools/",))
        self.assertEqual(code, 1)
        self.assertIn("[too-many-lines]", out)

    def test_working_tree_deletion_out_of_scope(self) -> None:
        os.remove(Path(self.repo, "lib/old.py"))
        code, out, _ = self.run_audit(head=None)
        self.assertEqual(code, 1)
        self.assertIn("[out-of-scope] lib/old.py", out)


class PatternTests(unittest.TestCase):
    def match(self, pat: str, path: str) -> bool:
        return asd.compile_pattern(pat).match(path) is not None

    def test_exact(self) -> None:
        self.assertTrue(self.match("docs/a.md", "docs/a.md"))
        self.assertFalse(self.match("docs/a.md", "docs/a.md.bak"))
        self.assertFalse(self.match("docs/a.md", "x/docs/a.md"))

    def test_star_does_not_cross_directories(self) -> None:
        self.assertTrue(self.match("docs/*.md", "docs/a.md"))
        self.assertFalse(self.match("docs/*.md", "docs/sub/a.md"))

    def test_double_star(self) -> None:
        self.assertTrue(self.match("docs/**/*.md", "docs/sub/deep/a.md"))
        self.assertTrue(self.match("docs/**/*.md", "docs/a.md"))
        self.assertFalse(self.match("docs/**/*.md", "other/a.md"))

    def test_double_star_trailing_and_leading(self) -> None:
        self.assertTrue(self.match("docs/**", "docs/a/b/c.md"))
        self.assertFalse(self.match("docs/**", "other/a.md"))
        self.assertTrue(self.match("**/x.py", "a/b/x.py"))
        self.assertTrue(self.match("**/x.py", "x.py"))
        self.assertFalse(self.match("**/x.py", "a/y.py"))
        self.assertFalse(self.match("docs/*", "docs/a/b.md"))

    def test_directory_prefix(self) -> None:
        self.assertTrue(self.match("docs/", "docs/sub/a.md"))
        self.assertFalse(self.match("docs/", "docs2/a.md"))
        self.assertFalse(self.match("docs/", "docs"))

    def test_regex_metacharacters_are_literal(self) -> None:
        self.assertTrue(self.match("a+b(1).py", "a+b(1).py"))
        self.assertFalse(self.match("a.py", "aXpy"))

    def test_invalid_patterns_rejected(self) -> None:
        for bad in ("../x", "docs/../../x", "/abs/x", "C:/x", ""):
            with self.assertRaises(asd.AuditError, msg=bad):
                asd.compile_pattern(bad)


class UsageErrorTests(GitRepoCase):
    def test_unknown_base_is_exit_2(self) -> None:
        code, _, err = self.run_audit(base="no-such-rev")
        self.assertEqual(code, 2)
        self.assertIn("[ERROR]", err)

    def test_option_like_rev_rejected(self) -> None:
        code, _, err = self.run_audit("--base=--output=x", base=self.base)
        self.assertEqual(code, 2)
        self.assertIn("[ERROR]", err)

    def test_not_a_git_repo_is_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = asd.main(["--repo", d, "--scope", "x/"])
            self.assertEqual(code, 2)

    def test_missing_scope_is_exit_2(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = asd.main(["--repo", self.repo])
        self.assertEqual(code, 2)

    def test_bad_pattern_is_exit_2(self) -> None:
        code, _, err = self.run_audit(scope=("../escape",))
        self.assertEqual(code, 2)
        self.assertIn("..", err)


class OutputTests(GitRepoCase):
    def test_json_output(self) -> None:
        self.write("lib/old.py", "x = 3\n")
        self.commit("lib")
        code, out, _ = self.run_audit("--json")
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertFalse(data["ok"])
        self.assertEqual(data["violations"][0]["kind"], "out-of-scope")
        self.assertEqual(data["violations"][0]["path"], "lib/old.py")
        self.assertEqual(data["total_files"], 1)

    def test_cli_does_not_crash_on_legacy_codepage(self) -> None:
        self.write("lib/中文.py", "x = 3\n")
        self.commit("cn")
        env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "audit_surgical_diff.py"), "--repo", self.repo,
             "--base", self.base, "--head", "HEAD", "--scope", "tools/"],
            capture_output=True, env=env,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr.decode("utf-8", "replace"))
        self.assertNotIn(b"Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
