# Cloudflare security-audit-skill 唯讀審查

日期：2026-11-15。任務：T-20261115-04。作者：Codex。

**結論：可借用來源優先、證偽、證據缺口與防禦縱深的判斷方法；暫不安裝或執行完整 Skill。** Windows 原生的必要隔離與安全檔案操作尚未建立證據；quick 仍有多代理成本。這是對 Skill 的靜態評估，沒有套用其 full audit、啟動子代理、執行下載的 validator／測試或修改全域設定。

## 固定來源及檔案清冊

作者：Cloudflare。固定 commit：`c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`。以下來源全在同一版本的 [skills/security-audit 目錄](https://github.com/cloudflare/security-audit-skill/tree/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit)。以 Git 淺層複製後只讀文字／JSON，未安裝依賴。

| 代號 | 一手來源 | 本輪閱讀範圍 |
|---|---|---|
| C1 | [SKILL.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/SKILL.md) | 模式、安全、寫入隔離、預算與六階段契約 |
| C2 | [RECONNAISSANCE.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/RECONNAISSANCE.md) | 四個基線角色、既有帳本、coverage ID／狀態表 |
| C3 | [HUNTING.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/HUNTING.md) | hunter 輸入輸出、artifact 晉升、critic 與停止條件 |
| C4 | [VALIDATION-AND-REPORTING.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/VALIDATION-AND-REPORTING.md) | 三 finding 分支、獨立驗證、報告與 incomplete 規則 |
| C5 | [report-schema.json](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/report-schema.json) | 頂層 array／oneOf、required、禁止額外欄位 |
| C6 | [validate-findings.cjs](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/validate-findings.cjs)、[對應測試](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/validate-findings.test.cjs) | imports／CLI、schema 與語意限制、安全讀檔；測試 fixture、反例與程序／檔案操作 |
| C7 | [validate-coverage-ledger.cjs](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/validate-coverage-ledger.cjs)、[對應測試](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/validate-coverage-ledger.test.cjs) | imports／CLI、canonical ID、owner／狀態／attempts、安全讀檔；測試案例與副作用 |
| C8 | [AI-AND-LLM.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/AI-AND-LLM.md)、[SUPPLY-CHAIN-AND-RELEASE.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/SUPPLY-CHAIN-AND-RELEASE.md)、[DESKTOP-MOBILE-AND-LOCAL-IPC.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/DESKTOP-MOBILE-AND-LOCAL-IPC.md) | 與 agent／本機採用直接相關的適用條件、核心紀律、攻擊類別與驗證規則 |
| C9 | 同版本的 ATTACK-CLASSES.md、CLIENT-SIDE.md、CLOUD-AND-DEPLOYMENT.md、DATA-ISOLATION-AND-LIFECYCLE.md、MEMORY-SAFETY-AND-BINARY.md、PROTOCOLS-RPC-AND-MESSAGING.md、RESOURCE-EXHAUSTION-AND-AVAILABILITY.md、WEB-PROTOCOL-AND-AUTH.md | 清冊及適用條件／章節／驗證規則檢閱；非每個領域的完整安全稽核，連結由上方固定目錄取得 |

C8、C9 都是提示詞素材，不是本輪啟用的技能或代理指令。未逐行證明所有 schema interpreter 分支與反例的正確性，亦未把測試檔存在視為測試已通過。

## 模式、輸入與輸出

```text
focused 問題 --> guidance --> 讀相關指南，原回合回覆
                              不自動建完整輸出目錄

明確 full audit --> 設定 target / source_ref / profile / budget
                         |
                         v
  4 x recon --> ledger --> hunter wave --> coverage critic
                         |                        |
                         | standard 可再分波      | quick 到此停獵殺
                         v                        v
                 fresh candidate verifier --> findings.json
                         |
                final record verification
                (quick 與前次 verifier 合併)
                         |
                         v
                  兩個 validator --> 三份報告
                         |
                缺控制 / 缺預算 --> incomplete + 缺口
```

依 C1～C4，full audit 的輸入包括 target 絕對路徑、來源 commit／dirty 狀態、scope、profile、budget、所選 companion 及相容舊帳本。Parent 管理 `run-metadata.json`、`architecture.md`、`coverage-ledger.json`、`findings.json`、`REPORT.md`、`FINDINGS-DETAIL.md`、`NEEDS-VALIDATION.md`；子代理只能寫自己的 scratch，不能寫共用檔或 retained artifacts。輸出目錄預設在目標外；放目標內需使用者明確指定且確認整目錄被版本控制忽略（C1）。

Hunter 回傳一個 JSON 物件，包含 units、candidates、hardening、uncovered；每個已分派 coverage ID 恰出現一次。Parent 合併、去重及更新帳本，verifier 回傳獨立判斷；不是讓不同代理競寫 findings（C3、C4）。

## 程式副作用、依賴與控制界線

| 元件 | 已查輸入輸出／副作用 | 能證明與不能證明 |
|---|---|---|
| Skill／companion Markdown | 要求執行者讀目標、派代理、管理 scratch／artifacts、呼叫 Node validator（C1～C4、C8） | 指示是工作契約；沒有自行建立容器、網路防火牆、ACL 或資源配額 |
| findings validator | CLI 讀指定 JSON，加讀同目錄 schema；fs／path／util，stdout PASS、stderr 診斷，成功回 0，錯誤回 1（C6） | 所查主程式無第三方 npm import、網路呼叫、子程序或寫檔；只判格式／部分語意，不能證明引用原始碼真實或漏洞已重現 |
| ledger validator | CLI 讀指定 JSON；node:fs／path／util，stdout／stderr 與結束碼同上（C7） | 檢查 canonical ID、狀態與 ownership 字串規則；不等於實際 artifacts 的檔案類型、晉升流程、來源證據或整個審查覆蓋率已成立 |
| 兩份測試 | 使用 node:test／assert、fs／os／path、child_process；建立 OS 暫存目錄、寫 JSON、spawnSync Node，部分測試 spawn mkfifo、建立 symlink，finally rmSync 清除（C6、C7） | 測試會執行程式、建立／刪除檔案及啟動子程序，不是無副作用資料。未執行，不能報通過數；也沒有因「零依賴」豁免安全審批 |

C6 限制輸入 5 MiB、64 層巢狀、陣列 1,000 筆、錯誤最多 100；C7 限制 5 MiB、10,000 units、巢狀集合 1,000 筆、64 層、遍歷 500,000 values、錯誤最多 100。這些是解析器上限，不是目標程序的 CPU／記憶體／磁碟限額。finding schema 的 additionalProperties=false 與語意檢查可以阻止狀態欄位混用，但不能對抗內容本身造假（C5～C7）。

**Windows 的實際程式門檻**：C6 的 readFileWithinLimit（604～648 行）與 C7 同名函式（721～759 行）要求 O_NOFOLLOW、O_NONBLOCK 是非零整數；不足就丟出安全讀取錯誤，不退回普通 readFile。測試亦用 HAS_SAFE_INPUT_OPEN，部分 symlink／FIFO 案例在 win32 跳過。故不能宣稱「只要裝 Node 就可在所有 Windows 上完整使用 CLI」。本輪未執行 Node 能力探測，當前主機可否通過是未查證；不要繞過這個檢查（C6、C7）。

## 最低代理呼叫預算

以下是 C1 Cost budget、C2 基線角色、C3 critic 波次與 C4 驗證規則的算術估計，不是實測 token／費用。單位為一次 delegated agent invocation；parent 自身模型回合與工具費未計入，美元與訂閱耗額未知。

定義 H 為 hunter 呼叫數，C 為需要 Phase 3 驗證的去重候選數，R 為 Phase 3 後保留的 confirmed／needs_validation 數；額外 recon、補獵殺波與重大替換的獨立 verifier 另加。

| 模式 | 啟動前最低保留 | 一波估計／例子 |
|---|---|---|
| guidance | 必要子代理 0；可由 parent 聚焦閱讀 | 不強制四次 recon 或完整六階段；parent 仍消耗本次模型用量 |
| quick | 4 recon + 1 final post-wave critic + 至少 1 verifier = 6，獵殺另計 | 實際基本式 `5 + H + C`；H=1、C=1 時 7。C=0 時不必花掉 verifier 保留額，但啟動 gate 仍要預留 |
| standard | 4 recon + 1 post-wave critic + 1 distinct final-clean critic + 至少 1 verifier = 7，獵殺另計 | 實際基本式 `6 + H + C + R`；H=1、C=1、R=1 時 9。若候選 Phase 3 全被 rejected，R=0；再波或替換會增加 |

6／7 是 pre-recon gate 的最低保留，不是能完成有效獵殺的全包預算；即使通過該門檻，也要確認剩餘額度足夠 H 與預期驗證。standard／deep 每波都需 post-wave critic，另保留最終 clean critic；不能只付一次 critic 後假稱完整覆蓋。quick 恰好一波與一次 final critic，新增缺口列 deferred，不追加第二波；屬部分覆蓋（C1、C3）。

預算不足時，在任何 recon 前就停止；若驗證中耗盡，未驗候選留 ledger candidate，run_status=incomplete，不可為了結案把它塞進 needs_validation 或超過使用者的硬預算。重大替換可能需要再一名全新 verifier，沒有固定總呼叫上限保證（C1、C4）。

## 提示詞規範與 Windows 隔離缺口

| 必要條件 | 來源契約 | 本輪狀態 |
|---|---|---|
| 無外網／必要時獨立 loopback | C1 universal safety | 未配置也未實測；本 session 可上網取來源不等於目標執行具備禁網 |
| 空環境＋安全允許清單、專屬 home／temp／cache | C1、C3、C4 | 未建立；不得讀取／搬運真憑證來補測 |
| 目標與工具鏈唯讀、只允許 scratch 寫入 | C1 write isolation | clone／worktree 本身不實施此限制；未建立 OS ACL／掛載隔離證據 |
| CPU、記憶體、程序數、檔案大小、磁碟、時限 | C1 universal safety | 未建立完整限額；spawn timeout 單項不足 |
| parent 安全晉升 | C1 的 descriptor traversal、no-follow、regular file、link count=1、排他建立與累計大小檢查 | Markdown 給程序，未附已驗證的 Windows 等價實作；reparse point／hardlink／競態行為未測 |

任何一項不足就不執行目標建置、測試、瀏覽器或 fixture；不要以 project trust、JSON validator 通過或「沒有修改原始碼」代替上述控制。Windows 並非永遠不能提供等價隔離，這裡的結論是本輪沒有可核對的控制證據，也沒有偷偷啟動 WSL／VM／容器（C1）。

## needs_validation 的正確用法

依 C4～C6，三個狀態分別是 finding 的證據狀態：

| 狀態 | 必要條件 | 不可混用 |
|---|---|---|
| confirmed | 完整來源鏈、條件、獨立驗證、實際 observed_result、修正策略、severity／confidence | 不能把推論當執行輸出；severity 不高於證明的 impact |
| needs_validation | 有來源支持的邊界假說、精確 blocker、至少一項適用 local 或 owner-observed deployment 計畫 | 不給 severity／execution／remediation／confirmed root_cause；不是所有猜測或沒預算驗的候選收容所 |
| rejected | 來源或局部證據已反駁候選，有 reason | 不當成漏洞，也不保留 severity |

例如來源可追到某身份檢查，但部署端是否套用決定性代理規則未知，才可寫 needs_validation 並請擁有者觀察該設定；不能要求對正式端點發測試流量。若 A 層已阻擋路徑，僅缺 B 層而無具體邊界結果，列 hardening。這些 finding 狀態不得取代 advisor 的 ship／fix-first／rethink 最終裁決；本輪沒有修改 advisor 契約（C1、C4；本 clone 對應筆記及既有路由規範）。

## 可採納範圍、未查項目與未來動態驗證前提

目前可在 Windows 既有人工／agent 唯讀流程參考 C8 的權限追蹤、同權限與跨邊界區分、C4 的證據缺口寫法；不啟動此 Skill、不消耗多模型稽核配額。完整 audit 與兩支 CLI 暫不採納，沒有通過動態測試的結論。

未查項目：實際 Node 平台常數與 CLI 行為、Windows 競態安全 API、沙盒禁網／資源控制、所有 schema interpreter 分支的正確性、完整跨檔／跨帳本一致性與實際來源事實、模型總用量。C9 非逐領域完整稽核；也未執行外部 SkillSpector 或既有安全檢查程式，本報告不能代替採納前的安全審批。

若未來另獲動態執行授權，先完成既定第三方 Skill 安全審批，再選能實施上表全部控制的隔離環境。使用單一假資料 fixture、固定來源／工具鏈、禁網與允許清單環境；先驗證越界寫入、外連及超額資源均被 OS 阻止，再在隔離內驗正例／壞 JSON、超限、symlink／特殊檔案的拒絕。Parent 只晉升預先列出的非機密最小證據；任一控制不足就停止，保持未驗證。這是後續驗證條件，不是本輪執行紀錄，也不新增 ROADMAP 工作。

## DoD 與文件檢查

固定來源、檔案清冊、已查／未查、代理預算、沙盒限制、needs_validation 用法、採納裁決及未來測試前提均見上文。文件檢查結果如下；不宣稱已跑第三方測試或完成六階段稽核。

2026-11-15 執行 `python tools/verify_zhtw_vocab.py --check docs && python tools/verify_inbox.py`：繁中檢查結束碼 0；inbox 檢查結束碼 1，117 篇筆記、229 項任務。錯誤限於 README 自動區塊過期、產出物導覽漏列本輪三份新報告。遵守本次只新增三份 docs／不改 README 的範圍，未重產索引、未放寬驗證；因此本任務的「通過 repo 文件檢查」尚未達成，狀態為 PARTIAL。依共同守則未提交；由整合者補索引、驗證後逐份提交，非沙盒已拒絕 commit。notes／README／ROADMAP 未改，未 push。

整輪清理限制：已嘗試以 PowerShell 確認暫存絕對路徑及非 reparse point 後遞迴清除 `.work-tmp/`，整個命令被自動核准審查以 `blocked by policy` 拒絕，沒有執行成功或提供更細原因。後續唯讀確認該目錄仍存在，內含本輪三份第三方淺層來源副本；未執行其中程式。暫存清理尚未完成，整合者須另行清除，不得將它們加入提交。
