# Claude Code 原生顧問（`/advisor`）計費與快取行為查證

> 對應任務：`T-20261108-07`。來源筆記：[`notes/2026-11-08-claude-code-builtin-advisor-command-evaluation.md`](../notes/2026-11-08-claude-code-builtin-advisor-command-evaluation.md)。
> 查證日期：2026-11-17。依據只有官方文件兩頁，都是當天直接下載 Markdown 原文後逐句核對：
>
> - Claude Code 文件：[Escalate hard decisions with the advisor tool](https://code.claude.com/docs/en/advisor)（下稱「CC 頁」）
> - Claude API 文件：[Advisor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)（下稱「API 頁」；筆記裡的 `docs.claude.com` 網址會轉址到這裡）
>
> **範圍與限制**：這是文件查證，**沒有實測**。沒有開顧問跑一輪去量 token，也沒有對照帳單。CC 頁開頭註明這個功能是實驗性的，行為、計費與可用範圍都可能變動；以下結論只代表 2026-11-17 的文件內容。

## 1. 結論

```text
主模型（便宜）──▶ 決定要問顧問
                      │
                      ▼
        顧問模型（貴）重讀「整段對話」          ← 每次呼叫都重讀，Claude Code 裡不快取
                      │                           輸入量 ≈ 當下對話長度
                      ▼
        回一段建議（通常幾百到一兩千 token）    ← 以顧問模型費率計
                      │
                      ▼
主模型繼續做（建議本身進主模型的快取）
```

- 顧問**每次**被呼叫都收到完整對話，沒有只給部分脈絡的選項。
- 在 Claude Code 裡，顧問讀對話的這段輸入**不快取**，每次都重新處理。
- 顧問的 token 以**顧問模型**的費率計；訂閱方案則算進方案用量上限，Fable 顧問在部分方案改扣用量額度（usage credits）。
- 所以單次顧問呼叫的成本大致與「當下對話長度 × 顧問模型輸入單價」成正比：**對話越長、越晚問，越貴**；Claude Code 沒有限制呼叫次數的設定。

## 2. 三個問題逐項查證

| 問題 | 結論 | 官方依據 |
| :--- | :--- | :--- |
| 顧問每次呼叫是否收到完整對話？ | **是。** 包含系統提示、工具定義、先前各輪與工具結果、主模型本輪已寫出的文字。主模型呼叫顧問時不帶參數，也無法挑選要傳什麼。 | CC 頁[開頭段落](https://code.claude.com/docs/en/advisor)與 [What you see during a session](https://code.claude.com/docs/en/advisor#what-you-see-during-a-session)（顧問一律收到完整對話）；API 頁 [How it works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#how-it-works)（列出對話包含哪些部分）與 [Successful advisor call](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#successful-advisor-call)（呼叫的 `input` 永遠是空的，由伺服器組出完整對話） |
| 顧問端輸入是否有快取？預設開或關？ | **Claude Code：不快取。** CC 頁原文："Each advisor call processes the full transcript anew, with no reuse between calls." **API：預設關，可以自己開。** 工具定義的 `caching` 參數預設是 `null`（關閉）；開了之後第二次起才讀得到快取，文件說大約三次呼叫才回本。Claude Code 有沒有提供開啟這個參數的設定：**未載明**（CC 頁沒有提到任何相關設定）。 | CC 頁 [Impact on prompt caching](https://code.claude.com/docs/en/advisor#impact-on-prompt-caching)；API 頁 [Tool parameters](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#tool-parameters) 與 [Advisor-side caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#advisor-side-caching) |
| 顧問 token 以哪個模型的費率計？ | **顧問模型的費率**，與主模型分開算。API 計費：付顧問模型的輸入與輸出費率。訂閱方案：算進方案的用量上限；Fable 當顧問時，在 Fable 用量改扣用量額度的方案上一樣改扣用量額度。顧問用量會算進 `/usage` 顯示的 session 總量。 | CC 頁 [Cost](https://code.claude.com/docs/en/advisor#cost)；API 頁 [Usage and billing](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#usage-and-billing)（顧問是獨立的一次推論，用量列在 `usage.iterations[]` 的 `advisor_message`，不併入頂層 `usage`） |

### 2.1 順帶查到、會影響成本的事項

| 事項 | 文件內容 | 出處 |
| :--- | :--- | :--- |
| 開關顧問會不會讓主模型的快取失效 | 不會。和切換主模型不同，中途開關 `/advisor` 不影響主模型已快取的前綴；顧問回傳的建議會成為對話的一部分，在之後的回合被快取 | CC 頁 Impact on prompt caching |
| 顧問輸出多長 | 一般是 400～700 個文字 token，含思考共約 1,400～1,800；困難的推理題會長很多 | API 頁 Usage and billing、Capping advisor output |
| 能不能限制呼叫次數 | Claude Code：沒有設定可以限制或強制呼叫次數，只能在指示裡要求多問或少問。API：`max_uses` 只限單一回合；整段對話沒有內建上限，要自己在用戶端計數 | CC 頁 [When Claude consults the advisor](https://code.claude.com/docs/en/advisor#when-claude-consults-the-advisor)；API 頁 Tool parameters、Cost control |
| 顧問端有沒有 context 管理 | 沒有。顧問不帶工具、不做 context 管理 | API 頁 How it works |
| 子代理 | 子代理會沿用已設定的顧問（各自依自己的模型檢查配對是否允許） | CC 頁 [Choose an advisor model](https://code.claude.com/docs/en/advisor#choose-an-advisor-model) |
| 怎麼完全關掉 | `/advisor off`；或設環境變數 `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` 整個停用 | CC 頁 [Turn the advisor off](https://code.claude.com/docs/en/advisor#turn-the-advisor-off) |
| 可用範圍 | 需走 Anthropic API、Claude Platform on AWS 或 Google Cloud 上由 Anthropic 管理的 Claude；Amazon Bedrock、Microsoft Foundry 等不支援。經 gateway 時要看 gateway 是否原樣轉送 | CC 頁 [Requirements](https://code.claude.com/docs/en/advisor#requirements) |

### 2.2 文件未載明的事項

- 訂閱方案下，顧問 token 換算成用量上限的比例（與主模型用量怎麼折算）：未載明，只說「算進方案用量上限」。
- Claude Code 呼叫顧問時是否設了輸出上限（API 的工具層 `max_tokens`）：未載明。
- Claude Code 是否有任何方式開啟顧問端快取：未載明。CC 頁只陳述「不快取」。
- 對話經過 `/compact` 之後顧問讀到的是壓縮後還是原始對話：未載明。依「顧問收到完整對話」推論應是當下 context 裡的內容，但文件沒有明講，**不當作結論**。

## 3. 對照筆記第 0 節的留言

| 留言的說法 | 官方文件 | 判定 |
| :--- | :--- | :--- |
| `江品陞`：會把當輪整個 Context 送給顧問 | CC 頁與 API 頁都寫顧問收到完整對話 | **證實** |
| `江品陞`：沒有快取 | CC 頁：顧問讀對話的部分不快取，每次重新處理。補充：這是 Claude Code 的行為；底層 API 可以開顧問端快取，只是預設關閉 | **證實**（限 Claude Code） |
| `江品陞`：顧問選 Fable 會非常貴 | 顧問 token 以顧問模型費率計，Fable 在部分方案另扣用量額度。「非常貴」是程度判斷，文件沒有給數字 | 方向與文件一致；程度**未查證** |
| `Richard Chan`：Context 整包推給顧問，對話很長時對 token 用量影響很大 | 同第一列；輸入量隨對話長度成長是「每次重讀完整對話且不快取」的直接結果 | **證實**（影響幅度文件沒有數字） |
| `Jim Ho`：好用而且很省額度 | CC 頁說顧問只在關鍵決策點被呼叫，便宜主模型配強顧問通常比全程用強模型便宜。這是和「全程用強模型」比，不是和「不開顧問」比 | 與文件**不衝突**，但比較基準不同；留言沒有說明對話長度與呼叫次數，無法判定 |
| `江品陞`、`SparklyQuince4034`：改用子代理，或先把對話整理成檔案再給顧問看 | CC 頁的比較表把子代理列為另一種做法（強模型只跑被委派的子任務）。文件沒有評論「整理成檔案」這個做法 | 子代理是文件列出的替代方案；「比較省」**文件未載明** |

## 4. 怎麼用（依查證結果）

| 情境 | 做法 | 理由 |
| :--- | :--- | :--- |
| 對話剛開始、任務會很長、想在定方向前問一次 | 可以開顧問 | 此時對話短，重讀成本低；文件也說它適合長任務的關鍵決策點 |
| 對話已經很長，中途想要第二意見 | 不開顧問。改派子代理並只給必要脈絡，或先把現況整理成一份檔案，開新對話問 | 顧問一定重讀整段對話且不快取，輸入量就是當下對話長度 |
| 短任務、例行工作 | `/advisor off` | 文件自己說短任務加值有限 |
| 已經開了顧問 | 定期看 `/usage`；發現顧問被呼叫很多次就關掉或在指示裡要求少問 | Claude Code 沒有次數上限設定 |
| 顧問想用 Fable | 先確認所在方案的 Fable 用量是不是扣用量額度 | Fable 顧問的計費跟著 Fable 的計費方式走 |

這份結論已寫進 [`SanHsien/agent-advisor`](https://github.com/SanHsien/agent-advisor) 的 `claude/plugins/agent-advisor-claude/skills/orchestration/references/cost-policy.md`（「選擇合作方式」段新增一條「顧問呼叫成本隨對話長度成長」）。

## 5. 未驗證與限制

- 全部是文件查證，沒有實際開顧問量測 token、也沒有核對帳單或 `/usage` 的數字。
- 功能是實驗性的；官方文件之後改了，這份就過期。重查時以兩頁的 Cost、Impact on prompt caching、Usage and billing 三段為準。
- 「成本與對話長度成正比」是由「每次重讀完整對話、不快取、以顧問模型輸入費率計」三點推出來的，官方文件沒有直接寫這句話，也沒有給成本數字。
- 留言數字（例如一週額度用掉三分之一）沒有查證，也不在這份文件的範圍。
