#!/usr/bin/env python3
"""
tools/verify_re_and_android_specs.py
逆向工程流水線（REA + CLI-Anything）與 Android 官方 33 Skills 防幻覺規範之「外部裁判」結構驗證器（純 Python stdlib）。

驗證目標：
1. docs/reverse-engineering-pipeline-spec.md：
   - 驗證「觀測行為」「理解結構」「重造功能」三階段運作模型；
   - 驗證 Cleanroom（無菌室）重造規範（防版權污染、I/O 契約、Agent-Native 乾淨實作）；
   - 驗證明確將 desktop-sense 標註為「選用、未採用」並附理由。
2. docs/rea-sandbox-evaluation-evidence.md：
   - 驗證 Adoptium JDK 21 與 Ghidra 12.2 的 SHA-256 官方與本地雜湊比對（MATCH）；
   - 驗證 Electron app.asar 解包統計與原始碼隔離政策；
   - 驗證系統環境變數 PATH 與全域登錄檔零變更/零污染結論，及未改寫正式 Agent 配置。
3. docs/android-official-skills-anti-hallucination.md：
   - 驗證 33 個官方 Skills 完整盤點表格與代表性技能；
   - 驗證 XML View 遷移至 Jetpack Compose 之現代防幻覺規範（廢除 findViewById/ViewBinding/synthetic、UDF、LazyColumn 等）；
   - 驗證 Google Play Billing 與 Policy Insights 政策合規審查防線（AcknowledgePurchaseParams、Data Safety 與權限宣告一致性）。
4. docs/android-cli-plugin-windows-validation.md：
   - 驗證對官方 install.cmd 修改 Windows 全域 Registry PATH (HKCU\\Environment) 之安全攔截與違規記錄；
   - 驗證對超過 1 GB（1.5 GB ~ 3.5 GB）下載硬閘門之觸發停下與安全審查記錄；
   - 驗證提出無侵入式沙盒安裝架構建議。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


def find_repo_root(start: Optional[Path] = None) -> Path:
    """自動推導 repository 根目錄。"""
    if start is not None:
        return start.resolve()
    cur = Path(__file__).resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "notes").is_dir() and (parent / "docs").is_dir():
            return parent
    return Path.cwd()


def load_content(source: Union[Path, str]) -> str:
    """載入內容。支援傳入 Path 物件、檔案路徑字串或原始文字內容。

    安全規範：切勿對多行內文字串直接呼叫 Path(arg).exists()，
    以避免在 Linux CI 上觸發 ENAMETOOLONG (Errno 36)。
    """
    if isinstance(source, Path):
        return source.read_text(encoding="utf-8")
    if isinstance(source, str):
        # 僅在單行且長度合理的情形下嘗試當成檔案路徑檢查
        if "\n" not in source and len(source) < 240:
            try:
                p = Path(source)
                if p.is_file():
                    return p.read_text(encoding="utf-8")
            except OSError:
                pass
        return source
    raise TypeError(f"不支援的參數型別：{type(source)}")


def verify_re_pipeline_spec(source: Union[Path, str]) -> List[str]:
    """驗證 docs/reverse-engineering-pipeline-spec.md：

    - 驗證「觀測行為」「理解結構」「重造功能」三階段
    - 驗證 Cleanroom（無菌室）重造規範
    - 驗證明確將 desktop-sense 標註為「選用、未採用」
    """
    text = load_content(source)
    errors: List[str] = []

    # 1. 驗證三階段運作模型
    has_stage1 = bool(re.search(r"阶段一|階段一.*?(?:動態行為觀測|行為觀測)", text)) and (
        "行為觀測" in text or "Behavior Observation" in text
    )
    has_stage2 = bool(re.search(r"阶段二|階段二.*?(?:結構反編譯|結構逆向)", text)) and (
        "結構" in text or "Structural Decompilation" in text
    )
    has_stage3 = bool(re.search(r"阶段三|階段三.*?(?:無菌室乾淨重造|無菌重造|Cleanroom)", text)) and (
        "Cleanroom" in text or "無菌" in text or "重造" in text
    )

    if not has_stage1:
        errors.append("缺少階段一「行為觀測 (Behavior Observation)」之規格定義")
    if not has_stage2:
        errors.append("缺少階段二「結構逆向／反編譯 (Structural Decompilation)」之規格定義")
    if not has_stage3:
        errors.append("缺少階段三「無菌室乾淨重造 (Cleanroom Re-implementation)」之規格定義")

    # 2. 驗證 Cleanroom 重造規範
    has_cleanroom_heading = bool(re.search(r"(?:Cleanroom|無菌室)", text))
    has_copyright_guard = "防版權污染" in text or "不複製任何反編譯程式碼" in text or "不複製" in text
    has_agent_native = "Agent-Native" in text or "重新實作核心演算法" in text
    has_spec_driven = "規格定義" in text or "I/O 契約" in text or "I/O" in text

    if not (has_cleanroom_heading and has_copyright_guard and (has_agent_native or has_spec_driven)):
        errors.append("缺少 Cleanroom 無菌室重造規範（需明載防版權污染、僅依規格/I/O契約與 Agent-Native 乾淨實作）")

    # 3. 驗證 desktop-sense 標註為「選用、未採用」
    if "desktop-sense" not in text:
        errors.append("缺少組件矩陣中對 desktop-sense 的分析說明")
    else:
        has_not_adopted = "選用、未採用" in text
        has_adopted_erroneously = bool(re.search(r"\|\s*\*\*desktop-sense\*\*.*?(?:【核心採用】|核心採用|已採用)", text))
        has_rejection_reason = "未採用理由" in text or "隱私" in text or "Token" in text
        if not has_not_adopted or has_adopted_erroneously or not has_rejection_reason:
            errors.append("未明確將 desktop-sense 標註為「選用、未採用」或缺少具體排除理由（隱私安全/Token開銷/替代方案）")

    return errors


def verify_rea_sandbox_evidence(source: Union[Path, str]) -> List[str]:
    """驗證 docs/rea-sandbox-evaluation-evidence.md：

    - 驗證 SHA-256 校驗（JDK 21 與 Ghidra 12.2 官方與本地雜湊比對 MATCH）
    - 驗證 ASAR 解包統計與原始碼隔離政策
    - 驗證系統 PATH 零污染、登錄檔零變更與未改寫正式 Agent 配置結論
    """
    text = load_content(source)
    errors: List[str] = []

    # 1. 驗證 SHA-256 校驗
    has_sha256 = "SHA-256" in text
    sha256_hashes = re.findall(r"\b[0-9a-f]{64}\b", text)
    has_jdk = "Adoptium" in text or "JDK 21" in text or "jdk-21" in text
    has_ghidra = "Ghidra" in text
    has_match = "MATCH" in text or "完全一致" in text

    if not (has_sha256 and len(sha256_hashes) >= 2 and has_jdk and has_ghidra and has_match):
        errors.append("缺少 Adoptium JDK 21 與 NSA Ghidra 之官方與本地下載 SHA-256 逐字節 MATCH 比對紀錄")

    # 2. 驗證 ASAR 解包與原始碼隔離政策
    has_asar = "app.asar" in text or "ASAR" in text
    has_unpack_stats = bool(
        "node_count" in text and "occurrence_count" in text and ("1,221" in text or "1221" in text)
    )
    has_isolation_policy = (
        ("沙盒暫存區" in text or "%TEMP%" in text)
        and ("未寫入任何 Git 倉庫" in text or "嚴禁 commit" in text)
    )

    if not (has_asar and has_unpack_stats):
        errors.append("缺少 Electron 應用 app.asar 之解包統計數據與模組分析證據")
    if not has_isolation_policy:
        errors.append("缺少解包原始碼留存於隔離沙盒暫存區且嚴禁入庫（零 Git 污染）之安全隔離政策")

    # 3. 驗證系統 PATH 零污染與環境清潔度結論
    has_path_zero = bool(re.search(r"(?:系統環境變數 PATH|PATH).*?(?:零變更|零污染|不更動系統 PATH)", text))
    has_reg_zero = bool(re.search(r"(?:全域登錄檔|登錄檔).*?(?:零變更|不寫入系統登錄檔)", text))
    has_agent_unmodified = "未改寫" in text or "npx rea-agents setup" in text or "完全未改寫" in text

    if not (has_path_zero and has_reg_zero and has_agent_unmodified):
        errors.append("缺少環境清潔度結論（需記錄全域登錄檔零變更、系統 PATH 零變更/零污染，及未改寫正式 Agent 配置）")

    return errors


def verify_android_skills_anti_hallucination(source: Union[Path, str]) -> List[str]:
    """驗證 docs/android-official-skills-anti-hallucination.md：

    - 驗證 33 個官方 Skills 全景盤點表格與代表性技能
    - 驗證 XML View 遷移至 Jetpack Compose 之現代防幻覺規範
    - 驗證 Google Play Billing 與 Policy Insights 政策合規審查防線
    """
    text = load_content(source)
    errors: List[str] = []

    # 1. 驗證 33 個官方 Skills 清單
    has_33_claim = "33 個" in text or "33 個 Skills" in text

    # 解析 Markdown 表格項目
    table_rows: List[str] = []
    for line in text.splitlines():
        line_str = line.strip()
        if re.match(r"^\|\s*\d+\s*\|", line_str):
            table_rows.append(line_str)

    skill_count = len(table_rows)
    if not (has_33_claim and skill_count >= 33):
        errors.append(f"官方 Skills 清單盤點不足 33 個（表格解析出 {skill_count} 個項目）")

    # 檢查關鍵代表性技能存在
    required_key_skills = [
        "agp-9-upgrade",
        "camerax",
        "migrate-xml-views-to-jetpack-compose",
        "play-billing-library-version-upgrade",
        "play-policy-insights",
        "projected-hardware",
    ]
    missing_key_skills = [s for s in required_key_skills if s not in text]
    if missing_key_skills:
        errors.append(f"Skills 盤點清單遺漏核心關鍵技能：{', '.join(missing_key_skills)}")

    # 2. 驗證 XML View 遷移至 Jetpack Compose 之現代防幻覺規範
    has_compose_heading = bool(re.search(r"XML View 遷移至 Jetpack Compose", text))
    has_toxic_views_ban = bool(re.search(r"findViewById", text)) and bool(re.search(r"ViewBinding", text)) and (
        "kotlinx.android.synthetic" in text or "synthetic" in text
    )
    has_udf = "單向流" in text or "UDF" in text or "StateFlow" in text or "rememberSaveable" in text
    has_lazy_list = "LazyColumn" in text or "derivedStateOf" in text or "remember(" in text

    if not (has_compose_heading and has_toxic_views_ban and has_udf and has_lazy_list):
        errors.append("缺少 XML View 遷移至 Jetpack Compose 之完整防幻覺規範（需禁止 findViewById/ViewBinding/synthetic、要求 UDF 與 LazyColumn 重組優化）")

    # 3. 驗證 Google Play Billing 與 Policy Insights 政策合規審查防線
    has_billing_heading = "Play Billing" in text and "Policy Insights" in text
    has_acknowledge = "AcknowledgePurchaseParams" in text
    has_data_safety = "Data Safety" in text or "資料安全" in text or "權限宣告" in text

    if not (has_billing_heading and has_acknowledge and has_data_safety):
        errors.append("缺少 Google Play Billing 與 Policy Insights 政策合規審查防線（需包含 AcknowledgePurchaseParams 確認閉環與 Data Safety 權限宣告一致性）")

    return errors


def verify_android_cli_validation(source: Union[Path, str]) -> List[str]:
    """驗證 docs/android-cli-plugin-windows-validation.md：

    - 驗證對官方 install.cmd 修改 Windows 全域 Registry PATH 之安全攔截與違規記錄
    - 驗證對超過 1 GB（1.5 GB ~ 3.5 GB）下載硬閘門之觸發停下與安全審查記錄
    - 驗證提出無侵入式沙盒安裝架構建議
    """
    text = load_content(source)
    errors: List[str] = []

    # 1. 驗證修改 Registry PATH 違規攔截
    has_reg_mention = "HKCU\\Environment" in text or "HKCU" in text
    has_reg_violation = (
        ("強制修改系統註冊表" in text or "Registry Violation" in text)
        and ("不改 PATH" in text or "不得修改系統設定" in text)
    )
    if not (has_reg_mention and has_reg_violation):
        errors.append("缺少對官方 install.cmd 企圖強制覆寫 Windows 全域 Registry Path (HKCU\\Environment) 之違規審查與攔截紀錄")

    # 2. 驗證超過 1 GB 下載硬閘門觸發停下
    has_size_mention = "1 GB" in text or "1.5 GB" in text or "3.5 GB" in text
    has_gate_triggered = (
        "硬閘門觸發停下" in text
        or "需要下載超過 1 GB 就停在那一項" in text
        or "超過 1 GB 就停在那一項" in text
    )
    has_stop_download = "不執行遠端安裝腳本" in text or "不執行" in text or "停在那一項" in text

    if not (has_size_mention and has_gate_triggered and has_stop_download):
        errors.append("缺少對 Android SDK 依賴超過 1 GB（1.5 GB ~ 3.5 GB）下載硬閘門之觸發停下與安全評估結論")

    # 3. 驗證無侵入式沙盒安裝架構建議
    has_sandbox_proposal = "沙盒安裝" in text or "無侵入式沙盒安裝架構" in text or "_sandbox\\android-cli" in text
    if not has_sandbox_proposal:
        errors.append("缺少綠色沙盒化安裝與無侵入式架構建議（如 _sandbox\\android-cli 目錄與隔離腳本）")

    return errors


def verify_all_specs(repo_root: Optional[Path] = None) -> Tuple[bool, Dict[str, List[str]]]:
    """執行全數逆向工程與 Android 官方規格外部裁判驗證。"""
    root = repo_root or find_repo_root()
    results: Dict[str, List[str]] = {}

    targets = [
        ("docs/reverse-engineering-pipeline-spec.md", verify_re_pipeline_spec),
        ("docs/rea-sandbox-evaluation-evidence.md", verify_rea_sandbox_evidence),
        ("docs/android-official-skills-anti-hallucination.md", verify_android_skills_anti_hallucination),
        ("docs/android-cli-plugin-windows-validation.md", verify_android_cli_validation),
    ]

    for rel_path, verifier in targets:
        full_path = root / rel_path
        if not full_path.exists():
            results[rel_path] = [f"目標檔案不存在：{rel_path}"]
        else:
            results[rel_path] = verifier(full_path)

    all_passed = all(len(errs) == 0 for errs in results.values())
    return all_passed, results


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="逆向工程流水線（REA + CLI-Anything）與 Android 官方 33 Skills 防幻覺規範之外部裁判結構驗證器"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="專案根目錄（預設自動搜尋包含 notes/ 與 docs/ 之根目錄）",
    )
    args = parser.parse_args(argv)

    root = find_repo_root(args.repo_root)
    print(f"[*] 執行外部裁判規格結構校驗，專案根目錄：{root}")

    all_passed, results = verify_all_specs(root)

    for rel_path, errs in results.items():
        if errs:
            print(f"\n[FAIL] ❌ {rel_path} 發現 {len(errs)} 項規格缺陷：")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"[PASS] ✅ {rel_path} 結構與規格契約完全相符")

    if all_passed:
        print("\n[SUCCESS] 🎉 全數逆向工程與 Android 官方規格文件均通過外部裁判結構驗證！")
        return 0
    else:
        print("\n[ERROR] 外部裁判驗證未通過，請依上述錯誤修正文件。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
