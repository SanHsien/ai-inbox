# 靶心人故事編輯器 Generative UI 互動規格 (Target Story Generative UI Spec)

> 本規格文件收錄於 `docs/target-story-generative-ui-spec.md`，定義基於許榮哲「靶心人故事模型」的 Generative UI / Antigravity Widget 互動架構、狀態機、視覺排版與資料契約。以 ai-inbox 範本形式交付。

---

## 1. 核心模型與幾何佈局 (V-Shape Geometry)

靶心人（Target Story Formula）以 7 大核心情節節點構成經典的 V 字型情緒走勢：
- **下降段（危機加劇）**：
  1. `目標 (Target)`：主角的渴望或必須解決的困境（高點開始）
  2. `阻礙 (Obstacle)`：意料之外的重大困難（情緒受挫）
  3. `努力 (Effort)`：主角傾盡資源的第一重嘗試（暫時掙扎）
  4. `意外 (Twist/Accident)`：努力反而引爆更糟的意外危機（谷底低點）
- **上升段（超越與升華）**：
  5. `轉彎 (Turning Point)`：由先前的阻礙引導出全新認知或方法（反彈回升）
  6. `超越 (Climax/Transcendence)`：付出代價後的極限突破（高潮迸發）
  7. `結局 (Resolution)`：最終狀態，其精神層次必須超越起點目標（高點落幕）

### 佈局呈現
- 3 欄 4 排或折線 SVG 畫布，清晰呈現 V 字型軌跡。
- 節點間具備向右連通的動態 SVG 箭頭。
- 關鍵因果標示：
  - **H1 箭頭**：結局與目標對照（驗證結局 > 目標）
  - **H2 箭頭**：轉彎與阻礙對照（驗證轉折由阻礙引發）
  - **H3 箭頭**：意外與努力對照（驗證意外由努力引起，非天外飛仙）

---

## 2. 雙向狀態機與互動機制 (State Machine & Drill-down)

### 2.1 雙層資料架構
1. **宏觀層（Macro Level）**：7 個主節點的 4 句 7 字核心摘要（嚴格 28 字契約）。
2. **微觀層（Micro 3x3 Drill-down）**：
   - 點擊任一節點，原地展開或浮層展示 3x3（九宮格）內部情節細化：
     - `[0,0] 觸發契機` ｜ `[0,1] 環境細節` ｜ `[0,2] 角色心理`
     - `[1,0] 行動抉擇` ｜ `[1,1] 核心對話` ｜ `[1,2] 衝突爆發`
     - `[2,0] 代價承受` ｜ `[2,1] 伏筆暗藏` ｜ `[2,2] 轉移過渡`
   - 九宮格內文字修改時，即時透過雙向綁定更新 Macro 摘要與全局 JSON。

### 2.2 三伏三冒檢驗面板 (Foreshadowing & Payoff Tab)
- 提供專屬分頁，盤點劇本中的 3 處伏筆與 3 處呼應：
  - 伏筆 A（前半段埋下） ⟷ 呼應 A（後半段回收）
  - 伏筆 B ⟷ 呼應 B
  - 伏筆 C ⟷ 呼應 C
- 自動評估兩者間距（跨越節點數：太緊 <2 節點、剛好 2-4 節點、太鬆 ≥5 節點）。

---

## 3. 資料結構契約 (JSON Export Contract)

```json
{
  "title": "故事標題",
  "theme": "故事核心母題",
  "nodes": {
    "target": { "summary": "七字句一七字句二七字句三七字句四", "grid": [["...", "...", "..."], ["...", "...", "..."], ["...", "...", "..."]] },
    "obstacle": { "summary": "...", "grid": [...] },
    "effort": { "summary": "...", "grid": [...] },
    "twist": { "summary": "...", "grid": [...] },
    "turning": { "summary": "...", "grid": [...] },
    "climax": { "summary": "...", "grid": [...] },
    "resolution": { "summary": "...", "grid": [...] }
  },
  "foreshadowing": [
    { "plant_node": "target", "payoff_node": "resolution", "description": "象徵物伏筆" },
    { "plant_node": "obstacle", "payoff_node": "turning", "description": "技能伏筆" },
    { "plant_node": "effort", "payoff_node": "climax", "description": "情感承諾" }
  ]
}
```
此 JSON 格式可無縫傳入 `tools/verify_story_structure.py` 進行全自動因果與字數合規性檢查。
