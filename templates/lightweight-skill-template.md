---
name: your-skill-name
description: Does one specific job in one sentence, for example converting meeting notes into action items. Use when the user mentions meeting notes, minutes, transcripts, or asks for action items. 當使用者提到會議記錄或逐字稿時使用。
---

# 輕量化 Agent Skill 範本

> 規範：[`docs/agent-skills-curation-and-context-budget-spec.md`](../docs/agent-skills-curation-and-context-budget-spec.md)｜檢查：`tools/audit_skills_context_budget.py`
> 用法：複製成 `<skills 目錄>/<name>/SKILL.md`，資料夾名要等於 frontmatter 的 `name`；改完刪掉「## 範本使用說明」以下全部（含本行以上的這段引言）。

## 何時用 / When to use

- 觸發：使用者說了 {觸發詞 1}、{觸發詞 2}，或貼了 {檔案類型}。
- 不要用：{相近但不該觸發的情境}（交給 `other-skill`）。

## 前置檢查 / Preflight

1. 需要的輸入：{檔案／參數}。缺了就問使用者，不要猜。
2. 需要的工具：{指令或套件}。先確認存在再往下。

## 步驟 / Steps

1. {動詞開頭的一個動作}。
2. {下一個動作}。需要細節時讀同資料夾的 `reference.md`（只放一層連結，檔案要真的存在）。
3. 驗證：{可執行的檢查，例如 `python scripts/check.py out.json`}；失敗就回到第 2 步。

## 輸出 / Output

- 格式：{固定模板或欄位}。
- 完成條件：{可觀察的結果}，缺一項就不算完成。

## 邊界 / Boundaries

- 只改 {範圍}；不碰 {範圍外}。
- 破壞性動作（刪除、覆寫、推送）先取得使用者同意。

---

## 範本使用說明（交付前刪除）

### 反映規範的硬規則

| 項目 | 規則 |
| :--- | :--- |
| `name` | 小寫字母、數字、連字號，≤ 64 字元；不含 `anthropic`／`claude`；與資料夾同名 |
| `description` | ≤ 1,024 字元；第三人稱；第一句做什麼，第二句何時用；建議 ≤ 150 tokens |
| 本文 | ≤ 8,192 bytes（本 repo 政策）；官方建議 < 500 行；細節拆附屬檔案 |
| 連結 | 附屬檔案只從 SKILL.md 直接連一層；路徑用正斜線 |

### 中英雙語撰寫指引

- description 用一種主要語言即可；要雙語就各一句、不重複同一件事（雙語會讓常駐成本接近兩倍）。
- 中文每字約 1 token、英文約 4 字元 1 token（本 repo 估算法，未實測）：同樣資訊中文通常較省。
- 步驟用動詞開頭：「讀取…」「執行…」/ "Read…", "Run…"。一個步驟一個動作。
- 同一概念全篇用同一個詞（例如固定用「輸出」，不要混用「結果」「產物」）。
- 不寫模型本來就知道的背景知識；每段先問「刪掉會不會做錯？」。

### 反範例 / Anti-patterns

```yaml
# 壞：沒有觸發時機、第一人稱、太泛
description: I can help you with documents
# 壞：只說做什麼，沒說何時用
description: Processes data
# 壞：name 含保留字與底線
name: Claude_Helper
```

- 壞：本文貼整份官方文件或長篇背景 → 改成連結附屬檔案，或不寫。
- 壞：「必須」「永遠」「禁止」滿篇 → 只留給硬閘門，其餘寫預設與例外。
- 壞：與全域規則重述同一件事 → 引用規則，寫「以全域規則為準」。
- 壞：一個技能做兩件不相干的事 → 拆成兩個技能。
- 壞：檔內放日期或版本號當條件 → 放「舊做法」區塊。

### 交付前檢查

```bash
mkdir -p /tmp/skills-check/your-skill-name
cp templates/lightweight-skill-template.md /tmp/skills-check/your-skill-name/SKILL.md
python tools/audit_skills_context_budget.py /tmp/skills-check --strict   # 退出碼 0 才算通過
```
