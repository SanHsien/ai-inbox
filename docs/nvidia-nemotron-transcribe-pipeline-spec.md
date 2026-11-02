# NVIDIA Nemotron 3.5 Transcribe 語音辨識模型技術規格與 Windows 本機語音輸入適用性評估

- **文件版本**：1.0.0
- **查證日期**：2026-11-02
- **對應任務**：`T-20261031-34`（筆記：[`notes/2026-10-31-nvidia-nemotron-3-5-transcribe-prompt-guided-asr.md`](../notes/2026-10-31-nvidia-nemotron-3-5-transcribe-prompt-guided-asr.md)）
- **讀者**：正在評估「這個模型能不能放進 Windows 本機語音輸入工具」的人。
- **一手來源**：Hugging Face 模型卡 <https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B>（倉庫 revision `c17667641642c4265ff2b7037dd101b7d4567634`，最後修改 2026-10-29；下文「模型卡」皆指此版本）。數字另以 Hugging Face API（`/api/models/...`、`/tree/main`）交叉核對。

---

## 1. 結論先講

**模型存在，名稱對得上**（`nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B`，Hugging Face 上線日期 2026-10-28，授權 OpenMDW-1.1）。但「能不能用在 Windows 本機語音輸入」要看你說的是哪種語音輸入：

| 你要做的事 | 能不能 | 依據與條件 |
| :--- | :--- | :--- |
| 錄好的音檔轉文字（會議錄音、訪談、整段口述後再貼上） | **可以，但門檻高** | 見第 6 節：官方支援的 Windows 路徑只有「WSL2 + vLLM／Transformers」與「原生 Windows + GGML」；GPU 與顯存要求見第 5、6 節 |
| 邊說邊出字的即時聽寫（按住說話、即時上字） | **不適合** | 模型卡原話：「This is an offline model. Internal audio chunking does not make it a real-time streaming ASR service.」；官方即時方案是另一個較小的串流模型（第 9 節） |
| 一般消費級顯卡（例如 12–24 GB 顯存） | **官方沒有背書，未驗證** | 官方硬體表沒有任何消費級 Ada／Ampere 顯卡；唯一的消費級項目是 RTX 5090 + NVFP4（第 5 節） |
| 繁體中文（台灣）聽寫 | **未驗證** | 模型卡只寫 Chinese Mandarin，品質等級是最低一級 Supported；輸出繁簡未說明（第 7 節） |

一句話：這是一個**離線、大型（磁碟 20–63 GiB）、以資料中心／高階 GPU 為目標**的語音語言模型；適合當「錄音後處理」管線的一環，不適合當輕量、低延遲的聽寫引擎。

---

## 2. 筆記說的與模型卡對照（哪些成立、哪些不成立）

筆記是 agent 自動產生的線索，以下逐項用模型卡核對。

| 筆記說法 | 核對結果 |
| :--- | :--- |
| 「34B 混合專家，僅激活 4.3B」 | **成立**。模型卡 Model Summary：Total Parameters 34B（4.3B active），**含音訊編碼器**。Hugging Face API 的 safetensors 總參數為 33,697,781,029。 |
| 「30B-A4B」命名 | 倉庫名稱是 30B-A4B，但模型卡寫總參數 34B；基底語言模型是 `Nemotron-3.5-Lightning-30B-A3B`。所以**名稱裡的 30B 不等於總參數量**，引用時以模型卡的 34B／4.3B 為準。 |
| 「Mamba-2 + Transformer 混合架構」 | 成立。模型卡：Mamba-2–Transformer hybrid Mixture of Experts language model，搭配 Transformer ASR 編碼器與說話人編碼器。 |
| 「65,536 上下文、單次 1 小時音訊」 | 成立，但模型卡加註：訓練時最長 1 小時／65,536 token，「not guaranteed to generalize beyond these limits」。 |
| 「約 800M 語音編碼器」 | 成立。模型卡：約 800M 的 joint audio encoder；基底元件另列 600M 預訓練 ASR transformer 與約 99M 的 Nemotron-3-Diarization 說話人編碼器（兩者與 800M 的包含關係模型卡未說明）。 |
| 「8 人重疊爭辯說話人分離」 | **不能當規格**。模型卡只在訓練資料說明「AuMix 合成最多 8 位說話人的對話」；推論用的官方提示詞只列 4 個標籤 `<spk:0>`–`<spk:3>`。沒有任何「最多辨識 8 人」的保證，也沒有 8 人的評測。 |
| 「RTX 4090 / 5090 以 FP8／NVFP4 流暢運行」 | **不成立或未驗證**。官方硬體表只有 RTX 5090 + NVFP4（vLLM／Transformers／GGML）；RTX 4090 沒列；FP8 在消費級顯卡上沒有官方項目。「流暢」沒有任何量測。 |
| 「Mamba 讓長錄音辨識速度獲得數倍提升」 | **無來源**。模型卡沒有與純 Transformer 的比較。不要引用。 |
| 「顛覆 Whisper」「Whisper 多人搶話崩潰」「WhisperX 切片斷裂」及比較表 | **模型卡完全沒有提到 Whisper**。比較表的 Whisper 欄為筆記自行填寫，**未驗證**，本文不沿用。

**為什麼本文沒有 Whisper 對比表**：任務 DoD 原要求 Whisper 對比基準表，但模型卡沒有任何 Whisper 數據，一手來源查無，硬做表只會是未驗證的數字；本文改列模型卡實際有的對照（Open ASR Leaderboard 上與 Qwen3-ASR-1.7B、Parakeet-TDT-0.6B-v3 的比較，見模型卡「Results at a Glance」）。若要 Whisper 對比，需自行用同一批錄音實測。 |
| 「內建字級時間戳記」 | 成立但有條件：需 vLLM + NeMo 的 CTC 時間戳中介軟體，不是所有執行路徑都有（第 4.3 節）。 |
| 「Contextual Entity Biasing 大幅降低 WER」 | 方向成立：用 `Context terms:` 提示可降低專有名詞錯誤，數字見第 4.2 節。 |
| 「Direct Audio QA」 | 成立，但模型卡註明音訊理解**僅在英文評測**，其他語言「may not work reliably」。 |
| 「支援 BF16、FP8、NVFP4」 | 成立，分別是三個倉庫（第 5 節）。 |
| 「原生支援 `AutoModelForMultimodalLM`、`AutoProcessor`」 | 成立，但需要從原始碼安裝 transformers：`pip install git+https://github.com/huggingface/transformers`（模型卡寫法）。 |

---

## 3. 基本規格（全部來自模型卡）

| 項目 | 內容 |
| :--- | :--- |
| 模型名稱 | NVIDIA-Nemotron-3.5-Transcribe-30B-A4B |
| 發行 | Hugging Face、NVIDIA NeMo Speech（GitHub）、build.nvidia.com、NGC；日期 2026-10-28 |
| 總參數／激活參數 | 34B／4.3B（含音訊編碼器）；語言骨幹約 3.5B 激活 + 約 800M 音訊編碼器 |
| 架構 | Mamba-2–Transformer hybrid MoE 語言模型 + Parallel Expert Encoder（Transformer ASR 編碼器與 Sortformer 說話人編碼器）+ CTC 時間戳對齊頭；內建 Multi-Token Prediction |
| 輸入 | 音訊 + 文字提示；格式 `.wav`、`.flac`、`.mp3`、`.ogg`（能解碼成 PCM 者）；內部處理 16 kHz 單聲道 float32 |
| 輸出 | 文字；啟用時間戳時另有 `ctc_timestamps` 結構 |
| 上下文長度 | 65,536 tokens；錄音最長 1 小時（訓練上限） |
| 語言 | 40 種（含 Chinese Mandarin、Japanese、Korean、English 等）；逐語言的功能矩陣在模型卡 Language Support Matrix |
| 授權 | OpenMDW-1.1（<https://openmdw.ai/license/1-1/>）。倉庫 `LICENSE` 檔內容：授予在無限制下處理 Model Materials 的權利；散布時須保留該協議副本與來源聲明；對模型提起專利或著作權訴訟者權利終止；**不對輸出的使用設限**；無擔保。模型卡另說明「ready for commercial or non-commercial use」。Hugging Face 的 license 欄顯示 `other`（license_name: openmdw-1.1）。 |
| 即時性 | **離線模型**，非串流 |
| 建議取樣 | 轉寫／翻譯／語言辨識：temperature 0、關閉 reasoning；音訊理解：temperature 0.6、top_p 0.95、開啟 reasoning |
| 附帶元件第三方授權 | 倉庫含 `THIRD_PARTY_NOTICES.md`、`licenses/Qwen3-ASR-LICENSE.txt`、`licenses/vLLM-LICENSE.txt`；模型卡的「生成迴圈防護函式」改編自 Qwen3-ASR，為 Apache-2.0 而非 OpenMDW-1.1 |

---

## 4. 呼叫規格（照做即可）

以下參數取自模型卡「Inference Setup and Prompts」，**本文沒有實際跑過模型**（沒有符合條件的硬體），所以是「照模型卡抄錄並標明出處」，不是實測結果。

### 4.1 提示詞：用使用者訊息放指令，系統提示詞留空

模型卡規則：轉寫、翻譯、語言辨識時**系統提示詞留空**（直接省略 system 訊息），把指令寫在 user 訊息並附音訊。

| 目的 | user 提示詞（模型卡原文） |
| :--- | :--- |
| 逐字稿（含贅字、重複） | `Audio transcription. Language: as spoken. Wording: verbatim, including fillers and repetitions. Formatting: punctuation and capitalization. Output: transcript only.` |
| 可讀稿（去贅字與無意義重複） | `Audio transcription. Language: as spoken. Wording: omit fillers and accidental repetitions; keep the remaining spoken wording unchanged. Formatting: punctuation and capitalization. Output: transcript only.` |
| 專有名詞偏置 | `Transcribe with punctuation and capitalization. Context terms: <names and terms>.` |
| 說話人標籤 + 時間戳 | `Transcribe this audio with punctuation and capitalization. Include all spoken words and verbal fillers. Write numbers in their standard written form. Put speaker tags <spk:0> <spk:1> <spk:2> <spk:3> on the transcription.`（同時要求時間戳，見 4.3） |
| 只轉寫最靠近麥克風的人（模型卡標示 experimental） | `Transcribe this audio. Include all spoken words and verbal fillers. Write numbers as spoken. No punctuation or capitalization. Transcribe only the speaker nearest to the microphone. Do not transcribe any other voices.` |
| 翻譯 | `Please translate the given speech to <target language>.` |

「可讀稿」是模型卡 Prompt Guide 的「Readable text」，用途寫為「Captions, notes, and searchable recordings」。注意這是提示詞行為，**沒有保證每個贅字都被刪**，要驗證請自備測試音檔。

### 4.2 專有名詞偏置的效果（模型卡實測，英文）

| 評測 | 無提示 | 有提示 |
| :--- | ---: | ---: |
| ContextASR-Bench 整體 WER（%） | 3.33 | 1.71（Fine） |
| ContextASR-Bench 名詞實體 WER（%） | 12.21 | 2.20（Fine） |
| Contextual Earnings22 關鍵字 Recall（%） | 58.16 | 89.50（Global）／96.05（Local） |

這些是**英文**資料集上的結果；中文專有名詞是否同樣有效，模型卡沒有數字，未驗證。

### 4.3 字級時間戳與說話人（需 vLLM + NeMo 中介軟體）

來源：模型卡「Word Timestamps and Speaker Diarization」。條件與參數：

1. 以 `vllm serve` 啟動時必須帶 `--middleware nemo.collections.speechlm2.vllm.salm.ctc_serving.ctc_timestamp_middleware` 與 `--trust-request-mm-kwargs`，並設環境變數 `VLLM_USE_V2_MODEL_RUNNER=0`（模型卡：字級時間戳需要 V1 model runner）。
2. 請求要帶 `extra_body["mm_processor_kwargs"] = {"capture_ctc_timestamps": True}`，且 `skip_special_tokens` 保持 `False`。
3. 時間戳請求限制：**一次一段錄音**、`stream=false`、`n=1`。
4. 回應的 `ctc_timestamps` 包含：`words`（每字的 `word`／`start`／`end`／`speaker`，秒為單位，相對於輸入音訊）、`diarization`（說話人活動區段）、`speaker_tag_to_diarization_speaker`（轉寫標籤與分離結果的對應）、`error`（成功為 `null`）。
5. **使用前必須檢查 `error`**；沒有加說話人標籤的轉寫會被當成單一說話人對齊；評估說話人分離時要用 `diarization` 區段，不要用字級時間戳。

最小檢查碼（只驗回應結構，模型卡範例的精簡版）：

```python
alignment = response.model_dump()["ctc_timestamps"]
if alignment["error"] is not None:
    raise RuntimeError(alignment["error"])
words = alignment["words"]
# 基本健全性：每個字 start < end，且整體時間不倒退
assert all(w["start"] < w["end"] for w in words), "存在 start >= end 的字"
assert all(a["start"] <= b["start"] for a, b in zip(words, words[1:])), "字級時間戳倒退"
```

這兩行 `assert` 是本文補的健全性檢查（模型卡沒有這段），用意是在 `error` 為 `null` 時仍擋掉明顯壞的輸出。

模型卡的多說話人成績（全場錄音，英文為主）：AMI IHM cpWER 10.29%、AMI SDM 17.34%、NOTSOFAR-1 單通道遠場 25.91%；中文 AISHELL-4 cpCER 32.91%、AliMeeting 34.95%。遠場、多人的中文會議，錯誤率明顯高於近場英文，這是評估時要有的預期。

### 4.4 長錄音與輸出截斷

- vLLM 預設最長解碼 600 秒，要處理 1 小時要設 `VLLM_MAX_AUDIO_DECODE_DURATION_S=3600` 與 `VLLM_MAX_AUDIO_CLIP_FILESIZE_MB=180`（模型卡啟動指令）。
- 模型卡提醒：密集的一小時對話可能需要約 20,000 個輸出 token；`max_tokens` 預設 16,384 時可能被截斷，要提高或移除。
- 模型卡指出模型「在少數情況下可能無法終止生成而陷入迴圈」，建議對最終輸出套用一次其提供的 `cleanup_generation_loops` 函式（字元連續重複 ≥21 次折成 1 個；1–4096 字元區塊連續重複 ≥20 次折成 1 份）。該函式在模型卡內有完整程式碼，使用時需附 Apache-2.0 聲明。

### 4.5 音訊直接問答（Direct Audio QA）

- 條件：user 訊息放問題與音訊；`enable_thinking=true`；temperature 0.6、top_p 0.95、top_k -1、`max_tokens` 20,480，並設 `reasoning_budget=16384`、`thinking_token_budget=17408`。
- 建議的系統提示詞（模型卡原文）：`Answer the question directly using evidence from every provided audio clip in order. Answer every requested part, preserve exact names and numbers, and give a concise, specific answer first. Do not invent details.`
- **限制**：評測只做了英文。中文錄音的會議紀要問答，模型卡不保證可靠。重要結論要回頭對照逐字稿。

---

## 5. 磁碟與硬體需求

### 5.1 權重大小（Hugging Face `/tree/main` 檔案大小加總，2026-11-02 計算）

| 倉庫 | 精度 | 檔案總量 |
| :--- | :--- | ---: |
| `nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B` | BF16 | 62.9 GiB（67.5 GB） |
| `nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-FP8` | FP8 | 32.3 GiB（34.7 GB） |
| `nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-NVFP4` | NVFP4 | 20.1 GiB（21.6 GB） |
| `nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-DFlash2` | 草稿模型（推測式解碼） | 約 0.57B 參數 |

4.3B 是「激活」參數，**載入時 MoE 的全部專家權重仍要放得進記憶體**（總參數 34B），所以顯存需求看總量，不看 4.3B。模型卡沒有給「最低顯存」數字，只給了硬體清單；下表的顯存門檻是本文依權重大小做的**下限推算**（權重本身就要這麼多，尚未計入 KV／狀態快取與啟動額外開銷），不是官方規格。

| 精度 | 權重本身至少 | 備註 |
| :--- | ---: | :--- |
| BF16 | 62.9 GiB | 官方硬體表：A100 80GB、H100、H200、B200 等 |
| FP8 | 32.3 GiB | 官方硬體表：H100、H200、L40S 48GB 等 |
| NVFP4 | 20.1 GiB | 官方硬體表：RTX 5090（其顯存容量模型卡未寫，本文未查證）、Blackwell 系列 |

### 5.2 官方硬體相容表（模型卡 Software Integration，節錄）

| 硬體 | 精度 | 執行環境 | 作業系統 |
| :--- | :--- | :--- | :--- |
| A100 80GB | BF16 | vLLM 0.32.0、Transformers | Linux；Windows 經 WSL2 |
| H100 | BF16、FP8 | vLLM、Transformers、SGLang-Omni 0.2.0 | Linux；Windows 經 WSL2 |
| L40S 48GB | FP8 | vLLM、Transformers | Linux；Windows 經 WSL2 |
| **RTX 5090** | **NVFP4** | vLLM、Transformers、**GGML** | Linux；Windows 經 WSL2；**原生 Windows 僅 GGML** |
| **RTX PRO 6000 Blackwell Server Edition** | BF16、FP8、NVFP4 | vLLM、Transformers、**GGML**、SGLang-Omni | Linux；Windows 經 WSL2；**原生 Windows 僅 GGML** |
| DGX Spark (GB10)、B200、GB200、GB300、Jetson Thor、H200 | 各有列 | vLLM、Transformers | Linux；Windows 經 WSL2 |

重點：**官方列出的硬體不包含 RTX 4090／4080／3090 等一般顯卡**。沒列不等於一定跑不起來，但是「官方未背書、本文未驗證」。

快速啟動範例的目標是單張 **H100 80 GB**（`--gpu-memory-utilization 0.94`、`--max-model-len 65536`、`--max-num-seqs 192`）；模型卡明講其他硬體可能要調整這些參數。

### 5.3 效能數字的出處與限制

模型卡寫：用優化版 vLLM 實作的 Nemotron Transcribe NIM，單張 RTX PRO 6000 Blackwell 最高每秒轉寫 2,238 秒音訊（NVFP4 + DFlash2），30 秒錄音回傳逐字稿需 0.13 秒。**但這些優化「not yet part of the open-source release」**，開源版 vLLM 整合「expected to be roughly two times slower」。所以自己跑開源權重，不能拿這兩個數字當預期。

---

## 6. Windows 本機部署路徑與條件

| 路徑 | 官方支援情形 | 需要什麼 | 本文判斷 |
| :--- | :--- | :--- | :--- |
| **WSL2 + vLLM 0.32.0 + NeMo Speech** | 模型卡：「Linux runtimes can also run on Windows through WSL2」 | WSL2 內的 Linux 環境、能被 WSL2 使用的 NVIDIA GPU、Python 3.13（模型卡用 `uv venv --python 3.13`）、從 `NVIDIA-NeMo/Speech` 原始碼安裝、下載權重 | 唯一涵蓋 BF16／FP8／NVFP4 與字級時間戳的路徑。條件多、佔磁碟（Python 環境 + 20–63 GiB 權重）。 |
| **WSL2 + Transformers** | 同上 | 從原始碼安裝 transformers | 簡單轉寫可行；模型卡未說明 Transformers 路徑能不能出字級時間戳，**未驗證**。 |
| **原生 Windows + GGML** | 模型卡：僅 RTX 5090（NVFP4）與 RTX PRO 6000 Blackwell | 上述 GPU | 模型卡的硬體表有列，但**整份模型卡沒有 GGML 的下載來源、指令或功能範圍**，GGML 路徑能否出時間戳、說話人標籤：**未驗證**。 |
| **SGLang-Omni 0.2.0** | 模型卡寫於 H100 與 RTX PRO 6000 驗證；**不需要 NeMo** | `sgl-omni serve --model-path ...`，提供 `/v1/audio/transcriptions` | 模型卡明講：字級時間戳、說話人、翻譯與推測式解碼**不在此整合內**；模型卡未單獨說明 SGLang-Omni 在 Windows 的支援，視為經 WSL2。只適合整檔轉寫。 |

快速啟動（單卡 vLLM，節錄模型卡）的最關鍵設定：

```bash
export VLLM_PLUGINS=nemo_speechlm
export VLLM_MAX_AUDIO_DECODE_DURATION_S=3600
export VLLM_MAX_AUDIO_CLIP_FILESIZE_MB=180
export VLLM_USE_V2_MODEL_RUNNER=0   # 字級時間戳需要
vllm serve ./NVIDIA-Nemotron-3.5-Transcribe-30B-A4B --trust-remote-code --dtype bfloat16 \
  --max-model-len 65536 --speculative-config '{"method":"mtp","num_speculative_tokens":8}' \
  --middleware nemo.collections.speechlm2.vllm.salm.ctc_serving.ctc_timestamp_middleware ...
```

這只是示意；完整指令（約 15 個參數）以模型卡為準，不要只抄這一段。啟動後服務綁 `127.0.0.1:8000`，用 OpenAI 相容客戶端呼叫 `/v1/chat/completions`，音訊以 `audio_url` 的 base64 data URL 傳入。`--trust-remote-code` 會執行倉庫提供的程式碼，**只在自己信任該倉庫版本時使用**，並建議固定 revision。

---

## 7. 語言與品質：對台灣使用者的意義

模型卡 Language Support Matrix：

| 語言 | ASR | 多人 ASR | 語碼轉換 | 品質等級 |
| :--- | :-: | :-: | :-: | :--- |
| English（美／印／英） | ✓ | ✓ | ✓ | Leading |
| Korean | ✓ | ✓ | ✓ | Leading |
| Japanese | ✓ | ✓ | ✓ | Production-ready |
| **Chinese Mandarin** | ✓ | ✓ | ✓ | **Supported（「may need fine-tuning」）** |

模型卡對品質等級的定義：Leading＝開箱即近乎最佳；Production-ready＝達到生產品質；**Supported＝可用，可能需要微調**。

中文相關成績：FLEURS 字元錯誤率 8.62%、CoVoST2 9.74%；中英夾雜 ASCEND 混合錯誤率 18.74%。

對語音輸入工具的影響：

1. 官方只寫 Mandarin，**沒有寫台灣口音、也沒有說輸出簡體或繁體**。模型卡內部評測提示詞有「Write Mandarin in simplified Chinese characters」的字樣，顯示至少部分評測以簡體為準；要輸出繁體必須自己在提示詞要求並驗證，**未驗證**。
2. 對台灣使用者最關鍵的品質（繁體、台灣用語、國台語夾雜）沒有任何數據，上線前必須用自己的錄音做 WER／CER 測試。

---

## 8. 上線前要自己做的驗收

模型卡的數字都是 NVIDIA 在他們環境量的，**不能代替你自己的資料**。建議最小驗收（不需要本 repo 的任何工具）：

1. 準備 10–20 段你實際會說的錄音（含你常用的專有名詞、中英夾雜、背景噪音），各配一份人工校對的逐字稿。
2. 用第 4.1 節的「逐字稿」與「專有名詞偏置」兩種提示詞各跑一次，算字元錯誤率（CER），比較有無 `Context terms:` 的差異。
3. 記錄：單段 30 秒錄音從送出到收到全文的牆鐘時間，與 GPU 顯存峰值。若超過你的使用情境能接受的延遲，就不要用在即時輸入。
4. 對含時間戳的輸出跑 4.3 節的健全性檢查，統計失敗比例。
5. 檢查有沒有無限重複輸出；有就啟用 4.4 節的防護函式並記錄頻率。

「能用」的判準由你自訂（例如 CER 上限、延遲上限）；這些門檻是你專案的取捨，不是模型卡的規格。

---

## 9. 即時聽寫的替代：同一系列的串流模型

若目標是 Windows 即時聽寫，NVIDIA 另有 `nvidia/nemotron-3.5-asr-streaming-0.6b`（Hugging Face API 查證：約 0.64B 參數、授權 openmdw-1.1、語言標籤含 `zh`、最後修改 2026-09-10）。其模型卡自述為「cache-aware streaming」的 600M 參數 FastConformer-RNNT 模型，面向低延遲語音代理場景，並支援 40 個 language-locale。

本文**只確認它存在與上述標示**，沒有讀完它的模型卡：Windows 原生支援、顯存需求、繁體輸出、中文錯誤率都未驗證，如要採用請另做評估。

---

## 10. 決策建議

```text
要做「錄音檔 → 逐字稿／說話人／摘要」的後處理，而且有 WSL2 + 高階 NVIDIA GPU（或雲端 GPU）
  → 可試：先用 NVFP4 或 FP8 小範圍驗收（第 8 節），再決定

要做「按住說話、即時上字」
  → 不選本模型；改評估第 9 節的串流模型，或其他即時方案

只有一般消費級顯卡或只有 CPU
  → 官方未背書，不建議在此投入；可先用雲端 API 或較小的模型
```

本 repo 不提供推論腳本、驗證器或提示詞庫（筆記的 `T-20261031-35`、`T-20261031-36` 已標為不做：沒有可實際執行此模型的環境）。

---

## 11. 未驗證項目與限制

- 本文沒有執行過這個模型，所有效能、錯誤率、參數均為模型卡或 Hugging Face API 內容的轉述。
- GGML 路徑的取得方式、功能範圍：模型卡沒有說明，未驗證。
- Transformers 路徑的字級時間戳／說話人輸出：未驗證。
- RTX 4090 等官方未列的消費級顯卡：未驗證。
- 繁體中文輸出、台灣口音、中文專有名詞偏置效果：未驗證。
- 模型卡中的「Technical Report」連結（<https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf>）本次未開啟，未引用其內容。
- 筆記引用的 Threads 貼文（<https://www.threads.com/@it.oppa.twhk/post/DfE-QUGCNJ1>）本次未開啟，未驗證；筆記中與模型卡不符之處已於第 2 節列出。
- 筆記列的 `https://docs.nvidia.com/nemo-framework/` 與本模型的關聯，本次未查證。
- 模型卡會更新；本文以 revision `c17667641642c4265ff2b7037dd101b7d4567634` 為準。

---

## 12. 來源（皆於 2026-11-02 讀取）

- 模型卡與倉庫：<https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B>（`README.md`、`LICENSE`、`config.json` 檔案清單）
- Hugging Face API：<https://huggingface.co/api/models/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B>（參數量、授權欄位、語言標籤、revision）
- 量化版本：<https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-FP8>、<https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-NVFP4>、<https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-DFlash2>（API 參數量與檔案大小）
- 授權全文：<https://openmdw.ai/license/1-1/>（本次未開啟；以倉庫 `LICENSE` 檔內容為準）
- 串流模型：<https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b>（API 欄位與模型卡開頭）
- 基底模型：<https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16>（僅確認於模型卡中的引用，本次未開啟）
