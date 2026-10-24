# 學術論文雙語排版與公式保護閱讀工具手冊：Moonlight 與開源 MinerU 對比指南

> 本手冊為學術論文雙語研讀專用工具手冊，針對英文學術論文（尤其是 CV、NLP、Robotics、AI 系統論文）中常見的雙欄排版破碎、數學公式被模型破壞竄改、文獻引用失真三大痛點，提供商業工具 **Moonlight** 與開源本地方案 **MinerU** 的全方位對比、操作指南與工作流選型建議。  
> 交付形式：以 `ai-inbox` 範本手冊（`docs/academic-bilingual-paper-reader-guide.md`）交付。

---

## 1. 學術論文雙語閱讀的核心痛點

傳統機器翻譯（如 Google 翻譯、常見瀏覽器擴充套件）在閱讀學術 PDF 時往往引發嚴重挫折：

```text
┌────────────────────────────────────────────────────────┐
│ 學術論文 PDF 傳統翻譯三大災難                          │
├────────────────────────────────────────────────────────┤
│ 1. 排版崩壞：雙欄排版錯亂、跨頁斷句、欄間文字串讀混淆   │
│ 2. 公式破壞：LaTeX 數學符號與上下標被誤譯、吃字或亂碼   │
│ 3. 引用混淆：文獻引用 [Author, Year] 與交叉參照失效      │
└────────────────────────────────────────────────────────┘
```

1. **雙欄排版斷裂（Column Splitting & Line Breaks）**：
   - 傳統工具無法正確辨識雙欄排版閱讀順序，常將左欄底部與右欄頂部文字接合，或把行尾連字號（hyphenation）錯誤拼接成無意義單詞。
2. **數學公式破壞（Formula Corruption）**：
   - 複雜數學式（如 $\arg\min_{\theta} \mathbb{E}_{x \sim p}[\|f_\theta(x) - y\|^2]$、矩陣上下標、特殊符號 $\nabla, \sum, \prod$）被當作一般英文送入翻譯模型，導致符號遺失、變數被替換為漢字或輸出損壞。
3. **學術引用與圖表混淆（Citation & Cross-reference Distortion）**：
   - 文中文獻錨點（如 `[Vaswani et al., 2017]`、`Eq. (4)`、`Fig. 2`）被生硬直譯，破壞學術閱讀的索引便利性。

---

## 2. Moonlight vs. MinerU 全方位對比矩陣

| 評比維度 | **Moonlight** (`themoonlight.io`) | **MinerU** (`opendatalab/MinerU`) |
| :--- | :--- | :--- |
| **工具定位** | 雲端商業 SaaS / Chrome 擴充 / 行動端 App | 本地開源多模態文檔解析工具庫 (GitHub 20k+ ⭐) |
| **部署門檻** | **零門檻**：安裝瀏覽器擴充功能即可開箱即用 | **需環境**：需 Python 3.10+、PyTorch 與 CUDA GPU 支援 |
| **閱讀介面** | **原生雙欄同步滾動**：左欄中文對照，右欄原始 PDF，支援原文/雙語/譯文一鍵切換 | **無內建閱讀器**：輸出標準 Markdown/JSON，需搭配 VS Code、Obsidian 等 Markdown 編輯器 |
| **公式保護能力** | 優良：自動隔離數學區塊並以 KaTeX 漂亮渲染 | **極致頂級**：搭載專用 MFD（公式偵測）與 MFR（公式識別）模型，轉出精準 LaTeX 源碼 |
| **排版還原度** | 優良：針對學術論文自訂最佳化排版視圖 | **學術級頂級**：完美抽離多欄、標題層級、表格、圖表旁註與腳註 |
| **數據隱私與合規** | **雲端處理**：PDF 會上傳至服務商雲端解析（適合公開 arXiv 論文） | **100% 本地運算**：完全離線運行，絕對零隱私外洩（適合未公開專利與商務機密） |
| **費用與配額** | Freemium：提供免費每日額度，高頻使用需付費訂閱 | **完全免費開源**：採 Apache 2.0 / 專用開源協議，無使用次數限制 |
| **批次與自動化** | 不支援（僅限手動單篇閱讀） | **原生支援**：具備強大 CLI 與 Python API，可整合進自動化文獻解析管線 |

---

## 3. Moonlight 快速上手與在線泛讀指南

### 3.1 適用情境
- 每日瀏覽追蹤 arXiv、OpenReview 最新放出的公開論文。
- 需要在 5~10 分鐘內快速瀏覽 Abstract、Introduction、Method 大綱與 Conclusion。
- 手機/平板端移動閱讀，需輕量雙語對照。

### 3.2 操作流程
1. **安裝擴充功能**：在 Chrome Web Store 安裝 *Moonlight - AI Paper Reading Assistant*。
2. **開啟論文網頁**：直接造訪 arXiv 論文頁面（例如 `https://arxiv.org/abs/2401.xxxxx`）或直接在瀏覽器打開 PDF 檔案。
3. **啟動雙語視圖**：點擊瀏覽器側邊的 Moonlight 圖示，頁面自動載入雙欄閱讀視圖：
   - **左欄（譯文/對照欄）**：重新編排的高清字體中文排版，公式以 LaTeX 區塊獨立保留。
   - **右欄（原始 PDF 欄）**：保留論文原始向量字體、排版格局與高解析度圖表。
4. **互動閱讀技巧**：
   - **雙向游標對齊**：滑鼠懸停於左欄某段，右欄對應原始段落自動高亮，反之亦然。
   - **雙語切換**：使用頂部快捷鍵切換「僅原文」、「僅譯文」或「雙語交錯」。
   - **Contextual RAG 提問**：點選特定難懂公式或段落，呼叫側邊欄「Ask Paper AI」要求進一步解釋該變數的物理意義。

---

## 4. MinerU 本地私有化深度研讀工作流

### 4.1 適用情境
- 涉及內部未公開研究、機密專利申請草稿、受 NDA 保護的技術白皮書。
- 公式極度密集（如純理論數學、高能物理、密碼學、複雜 3D 幾何推導）之重要文獻。
- 欲建立個人離線向量知識庫（RAG），需將數百篇 PDF 批次轉為高品質 Markdown。

### 4.2 本地安裝與配置

推薦在具備 NVIDIA GPU（至少 8GB VRAM）的環境安裝：

```bash
# 1. 建立獨立虛擬環境
conda create -n mineru python=3.10 -y
conda activate mineru

# 2. 安裝 magic-pdf 與全功能依賴 (含 GPU 支援)
pip install -U magic-pdf[full] --extra-index-url https://wheels.myhloli.com

# 3. 下載模型權重 (版面分析、公式識別、表格識別模型，約 2GB)
# 依官方指示自動下載並配置 ~/.magic-pdf.json
```

### 4.3 CLI 轉檔指令

```bash
# 將單篇 PDF 轉換為包含精準 LaTeX 公式的 Markdown 結構
magic-pdf -p "paper.pdf" -o "./output" -m auto

# 批次處理整個目錄下的論文
magic-pdf -p "./papers_dir" -o "./markdown_output" -m auto
```

### 4.4 結合 LLM 之「公式保護」雙語 Markdown 產出管線

MinerU 輸出的 Markdown 結構將數學公式完整封裝在 `$...$` 與 `$$...$$` 中。將其交由 LLM 翻譯為雙語閱讀版時，應使用以下防護策略：

```text
[原始 PDF] ──MinerU──▶ [精確 Markdown (含原始 LaTeX)]
                           │
                           ▼
              [LLM 雙語翻譯 (公式嚴格保護 Prompt)]
                           │
                           ▼
          [雙語對照 Markdown (在 Obsidian / VS Code 閱讀)]
```

---

## 5. 總結與選型建議決策樹

```text
欲研讀的論文類型？
  ├─ 是公開 arXiv / 研討會論文？
  │    ├─ 需要快速在瀏覽器掃讀、泛讀 ──▶ 【首選 Moonlight】
  │    └─ 需要做深度筆記、沈澱至個人知識庫 ──▶ 【MinerU 轉檔後存入筆記庫】
  │
  └─ 是機密專利、公司內部報告、未發表草稿？
       └─ 嚴禁上傳任何雲端 ──▶ 【唯一選擇 MinerU 本地離線解析】
```
