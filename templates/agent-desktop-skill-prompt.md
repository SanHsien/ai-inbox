# Agent 桌面操控指令集與 STALE_REF 安全重試 Prompt 模板

> 本文件為可直接嵌入多 Agent（Antigravity、Claude Code、Codex、Hermes）系統提示詞（System Prompt）或 `AGENTS.md` 的跨平台桌面 GUI 操作標準指南。

---

## 1. 桌面操作基本原則與架構認知

你擁有透過 `agent-desktop` CLI 直讀作業系統無障礙樹（Accessibility Tree）以操控桌面視窗之能力。
- **核心思維**：不截圖、不盲猜像素座標 (x, y)。所有觀察與行動均透過結構化語意節點（Ref）完成。
- **標準三部曲（Observe-Act-Verify Loop）**：
  1. **Observe（觀察）**：執行 `snapshot` 或 `find` 取得當前視窗語意樹與合格 Ref。
  2. **Act（行動）**：使用限定命名空間的 Ref（如 `'@s8f3k2p9:e12'`）下達語意動作（click、set-value、toggle）。
  3. **Verify（驗證）**：再次進行局部觀察（`--root` 或 `get`），確認狀態真實改變，絕不假設動作成功即結束。

---

## 2. Windows PowerShell 防雷語法（強制合約）

在 Windows 11 原生 PowerShell 環境下，`@` 是 splatting 展開運算子。未加引號的 `@ref` 會被 PowerShell 吞掉並拋出 `INVALID_ARGS`。
- ❌ **嚴禁寫法**：
  ```powershell
  agent-desktop click @s8f3k2p9:e12
  agent-desktop set-value @s8f3k2p9:e4 hello
  ```
- ✅ **唯一合法寫法（強制單引號包裹）**：
  ```powershell
  agent-desktop click '@s8f3k2p9:e12'
  agent-desktop set-value '@s8f3k2p9:e4' 'hello'
  ```

---

## 3. 錯誤代碼與重試安全合約（Disposition Retry Contract）

每次執行操作均回傳標準 JSON Envelope。當 `ok: false` 時，**必須依循以下狀態機處置，嚴禁陷入重複盲點的 Doom Loop**：

```text
               ┌──────────────────────────────┐
               │         操作回傳失敗         │
               └──────────────┬───────────────┘
                              │
               ┌──────────────┴───────────────┐
               ▼                              ▼
      [code == "STALE_REF"]       [disposition.retry]
               │                              │
               │                   ┌──────────┴──────────┐
               │                   ▼                     ▼
               │                ["safe"]             ["unsafe"]
               │                   │                     │
               ▼                   ▼                     ▼
      重新執行 snapshot         安全重試動作           立即暫停並回報使用者
      取得全新 Ref 後繼續       (非破壞性操作)         (嚴禁盲目循環重試)
```

### 3.1 關鍵錯誤處置守則

1. **`STALE_REF`**：
   - 意義：目標元件在快照後已重繪或消失。
   - 處置：**絕不可拿舊 Ref 繼續重試**。必須立刻執行 `agent-desktop snapshot -i` 取得新快照，換用新 Ref 重新操作。
2. **`AMBIGUOUS_TARGET`**：
   - 意義：多個元素具備相同特徵，無法判定唯一目標。
   - 處置：改用 `--exact` 匹配完整名稱，或使用 `--root '@<snapshot_id>:<container_id>'` 限制搜尋區域。
3. **`POLICY_DENIED`**：
   - 意義：指令在當前 Headless 模式下受政策保護阻止（例如 Windows 下 `type`、`right-click` 需實體焦點）。
   - 處置：文字輸入優先改用語意式的 `set-value`；若確實需實體按鍵模擬，明確加上全域 `--headed` 參數。
4. **`disposition.retry: "unsafe"`**：
   - 意義：動作可能已對系統造成不可逆副作用（如表單已發送、付款按鈕已點擊、檔案已寫入）。
   - 處置：**強制煞車**。先讀取現有狀態（`get` 或 `snapshot`），若無法確認結果，立即向使用者報告狀況。

---

## 4. 密集大型介面之高效兩段式下鑽（Token 節省 95%）

當面對複雜軟體（VS Code、Slack、瀏覽器大量 DOM）時，嚴禁無腦全視窗 dump。請依序執行「骨架速描 $\to$ 區域下鑽」：

```powershell
# 步驟 1：骨架速描 (Shallow Map)
# 快速獲取整體架構，折疊密集子分支並回傳 children_count (僅消耗 ~40 tokens)
agent-desktop snapshot --skeleton --app "Slack" -i --compact

# 步驟 2：鎖定目標區域下鑽 (Drill-down)
# 針對剛才識別出的側邊欄容器 @s8f3k2p9:e3 展開細部節點 (消耗 ~60 tokens)
agent-desktop snapshot --root '@s8f3k2p9:e3' -i --compact

# 步驟 3：鎖定目標 Ref 進行點擊
agent-desktop click '@s8f3k2p9:e15'

# 步驟 4：二次觀察確認狀態
agent-desktop snapshot --root '@s8f3k2p9:e3' -i --compact
```

---

## 5. 常見作業速查指令表

| 目的 | PowerShell 完整指令 |
| :--- | :--- |
| **環境就緒檢查** | `agent-desktop status` |
| **顯示器清單** | `agent-desktop list-displays` |
| **執行中應用清單** | `agent-desktop list-apps` |
| **觀察視窗骨架** | `agent-desktop snapshot --skeleton --app "<AppName>" -i --compact` |
| **區域深入觀察** | `agent-desktop snapshot --root '@<snap_id>:<ref_id>' -i --compact` |
| **條件搜尋元素** | `agent-desktop find --role button --name "Save" --exact` |
| **語意點擊** | `agent-desktop click '@<snap_id>:<ref_id>'` |
| **無頭文字賦值** | `agent-desktop set-value '@<snap_id>:<ref_id>' '目標文字'` |
| **核取方塊切換** | `agent-desktop toggle '@<snap_id>:<ref_id>'` |
| **滾動頁面** | `agent-desktop scroll --down '@<snap_id>:<ref_id>'` |
| **按鍵組合** | `agent-desktop press ctrl+s` |
| **視窗管理** | `agent-desktop restore --app "<AppName>"` / `agent-desktop focus-window --app "<AppName>"` |
