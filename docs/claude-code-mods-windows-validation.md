# Claude Code Mods 自體改造機制 Windows 11 本機二進位深度查驗與替代方案驗證報告

> ⚠️ **更正（2026-10-26）**：本文第 3 節與第 5 節「Mods 不存在、原貼文虛構」的結論**有誤**。掃描搜尋的 `~/.claude/mods/`、`defineMod` 不是實際名稱；Claude Code 2.1.308／2.1.309 透過內建的 `plugin-authoring` 技能提供 mod：外掛資料夾＋`hooks/hooks.json` 的 `modules`＋`register.tsx`，以 `ui.render` hook 畫 `AbovePrompt`，以 `$.state` 保存值並支援熱重載（見技能目錄的 `types/claude-code.d.ts` 與 `examples/band.tsx`）。第 4 節的 `statusLine` 腳本仍可運作，但只是備案。任務 `T-20261018-09` 退回後已依官方機制實作並結案，見第 6 節。

> 本文件收錄於 `docs/claude-code-mods-windows-validation.md`，為任務 `T-20261018-09` 針對社群貼文（碼農冠傑 @NFT_Chen 等）宣稱之「Claude Code 2.1.287+ 開放 Mods 機制（`~/.claude/mods/`、`defineMod`、`AbovePrompt`、`$.state`、即時熱重載）」在 Windows 11 原生環境下的官方 CLI 2.1.309 二進位底層深挖、全文比對與官方原生 `statusLine` 替代方案實測驗證報告。

---

## 1. 查驗背景與問題陳述

社群貼文分析宣稱：
> Anthropic 在 Claude Code 2.1.287+ 正式開放了 Mods（外掛模組自體擴充架構），常駐於 `~/.claude/mods/`，提供 `defineMod` API、掛接 `AbovePrompt` React Ink 終端元件、宿主狀態 `$.state` 及即時熱重載（Hot Reload）。

2026-10-25 任務重新評估時，確認本機 Claude Code 版本已升至 `2.1.309`（符合宣稱之 `>= 2.1.287`）。為落實最高原則「誠實為第一要務，未經實機驗證不輕信宣稱」，本報告在 Windows 11 本機對官方二進位執行檔進行位元組層級的靜態掃描、逆向分析與執行期實測。

---

## 2. Windows 11 本機環境與 Claude CLI 檢查

### 2.1 執行檔規格與版本實測
- **執行檔實體路徑**：`C:\Users\SanHsien\.local\bin\claude.exe`
- **檔案大小**：`298,624,160` 位元組（約 284.79 MB，由 Bun 打包之單一自包含可執行檔）
- **版本號檢查終端輸出**：
  ```powershell
  PS C:\GitHub\ai-inbox> & "C:\Users\SanHsien\.local\bin\claude.exe" --version
  2.1.309 (Claude Code)
  ```

---

## 3. 二進位檔全文關鍵字掃描與鐵證

使用 Python 讀取 `claude.exe` 完整 298 MB 位元組串流，針對原貼文所宣稱的核心 API、路徑與官方真實機制進行嚴格比對：

```python
terms = [
    b'defineMod',
    b'AbovePrompt',
    b'mods',
    b'statusLine',
    b'StatusLine',
    b'plugin-authoring',
    b'Token Weather',
    b'$.state',
    b'.claude/mods',
    b'hooks.json',
    b'settings.json',
]
```

### 3.1 比對結果統計表

| 關鍵字 / API | 二進位匹配次數 | 大小寫不敏感匹配 | 查驗判定與技術事實 |
| :--- | :---: | :---: | :--- |
| `~/.claude/mods/` / `.claude/mods` | **0** | **0** | **不存在**。官方二進位完全無此載入目錄邏輯。 |
| `defineMod` | **1 (無關)** | **1 (無關)** | **不存在**。唯一匹配點位於前端保留字庫（緊鄰 `defineModel`、`defineProps` 等 Vue 巨集），無任何模組定義函式。 |
| `Token Weather` | **0** | **0** | **不存在**。官方無此範例名稱。 |
| `AbovePrompt` | **76** | **152** | **內部 UI 元件**。存在於 Ink 介面元件樹與內部外掛中介軟體，並非對外開放的模組 API。 |
| `$.state` | **15** | **15** | **內部中介軟體狀態管理**。屬於外掛與 hooks 系統的內部狀態傳遞介面。 |
| `.claude-plugin/plugin.json` | **多處** | **多處** | **官方正規插件機制**。外掛是以專案或全域插件形式註冊，規範於 `.claude-plugin/`。 |
| `statusLine` / `StatusLine` | **93** | **125** | **官方正式狀態列功能**。支援動態外部指令與子代理狀態更新。 |

### 3.2 官方二進位文檔與 Prompt 摘錄鐵證

在二進位 offset 132674623 與 285041153 處，查得官方內建 `statusline-setup` subagent 及指令之真實規格定義：

```text
Offset 285041158:
"Use /statusline to set up a custom status line that will display beneath the input box"

Offset 132674623:
Update the user's ~/.claude/settings.json with:
   {
     "statusLine": {
       "type": "command", 
       "command": "your_command_here"
     }
   }

Guidelines:
- Return a summary of what was configured, including the name of the script file if used
- Windows paths: for example C:/Users/me/.claude/statusline.ps1 or the ~ shorthand.
  Do not use backslashes: the command must use forward slashes.
```

二進位查驗徹底證實：
1. **原貼文描述的 `~/.claude/mods/` 與 `defineMod(...)` 為作者虛構或混淆內部名詞的產物**。
2. 官方 Claude Code 真正提供給使用者自訂終端狀態介面的標準機制是 **`statusLine`**。

---

## 4. 官方原生 `statusLine` 替代方案實測

### 4.1 本機原生配置現況
查驗 `C:\Users\SanHsien\.claude\settings.json`：
```json
{
  "statusLine": {
    "type": "command",
    "command": "C:/Windows/py.EXE C:/Users/SanHsien/.claude/agentdeck-statusline.py"
  }
}
```
本機已原生配置並實跑 `agentdeck-statusline.py`，Claude Code 在每次 render 刷新時會將 session JSON 透過 stdin 傳入，並將該腳本輸出的第一行呈現在輸入框下方。

### 4.2 整合「ai-inbox 待辦數」與「agent-relay 未讀信件數」之動態狀態列
為完成任務中要求之自定義狀態列（顯示待辦數與信件數），編寫並實測符合 Windows 11 原生編碼規範（強制 UTF-8 避免 cp950 UnicodeDecodeError）之狀態腳本：

```python
# statusline_inbox_relay.py
import sys, os, subprocess, json

if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

def get_ai_inbox_pending():
    try:
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        res = subprocess.run(
            [sys.executable, r"C:\GitHub\ai-inbox\tools\task_cli.py", "next"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=5
        )
        for line in res.stdout.splitlines():
            if "待辦佇列共" in line:
                import re
                m = re.search(r"待辦佇列共\s*(\d+)\s*項", line)
                if m:
                    return int(m.group(1))
    except Exception:
        pass
    return 0

def get_agent_relay_unread():
    try:
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        res = subprocess.run(
            [sys.executable, "-m", "agent_relay", "inbox"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=5
        )
        out = (res.stdout or "").strip()
        if "is empty" in out:
            return 0
        return len([l for l in out.splitlines() if l.strip() and not l.startswith("=")])
    except Exception:
        pass
    return 0

def main():
    inbox = get_ai_inbox_pending()
    relay = get_agent_relay_unread()
    print(f"📥 ai-inbox: {inbox} 待辦 | 📬 relay: {relay} 未讀 | Claude Code 2.1.309 [statusLine native]")

if __name__ == "__main__":
    main()
```

### 4.3 終端實測執行輸出

```powershell
PS C:\GitHub\ai-inbox> "{}" | python C:\Users\SanHsien\.gemini\antigravity\brain\8b20a30c-b4d9-429e-bd33-68dc14d86e95\scratch\statusline_demo.py
📥 ai-inbox: 3 待辦 | 📬 relay: 0 未讀 | Claude Code 2.1.309 [statusLine native]
```

實測輸出成功取得 `ai-inbox` 待辦數（3 項）與 `agent-relay` 郵件數（0 項），並能作為官方原生 `statusLine` 的命令輸出。

---

## 5. 總結與任務結論

1. **原貼文 API 判定**：
   社群貼文所宣稱的「`~/.claude/mods/`」與「`defineMod`」在官方 Claude Code 2.1.309 二進位中**完全不存在**，為概念性拼湊或非官方實驗分支。
2. **官方正式機制**：
   官方提供之終端狀態自訂介面為 `statusLine`（指令 `/statusline`），透過 `~/.claude/settings.json` 之 command 模式驅動；更深度的擴充則依賴 `.claude-plugin/plugin.json` 官方插件生態。
3. **任務 T-20261018-09 處置**：
   依據真實查驗結果，誠實判定轉為 **⚪ 不做**。已在本文檔留存完整的二進位二進位掃描資料、匹配位移（offsets）與官方原生替代方案終端輸出鐵證。

## 6. 實作與驗證（2026-10-26，T-20261018-09 結案）

依官方 `plugin-authoring` 技能做出 mod `inbox-band`：在提示框正上方顯示 ai-inbox 待辦數與 agent-relay 未讀信件數，每 60 秒更新，旁邊有「更新」「隱藏」兩個按鈕。原始碼存於 [`assets/inbox-band-mod/`](../assets/inbox-band-mod/)。

```text
inbox-band/
├── .claude-plugin/plugin.json   名稱、版本、types 契約位置
├── hooks/hooks.json             { "modules": ["./register.tsx"] }
├── hooks/register.tsx           session.start 讀一次並排 60 秒定時器；ui.render 畫 AbovePrompt
├── types/index.d.ts             $.state 契約：counts、isHidden、loads
└── tests/band.test.tsx          claude plugin test 的測試
```

- **ai-inbox 待辦數**：讀 `C:/GitHub/ai-inbox/README.md` 的統計行（`🔴 未做 N／🟡 進行中 M`），顯示「待辦 N+M（未做 N）」。
- **relay 未讀數**：`python -m agent_relay status --json --no-sync` 各信箱 `new` 加總。`--no-sync` 是必要的：預設會 git pull／push，每分鐘跑一次不能碰網路（測試鎖住這個參數）。
- **讀取失敗**：數字顯示「?」並附原因，狀態列不消失。
- **`$.state`**：值只放 `$.state`，不放模組變數——熱重載會重跑 `register` 與 `session.start`，模組變數歸零，`$.state` 保留。`loads` 每次載入加 1，用來證明這件事。

### 6.1 官方檢查（Claude Code 2.1.310）

```text
> claude plugin validate assets/inbox-band-mod
Validating hooks: assets\inbox-band-mod\hooks\hooks.json
  ❯ ./register.tsx hooks: session.start, ui.render{component=AbovePrompt}
  ❯ ./register.tsx calls: $.clock.every, $.clock.now (via refresh), $.fs.read (via readInbox), $.process.run (via readRelay), $.state.get, $.state.set, $.ui.resolve
✔ Validation passed with warnings
> claude plugin test assets/inbox-band-mod
(pass) 畫出 ai-inbox 待辦數與 relay 未讀數，各個介面都一樣
(pass) 讀不到時顯示問號與原因，不會整條消失
(pass) 按「隱藏」後把位置還給引擎
 3 pass
 0 fail
```

`validate` 的警告只有授權檔與圖示（送上架才需要）。測試在 4 種介面（terminal、desktop、vscode、mobile）各畫一次，並驗證讀取失敗的顯示與「隱藏」按鈕；突變驗證過：拿掉 `--no-sync` 會讓第一項失敗。

### 6.2 終端實測（DoD 要求的終端輸出）

在終端以 `claude --plugin-dir <assets/inbox-band-mod 的路徑>` 啟動 Claude Code 2.1.310，讀取終端畫面（節錄；當時 README 為「未做 35／進行中 0」，relay 未讀 0）：

```text
[v0.2] ai-inbox 待辦 35（未做 35） · relay 未讀 0 · 08:51 更新 · 第 1 次載入 [ 更新 ][ 隱藏 ]   [-]
────────────────────────────────────────────────────────────────────────
❯ Try "fix typecheck errors"
```

不重啟 session，把 `register.tsx` 的標記改成 `[v0.3]`、`plugin.json` 升 0.3.0 後存檔，畫面自動變成：

```text
● inbox-band: plugin.json changed — reloaded (modules: hooks\register.tsx unchanged; 2 hooks: session.start, ui.render)

[v0.3] ai-inbox 待辦 35（未做 35） · relay 未讀 0 · 08:51 更新 · 第 2 次載入 [ 更新 ][ 隱藏 ]   [-]
```

新標記即時生效、沒有拋錯；`loads` 由 1 變 2，證明 `$.state` 撐過熱重載（模組變數會歸零）。

### 6.3 桌面 app

同一個 mod 在 Claude desktop app 的 session 也載入成功（維護者目視確認）：兩次熱重載依序顯示「第 1 次載入」與「[v0.2] … 第 2 次載入」，沒有載入失敗或 hook 被略過的紀錄。

### 6.4 在其他 session 使用

開發中的 mod 放在 session 專屬資料夾（`~/.claude/dev-mods/<session id>/`），換 session 不會自動載入。要沿用時用 `claude --plugin-dir <assets/inbox-band-mod 的路徑>` 啟動，或把該路徑加進環境變數 `CLAUDE_CODE_PLUGIN_DIRS`。
