# 反 AI 罐頭設計前端工程規範 (Anti-AI-Slop Frontend Guidelines)

本規範提煉自 Shipper `epstein.md` 核心設計哲學，旨在消除由 AI（如 v0、bolt.new、Lovable、Claude Artifacts）生成前端介面時普遍出現的「千篇一律視覺疲勞（AI Slop）」。

核心哲學：**「好設計不是告訴模型要做什麼，而是以嚴密的負向約束（Negative Constraints as Spec）明確禁止老套路」**。

---

## 1. 核心禁制清單（Negative Constraints）

在生成或審核 HTML、CSS、Tailwind 樣式與 UI 元件時，嚴禁出現下列典型 AI 罐頭特徵：

| 規則編號 | 罐頭特徵 (AI Slop) | 違規模式與特徵代碼 | 嚴禁理由 |
| :--- | :--- | :--- | :--- |
| **SLOP-01** | **浮誇無腦陰影**<br>*(Overused Box Shadows)* | `shadow-2xl`, `shadow-xl`, `box-shadow: 0 25px 50px...`<br>高擴散、半透明黑色的模糊陰影 | 缺乏真實物理光源層次，使卡片呈現廉價飄浮感與髒污邊緣。 |
| **SLOP-02** | **俗套藍紫漸層**<br>*(Blue/Purple Gradients)* | `from-indigo-` / `via-purple-` / `to-pink-`<br>`linear-gradient(135deg, #6366f1, #a855f7)` | 典型 Cyberpunk 模板老套路，嚴重干擾文字可讀性與專業度。 |
| **SLOP-03** | **無意義裝飾 Emoji**<br>*(Decorative Emojis)* | 標題、功能按鈕或項目清單前的 🚀、💡、🔥、✨、🎉、🔮 | 廉價裝飾符號，缺乏語意價值，破壞資訊層級。 |
| **SLOP-04** | **虛假動態徽章**<br>*(Fake LIVE Badges)* | 無即時資料流卻加上閃爍綠點的 `LIVE`、`Active Now`、`Real-time` 呼吸燈 | 誤導使用者認知，製造虛假動態焦慮。 |
| **SLOP-05** | **AI 罐頭黑話文案**<br>*(AI Buzzwords)* | *delve*, *vibe*, *seamlessly*, *elevate*, *revolutionize*, *tapestry*, *empower*, *unleash*, *game-changer* 等 | 空洞行銷黑話，缺乏具體產品數據與實質功能資訊。 |

---

## 2. 正向工程標準（Positive Standards）

去除裝飾性干擾，回歸簡潔、純粹、專業的高性能介面工程：

### 2.1 實色表面與 1px 細緻邊框（Border Over Shadow）
- 採用清晰的表面邊界：`border border-slate-200 dark:border-slate-800`。
- 層級區分依賴表面背景色階（Surface Tinting），例如：
  - 頁面背景：`bg-slate-950`
  - 卡片表面：`bg-slate-900`
  - 懸停/聚焦態：`bg-slate-800/60`
- 陰影僅允許在浮層下拉選單（Dropdown / Popover）使用極其微弱且具備物理收斂性的 `shadow-sm`。

### 2.2 語意化字型層級（Semantic Typography）
- 採用系統無襯線字型或現代幾何字體：`Inter`, `Roboto`, `system-ui`, `-apple-system`, `sans-serif`。
- 階層建立透過字重（`font-medium`, `font-semibold`）、字距微調（`tracking-tight`）與顏色對比度（`text-slate-100`, `text-slate-400`），而非無節制放大字號。
- 等寬字型應用：針對數字、Hash、狀態代碼、時間戳記強制套用等寬字型（`font-mono`），確保排版對齊與資料易讀性。

### 2.3 數據先行與真實活人文案（Data-First & Functional Copy）
- 標題直接指涉模組功能（例如：`系統指標監控面板`、`節點連線清單`）。
- 內容以真實數據、狀態單位與具體動作說話（例如：`延遲 14ms · 封包丟失率 0.00% · 運作時間 99.98%`）。
- 動作按鈕使用明確動詞：`重試連線`、`匯出報告`、`套用篩選`，不使用 `開始探索體驗` 等空泛文案。

---

## 3. 範例元件生成對照（Demo Implementation）

本規範提供了一份零罐頭感、生產級水準的前端示範元件：
- 示範檔案位置：[`assets/anti-slop-demo/index.html`](../assets/anti-slop-demo/index.html)
- 示範主題：`分散式任務節點監控面板 (Distributed Task Node Monitor)`

### 規範對照檢核表：

| 檢查項目 | 罐頭作法 (禁止) | 示範元件作法 (採用) | 對應規則 |
| :--- | :--- | :--- | :--- |
| **邊界與深度** | `shadow-2xl` 黑色模糊陰影 | `border border-slate-800 bg-slate-900/80` 細邊框與實色層級 | SLOP-01 |
| **色彩基調** | 藍紫/粉紅霓虹漸層背景 | Slate 深色單色調 + 語意化狀態強調色（翡翠綠 / 琥珀黃） | SLOP-02 |
| **圖示與符號** | 標題置入 🚀✨ 裝飾 Emoji | 簡潔 SVG 圖示或俐落純文字排版，無裝飾 Emoji | SLOP-03 |
| **狀態指示** | 假 LIVE 呼吸燈閃爍動畫 | 顯示具體數值與更新週期：`更新間隔: 5s`，精確顯示目前狀態 | SLOP-04 |
| **文字內容** | 充斥 *Elevate your workflow seamlessly* | 具體數據：`99.95% 可用率`、`4 節點在線`、`平均處理耗時 18.2ms` | SLOP-05 |

---

## 4. 自動化掃描與驗收指引

維護者可透過靜態掃描工具 `tools/verify_no_slop.py` 對產出的 HTML 進行自動化驗證：
```bash
python tools/verify_no_slop.py assets/anti-slop-demo/index.html
```
驗收通過標準為：掃描報告為 `0 violations found (PASS)`。
