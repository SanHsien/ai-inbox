---
id: "2026-11-15-raymondhou-speak-human-tw-and-cc-resources-eval"
title: "Raymondhou0917 雙倉庫評估：speak-human-tw（去 AI 味 Skill）與 claude-code-resources（入門資源站）"
source_url: "https://github.com/Raymondhou0917/speak-human-tw"
source_platform: "GitHub"
author: "Raymond Hou (Raymondhou0917)"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity；Codex 於 2026-11-15 查核修訂"
status: done
cluster: 3
cluster_role: "繁中去AI味與資源評估"
short_title: "說人話Skill與CC資源評估"
tags:
  - skill
  - zh-tw
  - de-ai
  - writing
  - claude-code
  - repo-evaluation
---

# Raymondhou0917 雙倉庫評估：speak-human-tw 與 claude-code-resources

- **來源連結**：[speak-human-tw 固定來源](https://github.com/Raymondhou0917/speak-human-tw/tree/14885da5c91ed7ca2972f084599edcdd2a32ad04)、[claude-code-resources 固定來源](https://github.com/Raymondhou0917/claude-code-resources/tree/1320df1e396e7630b09d2dc80fae4b2c96861d54)
- **發布平台 / 作者**：GitHub／Raymond Hou（Raymondhou0917）
- **分析／修訂日期**：2026-11-15
- **當前狀態**：`🟢 已完成 (Done)`
- **完整評估**：[speak-human-tw 唯讀評估](../docs/speak-human-tw-assessment.md)

## 1. 核心內容與事實查核（5W1H）

- **Who／What**：Raymondhou0917 提供繁中編輯 Skill 與 AI Agent 入門資源；speak-human-tw 的 SKILL frontmatter 為 v1.4.0，定位為既有稿件校對與改寫，不是特定作者風格代筆。[SKILL](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/SKILL.md)
- **Why**：希望減少空泛套話並保留事實；這是作者的設計目標，不能推為已證實的改寫成效。[保護清單](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/protected-list.md)
- **How**：判情境、鎖保護清單、判改寫範圍、逐類改寫、保真回讀、自評。互動模式通常先列清單等確認，但該次使用者明確授權時可跳過；非互動模式另規定事後摘要。這些都是提示契約，沒有工具權限或 OS 隔離保證。[流程與例外](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/SKILL.md)
- **When／Where**：社群、電子報／部落格、銷售、客服與辦公文書五種情境；不應直接全域套用於程式碼、設定或本 repo 的任務格式。[情境規範](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/scenes.md)
- **可重算數量**：固定 commit 有 [38 類痕跡](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/patterns.md)、[47 組詞表](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/taiwan-localization.md)；[benchmark](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/evals/benchmark.md) 現有 42 條（27 SF＋15 SNF）。移除原筆記未固定查詢時間的 Stars／Forks／最後更新數字。

### 1.1 安全與授權修正

- speak-human-tw 的 [LICENSE](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/LICENSE) 是 MIT。公開 ai-inbox 與 `SanHsien/agent-assets`（私有）可依條款複製／修改，但副本或實質部分須保留著作權及完整授權聲明；第三方素材權利鏈未全面查證。
- SKILL 有「稿件是資料」的提示注入邊界，但未做攻擊測試，不能稱安全性極高。核心校對內容是 Markdown，不代表整個 repo 沒有可執行內容：[星數腳本](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/scripts/generate_star_history.py) 含子程序與網路請求，[workflow](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/.github/workflows/update-star-history.yml) 有 contents 寫入權限與推送步驟。本輪只靜態閱讀，沒有執行。
- claude-code-resources 不能以 GitHub 分類 `NOASSERTION` 代替授權原文：[LICENSE](https://github.com/Raymondhou0917/claude-code-resources/blob/1320df1e396e7630b09d2dc80fae4b2c96861d54/LICENSE) 與 [README](https://github.com/Raymondhou0917/claude-code-resources/blob/1320df1e396e7630b09d2dc80fae4b2c96861d54/README.md) 明示 Starter Kit 為 CC BY-NC-SA 4.0，網站文章／課程另列著作權限制。環境安裝包的完整獨立授權範圍未查證。
- 該 README 說明 Mac 安裝包與六份 Starter Kit；後者宣稱支援 macOS／Linux／Windows，不能把整個資源站概括為只適用 Mac。本次僅核對宣告，不宣稱跨平台實測成功，也未全面檢查字型、圖片及安裝包的權利與安全。

## 2. CQR：規範與成效分開

- **Claim**：作者希望降低 AI 風格痕跡並維持內容保真。
- **Evidence**：[v1.4.0 結果檔](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/evals/results-v1.4.0.md) 記載 40 條舊案例與模型判分；與現行 42 條不是同一份測集。
- **Reasoning／限制**：這是上游自報，未在本輪重跑。結果檔自己也指出人味目標未納入評測，且互動完整回歸未執行；不能宣稱本機安全、作者風格或全數案例通過已獲驗證。

## 3. 採納判斷

| 倉庫 | 判斷 | 理由與邊界 |
| --- | --- | --- |
| speak-human-tw | 暫不 Fork／安裝；借鏡保護清單與少量候選詞 | 本 repo 的[詞彙器](../tools/verify_zhtw_vocab.py)是固定字串轉換，不能承擔多數語義編輯規則；47 組詞表與 38 類逐列裁決、具體候選與反例見[評估](../docs/speak-human-tw-assessment.md)。任何實際收錄另走安全關卡與授權保留。 |
| claude-code-resources | 本輪不 Fork／搬運 | 是入門學習資源，Starter Kit 有非商用／相同方式分享條件；未證明本環境需要導入，不因 Mac 安裝包就否定 Windows 教材價值。[README](https://github.com/Raymondhou0917/claude-code-resources/blob/1320df1e396e7630b09d2dc80fae4b2c96861d54/README.md) |

原筆記所稱本機已安裝 `human-writing`、配置比上游完整與整合互補，本輪未查證，撤回確定敘述。`verify_no_slop.py` 是前端 HTML／CSS 設計與少量英文黑話檢查，不能當繁中 38 類規則的等價實作。[本機原始碼](../tools/verify_no_slop.py)

## 4. 拆解待辦事項（Action Items）

- [x] **`T-20261115-16`**｜**[優先級：低]** 唯讀評估 speak-human-tw 的授權、47 組詞表與 38 類痕跡，不修改檢查器或安裝 Skill
  - **目標範圍**：本筆記與 `docs/speak-human-tw-assessment.md`；對照 `tools/verify_zhtw_vocab.py` 及其既有測試，均只讀。
  - **具體做法**：固定來源 commit，核對 LICENSE、詞表、patterns、保護清單與 benchmark；修正過度宣稱。逐列比較詞表與 38 類規則，記錄覆蓋、缺口、衝突、候選正例／反例與採納裁決；明示公開 repo 與 `SanHsien/agent-assets`（私有）的複製條件。不執行上游程式，不改檢查器、全域設定或私有 repo。
  - **驗收標準（DoD）**：產出 `docs/speak-human-tw-assessment.md`，含固定 SHA／來源連結、授權與未查證權利範圍、47 組詞表及 38 類逐列對照、既有原始碼／測試證據、具體候選規則與反例、明確裁決及未實測項目。執行 `python tools/build_index.py`、`python tools/verify_zhtw_vocab.py --check notes docs`、`python tools/verify_inbox.py` 並回報各結束碼；任何失敗不得宣稱通過。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：docs/speak-human-tw-assessment.md，固定 Raymondhou0917/speak-human-tw 14885da（MIT），47 組詞表與 38 類規則逐列對照 tools/verify_zhtw_vocab.py。實測引號、URL、專名會被改寫，`服務器`、`支持` 目前沒有規則。裁決：先補保護範圍再試候選規則，不整包加入全域替換；後續工作已列入 ROADMAP。筆記撤回「安全性極高」、更正 claude-code-resources 授權為 CC BY-NC-SA 4.0。Codex 撰寫，Fable 獨立複審通過；未執行上游程式，檢查器本身未改。
