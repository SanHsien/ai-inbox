#!/usr/bin/env python3
"""
tools/verify_generative_ui_assets.py
assets/ 全庫 6 個單檔 HTML Generative UI 互動展示之「外部裁判」結構與安全驗證器（純 Python stdlib）。

驗證規格：
1. 檔案存在性與基礎 HTML5 結構：
   - 6 個 HTML 檔案皆存在於 assets/ 下；
   - 具備 <!DOCTYPE html> 宣告（不分大小寫）；
   - 具備 UTF-8 編碼宣告（<meta charset="UTF-8"> 等）；
   - 具備非空 <title> 標籤。
2. 外部資源引用安全性：
   - 所有外部 <script src="..."> 與 <link href="..."> 若為外部網址一律使用 https://；
   - 嚴禁 http:// 明文傳輸；
   - 嚴禁使用 file:// 協定或指向本機磁碟路徑（如 C:\\ 或 C:/）。
3. 核心契約與特定檔案安全規範：
   - assets/openlibrary_demo/video_seek_canvas.html 必須實作 seek 時間函式契約；
   - assets/health-bank-dashboard/index.html 不得含有未遮蔽之台灣身分證字號格式，且必須包含免責聲明。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _judge_common import (  # noqa: E402
    doc_guard,
    ensure_utf8_output,
    find_repo_root as _common_find_repo_root,
    report_results,
    strip_html_comments,
)

# 6 個標準 Generative UI HTML 資產相對路徑
EXPECTED_HTML_ASSETS: List[str] = [
    "assets/anti-slop-demo/index.html",
    "assets/target-story-editor/index.html",
    "assets/health-bank-dashboard/index.html",
    "assets/open-meteo-weather-chart/index.html",
    "assets/creative-coding-demo/threejs-particle-galaxy.html",
    "assets/openlibrary_demo/video_seek_canvas.html",
]

# DOCTYPE 正則（不分大小寫）
DOCTYPE_RE = re.compile(r"<!DOCTYPE\s+html>", re.IGNORECASE)

# UTF-8 charset 正則
CHARSET_UTF8_RE = re.compile(r'<meta[^>]+charset=["\']?utf-8["\']?', re.IGNORECASE)

# 非空 title 標籤正則
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)

# script src 與 link href 正則
SCRIPT_SRC_RE = re.compile(r'<script\b[^>]*\bsrc=["\']([^"\']+)["\']', re.IGNORECASE)
LINK_HREF_RE = re.compile(r'<link\b[^>]*\bhref=["\']([^"\']+)["\']', re.IGNORECASE)

# seek 時間函式契約正則（支援 function seek(、window.seek =、const/let seek =）
SEEK_CONTRACT_RE = re.compile(
    r"(?:function\s+seek\s*\(|window\.seek\s*=\s*(?:function|\()|const\s+seek\s*=\s*(?:function|\()|let\s+seek\s*=\s*(?:function|\())"
)

# 台灣身分證字號正則（1 個大寫字母 + 1/2/8/9 + 8 個數字，防範真實個資外洩）
TW_ID_RE = re.compile(r"\b[A-Z][1289]\d{8}\b")

# 本機磁碟路徑正則（如 C:\ 或 D:/）
LOCAL_DRIVE_RE = re.compile(r"^[a-zA-Z]:[/\\]")


def find_repo_root(start: Optional[Path] = None) -> Path:
    """自動推導 repository 根目錄（共用實作見 _judge_common）。"""
    return _common_find_repo_root(start, markers=('assets', 'tools'), anchor=Path(__file__))


def verify_html_baseline(html_content: str, rel_path: str = "") -> List[str]:
    """
    驗證 HTML 基礎結構：
    - 具備 <!DOCTYPE html> 宣告；
    - 具備 UTF-8 編碼宣告；
    - 具備非空 <title> 標籤。
    """
    errors: List[str] = []
    prefix = f"[{rel_path}] " if rel_path else ""

    # 1. DOCTYPE 校驗
    if not DOCTYPE_RE.search(html_content):
        errors.append(f"{prefix}缺少標準 HTML5 <!DOCTYPE html> 宣告")

    # 2. UTF-8 charset 校驗
    if not CHARSET_UTF8_RE.search(html_content):
        errors.append(f"{prefix}缺少 UTF-8 編碼宣告 (<meta charset=\"UTF-8\">)")

    # 3. Title 標籤校驗
    title_match = TITLE_RE.search(html_content)
    if not title_match:
        errors.append(f"{prefix}缺少 <title> 標籤")
    else:
        title_text = title_match.group(1).strip()
        if not title_text:
            errors.append(f"{prefix}<title> 標籤內容不可為空")

    return errors


def verify_asset_security_urls(html_content: str, rel_path: str = "") -> List[str]:
    """
    驗證外部資源引用安全：
    - 所有外部 <script src="..."> 與 <link href="..."> 若為外部網址一律使用 https://；
    - 嚴禁 http:// 明文傳輸；
    - 嚴禁使用 file:// 協定或本機路徑（如 C:\\ 或 C:/）。
    """
    errors: List[str] = []
    prefix = f"[{rel_path}] " if rel_path else ""

    src_urls = SCRIPT_SRC_RE.findall(html_content)
    href_urls = LINK_HREF_RE.findall(html_content)
    all_urls = [("script src", u) for u in src_urls] + [("link href", u) for u in href_urls]

    for tag_type, url in all_urls:
        url_clean = url.strip()

        # 檢測明文 http://
        if url_clean.lower().startswith("http://"):
            errors.append(
                f"{prefix}{tag_type} 使用不安全的明文 HTTP 協定：'{url_clean}'，外部資源一律必須使用 https://"
            )

        # 檢測協議相對路徑 //（要求顯式 https://）
        elif url_clean.startswith("//"):
            errors.append(
                f"{prefix}{tag_type} 使用協定相對路徑：'{url_clean}'，外部資源必須明確指定 https://"
            )

        # 檢測 file:// 協定
        elif url_clean.lower().startswith("file://"):
            errors.append(
                f"{prefix}{tag_type} 引用禁止使用本機 file:// 協定：'{url_clean}'"
            )

        # 檢測本機絕對路徑（如 C:\path 或 C:/path）
        elif LOCAL_DRIVE_RE.match(url_clean):
            errors.append(
                f"{prefix}{tag_type} 引用禁止指向本機磁碟絕對路徑：'{url_clean}'"
            )

    return errors


def verify_video_seek_contract(html_content: str, rel_path: str = "") -> List[str]:
    """
    驗證 Code-as-Video 示範之 seek 時間函式契約：
    - openlibrary_demo/video_seek_canvas.html 必須實作 seek(t) 契約。
    """
    errors: List[str] = []
    prefix = f"[{rel_path}] " if rel_path else ""

    # 剝除 JS 註解（/* */ 與整行 //），避免註解中的 function seek( 騙過檢查
    code = re.sub(r"/\*[\s\S]*?\*/", "", html_content)
    code = re.sub(r"(?m)^[ \t]*//.*$", "", code)
    if not SEEK_CONTRACT_RE.search(code):
        errors.append(
            f"{prefix}未實作 seek 時間函式契約（必須包含 function seek(...) 或 window.seek = ...）"
        )

    return errors


def verify_health_bank_privacy_and_disclaimer(html_content: str, rel_path: str = "") -> List[str]:
    """
    驗證健康存摺展示安全與隱私規範：
    - 不含未遮蔽之真實台灣身分證字號格式（防範個資外洩）；
    - 必須包含醫療免責聲明。
    """
    errors: List[str] = []
    prefix = f"[{rel_path}] " if rel_path else ""

    # 1. 檢測身分證字號格式
    id_matches = TW_ID_RE.findall(html_content)
    if id_matches:
        masked_ids = [m[:3] + "****" + m[-3:] for m in id_matches]
        errors.append(
            f"{prefix}檢測到疑似未遮蔽之身分證字號格式：{masked_ids}，示範資料必須脫敏"
        )

    # 2. 檢測免責聲明
    has_disclaimer = "免責聲明" in html_content or "免責" in html_content
    if not has_disclaimer:
        errors.append(f"{prefix}缺少健康資訊或醫療免責聲明文字")

    return errors


def verify_single_html_asset(html_content: str, rel_path: str) -> List[str]:
    """
    對指定相對路徑的 HTML 檔案執行完整規則校驗。
    """
    errors: List[str] = []
    # 註解內的內容不會被瀏覽器執行或顯示，不得讓它滿足「必須存在」的檢查
    html_content = strip_html_comments(html_content)

    # 通用規則 1：基礎 HTML5 結構
    errors.extend(verify_html_baseline(html_content, rel_path))

    # 通用規則 2：外部資源安全性
    errors.extend(verify_asset_security_urls(html_content, rel_path))

    # 專屬規則 3：video_seek_canvas.html 時間函式契約
    norm_path = rel_path.replace("\\", "/")
    if "video_seek_canvas.html" in norm_path:
        errors.extend(verify_video_seek_contract(html_content, rel_path))

    # 專屬規則 4：health-bank-dashboard/index.html 隱私與免責聲明
    if "health-bank-dashboard" in norm_path:
        errors.extend(verify_health_bank_privacy_and_disclaimer(html_content, rel_path))

    return errors


def verify_all_generative_ui_assets(
    repo_root: Optional[Path] = None,
) -> Tuple[bool, Dict[str, List[str]]]:
    """
    驗證 assets/ 目錄下全數 6 個 HTML 展示檔。
    傳回：(是否全數通過, {檔案相對路徑: 錯誤清單})
    """
    root = repo_root or find_repo_root()
    results: Dict[str, List[str]] = {}

    for rel_path in EXPECTED_HTML_ASSETS:
        file_path = root / rel_path
        if not file_path.is_file():
            results[rel_path] = [f"目標展示檔案不存在：{rel_path}"]
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as ex:
            results[rel_path] = [f"無法以 UTF-8 讀取檔案內容：{ex}"]
            continue

        errors = verify_single_html_asset(content, rel_path)
        results[rel_path] = errors

    all_passed = all(len(errs) == 0 for errs in results.values())
    return all_passed, results


def main(argv: Optional[List[str]] = None) -> int:
    ensure_utf8_output()
    parser = argparse.ArgumentParser(
        description="assets/ 全庫 6 個單檔 HTML Generative UI 互動展示之外部裁判結構與安全驗證器"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="專案根目錄（預設自動搜尋包含 assets/ 與 tools/ 之目錄）",
    )
    args = parser.parse_args(argv)

    root = find_repo_root(args.repo_root)
    print(f"[*] 執行 Generative UI 互動展示資產結構與安全驗證，根目錄：{root}")

    all_passed, results = verify_all_generative_ui_assets(root)

    return report_results(
        results,
        success_msg='全數 6 個 Generative UI HTML 展示檔均通過外部裁判結構與安全驗證！',
        fail_label='安全或結構缺陷',
        ok_label='結構與安全規範完全相符',
        fail_msg='外部裁判驗證未通過，請修復上述問題。',
    )


if __name__ == "__main__":
    sys.exit(main())
