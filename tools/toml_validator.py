#!/usr/bin/env python3
"""
tools/toml_validator.py
TOML 設定檔輕量校驗工具（只用標準庫 tomllib，需要 Python 3.11+）。

檢查項目（規格與背景見 docs/toml-config-engineering-spec.md 第 5 節）：
  parse          語法是否能被 tomllib 解析（含重複鍵、重複定義表格、未跳脫的反斜線等）
  bom            檔案開頭有 UTF-8 BOM（Windows 記事本常見；tomllib 會拒絕）
  encoding       檔案不是合法 UTF-8
  float-version  名稱以 version 結尾的鍵被解析成浮點數（3.10 會變成 3.1，應該寫成 "3.10"）
  required       --require 指定的鍵不存在，或型別不對
  pep621         --profile pep621：pyproject.toml 的 [project] 必填欄位與 dynamic 規則

用法：
  python tools/toml_validator.py .                         # 掃描目錄下所有 .toml
  python tools/toml_validator.py pyproject.toml --profile pep621
  python tools/toml_validator.py cfg.toml --require server.port:int --require name:str

結束碼：0 無錯誤；1 有 error（或加 --strict 時有 warning）；2 用法錯誤。
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None  # type: ignore[assignment]

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".tox", "dist", "build"}
BOM = b"\xef\xbb\xbf"

TYPE_NAMES = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "table": dict,
}


@dataclass
class Finding:
    path: str
    severity: str  # "error" | "warning"
    code: str
    message: str


def supports_toml_v11() -> bool:
    """用實際解析探測：這個 Python 的 tomllib 認不認得 TOML 1.1 的多行內嵌表格。"""
    if tomllib is None:
        return False
    try:
        tomllib.loads("a = {\n x = 1,\n}\n")
    except tomllib.TOMLDecodeError:
        return False
    return True


def lookup(data: Any, dotted: str) -> tuple[bool, Any]:
    """用 a.b.c 取值。鍵本身含 '.' 的情況不支援（需要請改用程式碼檢查）。"""
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


def type_matches(value: Any, type_name: str) -> bool:
    expected = TYPE_NAMES[type_name]
    if type_name == "int":  # bool 是 int 的子類別，但 true 不該通過 int
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == "float":
        return isinstance(value, float)
    return isinstance(value, expected)


def parse_require(spec: str) -> tuple[str, Optional[str]]:
    """'a.b:int' -> ('a.b', 'int')；沒有型別則 ('a.b', None)。"""
    if ":" in spec:
        key, _, type_name = spec.rpartition(":")
        if type_name not in TYPE_NAMES:
            raise ValueError(f"未知型別 {type_name!r}，可用：{', '.join(sorted(TYPE_NAMES))}")
        return key, type_name
    return spec, None


def find_float_versions(data: Any, prefix: str = "") -> List[tuple[str, float]]:
    found: List[tuple[str, float]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            where = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, float) and str(key).lower().endswith("version"):
                found.append((where, value))
            else:
                found.extend(find_float_versions(value, where))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            found.extend(find_float_versions(item, f"{prefix}[{i}]"))
    return found


def check_pep621(data: dict, require_project: bool) -> List[Finding]:
    out: List[Finding] = []
    project = data.get("project")
    if project is None:
        if require_project:
            out.append(Finding("", "error", "pep621", "缺少 [project] 表格"))
        return out
    if not isinstance(project, dict):
        return [Finding("", "error", "pep621", "[project] 必須是表格")]
    dynamic = project.get("dynamic", [])
    if not isinstance(dynamic, list):
        out.append(Finding("", "error", "pep621", "project.dynamic 必須是字串陣列"))
        dynamic = []
    if "name" in dynamic:
        out.append(Finding("", "error", "pep621", "project.name 不可列在 dynamic（PEP 621 禁止）"))
    if "name" not in project:
        out.append(Finding("", "error", "pep621", "缺少必填欄位 project.name"))
    elif not isinstance(project["name"], str) or not project["name"].strip():
        out.append(Finding("", "error", "pep621", "project.name 必須是非空字串"))
    if "version" not in project and "version" not in dynamic:
        out.append(Finding("", "error", "pep621", "缺少 project.version，且未列在 project.dynamic"))
    if "version" in project and "version" in dynamic:
        out.append(Finding("", "error", "pep621", "project.version 已靜態給值，卻又列在 dynamic"))
    if "version" in project and not isinstance(project["version"], str):
        out.append(
            Finding("", "error", "pep621", f"project.version 必須是字串，實際是 {type(project['version']).__name__}")
        )
    if "requires-python" in project and not isinstance(project["requires-python"], str):
        out.append(Finding("", "error", "pep621", "project.requires-python 必須是字串（如 \">=3.11\"）"))
    return out


def validate_bytes(
    path: str,
    raw: bytes,
    requires: Sequence[str] = (),
    profile: Optional[str] = None,
    require_project: bool = False,
) -> List[Finding]:
    findings: List[Finding] = []
    if raw.startswith(BOM):
        findings.append(
            Finding(path, "error", "bom", "檔案開頭有 UTF-8 BOM，tomllib 會拒絕；請另存為無 BOM 的 UTF-8")
        )
        raw = raw[len(BOM):]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        findings.append(Finding(path, "error", "encoding", f"不是合法 UTF-8：{exc}"))
        return findings
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        findings.append(Finding(path, "error", "parse", str(exc)))
        if not supports_toml_v11():
            findings.append(
                Finding(
                    path,
                    "warning",
                    "parse",
                    "本機 tomllib 只支援 TOML 1.0；若檔案用了 1.1 語法（多行內嵌表格、\\e、\\xHH、省略秒），"
                    "請升級到 Python 3.15+ 或改寫成 1.0 語法",
                )
            )
        return findings

    for where, value in find_float_versions(data):
        findings.append(
            Finding(
                path,
                "warning",
                "float-version",
                f"{where} 被解析成浮點數 {value!r}；版本號請加引號（例如 \"3.10\"），否則尾端 0 會消失",
            )
        )
    for spec in requires:
        key, type_name = parse_require(spec)
        found, value = lookup(data, key)
        if not found:
            findings.append(Finding(path, "error", "required", f"缺少必填鍵 {key}"))
        elif type_name and not type_matches(value, type_name):
            findings.append(
                Finding(path, "error", "required", f"{key} 型別應為 {type_name}，實際是 {type(value).__name__}（值 {value!r}）")
            )
    if profile == "pep621" and Path(path).name == "pyproject.toml":
        for f in check_pep621(data, require_project):
            f.path = path
            findings.append(f)
    return findings


def iter_toml_files(targets: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for target in targets:
        p = Path(target)
        if p.is_dir():
            for sub in sorted(p.rglob("*.toml")):
                if not (set(sub.relative_to(p).parts[:-1]) & SKIP_DIRS):
                    files.append(sub)
        else:
            files.append(p)
    return files


def run(
    targets: Sequence[str],
    requires: Sequence[str] = (),
    profile: Optional[str] = None,
    require_project: bool = False,
) -> tuple[int, List[Finding]]:
    """回傳 (掃描到的檔案數, findings)。"""
    files = iter_toml_files(targets)
    findings: List[Finding] = []
    for f in files:
        try:
            raw = f.read_bytes()
        except OSError as exc:
            findings.append(Finding(str(f), "error", "io", f"無法讀取：{exc}"))
            continue
        findings.extend(validate_bytes(str(f), raw, requires, profile, require_project))
    return len(files), findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="TOML 設定檔校驗：語法、BOM、版本號浮點陷阱、必填鍵與型別、PEP 621。",
    )
    parser.add_argument("paths", nargs="+", help="檔案或目錄（目錄會遞迴找 *.toml）")
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="KEY[:TYPE]",
        help="每個檔案都必須有的鍵，如 server.port:int。TYPE：" + "/".join(sorted(TYPE_NAMES)),
    )
    parser.add_argument("--profile", choices=["pep621"], help="只對 pyproject.toml 套用 PEP 621 檢查")
    parser.add_argument("--require-project", action="store_true", help="pep621 profile：缺 [project] 也算錯誤")
    parser.add_argument("--strict", action="store_true", help="warning 也讓結束碼變 1")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    # 必須在 argparse 之前設定，否則 --help 在 cp950 管線會亂碼
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    if tomllib is None:
        print("需要 Python 3.11+（內建 tomllib）", file=sys.stderr)
        return 2
    try:
        for spec in args.require:
            parse_require(spec)
    except ValueError as exc:
        parser.error(str(exc))
    count, findings = run(args.paths, args.require, args.profile, args.require_project)
    if count == 0:
        print("沒有找到任何 .toml 檔案", file=sys.stderr)
        return 2
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    if args.format == "json":
        print(json.dumps({"files": count, "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(f"{f.severity.upper():7} [{f.code}] {f.path}: {f.message}")
        print(f"掃描 {count} 個檔案：{len(errors)} error、{len(warnings)} warning")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
