# 學術論文雙語排版與公式保護閱讀工具手冊：PaperRead、MinerU 與 Moonlight 對照

> 本手冊整理英文學術論文雙語研讀的工具選擇，針對雙欄排版破碎、數學公式被模型改壞、文獻引用失真三個痛點。  
> 主角是開源的 **PaperRead**（[`YuriyLin/PaperRead`](https://github.com/YuriyLin/PaperRead)），也就是[來源貼文](../notes/2026-10-17-moonlight-bilingual-paper-reader.md)介紹的那一套；**MinerU** 是批次轉檔的搭配工具；**Moonlight** 只留作對照。  
> 交付形式：以 `ai-inbox` 範本手冊（`docs/academic-bilingual-paper-reader-guide.md`）交付。

> **2026-11-16 更正**：本手冊第一版（`T-20261017-13`）把貼文裡的工具認成商業服務 Moonlight，全篇以 Moonlight 為主角。貼文作者在留言區給的連結是 `YuriyLin/PaperRead`，兩者性質相反（開源、資料在本機，對上雲端商業服務）。本版依 `T-20261017-35` 改以 PaperRead 為主角。第一版的「Moonlight 快速上手」步驟沒有實測依據，已刪除。

---

## 1. 學術論文雙語閱讀的核心痛點

傳統機器翻譯（如 Google 翻譯、常見瀏覽器擴充套件）在閱讀學術 PDF 時常出三種問題：

```text
┌────────────────────────────────────────────────────────┐
│ 學術論文 PDF 傳統翻譯三大災難                          │
├────────────────────────────────────────────────────────┤
│ 1. 排版崩壞：雙欄排版錯亂、跨頁斷句、欄間文字串讀混淆   │
│ 2. 公式破壞：LaTeX 數學符號與上下標被誤譯、吃字或亂碼   │
│ 3. 引用混淆：文獻引用 [Author, Year] 與交叉參照失效      │
└────────────────────────────────────────────────────────┘
```

1. **雙欄排版斷裂**：工具認不出雙欄的閱讀順序，把左欄底部與右欄頂部接在一起，或把行尾連字號拼成無意義的單詞。
2. **數學公式破壞**：複雜數學式（如 $\arg\min_{\theta} \mathbb{E}_{x \sim p}[\|f_\theta(x) - y\|^2]$）被當成一般英文送去翻譯，符號遺失或變數被換成漢字。
3. **引用與圖表混淆**：文中錨點（如 `[Vaswani et al., 2017]`、`Eq. (4)`、`Fig. 2`）被直譯，失去索引功能。

---

## 2. 三套工具對照

PaperRead 與 MinerU 的欄位依 2026-11-16 讀到的 repo 內容填寫（GitHub API、README、原始碼）；Moonlight 欄未重新查證，只寫性質。

| 評比維度 | **PaperRead** (`YuriyLin/PaperRead`) | **MinerU** (`opendatalab/MinerU`) | **Moonlight** (`themoonlight.io`) |
| :--- | :--- | :--- | :--- |
| **定位** | 論文閱讀、文獻探索、筆記整理的本機工作區（貼文介紹的就是這套） | PDF 轉 Markdown／JSON 的文件解析工具 | 雲端商業論文閱讀服務（第一版誤認的對象） |
| **授權** | `LICENSE` 是 MIT；貼紙素材另有各自授權 | Apache 2.0 加附加條款（達一定規模的商業使用要另取授權） | 商業服務 |
| **規模（2026-11-16）** | 367 顆星、17 個 fork；2026-10-09 建立，最新版 v1.5.3（2026-11-13） | 約 8.4 萬顆星；最新版 4.2.3（2026-11-16） | 未查證 |
| **安裝** | Windows x64 安裝檔、macOS arm64 DMG、Linux AppImage；或 Docker 瀏覽器版；或 `pip install -e .` 從原始碼跑 | `uv pip install -U "mineru>=4.0,<5"`，Python 3.11–3.14；預設安裝可用 CPU | 未查證 |
| **閱讀介面** | 有：左欄譯文、右欄 PDF 原頁，可切原文／譯文／雙語，另有筆記、問 AI、研究面板 | 無，輸出檔要用自己的編輯器看 | 有（未查證細節） |
| **翻譯模型** | 自己選：本機 CLI（Claude Code、Codex CLI、Antigravity CLI）、雲端 API、本機 Ollama／LM Studio | 不翻譯，只解析 | 服務內建 |
| **資料去向** | 文獻庫在本機（`~/PaperRead`，JSON 檔）；翻譯與問答的內容送到所選模型 | 預設本機解析；加 `--remote` 才上傳；另有預設開啟的使用統計（不含文件內容，可關） | 文件上傳到服務商 |
| **批次自動化** | 有整個資料夾匯入與 Zotero 匯入，定位仍是互動閱讀 | 有 CLI，適合接進自動化流程 | 未查證 |

---

## 3. PaperRead：唯讀評估結果（`T-20261017-35`）

> **評估方式與限制**：2026-11-16 用 GitHub API 讀 README、`LICENSE`、`CHANGELOG.md`、`CONTRIBUTING.md`、Docker 設定、檔案樹與幾支關鍵原始檔（`easyread/engines.py`、`prompts.py`、`updates.py`、`netcheck.py`、`cli_models.py`、`selectable_text.py`），對應 commit `22ccc94`（2026-11-14）。  
> **沒有 clone、沒有安裝、沒有執行。** 本節所有「行為」都是從原始碼與文件讀出來的，不是實測結果；需要實跑才能回答的項目列在 3.5 節。

### 3.1 專案組成

- Python 套件名仍是 `easyread`（沿用上游 [EasyRead](https://github.com/Edwardxlai/easyread)），後端是本機 HTTP 服務，預設開在 `http://127.0.0.1:8765`；桌面版是 Electron 外殼。
- 語言比例：Python 與 JavaScript 各約 140 萬位元組，另有少量 TypeScript（筆記編輯器）。
- `tests/` 有 Python 與 Node 兩套測試，GitHub Actions 有 `test.yml`、`docker.yml`、`release.yml`。
- 檔案樹共 1,033 項，其中 200 多個是貼紙素材。

### 3.2 安裝方式（三選一，都還沒在本機試過）

| 方式 | 指令或檔案 | 讀到的重點 |
| :--- | :--- | :--- |
| 安裝檔 | Releases 的 `PaperRead-Setup-1.5.3.exe`（約 196 MB） | README 沒提程式碼簽章；個人專案的安裝檔，執行前要走第三方程式檢查流程 |
| Docker | `docker compose up -d` 後開 `http://localhost:8765` | 映像檔用 `python:3.12-slim`；連接埠只綁 `127.0.0.1`；設定檔註明服務沒有登入機制，另有 Host 標頭檢查（PR #3、#4） |
| 原始碼 | `python -m pip install -e .` 後執行 `easyread` | 需要 Python 3.10 以上；改桌面版另需 Node.js 22 以上 |

### 3.3 公式與引用怎麼處理

PaperRead 的做法是**請模型把公式重寫成 KaTeX 能顯示的 TeX**，不是把公式抽出來隔離、翻完再放回去。依據是 `easyread/prompts.py` 的翻譯規則：

- 行內數學一律寫成 `$TeX$`，行間公式獨立成區塊並保留原編號；看不清楚就標「待核對」，不猜。
- 數字引用 `[n]` 照原樣保留；作者加年份的引用改寫成站內連結；參考文獻列表不翻譯；腳註用 `[^n]`，與文獻引用分開。
- 圖、表、公式、章節的交叉參照改寫成可點的站內連結。
- 另有「裸露 TeX 修復」機制（`repair_guard.py`），格式出錯時只重試出錯的區塊。

這代表公式正不正確要看所接的模型。issue #9（2026-11-14 開，未關）回報的正是這件事：用 3B、4B 的本機小模型時，提示詞裡的公式範例會被照抄進譯文。對照本 repo 的 [`templates/latex-citation-protection-prompt.md`](../templates/latex-citation-protection-prompt.md)：那份範本要求公式逐字不變，PaperRead 的規則是允許模型重排成等價的 TeX，兩者標準不同，不能拿 `tools/verify_academic_and_latex_guard.py` 的逐字比對直接驗 PaperRead 的輸出。

### 3.4 接本機 CLI 時實際執行什麼

讀 `easyread/engines.py` 得到的呼叫方式：

| 模型後端 | 呼叫方式 | 權限範圍 |
| :--- | :--- | :--- |
| Claude Code | `claude -p`，帶 `--allowedTools Read`、`--strict-mcp-config`、`--disable-slash-commands`、`--no-session-persistence`；翻譯時再加 `--tools Read` | 只開放讀檔工具，不載入使用者的 MCP 設定 |
| Codex CLI | `codex exec --sandbox read-only --ephemeral --skip-git-repo-check` | 唯讀沙盒 |
| Antigravity CLI | 帶 `--dangerously-skip-permissions` | **略過權限確認**，三者中限制最少 |

其他會碰到本機設定或對外連線的地方：

- 會**讀取** `~/.claude/settings.json` 與 `~/.codex/config.toml`、`~/.codex/models_cache.json`，用途是取得模型清單、預設模型與 API 位址；讀到的片段裡沒有寫入這些檔案的程式碼（只讀了部分檔案，不能保證全專案都沒有）。
- 每天向 `api.github.com` 查一次最新版本，可在設定裡關掉。
- 文獻搜尋（OpenAlex 等）與雲端模型會對外連線；README 寫明此時相關內容會送到所選服務。

採用建議：接 Claude Code 或 Codex CLI 的限制較嚴；Antigravity CLI 那條路徑帶了略過權限的旗標，本機要用就先不選它。

### 3.5 留言與 issue 提到的兩個限制

| 限制 | 來源 | 從 repo 讀到的現況 | 本機是否重現 |
| :--- | :--- | :--- | :--- |
| PDF 原頁是圖片，原文不能複製 | 貼文留言（`_zhi07`），作者回覆改用「雙語」顯示 | `CHANGELOG.md` 的 v1.5.2 列有「PDF 原頁透明文字層」，寫明可複製原文；原始碼有對應的 `easyread/selectable_text.py`。看起來 v1.5.2 之後已處理 | **未實跑** |
| 背景翻譯或自動儲存時，閱讀位置往上跳 | issue #10（2026-11-14 開） | 仍是開啟狀態、沒有回覆；最新版 v1.5.3 早於這則 issue，所以還沒有修正版 | **未實跑** |

### 3.6 還沒做的部分（照實列出）

`T-20261017-35` 的驗收標準要求「實測段落」。以下項目都要實際執行才能回答，本次派工限定唯讀評估，**全部未做**：

1. 用含密集公式的 arXiv 論文跑一次雙語對照，檢查公式與引用標記是否保留。
2. 確認問 AI 能否接上本機的 Claude Code 或 Codex CLI。
3. 在本機重現 3.5 節的兩個限制。
4. clone 到隔離目錄後的完整安全檢查（本次只讀了部分檔案，沒有掃過全部原始碼與相依套件）。

未實跑的原因：派工範圍排除 clone、安裝與執行；而且照本 repo 規則，第三方程式要先通過檢查流程才能在本機執行。

---

## 4. MinerU：批次轉檔的搭配工具

### 4.1 適用情境

- 要把大量 PDF 轉成 Markdown，放進自己的筆記庫或檢索流程。
- 公式極密集的文獻，需要拿到 LaTeX 原始碼而不是畫面。
- 文件不能離開本機（不加 `--remote`，並關掉使用統計）。

### 4.2 安裝與指令（依 2026-11-16 的官方 README，本機未實跑）

```bash
# 建立環境並安裝（Python 3.11–3.14）
pip install uv
uv venv .mineru --python 3.12
uv pip install -U "mineru>=4.0,<5"

# 解析單篇 PDF；預設在本機處理
mineru parse "paper.pdf" --json

# 關掉使用統計
mineru telemetry disable
```

- 第一版手冊寫的 `pip install magic-pdf[full]` 與 `magic-pdf -p` 是舊版指令，現行 4.x 版已改成上面的 `mineru`。
- 預設安裝可在只有 CPU 的機器上跑；`full` 附加元件才需要 8 GB 以上顯示記憶體的 NVIDIA 顯示卡。
- `mineru parse` 加 `--remote` 會把文件送到遠端解析；機密文件不要加。
- 使用統計預設開啟，README 說明不含文件內容、檔名與路徑；要完全不外送就執行 `mineru telemetry disable`。

### 4.3 接上翻譯的流程

MinerU 只負責解析。要得到雙語版，把輸出的 Markdown 交給模型翻譯，並套用公式保護提示詞：

```text
[原始 PDF] ──MinerU──▶ [Markdown（公式是 LaTeX 原始碼）]
                           │
                           ▼
        [模型翻譯，套用 templates/latex-citation-protection-prompt.md]
                           │
                           ▼
        [雙語 Markdown] ──▶ tools/verify_academic_and_latex_guard.py 比對公式與引用
```

---

## 5. Moonlight（僅供對照）

- 雲端商業論文閱讀服務，文件要上傳到服務商，所以未公開的論文草稿、專利、受保密協議約束的文件不能用。
- 第一版手冊列的安裝步驟、介面操作、收費方式都沒有實測或查證依據，本版不再保留；要用請以官方網站為準。

---

## 6. 選型建議

```text
要讀的文件是什麼？
  ├─ 公開論文（arXiv、研討會）
  │    ├─ 想要雙欄對照、劃線、問 AI ──▶ PaperRead（先完成第 3.6 節的實測與安全檢查）
  │    └─ 想批次轉成 Markdown 進筆記庫 ──▶ MinerU
  │
  └─ 機密文件（專利草稿、內部報告、未發表稿）
       ├─ 只要解析 ──▶ MinerU，不加 --remote，關掉使用統計
       └─ 要翻譯或問答 ──▶ PaperRead 接本機模型（Ollama／LM Studio）；
                          接雲端模型或雲端服務（含 Moonlight）都會把內容送出去
```
