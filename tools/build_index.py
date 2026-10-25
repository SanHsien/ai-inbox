#!/usr/bin/env python3
"""
tools/build_index.py
從 notes/*.md（唯一資料來源）產生 README.md 內的任務總表、文章索引與知識圖譜。

    python tools/build_index.py          # 重寫 README.md 的自動產生區塊
    python tools/build_index.py --check  # 只檢查是否過期（CI 用），過期 exit 1

README 中只有 `<!-- BEGIN GENERATED: name -->` 與 `<!-- END GENERATED: name -->`
之間的內容由本腳本管理，其餘段落維持手寫。
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = REPO_ROOT / "notes"
README_FILE = REPO_ROOT / "README.md"

TASK_ID = r"T-\d{8}-\d{2}"
PRIORITIES = ("高", "中", "低")
PRIORITY_RANK = {"高": 0, "中": 1, "低": 2}
STATUSES = ("pending", "in-progress", "done", "archived")

# - [ ] **`T-20261017-01`**｜**[優先級：中]** 任務標題
TASK_LINE = re.compile(
    rf"^- \[(?P<box>[ xX])\] \*\*`(?P<id>{TASK_ID})`\*\*｜\*\*\[優先級：(?P<prio>[^\]]+)\]\*\* (?P<title>.+?)\s*$"
)
# 任務底下的縮排欄位：  - **目標範圍**：...
TASK_FIELD = re.compile(r"^\s{2,}- \*\*(?P<key>[^*]+)\*\*[：:]\s*(?P<value>.*?)\s*$")
FENCE_LINE = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})")
GENERATED_BLOCK = re.compile(
    r"(<!-- BEGIN GENERATED: (?P<name>[\w-]+) -->\n)(?P<body>.*?)(<!-- END GENERATED: (?P=name) -->)",
    re.DOTALL,
)


def fence_step(fence: str | None, line: str) -> tuple[str | None, bool]:
    """程式碼圍欄狀態機：回傳 (下一行開始時的圍欄狀態, 這一行是否屬於圍欄)。

    依 CommonMark：反引號圍欄的開頭行後面不可再出現反引號，否則是行內程式碼（例如 ```x``` 文字），
    不是圍欄；關閉行要用同一種符號、長度不短於開頭，且後面只能有空白。
    """
    m = FENCE_LINE.match(line)
    if fence is None:
        if m and not (m["fence"][0] == "`" and "`" in line[m.end():]):
            return m["fence"], True
        return None, False
    if m and m["fence"][0] == fence[0] and len(m["fence"]) >= len(fence) and not line[m.end():].strip():
        return None, True
    return fence, True


def iter_outside_fences(lines: list[str]):
    """逐行產生 (0-based index, line)，略過 ``` 或 ~~~ 程式碼圍欄區塊（含圍欄行本身）。"""
    fence: str | None = None
    for idx, line in enumerate(lines):
        fence, in_fence = fence_step(fence, line)
        if not in_fence:
            yield idx, line


def unclosed_fence_line(lines: list[str]) -> int | None:
    """到檔尾仍未關閉的圍欄，回傳其開頭行號（1-based）；後面的任務會被當成程式碼而消失。"""
    fence: str | None = None
    start = None
    for lineno, line in enumerate(lines, 1):
        before = fence
        fence, _ = fence_step(fence, line)
        if before is None and fence is not None:
            start = lineno
    return start if fence is not None else None


@dataclass
class Task:
    id: str
    done: bool
    priority: str
    title: str
    note: "Note"
    line: int
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def in_progress(self) -> bool:
        return not self.done and not self.archived and "進行中" in self.fields.get("狀態", "")

    @property
    def archived(self) -> bool:
        # 只看狀態文字開頭：避免「🟡 進行中（等待關閉 PR）」這類理由內含關鍵字被誤判為不做
        s = self.fields.get("狀態", "").lstrip()
        return not self.done and s.startswith(("⚪", "不做", "archived", "關閉", "已關閉"))

    @property
    def archive_reason(self) -> str:
        """從 `- **狀態**：⚪ 不做（原因）` 抽出原因；無括號則回傳原始狀態文字。"""
        s = self.fields.get("狀態", "").strip()
        m = re.search(r"[（(](.+)[）)]$", s)
        if m:
            return m.group(1).strip()
        cleaned = re.sub(r"^[⚪\s]*不做[：:\s—-]*", "", s).strip()
        return cleaned or "-"

    @property
    def created(self) -> str:
        d = self.id[2:10]
        return f"{d[:4]}-{d[4:6]}-{d[6:]}"


@dataclass
class Note:
    path: Path
    meta: dict[str, str]
    tags: list[str]
    tasks: list[Task] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return self.path.stem

    @property
    def link(self) -> str:
        return f"./notes/{self.path.name}"


def expected_note_status(note: Note) -> str:
    """依筆記底下任務狀態推算 frontmatter 應有的 status。

    - 無任務：維持既有 status（若無則 pending）
    - 全部任務皆為 ⚪ 不做 (archived)：archived
    - 有效任務（排除 ⚪ 不做）全數完成 (done)：done
    - 有任一任務已做或進行中：in-progress
    - 其餘（有效任務皆未開始）：pending
    """
    if not note.tasks:
        return note.meta.get("status") or "pending"
    active = [t for t in note.tasks if not t.archived]
    if not active:
        return "archived"
    done_count = sum(t.done for t in active)
    if done_count == len(active):
        return "done"
    if done_count > 0 or any(t.in_progress for t in active):
        return "in-progress"
    return "pending"


def ensure_utf8_stdout() -> None:
    """Windows cp950 終端 print emoji 會 UnicodeEncodeError；stdout 被取代（如測試擷取）時略過。"""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure:
        reconfigure(encoding="utf-8")


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]] | None:
    """解析筆記用到的 YAML 子集：`key: value` 與 `tags:` 清單。不合法回傳 None。"""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None
    meta: dict[str, str] = {}
    tags: list[str] = []
    current = None
    for raw in lines[1:end]:
        item = re.match(r"^\s+-\s+(.*)$", raw)
        if item and current == "tags":
            tags.append(item.group(1).strip().strip("\"'"))
            continue
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", raw)
        if not kv:
            continue
        current, value = kv.group(1), kv.group(2)
        if not value.startswith(("\"", "'")):
            value = value.split(" #", 1)[0]
        meta[current] = value.strip().strip("\"'")
    return meta, tags


def parse_note(path: Path) -> Note:
    text = path.read_text(encoding="utf-8")
    meta, tags = parse_frontmatter(text) or ({}, [])
    note = Note(path=path, meta=meta, tags=tags)
    task: Task | None = None
    key = ""
    fence: str | None = None
    for lineno, line in enumerate(text.split("\n"), 1):
        opened_here = fence is None
        fence, in_fence = fence_step(fence, line)
        if in_fence:
            if opened_here and not line.startswith(" "):
                task = None  # 頂層圍欄結束目前任務的欄位區
            continue
        m = TASK_LINE.match(line)
        if m:
            task = Task(
                id=m["id"],
                done=m["box"] in "xX",
                priority=m["prio"],
                title=m["title"],
                note=note,
                line=lineno,
            )
            note.tasks.append(task)
            continue
        if task is None:
            continue
        f = TASK_FIELD.match(line)
        if f:
            key = f["key"].strip()
            task.fields[key] = f["value"]
        elif line.strip() and not line.startswith(" "):
            task = None
        elif line.startswith("    ") and line.strip() and not task.fields.get(key):
            # 欄位值寫在下一行（更深縮排）時，取第一行內容
            task.fields[key] = line.strip().lstrip("-0123456789. ")
    return note


def filled(value: str) -> bool:
    """欄位有實際內容（不是空白，也不是範本的 `*（...）*` 佔位文字）。"""
    value = value.strip()
    return bool(value) and not value.startswith("*（")


# DoD 裡用反引號標出的本 repo 產出路徑，例如 `docs/x.md`；其他 repo 或全域路徑無法在此驗證，不檢查
DOD_ARTIFACT = re.compile(r"`((?:docs|templates|assets|tools|tests|notes)/[^`\s*<>]+\.\w+)`")


def missing_dod_artifacts(task: Task) -> list[str]:
    """DoD 要求產出、但本 repo 找不到的檔案。DoD 沒達成就不能算已做，這是最容易機械檢查的一種。"""
    dod = task.fields.get("驗收標準（DoD）", "")
    return [p for p in dict.fromkeys(DOD_ARTIFACT.findall(dod)) if not (REPO_ROOT / p).exists()]


def load_notes() -> list[Note]:
    notes = [parse_note(p) for p in NOTES_DIR.glob("*.md")]
    return sorted(notes, key=lambda n: (n.meta.get("analyzed_at", ""), n.slug))


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip() or "-"


def render_tasks(notes: list[Note]) -> str:
    tasks = sorted((t for n in notes for t in n.tasks), key=lambda t: t.id)
    active_tasks = sorted(
        (t for t in tasks if not t.done and not t.archived),
        key=lambda t: (0 if t.in_progress else 1, PRIORITY_RANK.get(t.priority, 9), t.id),
    )
    done_tasks = [t for t in tasks if t.done]
    archived_tasks = [t for t in tasks if t.archived]

    pending_count = sum(not t.in_progress for t in active_tasks)
    in_progress_count = sum(t.in_progress for t in active_tasks)
    archived_count = len(archived_tasks)
    done_count = len(done_tasks)

    summary_parts = [
        f"🔴 未做 {pending_count}",
        f"🟡 進行中 {in_progress_count}",
        f"🟢 已做 {done_count}",
    ]
    if archived_count > 0:
        summary_parts.append(f"⚪ 不做 {archived_count}")

    out = [
        f"> 共 {len(tasks)} 項任務：" + "／".join(summary_parts),
        "> 💡 **快速派工／認領**：執行 `python tools/task_cli.py next` 查看推薦待辦、`claim <ID>` 認領、`complete <ID> --evidence \"...\"` 結案。",
        "",
        "### 🔴 待辦與進行中（Active Queue — 依進行中與優先級排序）",
        "",
        "| 任務 ID | 狀態 | 優先級 | 待辦事項摘要 | 目標專案 / 範圍 | 來源分析文章 | 建立日期 |",
        "| :--- | :---: | :---: | :--- | :--- | :--- | :---: |",
    ]
    for t in active_tasks:
        status = "🟡 進行中" if t.in_progress else "🔴 未做"
        out.append(
            f"| `{t.id}` | {status} | {t.priority} | {_cell(t.title)} | {_cell(t.fields.get('目標範圍', ''))} "
            f"| [{t.note.slug}]({t.note.link}) | {t.created} |"
        )
    if not active_tasks:
        out.append("| *（目前沒有未完成任務）* | - | - | - | - | - | - |")

    out += [
        "",
        "### 🟢 已做（Done）",
        "",
        f"<details><summary>展開查看已完成任務（共 {done_count} 項）</summary>",
        "",
        "| 任務 ID | 完成日期 | 待辦事項摘要 | 驗收證據（PR / Commit / 路徑） | 來源分析文章 |",
        "| :--- | :---: | :--- | :--- | :--- |",
    ]
    for t in done_tasks:
        out.append(
            f"| `{t.id}` | {_cell(t.fields.get('完成日期', ''))} | {_cell(t.title)} "
            f"| {_cell(t.fields.get('實作紀錄 / 證據', ''))} | [{t.note.slug}]({t.note.link}) |"
        )
    if not done_tasks:
        out.append("| *（尚無已完成任務）* | - | - | - | - |")
    out += ["", "</details>"]

    if archived_tasks:
        out += [
            "",
            "### ⚪ 不做 / 已關閉（Archived）",
            "",
            f"<details><summary>展開查看已關閉或評估不做的任務（共 {archived_count} 項）</summary>",
            "",
            "| 任務 ID | 狀態 | 優先級 | 待辦事項摘要 | 關閉理由 | 來源分析文章 |",
            "| :--- | :---: | :---: | :--- | :--- | :--- |",
        ]
        for t in archived_tasks:
            out.append(
                f"| `{t.id}` | ⚪ 不做 | {t.priority} | {_cell(t.title)} | {_cell(t.archive_reason)} "
                f"| [{t.note.slug}]({t.note.link}) |"
            )
        out += ["", "</details>"]

    return "\n".join(out) + "\n"


STATUS_LABEL = {"pending": "🔴", "in-progress": "🟡", "done": "🟢", "archived": "⚪"}


def render_index(notes: list[Note]) -> str:
    out = [
        "| 日期 | 狀態 | 文章標題 / 主題 | 核心標籤 | 衍生任務（已做/有效） |",
        "| :---: | :---: | :--- | :--- | :---: |",
    ]
    for n in notes:
        tags = ", ".join(f"`{t}`" for t in n.tags[:3])
        done = sum(t.done for t in n.tasks)
        archived = sum(t.archived for t in n.tasks)
        active_total = len(n.tasks) - archived
        progress = f"{done} / {active_total}" + (f"（+{archived} 不做）" if archived else "")
        out.append(
            f"| {n.meta.get('analyzed_at', '-')} | {STATUS_LABEL.get(n.meta.get('status', ''), '?')} "
            f"| [{_cell(n.meta.get('title', n.slug))}]({n.link}) | {tags or '-'} | {progress} |"
        )
    return "\n".join(out) + "\n"


# 知識圖譜的集群。筆記以 frontmatter `cluster`（鍵）、`cluster_role`（在集群裡的角色）、
# `short_title`（圖譜顯示的短標題）歸入集群，圖譜由本腳本產生，不需手動加連結。
CLUSTERS = {
    "1": "多 Agent 共同大腦、通訊與協同調度",
    "2": "Code-as-Video、視覺動效與 Generative UI",
    "3": "Agent 原生工具鏈、環境感知與擴充生態",
    "4": "文獻研究、論文閱讀與全端工程實踐",
}


def render_clusters(notes: list[Note]) -> str:
    out = ["全庫筆記圍繞「AI 程式開發工業化與多代理協同」形成四個互相引用的集群：", ""]
    for key, name in CLUSTERS.items():
        out.append(f"**集群 {key}：{name}**")
        roles: dict[str, list[Note]] = {}
        for n in notes:
            if n.meta.get("cluster") == key:
                roles.setdefault(n.meta.get("cluster_role") or "其他", []).append(n)
        for role, members in roles.items():
            links = "、".join(f"[{_cell(n.meta.get('short_title') or n.meta.get('title', n.slug))}]({n.link})"
                             for n in members)
            out.append(f"- {role}：{links}")
        if not roles:
            out.append("- *（尚無筆記）*")
        out.append("")
    return "\n".join(out)


RENDERERS = {"tasks": render_tasks, "index": render_index, "clusters": render_clusters}


def build_readme(readme: str, notes: list[Note]) -> str:
    found = set()

    def replace(m: re.Match) -> str:
        name = m["name"]
        if name not in RENDERERS:
            return m.group(0)
        found.add(name)
        return m.group(1) + RENDERERS[name](notes) + m.group(4)

    result = GENERATED_BLOCK.sub(replace, readme)
    missing = set(RENDERERS) - found
    if missing:
        raise SystemExit(f"[FAIL] README.md 缺少自動產生區塊標記：{sorted(missing)}")
    return result


def main(argv: list[str]) -> int:
    ensure_utf8_stdout()
    import argparse

    parser = argparse.ArgumentParser(description="從 notes/ 重產 README.md 的任務表、文章索引與知識圖譜")
    parser.add_argument("--check", action="store_true", help="只檢查 README 是否過期，不寫檔（過期時 exit 1）")
    args = parser.parse_args(argv)  # 先解析：--help 只印說明，不可重寫 README
    current = README_FILE.read_text(encoding="utf-8")
    expected = build_readme(current, load_notes())
    if args.check:
        if current != expected:
            print("[FAIL] README.md 自動產生區塊已過期，請執行：python tools/build_index.py")
            return 1
        print("[PASS] README.md 與 notes/ 同步。")
        return 0
    if current != expected:
        README_FILE.write_text(expected, encoding="utf-8", newline="\n")
        print("[*] README.md 已更新。")
    else:
        print("[*] README.md 已是最新。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
