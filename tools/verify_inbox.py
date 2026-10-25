#!/usr/bin/env python3
"""
tools/verify_inbox.py
驗證 ai-inbox 的契約完整性（CI 與本地共用）：
1. notes/ 檔名、YAML frontmatter 必要欄位與狀態值合法，id 與檔名一致；每篇都歸入知識圖譜集群。
2. 任務 ID 在全庫只定義一次、格式符合範本；被引用的 ID 都有定義。
3. 筆記 status 與底下任務完成度一致。
4. README.md 自動產生區塊與 notes/ 同步（等同 build_index.py --check）。
5. README / notes / templates 內的相對連結都指向存在的檔案。
6. 沒有機密字串或無法公開解析的內部 Session 連結。
7. [Private Repo: 別名] 都登記在 private-aliases.json；本機有 private-aliases.local.json 時，
   私有 repo 真實名稱不得出現在任何會提交的檔案。
8. 會提交的檔案不得出現私人稱謂（公開 repo 用面向公眾的措辭）。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402

FILENAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
REQUIRED_KEYS = ("id", "title", "source_url", "analyzed_at", "status")
SECRET_PATTERNS = {
    "GitHub token": r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "Anthropic / OpenAI key": r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}",
    "Google API key": r"\bAIza[0-9A-Za-z_-]{35}\b",
    "Slack token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}",
    "private key": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "內部 Session 連結": r"conversation://",
}
LINK = re.compile(r"\]\((?!https?://|mailto:|#|<)([^)\s]+)\)")


def rel(path: Path) -> str:
    try:
        return path.relative_to(bi.REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def check_notes(notes: list[bi.Note]) -> list[str]:
    errors = []
    for n in notes:
        name = n.path.name
        if not FILENAME.match(name):
            errors.append(f"{name}: 檔名需為 YYYY-MM-DD-<slug>.md（slug 用小寫英數與連字號）")
        if not n.meta:
            errors.append(f"{name}: 缺少或無法解析 YAML frontmatter")
            continue
        for key in REQUIRED_KEYS:
            if not n.meta.get(key):
                errors.append(f"{name}: frontmatter 缺少必要欄位 '{key}'")
        if n.meta.get("id") and n.meta["id"] != n.slug:
            errors.append(f"{name}: frontmatter id '{n.meta['id']}' 與檔名不一致")
        if n.meta.get("analyzed_at") and not name.startswith(n.meta["analyzed_at"]):
            errors.append(f"{name}: analyzed_at '{n.meta['analyzed_at']}' 與檔名日期不一致")

        if n.meta.get("cluster") not in bi.CLUSTERS:
            errors.append(f"{name}: frontmatter 'cluster' 需為 {'/'.join(bi.CLUSTERS)} 之一（知識圖譜集群）")
        for key in ("cluster_role", "short_title"):
            if not n.meta.get(key):
                errors.append(f"{name}: frontmatter 缺少知識圖譜欄位 '{key}'")

        status = n.meta.get("status", "")
        if status and status not in bi.STATUSES:
            errors.append(f"{name}: status '{status}' 不合法，需為 {'|'.join(bi.STATUSES)}")
        elif status and n.tasks:
            expected = bi.expected_note_status(n)
            if status != expected:
                done = sum(t.done for t in n.tasks)
                arch = sum(t.archived for t in n.tasks)
                errors.append(
                    f"{name}: status 應為 '{expected}'（任務已做 {done}、不做 {arch}、總計 {len(n.tasks)}），目前為 '{status}'"
                )

        for t in n.tasks:
            if t.priority not in bi.PRIORITIES:
                errors.append(f"{name}:{t.line}: {t.id} 優先級 '{t.priority}' 不合法，需為 高/中/低")
            if not t.fields.get("目標範圍"):
                errors.append(f"{name}:{t.line}: {t.id} 缺少「目標範圍」欄位")
            if t.done and not bi.filled(t.fields.get("實作紀錄 / 證據", "")):
                errors.append(f"{name}:{t.line}: {t.id} 已勾選完成但沒有「實作紀錄 / 證據」")
            if t.done and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", t.fields.get("完成日期", "").strip()):
                errors.append(f"{name}:{t.line}: {t.id} 已勾選完成但「完成日期」不是 YYYY-MM-DD")
    return errors


def check_task_ids(notes: list[bi.Note], texts: dict[Path, str]) -> list[str]:
    errors = []
    defined: dict[str, bi.Task] = {}
    for t in (t for n in notes for t in n.tasks):
        if t.id in defined:
            prev = defined[t.id]
            errors.append(f"任務 ID 重複定義：{t.id}（{prev.note.path.name}:{prev.line} 與 {t.note.path.name}:{t.line}）")
        defined.setdefault(t.id, t)

    # 抓出看起來像任務定義、但不符合範本格式（因此不會進總表）的行
    loose = re.compile(rf"^- \[[ xX]\] .*{bi.TASK_ID}")
    for n in notes:
        for lineno, line in enumerate(texts[n.path].split("\n"), 1):
            if loose.match(line) and not bi.TASK_LINE.match(line):
                errors.append(f"{n.path.name}:{lineno}: 任務行格式不符範本，總表讀不到：{line[:60]}…")

    for path, text in texts.items():
        for ref in sorted(set(re.findall(bi.TASK_ID, text)) - set(defined)):
            errors.append(f"{rel(path)}: 引用了未定義的任務 {ref}")
    return errors


def check_links(texts: dict[Path, str]) -> list[str]:
    errors = []
    for path, text in texts.items():
        for target in LINK.findall(text):
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if target and not (path.parent / target).exists():
                errors.append(f"{rel(path)}: 連結目標不存在 {target}")
    return errors


SESSION_LINK_LABEL = "內部 Session 連結"


def check_secrets(texts: dict[Path, str], skip_labels: tuple[str, ...] = ()) -> list[str]:
    errors = []
    for path, text in texts.items():
        for label, pattern in SECRET_PATTERNS.items():
            if label in skip_labels:
                continue
            if re.search(pattern, text):
                errors.append(f"[!] {rel(path)}: 偵測到疑似{label}")
    return errors


ALIASES_FILE = bi.REPO_ROOT / "private-aliases.json"
LOCAL_ALIASES_FILE = bi.REPO_ROOT / "private-aliases.local.json"
PRIVATE_TAG = re.compile(r"Private Repo: ([^\]<]+)\]")
SCANNED_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".html", ".js", ".ts", ".sh", ".ps1", ".toml"}


def load_aliases() -> tuple[dict[str, str], dict[str, str]]:
    """回傳（公開別名 → 用途, 本機別名 → 真實 repo）。本機檔不存在時第二個為空（如 CI）。"""
    public = json.loads(ALIASES_FILE.read_text(encoding="utf-8"))["aliases"] if ALIASES_FILE.exists() else {}
    local = json.loads(LOCAL_ALIASES_FILE.read_text(encoding="utf-8")) if LOCAL_ALIASES_FILE.exists() else {}
    return public, local


def check_private_aliases(texts: dict[Path, str], public: dict[str, str], local: dict[str, str],
                          scan: dict[Path, str]) -> list[str]:
    errors = []
    for path, text in texts.items():
        for alias in sorted(set(PRIVATE_TAG.findall(text)) - set(public)):
            errors.append(f"{rel(path)}: 私有 repo 別名 '{alias}' 未登記在 private-aliases.json")
    for alias in sorted(set(local) - set(public)):
        errors.append(f"private-aliases.local.json: 別名 '{alias}' 未登記在 private-aliases.json")

    # 本機有真名對照表時，確認真名沒有出現在任何會被提交的檔案
    real_names = {v for v in local.values()} | {v.split("/")[-1] for v in local.values()}
    for path, text in scan.items():
        for name in sorted(n for n in real_names if n and n in text):
            errors.append(f"[!] {rel(path)}: 出現私有 repo 真實名稱 '{name}'，請改寫為 [Private Repo: <別名>]")
    return errors

# 公開 repo 不使用私人稱謂；詞彙以跳脫碼寫，避免本檔自己被掃到
SELF_REFERENCES = ("\u4e3b\u4eba", "\u5c0f\u514b", "\u5c0f\u746a")


def check_self_references(scan: dict[Path, str]) -> list[str]:
    errors = []
    for path, text in scan.items():
        for word in SELF_REFERENCES:
            if word in text:
                errors.append(f"{rel(path)}: 出現私人稱謂「{word}」，請改用面向公眾的措辭（如「維護者」）")
    return errors


def tracked_texts() -> dict[Path, str]:
    """會被提交的文字檔：已追蹤＋未追蹤但沒被 .gitignore 排除（新筆記在 git add 前就要掃到）。

    不用 rglob：會掃到 .pytest_cache、node_modules、.relay-worktrees 等不會提交的檔案。
    沒有 git（例如解壓縮的原始碼）時退回 rglob。
    """
    try:
        listed = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=bi.REPO_ROOT, capture_output=True, check=True,
        ).stdout.decode("utf-8").split("\0")
        candidates = [bi.REPO_ROOT / name for name in listed if name]
    except (OSError, subprocess.CalledProcessError):
        candidates = [p for p in bi.REPO_ROOT.rglob("*") if ".git" not in p.parts]
    out = {}
    for p in candidates:
        if p.is_file() and p.suffix in SCANNED_SUFFIXES and p != LOCAL_ALIASES_FILE:
            out[p] = p.read_text(encoding="utf-8", errors="ignore")
    return out


def check_readme(notes: list[bi.Note]) -> list[str]:
    current = bi.README_FILE.read_text(encoding="utf-8")
    try:
        expected = bi.build_readme(current, notes)
    except SystemExit as e:
        return [str(e)]
    if current != expected:
        return ["README.md 自動產生區塊已過期，請執行：python tools/build_index.py"]
    return []


def main() -> int:
    bi.ensure_utf8_stdout()
    print("[*] 正在執行 ai-inbox 契約完整性驗證...")
    notes = bi.load_notes()
    tasks = [t for n in notes for t in n.tasks]
    print(f"[*] {len(notes)} 篇筆記、{len(tasks)} 項任務")

    md_files = [bi.README_FILE, *(n.path for n in notes), *sorted((bi.REPO_ROOT / "templates").glob("*.md"))]
    texts = {p: p.read_text(encoding="utf-8") for p in md_files}
    note_texts = {n.path: texts[n.path] for n in notes}
    readme_texts = {bi.README_FILE: texts[bi.README_FILE]}

    scan = tracked_texts()
    errors = [
        *check_notes(notes),
        *check_task_ids(notes, {**readme_texts, **note_texts}),
        *check_readme(notes),
        *check_links(texts),
        *check_secrets(texts),  # 文件（含 Session 連結檢查）
        *check_secrets(scan, skip_labels=(SESSION_LINK_LABEL,)),  # 全部會提交的文字檔（docs/、assets/、tools/ 等）
        # 別名登記也涵蓋 docs/、assets/ 等提交檔；tools/、tests/ 含正規表達式與測試假別名，不納入
        *check_private_aliases({**texts, **{p: s for p, s in scan.items()
                                            if p.relative_to(bi.REPO_ROOT).parts[0] not in ("tools", "tests")}},
                               *load_aliases(), scan),
        *check_self_references(scan),
    ]

    missing_dod = sorted(t.id for t in tasks if not t.done and not t.archived and not bi.filled(t.fields.get("驗收標準（DoD）", "")))
    if missing_dod:
        print(f"[WARN] {len(missing_dod)} 項未完成任務尚無可驗收的 DoD：{', '.join(missing_dod)}")

    errors = list(dict.fromkeys(errors))  # 同一檔案可能被 texts 與 scan 各掃一次，去重
    if errors:
        print("\n[FAIL] 驗證失敗，發現以下問題：")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("[PASS] 契約驗證通過！")
    return 0


if __name__ == "__main__":
    sys.exit(main())
