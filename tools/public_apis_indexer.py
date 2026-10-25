#!/usr/bin/env python3
"""
tools/public_apis_indexer.py
Public APIs 本地離線索引與免金鑰 API 篩選工具。

解析維護者的 fork 倉庫（SanHsien/public-apis）的 README.md，
篩選免金鑰（Auth: No）且支援跨域（CORS: Yes）之端點，產出結構化索引與 Markdown 快速查閱手冊。
只使用 Python 標準函式庫。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence


DEFAULT_SOURCE_PATHS = [
    Path(r"C:\GitHub\public-apis\README.md"),
    Path(__file__).resolve().parent.parent.parent / "public-apis" / "README.md",
    Path("public-apis/README.md"),
]

LINK_PATTERN = re.compile(r"\[(?P<name>[^\]]+)\]\((?P<url>[^)]+)\)")


@dataclass
class ApiEntry:
    category: str
    name: str
    url: str
    description: str
    auth: str
    https: bool
    cors: str

    def to_dict(self) -> dict:
        return asdict(self)


def parse_markdown_table_rows(
    content: str,
    ignore_categories: Sequence[str] = ("APIs Covered Under APILayer Suite!",),
) -> List[ApiEntry]:
    """解析 public-apis 的 README.md，抽出所有 API 項目。"""
    lines = content.splitlines()
    entries: List[ApiEntry] = []
    current_category: Optional[str] = None
    in_table = False

    for line in lines:
        sline = line.strip()

        # 辨識分類標題 ### Category
        if sline.startswith("### "):
            cat_name = sline[4:].strip()
            if cat_name in ignore_categories:
                current_category = None
            else:
                current_category = cat_name
            in_table = False
            continue

        if not current_category:
            continue

        # 辨識表格開頭
        if sline.startswith("API |") or sline.startswith("| API |"):
            in_table = True
            continue

        if in_table:
            # 遇到分隔線
            if sline.startswith("|:---") or sline.startswith(":---"):
                continue

            # 遇到空行或跳回頂端連結則結束該表格
            if not sline or sline.startswith("**[") or sline.startswith("<br") or sline.startswith("##"):
                in_table = False
                continue

            # 提取表格欄位
            # 格式通常為: | [API](url) | Description | Auth | HTTPS | CORS |
            if "|" in sline:
                raw_parts = [p.strip() for p in sline.strip("|").split("|")]
                if len(raw_parts) >= 5:
                    # 後三欄固定是 Auth / HTTPS / CORS；說明文字若含未跳脫的 "|"，
                    # 多出來的片段併回說明，避免欄位整體錯位。
                    api_col = raw_parts[0]
                    desc_col = " | ".join(raw_parts[1:-3])
                    auth_col = raw_parts[-3].replace("`", "").strip()
                    https_col = raw_parts[-2].strip()
                    cors_col = raw_parts[-1].strip()

                    match = LINK_PATTERN.search(api_col)
                    if match:
                        name = match.group("name").strip()
                        url = match.group("url").strip()
                    else:
                        name = api_col
                        url = ""

                    is_https = https_col.lower() == "yes"

                    entries.append(
                        ApiEntry(
                            category=current_category,
                            name=name,
                            url=url,
                            description=desc_col,
                            auth=auth_col,
                            https=is_https,
                            cors=cors_col,
                        )
                    )

    return entries


def filter_apis(
    entries: Iterable[ApiEntry],
    auth: Optional[str] = "no",
    cors: Optional[str] = "yes",
    https: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> List[ApiEntry]:
    """根據篩選條件過濾 API 清單。"""
    filtered: List[ApiEntry] = []

    auth_norm = auth.lower() if auth and auth.lower() != "all" else None
    cors_norm = cors.lower() if cors and cors.lower() != "all" else None
    cat_norm = category.lower() if category else None
    search_norm = search.lower() if search else None

    for e in entries:
        if auth_norm and e.auth.lower() != auth_norm:
            continue
        if cors_norm and e.cors.lower() != cors_norm:
            continue
        if https is not None and e.https != https:
            continue
        if cat_norm and cat_norm not in e.category.lower():
            continue
        if search_norm:
            haystack = f"{e.name} {e.description} {e.category}".lower()
            if search_norm not in haystack:
                continue
        filtered.append(e)

    return filtered


def group_by_category(entries: Iterable[ApiEntry]) -> dict[str, List[ApiEntry]]:
    grouped: dict[str, List[ApiEntry]] = {}
    for e in entries:
        grouped.setdefault(e.category, []).append(e)
    return grouped


def generate_markdown(
    entries: List[ApiEntry],
    title: str = "Public APIs 免金鑰與 CORS 支援精選手冊",
    source_ref: str = "SanHsien/public-apis",
    auth: str = "No",
    cors: str = "Yes",
) -> str:
    """生成分類 Markdown 查閱手冊。"""
    grouped = group_by_category(entries)
    sorted_categories = sorted(grouped.keys())

    lines: List[str] = [
        f"# {title}",
        "",
        f"- **資料來源**：`{source_ref}`",
        f"- **篩選條件**：`Auth: {auth}` 且 `CORS: {cors}`"
        + ("（免申請金鑰、支援前端/Generative UI 直連跨域）" if (auth, cors) == ("No", "Yes") else ""),
        f"- **涵蓋項目數**：共 {len(entries)} 個公開端點，跨 {len(sorted_categories)} 個分類",
        "",
        "---",
        "",
        "## 常用分類索引（Table of Contents）",
        "",
    ]

    for cat in sorted_categories:
        # 與 GitHub 標題錨點規則一致：空白轉 "-"、移除標點但不合併連續的 "-"
        # （"Cloud Storage & Backup" -> "cloud-storage--backup"）
        anchor = re.sub(r"[^a-z0-9_\-]", "", cat.lower().replace(" ", "-"))
        lines.append(f"- [{cat}](#{anchor}) ({len(grouped[cat])})")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 精選高頻核心 API 快速調用範本")
    lines.append("")
    lines.append("以下精選常見高品質免費端點，可直接在終端機 `curl` 或在前端 Generative UI `fetch()` 調用：")
    lines.append("")
    lines.append("### 1. Open-Meteo（全球氣象即時預報）")
    lines.append("```bash")
    lines.append('curl -s "https://api.open-meteo.com/v1/forecast?latitude=25.0330&longitude=121.5654&current_weather=true"')
    lines.append("```")
    lines.append("```javascript")
    lines.append("const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=25.0330&longitude=121.5654&current_weather=true');")
    lines.append("const data = await res.json();")
    lines.append("console.log('當前氣溫:', data.current_weather.temperature);")
    lines.append("```")
    lines.append("")
    lines.append("### 2. PokéAPI（寶可夢圖鑑與資料）")
    lines.append("```bash")
    lines.append('curl -s "https://pokeapi.co/api/v2/pokemon/ditto"')
    lines.append("```")
    lines.append("```javascript")
    lines.append("const res = await fetch('https://pokeapi.co/api/v2/pokemon/ditto');")
    lines.append("const ditto = await res.json();")
    lines.append("console.log('名稱:', ditto.name, '體重:', ditto.weight);")
    lines.append("```")
    lines.append("")
    lines.append("### 3. Open Library（全球圖書書籍檢索）")
    lines.append("```bash")
    lines.append('curl -s "https://openlibrary.org/search.json?q=the+lord+of+the+rings&limit=1"')
    lines.append("```")
    lines.append("```javascript")
    lines.append("const res = await fetch('https://openlibrary.org/search.json?q=the+lord+of+the+rings&limit=1');")
    lines.append("const books = await res.json();")
    lines.append("console.log('找到書籍數:', books.numFound);")
    lines.append("```")
    lines.append("")
    lines.append("### 4. JSONPlaceholder（假資料 RESTful CRUD 測試）")
    lines.append("```bash")
    lines.append('curl -s "https://jsonplaceholder.typicode.com/posts/1"')
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 分類詳細清單")
    lines.append("")

    for cat in sorted_categories:
        cat_entries = grouped[cat]
        lines.append(f"### {cat}")
        lines.append("")
        lines.append("| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for e in cat_entries:
            safe_name = e.name.replace("|", "/")
            link = f"[{safe_name}]({e.url})" if e.url else safe_name
            https_str = "Yes" if e.https else "No"
            # 清理說明文字中的表格分隔符
            clean_desc = e.description.replace("|", "/")
            lines.append(f"| {link} | {clean_desc} | {e.auth} | {https_str} | {e.cors} |")
        lines.append("")

    return "\n".join(lines)


def locate_source_file(custom_path: Optional[str] = None) -> Path:
    """定位 public-apis 的 README.md 路徑。"""
    if custom_path:
        p = Path(custom_path)
        if p.is_file():
            return p
        raise FileNotFoundError(f"找不到指定的 Public APIs 來源檔案: {custom_path}")

    for p in DEFAULT_SOURCE_PATHS:
        if p.is_file():
            return p

    raise FileNotFoundError(
        "無法在預設路徑中找到 Public APIs 來源檔案 (README.md)。"
        "請使用 --source 指定路徑，例如 C:\\GitHub\\public-apis\\README.md"
    )


def main() -> int:
    # 要在解析參數之前設定：--help 由 argparse 直接印出，晚設就會用系統編碼（Windows cp950）輸出成亂碼
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass

    parser = argparse.ArgumentParser(
        description="Public APIs 本地離線索引與免金鑰 API 篩選工具"
    )
    parser.add_argument(
        "--source",
        "-s",
        help="public-apis 倉庫的 README.md 路徑（預設自動尋找 C:\\GitHub\\public-apis\\README.md）",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="輸出 Markdown 手冊路徑（例如 docs/free-public-apis.md）",
    )
    parser.add_argument(
        "--json-output",
        "-j",
        help="輸出 JSON 結構化檔案路徑",
    )
    parser.add_argument(
        "--auth",
        default="no",
        help="篩選 Auth 模式 (no, apiKey, OAuth, all; 預設: no)",
    )
    parser.add_argument(
        "--cors",
        default="yes",
        help="篩選 CORS 模式 (yes, no, unknown, all; 預設: yes)",
    )
    parser.add_argument(
        "--category",
        "-c",
        help="依分類名稱篩選（例如 Weather, Books, Finance）",
    )
    parser.add_argument(
        "--search",
        "-q",
        help="關鍵字搜尋 API 名稱或描述",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="僅輸出統計摘要",
    )

    args = parser.parse_args()

    try:
        source_path = locate_source_file(args.source)
    except FileNotFoundError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    try:
        content = source_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as err:
        print(f"[ERROR] 無法讀取來源檔案 {source_path}: {err}", file=sys.stderr)
        return 1
    all_entries = parse_markdown_table_rows(content)

    filtered = filter_apis(
        all_entries,
        auth=args.auth,
        cors=args.cors,
        category=args.category,
        search=args.search,
    )

    grouped = group_by_category(filtered)

    print(f"[*] 來源檔案: {source_path}")
    print(f"[*] 總解析條目: {len(all_entries)} 筆")
    print(f"[*] 符合條件條目 (Auth: {args.auth}, CORS: {args.cors}): {len(filtered)} 筆")
    print(f"[*] 涵蓋分類數: {len(grouped)} 個")

    if args.summary:
        print("\n各分類項目分佈：")
        for cat, items in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  - {cat}: {len(items)}")
        return 0

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        md_text = generate_markdown(filtered, auth=args.auth, cors=args.cors)
        out_path.write_text(md_text, encoding="utf-8")
        print(f"[+] 已產出 Markdown 手冊: {out_path.resolve()}")

    if args.json_output:
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "source": str(source_path),
            "filters": {"auth": args.auth, "cors": args.cors},
            "total_count": len(filtered),
            "categories_count": len(grouped),
            "apis": [e.to_dict() for e in filtered],
        }
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[+] 已產出 JSON 結構化索引: {json_path.resolve()}")

    # 若未指定 output 也未指定 json_output，預設產出 docs/free-public-apis.md
    if not args.output and not args.json_output:
        default_out = Path(__file__).resolve().parent.parent / "docs" / "free-public-apis.md"
        default_out.parent.mkdir(parents=True, exist_ok=True)
        md_text = generate_markdown(filtered, auth=args.auth, cors=args.cors)
        default_out.write_text(md_text, encoding="utf-8")
        print(f"[+] 已產出預設 Markdown 手冊: {default_out.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
