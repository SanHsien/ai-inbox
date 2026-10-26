# Codex／Claude Code／Antigravity：AGENTS.md 起步與 Skill 預算控制手冊

> 查證日期：2026-10-26。對應任務 `T-20261026-29`。
> 來源筆記：`notes/2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md`（影片作者孔老師的教學框架，本文不採信影片內的產品行為描述，一律以官方文件為準）。
> 官方文件連結集中在第 9 節。本機 `codex` 只用 `--help` 唯讀查證（`codex-cli 0.150.0`）。

## 1. 結論

1. 專案根目錄放 `AGENTS.md` 當**單一入口**，各工具啟動時自動讀入，不需每次手動 `@Skill` 重述專案規則。Codex、Claude Code 都有官方支援（見第 2 節）。
2. Skills 是**漸進載入**：啟動時只放 `name`＋`description`，選中後才讀完整 `SKILL.md`。所以預算要管的是「所有 skill 的描述加總」，不是單一 skill 的長度。
3. 影片筆記提的「8KB 預算」不是 Codex 的原文規格。官方數字是：**AGENTS.md 合併上限預設 32 KiB；技能清單上限為模型視窗的 2%，視窗未知時 8,000 字元**。本文第 5 節把它整理成可檢驗的標準。

## 2. 各工具怎麼讀入口檔（官方行為）

| 工具 | 專案指令檔 | 技能目錄 | 來源 |
|------|-----------|---------|------|
| Codex | `AGENTS.md`（每層可用 `AGENTS.override.md` 覆蓋；可用 `project_doc_fallback_filenames` 加備用檔名） | 專案 `.agents/skills`（由 cwd 往上到 repo 根）、使用者 `$HOME/.agents/skills`、管理員 `/etc/codex/skills` | 第 9 節 [1][2] |
| Claude Code | **有 `CLAUDE.md` 時只讀 `CLAUDE.md`**；只有 `AGENTS.md` 時（需 v2.1.277 以上）直接讀 `AGENTS.md`；`CLAUDE.md` 內寫 `@AGENTS.md` 可匯入（最多 4 層） | 專案 `.claude/skills/<name>/SKILL.md`、個人 `~/.claude/skills/` | [3][4] |
| Antigravity | 官方 codelab 未提 `AGENTS.md`／`GEMINI.md`；Gemini API 的 Antigravity Agent 文件稱會載入環境中的 `.agents/AGENTS.md`（此為託管 agent 環境，是否等同桌面 IDE **未查證**） | 專案 `.agents/skills/`、全域 `~/.gemini/config/skills/`（CLI 另有 `~/.gemini/antigravity-cli/skills/`，codelab 兩處矛盾） | [5][6] |

跨工具的共同點：`AGENTS.md` 是開放格式、純 Markdown、離被編輯檔案最近的那份優先（[agents.md](https://agents.md)）。

### Codex 載入順序（官方 [1]）

```text
~/.codex/ (或 $CODEX_HOME)
   AGENTS.override.md > AGENTS.md     <- 全域層，只取第一個非空檔
        │
        ▼
<repo 根>/AGENTS.override.md > AGENTS.md > project_doc_fallback_filenames
        │   每層至多取一個檔
        ▼
<repo 根>/services/api/AGENTS.md      <- 一路走到目前工作目錄
        │
        ▼
由根往下串接（空行分隔），後面的覆蓋前面的；合併後超過 project_doc_max_bytes 就截斷
每次執行只建一次，改檔後要重開 Codex
```

## 3. 起步序列圖

```text
 使用者            Codex / Claude Code / Antigravity            檔案系統
   │  在專案目錄啟動 │                                              │
   │───────────────▶│  1 找入口檔：AGENTS.md（Claude 有 CLAUDE.md 則讀它）│
   │                │─────────────────────────────────────────────▶│
   │                │◀──────────── 入口檔內容（<= 上限）───────────────│
   │                │  2 列出可用 skill：只載入 name + description    │
   │                │─────────────────────────────────────────────▶│
   │                │◀──────── 技能清單（<= 技能預算）────────────────│
   │  下達任務       │                                              │
   │───────────────▶│  3 任務與某 skill 描述相符，或使用者點名 $skill  │
   │                │  4 才讀該 skill 完整 SKILL.md                  │
   │                │─────────────────────────────────────────────▶│
   │                │◀─────────── SKILL.md 全文 ────────────────────│
   │                │  5 SKILL.md 指到 references/ 或 scripts/ 才再讀 │
   │◀───────────────│  6 回報結果與驗證證據                           │
```

步驟 2 與 4 是「Just-In-Time 載入」：未被選中的 skill 只佔描述那幾行。Codex 的明確呼叫是 `/skills` 或輸入 `$`；隱含呼叫靠描述比對，可在 `agents/openai.yaml` 設 `allow_implicit_invocation: false` 關掉（明確 `$skill` 仍可用）[2]。

## 4. 建議的目錄範例

```text
my-repo/
├── AGENTS.md                      # 唯一入口：指令、禁區、驗收標準（DoD）、技能索引
├── .agents/
│   └── skills/                    # Codex、Antigravity 的專案技能目錄
│       └── release-notes/
│           ├── SKILL.md           # 只放流程與觸發描述；細節往下拆
│           ├── references/        # 需要才讀
│           └── scripts/           # 執行，不讀進上下文
├── .claude/
│   └── skills/ -> (或複製 .agents/skills 的內容)   # Claude Code 的專案技能目錄
├── CLAUDE.md                      # 只有一行：@AGENTS.md（讓 Claude Code 與其他工具共用）
└── services/
    └── api/AGENTS.md              # 子目錄專屬規則（Codex 往下串接、其他工具取最近的一份）
```

說明：

- Claude Code 的技能目錄是 `.claude/skills/`，**不是** `.agents/skills/`（[4]）；要共用就複製或用符號連結（Codex 文件稱會跟隨符號連結的 skill 資料夾 [2]；Windows 上建符號連結需權限，未實測）。
- 本 repo 與維護者環境的慣例是專案只放 `AGENTS.md`、不建 `CLAUDE.md`（見 `AGENTS.md` 協作約定）。上圖的 `CLAUDE.md` 只是給**需要相容舊版 Claude Code** 時的選項；v2.1.277 以上沒有 `CLAUDE.md` 會直接讀 `AGENTS.md` [3]。

## 5. 起步協議範本（可放進 `AGENTS.md` 開頭）

```markdown
## 開工協議
1. 先讀本檔；子目錄若有 AGENTS.md，以最近的為準。
2. 只在任務相符時載入 skill；一次最多同時使用 3 個 skill。
3. 動手前列出會改的檔案；完成後附驗證指令與輸出，沒跑就寫「未驗證」。
4. 禁區：<列出不可碰的目錄與動作>
5. 驗收（DoD）：<列出測試指令，例如 python -m unittest discover -s tests>
```

第 2 行的「最多 3 個」是**本文建議值，不是官方限制**；理由是官方只限制清單預算，沒有限制同時啟用數量，過多全文載入會擠掉工作上下文。

## 6. 預算檢驗標準

| 項目 | 標準 | 依據 |
|------|------|------|
| Codex 入口檔鏈（含 override）總 bytes | <= 32,768（`project_doc_max_bytes` 預設 32 KiB） | 官方 [1] |
| Codex 技能清單（所有 skill 的 name + description） | <= 模型視窗的 2%；視窗未知時 <= 8,000 字元；可用 `skills.max_context_tokens` 調高，最高 10,000 tokens；超過時先縮短描述、再省略部分 skill 並警告 | 官方 [2] |
| Claude Code 單一 skill 的 description + when_to_use | 清單中超過 1,536 字元會被截斷 | 官方 [4] |
| Claude Code 單份 CLAUDE.md | 建議 < 200 行（官方建議值，非硬限制） | 官方 [3] |
| 單一 `SKILL.md` | 建議 < 500 行，細節拆到 `references/` | Claude Code 官方範例 [4]；Codex 文件未訂此數字 |
| 同時使用的 skill 數 | <= 3 | **本文建議，非官方** |

檢驗腳本（只用標準庫；把「根目錄、目前目錄、技能目錄」三個路徑傳進去）：

```python
import re, sys
from pathlib import Path

AGENTS_LIMIT = 32 * 1024     # Codex project_doc_max_bytes 預設 32 KiB
SKILL_LIST_LIMIT = 8000      # Codex 技能清單在視窗大小未知時的字元預算

def agents_chain(root: Path, cwd: Path):
    """由 root 走到 cwd，每層取 AGENTS.override.md > AGENTS.md（至多一個）。"""
    parts = [root] + [root / p for p in cwd.relative_to(root).parents][::-1][1:] + ([cwd] if cwd != root else [])
    seen, out = set(), []
    for d in parts:
        if d in seen: continue
        seen.add(d)
        for name in ("AGENTS.override.md", "AGENTS.md"):
            f = d / name
            if f.is_file() and f.stat().st_size > 0:
                out.append(f); break
    return out

def skill_list_chars(skills_dir: Path):
    total, rows = 0, []
    for md in sorted(skills_dir.glob("*/SKILL.md")):
        head = md.read_text(encoding="utf-8", errors="replace").split("---")
        fm = head[1] if len(head) > 2 else ""
        name = (re.search(r"^name:\s*(.+)$", fm, re.M) or [None, md.parent.name])[1].strip()
        desc = (re.search(r"^description:\s*(.+)$", fm, re.M) or [None, ""])[1].strip()
        n = len(name) + len(desc)
        total += n; rows.append((n, name))
    return total, sorted(rows, reverse=True)

if __name__ == "__main__":
    root, cwd, skills = map(Path, sys.argv[1:4])
    files = agents_chain(root, cwd)
    size = sum(f.stat().st_size for f in files)
    print(f"AGENTS 鏈: {[str(f.relative_to(root)) for f in files]} 共 {size} bytes / {AGENTS_LIMIT} -> {'OK' if size <= AGENTS_LIMIT else 'OVER'}")
    total, rows = skill_list_chars(skills)
    print(f"技能 {len(rows)} 個，name+description 共 {total} 字元 / {SKILL_LIST_LIMIT} -> {'OK' if total <= SKILL_LIST_LIMIT else 'OVER'}")
    print("最長三個:", rows[:3])
```

限制：只解析單行 `name:`／`description:`，多行 YAML 描述會被低估；它檢查的是字元數，不是 token 數。

### 實測（2026-10-26，Python 3.14.9，`PYTHONUTF8=1 python budget.py <根> <cwd> <技能目錄>`）

對本 repo（`ai-inbox`）的 `AGENTS.md` 與一個只含 2 個極短 skill 的範例目錄：

```text
AGENTS 鏈: ['AGENTS.md'] 共 12516 bytes / 32768 -> OK
技能 2 個，name+description 共 5 字元 / 8000 -> OK
```

對維護者本機 `~/.claude/skills`（Claude Code 技能目錄，只看彙總數字）：

```text
技能 96 個，name+description 共 12638 字元 / 8000 -> OVER
最長三個: [(835, 'info-diet'), (639, 'phantom-pushback'), (549, 'review-loop')]
```

解讀：這份清單若原樣放進 **Codex** 會超過 8,000 字元的預算（Codex 會縮短描述、可能省略部分 skill）。Claude Code 的規則不同（單一描述 1,536 字元截斷），所以這個 OVER 只代表「搬到 Codex 前要先瘦身」，不代表 Claude Code 現況有問題。Codex 實際載入時用的是 token 預算而非字元，**本文未在 Codex 上實測清單被截斷的行為**。

## 7. Skill 設計規則（JIT）

1. **描述寫觸發條件，不寫內容**：`description` 是唯一會常駐的部分，Codex／Antigravity 都靠它比對 [2][5]。一句話講「何時用」，前面放主要用途。
2. **細節往下拆**：`SKILL.md` 只放流程；長參考放 `references/`，可執行的放 `scripts/`（執行不佔上下文）。
3. **有副作用的 skill 關掉隱含呼叫**：Codex 用 `allow_implicit_invocation: false` [2]；Claude Code 用 `disable-model-invocation: true`（描述也會從上下文移除）[4]。
4. **同名不合併**：Codex 不合併同名 skill，兩份都會出現在選單 [2]；專案與使用者層不要放同名。
5. **停用**：Codex 在 `~/.codex/config.toml` 加 `[[skills.config]]`（`SKILL.md` 路徑與 `enabled = false`），重啟生效 [2]。

## 8. 本機查證與限制

- `codex --help`（`codex-cli 0.150.0`）：列出 `exec`、`agents`、`plugin`、`doctor` 等子指令與 `-c key=value` 覆寫設定；**沒有** AGENTS.md 或 skill 專屬的旗標。AGENTS.md 與 skills 的行為以官方文件為準，本機未對 Codex 實際載入做行為測試（未啟動模型會話）。
- 影片筆記中的「Grok Bot + Herdr 統一進入點」未在本文查證，不引用。
- Antigravity 的 `AGENTS.md`／`GEMINI.md` 載入規則：官方 codelab 未提，第三方文章稱有 12,000 字元上限，**未查證，不採用**。
- 官方文件網址 `developers.openai.com/codex/...` 查證當天會 308 轉址到 `learn.chatgpt.com`，下方列轉址後的位址。

## 9. 來源

1. OpenAI，Codex AGENTS.md 指南：<https://learn.chatgpt.com/docs/agent-configuration/agents-md>（原址 <https://developers.openai.com/codex/guides/agents-md>）
2. OpenAI，Codex Skills：<https://learn.chatgpt.com/docs/build-skills>（原址 <https://developers.openai.com/codex/skills>）
3. Anthropic，Claude Code 記憶（CLAUDE.md／AGENTS.md）：<https://code.claude.com/docs/en/memory>
4. Anthropic，Claude Code Skills：<https://code.claude.com/docs/en/skills>（頁面約 118k 字元，本次只讀到前 100k；未涵蓋之處不下結論）
5. Google，Authoring Antigravity Skills codelab：<https://codelabs.developers.google.com/getting-started-with-antigravity-skills>
6. Google，Gemini API Antigravity Agent：<https://ai.google.dev/gemini-api/docs/antigravity-agent>（僅經搜尋摘要，未全文讀取）
7. AGENTS.md 開放格式：<https://agents.md>
