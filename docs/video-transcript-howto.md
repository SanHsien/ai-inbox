# 影片逐字稿 SOP：字幕取不到時，用 yt-dlp 抓音訊 + Whisper 本機 GPU 轉寫

> 給後續接手的 AI Agent 看。目的：分析 YouTube 等影片時，**取得影片實際內容**，而不是只憑標題與說明欄推測。
> 工具腳本：[`tools/video_transcript.py`](../tools/video_transcript.py)；單元測試：[`tests/test_video_transcript.py`](../tests/test_video_transcript.py)。
> 首次驗證日期：2026-10-24（Windows 11 原生、Python 3.14、NVIDIA GeForce RTX 3060 12GB CUDA 實測通過）。

---

## 1. 何時用、何時不用

```text
要分析影片
   │
   ├─ 1) 先試官方字幕：python -m yt_dlp --skip-download --write-subs --write-auto-subs
   │       --sub-langs "zh-Hant,en" --sub-format vtt -o <前綴> <網址>
   │       成功 ──▶ 直接用字幕（最準、最快，不需轉寫）
   │       HTTP 429 / 無字幕 ▼
   ├─ 2) python tools/video_transcript.py <網址> --out <暫存資料夾>
   │       （自動偵測 RTX 3060 GPU，下載音訊 + faster-whisper CUDA float16 轉寫）
   └─ 3) 兩者皆失敗 ──▶ 請維護者貼逐字稿或摘要；筆記必須標明「未取得影片內容」
```

不適用：
- 需要看**畫面**才懂的內容（操作介面、圖表）。逐字稿只有口述，筆記要註明「畫面未看」。
- 付費牆或私人影片（下載會失敗；不要嘗試繞過登入或讀取瀏覽器 cookie）。
- 音訊無人聲或語言不明（腳本會因結果為空而報錯）。

---

## 2. 環境準備（本機已裝妥，以下供重裝或排查參考）

皆為 `pip --user` 安裝，不需系統管理員權限：

```powershell
python -m pip install --user -U yt-dlp "yt-dlp[curl-cffi]" faster-whisper "av>=14,<17" nvidia-cublas-cu12 nvidia-cudnn-cu12
```

### 本機已安裝版本與硬體（2026-10-24 實測狀態）

- **GPU**：NVIDIA GeForce RTX 3060 (12288 MiB, Driver 616.92)，`ctranslate2.get_cuda_device_count() == 1`
- **Python**：`C:\Python314\python.exe` (Python 3.14)
- **套件（User site-packages `C:\Users\SanHsien\AppData\Roaming\Python\Python314\site-packages`）**：
  - `yt-dlp` 2026.10.21 + `curl-cffi` 0.16.3
  - `faster-whisper` 1.2.1 + `ctranslate2` 4.8.3
  - `av` 16.1.0（鎖定 `<17`）
  - `nvidia-cublas-cu12` 12.9.2.10、`nvidia-cudnn-cu12` 9.27.0.42、`nvidia-cuda-nvrtc-cu12` 12.9.86

### 已知陷阱（每一條都是實際踩過的）

| 症狀 | 原因 | 解法 |
| --- | --- | --- |
| `yt-dlp` 指令找不到 | Scripts 目錄 `…\Python314\Scripts` 不在 PATH | 一律用 `python -m yt_dlp`；腳本已內建 |
| `TypeError: open() got an unexpected keyword argument 'metadata_errors'` | pip 預設裝到 `av` 19，與 `faster-whisper` 1.2.1 不相容 | `python -m pip install --user "av>=14,<17"`（實測 16.1.0 可用） |
| `RuntimeError: Library cublas64_12.dll is not found or cannot be loaded` | `ctranslate2` 走 CUDA 需要 `cublas64_12.dll` 與 `cudnn64_9.dll`，但 pip wheel 裝在 `site-packages/nvidia/*/bin`，不在系統 `PATH` | 安裝 `nvidia-cublas-cu12 nvidia-cudnn-cu12`；`tools/video_transcript.py` 的 `_register_cuda_dlls()` 已在啟動時自動掛載 DLL 路徑 |
| 字幕下載 `HTTP Error 429: Too Many Requests` | YouTube 字幕端點限流；裝 `yt-dlp[curl-cffi]` impersonation 也沒解 | 直接改走 `video_transcript.py` 音訊轉寫；**不要連續狂打字幕端點** |
| 抓網頁取得的字幕網址下載得到 0 位元組 | 自動字幕網址需額外簽章憑證 | 同上，不要手刻 `timedtext` 網址 |
| 終端機輸出中文變亂碼 | Windows 主控台編碼顯示問題，檔案本身是 UTF-8 | 用 `read_file` 或 `Get-Content -Encoding UTF8` 讀檔確認 |
| `yt-dlp` 警告 No supported JavaScript runtime | 未安裝 deno | 音訊下載仍可成功，可忽略 |

---

## 3. 使用方式

```powershell
cd C:\GitHub\ai-inbox
python tools/video_transcript.py https://youtu.be/<id> --out <暫存資料夾>
# 參數：
#   --device auto|cuda|cpu  預設 auto（偵測到 NVIDIA GPU 自動用 cuda + float16，否則 cpu + int8）
#   --model small           預設 small；要更高準確度可傳 medium 或 large-v3（RTX 3060 12GB 跑得動）
#   --lang zh               預設 zh
```

- 輸出：`<暫存資料夾>/transcript.txt`，每行 `[mm:ss] 文字`。
- 若 `<暫存資料夾>/audio.*` 已存在且非空，腳本會直接重用，不重複向 YouTube 下載。
- **暫存資料夾請放在 repo 以外**（例如各 Agent 的 scratch 目錄）。音訊與逐字稿是第三方內容，不要提交進本 repo。
- 失敗會明確丟出 `RuntimeError`（yt-dlp 失敗、找不到音訊、CUDA 載入失敗、轉寫為空），不會靜默產生空檔。

### 實測效能對照（2026-10-24，同一支 510 秒中文影片）

| 模式 | 裝置與精度 | 總耗時 | 輸出行數 | 備註 |
| --- | --- | --- | --- | --- |
| **GPU（預設 `auto` / `cuda`）** | RTX 3060 12GB (`float16`) | **93.5 秒** | 290 行 | 速度約為 CPU 的 **3.4 倍** |
| CPU (`--device cpu`) | CPU (`int8`) | 約 320 秒 | 247 行 | 無 GPU 環境的備援 |

---

## 4. 逐字稿的可信度與校對（必做）

Whisper `small` 會誤聽**專有名詞與外來語**。本次實例：

| 聽寫結果 | 實際 |
| --- | --- |
| 黑捲、黑准、Hagen | HeyGen |
| 全GPT、HRGPD | ChatGPT |
| Cloud | Claude |
| 安納蘇、令（聲音名稱） | 無法確認拼寫 |

規則：
1. 工具名、人名、數字依**上下文與官方網站**還原；還原不了的，筆記裡寫「聽寫為 X，無法確認」，不要猜；或改用 `--model medium` 重跑。
2. 逐字稿中的**數據與宣稱**（例如「不會被降權」）視為「講者宣稱」，要去官方來源查證後才能當事實；未查證就在筆記標「未查證」。

---

## 5. 筆記中的來源揭露（寫進 `notes/*.md`）

分析影片的筆記必須誠實標示取得內容的方式。擇一放在筆記最上方：

- **已取得逐字稿**：
  `> [!NOTE] 資料來源：以 tools/video_transcript.py（yt-dlp 下載音訊 + faster-whisper CUDA/CPU 轉寫）取得逐字稿；轉寫有誤聽（列出已知例子）；影片畫面未看。`
- **只有標題與說明欄**：
  `> [!WARNING] 本筆記未看影片、未取得字幕，以下僅依標題、說明欄與章節，具體做法未查證。`

---

## 6. 相關檔案

- [`AGENTS.md`](../AGENTS.md)：流程 A（文章／影片分析）與寫作鐵律。
- [`tools/video_transcript.py`](../tools/video_transcript.py)：轉寫腳本本體。
- [`tests/test_video_transcript.py`](../tests/test_video_transcript.py)：單元測試。
- [`notes/2026-10-24-ai-influencer-ig-story-chatgpt-heygen-elevenlabs.md`](../notes/2026-10-24-ai-influencer-ig-story-chatgpt-heygen-elevenlabs.md)：第一個用本流程完成的影片分析範例。
