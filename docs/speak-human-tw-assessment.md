# speak-human-tw 唯讀評估

查證日期：2026-11-15。作者：Codex。對應任務：T-20261115-16。

裁決：借鏡保護清單與少量技術複合詞，不整包併入詞彙替換器，也不在本輪安裝 Skill。MIT 允許在公開 repo 或 `SanHsien/agent-assets`（私有）使用、修改與散布其授權涵蓋的內容，但複製完整檔案或實質部分時必須保留著作權與完整授權聲明。本報告是靜態評估，不代表改寫品質、安全隔離或第三方來源權利已全面驗證。[授權原檔][license]

## 1. 固定來源與查核邊界

| 對象 | 固定版本／檔案 | 已查內容 |
| --- | --- | --- |
| Raymondhou0917/speak-human-tw | commit `14885da5c91ed7ca2972f084599edcdd2a32ad04`；SKILL frontmatter 為 v1.4.0 | LICENSE、SKILL.md、在地化詞表、patterns、protected-list、scenes、Codex 安裝說明、benchmark 與 v1.4.0 結果；另靜態抽查星數腳本與 workflow |
| 本 repo | 基準 HEAD `f1dcebb`（`tools/`、`tests/` 與 `92a90ca` 相同） | [詞彙檢查器](https://github.com/SanHsien/zhtw-vocab-guard/blob/main/tools/verify_zhtw_vocab.py)、[現有測試](https://github.com/SanHsien/zhtw-vocab-guard/blob/main/tests/test_verify_zhtw_vocab.py)（兩者 2026-11-19 已移至 [`SanHsien/zhtw-vocab-guard`](https://github.com/SanHsien/zhtw-vocab-guard)，連結指向新位置的最新版，不是基準 HEAD 當時的內容）、[前端 slop 檢查器](../tools/verify_no_slop.py) |
| Raymondhou0917/claude-code-resources | commit `1320df1e396e7630b09d2dc80fae4b2c96861d54` | 僅 [README][cc-readme] 與 [LICENSE][cc-license]，用於修正原筆記，不是安裝包安全審計 |

取得方式為淺層 clone 與固定 SHA 的 raw 檔案；只把外部內容當資料閱讀，沒有載入為執行指引、執行外部腳本、測試、安裝器或 workflow。Stars、Forks 和「最後更新」的即時數字不列為穩定證據。

實際盤點：[在地化表][localization] 有 47 組資料列；[patterns][patterns] 有連續編號的 38 類；[benchmark][benchmark] 現有 27 條 SF（應修改）與 15 條 SNF（應保留），合計 42 條。[v1.4.0 結果檔][results] 記載的是較早的 40 條（26＋14），不是本次重跑結果；不能把它的通過率套用到現行全部案例。五種情境與保真回讀是[提示規範][skill]，並非程式強制保證。

## 2. 授權與收錄邊界

- **公開 ai-inbox：可有條件收錄。** 上游 LICENSE 明載 MIT，允許複製、修改與散布；實際納入詞表、Skill 或實質衍生內容時，要隨內容保留 Raymond Hou 的著作權與完整 MIT notice，註明來源 SHA 和修改情形。只有「MIT」二字或一個來源連結不足以取代 notice。[原檔][license]
- **`SanHsien/agent-assets`（私有）：同樣可有條件收錄。** MIT 不要求公開修改，也沒有非商用限制；私有並不免除隨副本保留 notice 的條件。此處只判斷上游明示授權，未讀取或修改該私有 repo。[原檔][license]
- **第三方來源仍有界線。** patterns 開頭表示整理自維基百科與朱宥勳觀察，並稱範例已重寫；SKILL changelog 也提到比對 blader/humanizer。上游 MIT 宣告可確認，這些素材逐段的權利鏈則未查證，不推定 MIT 能替其他權利人授權。此報告用自寫評語與必要短詞對照，不搬運其完整範例；若日後整份移植，仍須核對擬複製部分的來源。[patterns][patterns]、[SKILL][skill]
- **另一倉庫不是「無授權」。** claude-code-resources 的 LICENSE／README 明示 Starter Kit 為 CC BY-NC-SA 4.0，網站文章與課程另列著作權限制；安裝包雖標「開源」，這兩檔未給出其獨立、完整的授權範圍，不能據此當 MIT 使用。此任務不收錄該倉庫內容。[LICENSE][cc-license]、[README][cc-readme]

本報告保留 MIT notice 於附錄。未把第三方 Skill 實際收錄到任何執行環境；靜態分析不替代採納前的 SkillSpector 與既有安全關卡。

## 3. 本 repo 現況與能力差距

檢查器共有 25 組規則（14 組 GLOBAL、11 組 DEGRADED_AND_CONTEXT），其中 `佔位符 → 佔位符` 不產生變更，實際有 24 組轉換。它以字串子串比對／替換為主，反覆轉換直到固定點；沒有詞性、實體、引文或作者語氣判斷。CLI 的 check／fix 會略過成對反引號與 Markdown 圍欄；API 的 `apply_zhtw_vocab` 預設 `skip_code=False`，呼叫端須明確選擇保護。[原始碼](https://github.com/SanHsien/zhtw-vocab-guard/blob/main/tools/verify_zhtw_vocab.py)

```text
既有流程：Markdown -> 略過程式碼 -> 固定詞組比對 -> 告警／固定點修補
上游規範：判情境 -> 鎖定事實與原話 -> 語義校對 -> 作者授權 -> 保真回讀
                           |
                           +-> 不能只換成一張全域替換表
```

現有測試涵蓋二次退化、語境詞組、反引號／圍欄保護、固定點與冪等性、CLI 檢查／修補及錯誤輸入；沒有引號原話、專名、URL 或承諾條款的通用保護。聚焦測試實跑 9 項通過（第 7 節）；這不等於 38 類風格規則已受測。[測試](https://github.com/SanHsien/zhtw-vocab-guard/blob/main/tests/test_verify_zhtw_vocab.py)

## 4. 在地化詞表逐列對照（47 組）

下表左欄對應上游原表順序；所有裁決是本次評估。**已有**指現有確切映射，**部分**指只有較窄詞組，**候選**指值得另案驗證，**人工**指不加入無語境的全域替換。候選也必須先保護引用、專名、URL 與程式碼，才考慮自動修補。[來源詞表][localization]

| # | 上游詞條／方向 | 本 repo 覆蓋與裁決；必要邊界 |
| --- | --- | --- |
| 1 | `視頻 → 影片` | 未有；候選，但 `短視頻` 須先採長詞規則，避免變成短影片而錯失短影音語義 |
| 2 | `質量 → 品質` | 未有；人工。物理質量不能改為品質 |
| 3 | `信息 → 資訊` | 未有；人工。術語「信息論」及來源原話不能直接改 |
| 4 | `網絡 → 網路` | 未有；候選，技術說明可試，書名／產品名保留 |
| 5 | `軟件／硬件 → 軟體／硬體` | 未有；兩個候選詞，先排除專名與引文 |
| 6 | `數據庫 → 資料庫` | 已有 GLOBAL；不重複增加 |
| 7 | `服務器 → 伺服器` | 未有；技術候選，原話與產品名稱保留 |
| 8 | `屏幕 → 螢幕` | 未有；介面說明候選，作品名稱保留 |
| 9 | `鼠標 → 滑鼠` | 未有；操作說明候選，引用名稱保留 |
| 10 | `打印 → 列印` | 部分：已有 `渲染時會打印`／`並打印路徑` 轉為輸出；直接加通用規則會與 stdout 語義衝突，人工 |
| 11 | `用戶端 → 使用者端` | 未有；人工。上游同列允許軟體語境保留用戶端／客戶端，不能當硬性禁詞 |
| 12 | `智能 → 智慧` | 未有；僅人工。可提議完整詞「人工智能」，不可改心理學、專名或原話 |
| 13 | `移動端 → 行動裝置／手機版` | 未有；人工，裝置與網站版本不是同一事物 |
| 14 | `博主／UP主 → 創作者等` | 未有；人工，職稱與平台身分需要上下文 |
| 15 | `粉絲量／漲粉 → 粉絲數／粉絲成長` | 未有；人工，描述數值或動作須分別處理 |
| 16 | `直播帶貨 → 直播銷售` | 未有；人工，引述市場類別或原文標籤須保留 |
| 17 | `短視頻 → 短影音` | 未有；長詞候選，須在第 1 列之前，並測固定點 |
| 18 | `公眾號 → 粉專／電子報或保留` | 未有；不自動改，不同平台產品不能視為等價 |
| 19 | `水平 → 水準` | 未有；人工，水平座標／水平擴充不能改 |
| 20 | `立馬 → 馬上／立刻` | 未有；人工，敘事口吻與原話須保留 |
| 21 | `挺（好的） → 蠻／滿（好的）` | 未有；人工，不替作者改口頭禪，挺身而出不適用 |
| 22 | `給力 → 有力等` | 未有；人工，保留引述與刻意用語 |
| 23 | `靠譜 → 可靠等` | 未有；人工，正式文體可建議，引用不改 |
| 24 | `貓膩 → 內情／蹊蹺` | 未有；人工，上游右欄混入簡體字，不照抄；內情與可疑行為亦非同義 |
| 25 | `接地氣 → 生活化等` | 未有；人工，可能是技術接地的比喻或作者語氣 |
| 26 | `性價比 → CP 值` | 未有；人工，正式報告可能更適合成本效益，不固定換外語縮寫 |
| 27 | `顏值 → 外型／長相` | 未有；人工，對象為人或產品會影響改法 |
| 28 | `默認 → 預設` | 部分：已有 `默認值 → 預設值`；只保留複合詞策略，法律上的默認不可改 |
| 29 | `運營 → 營運` | 未有；人工，專名與行業原文需保留 |
| 30 | `支持（某功能） → 支援` | 未有；人工或限完整技術詞組；支持某人不能改 |
| 31 | `兼容 → 相容` | 未有；軟體語境候選，人物評語與引述保留 |
| 32 | `卸載 → 移除／解除安裝` | 未有；人工，卸載貨物不等於解除安裝 |
| 33 | `註銷 → 刪除帳號` | 未有；不全域替換，註銷公司／證照不等於刪除帳號，更不能混為登出 |
| 34 | `反饋 → 回饋／意見` | 未有；人工，控制理論及引述有術語脈絡 |
| 35 | `溝通下／同步下 → 確認／更新` | 未有；人工，「同步下載」包含子串，不可替換破壞原意 |
| 36 | `落地 → 執行／實作` | 未有；人工，飛機落地及本 repo 的既有工作用語不列禁詞 |
| 37 | `打法 → 做法／策略` | 未有；人工，運動技術中的打法可正常使用 |
| 38 | `抓手 → 施力點等` | 未有；人工，機械抓手是實體構件 |
| 39 | `賦能 → 具體重寫` | 未有；人工，無單一字串目的詞，討論該詞時保留 |
| 40 | `閉環 → 具體重寫` | 未有；人工，控制系統閉環不是套話 |
| 41 | `顆粒度 → 細緻度等` | 未有；人工，材料顆粒度是物理性質 |
| 42 | `復盤 → 檢討／回顧` | 未有；人工，上游也允許口語保留，棋局復盤不改 |
| 43 | `代碼／底層代碼 → 程式碼／具體實作` | 部分：已有更完整的 `源代碼 → 原始碼`；通用規則可能破壞該映射，錯誤代碼不改 |
| 44 | `對標 → 以某物為基準等` | 未有；人工，必須保留具體比較對象 |
| 45 | `爆款 → 熱銷／熱門等` | 未有；人工，商品與文章不能固定用同一替換詞 |
| 46 | `軟著陸 → 平穩過渡等` | 未有；人工，上游明列經濟與航空例外 |
| 47 | `降維打擊 → 優勢等` | 未有；人工，先核對有無誇大證據，不換成另一句誇大話 |

原表之外的其餘區塊亦需保留界線：[在地化層][localization] 的語境詞（優化、平台／內容／流量、小夥伴、寶藏、文檔、提及詞）、全形標點、引號、語氣詞／量詞／敬語／翻譯腔，以及專名／引文／術語／玩梗豁免，本 repo 均無對應語義引擎。尤其 `文檔` 並非上游全面禁詞；不能把上游的風格偏好升格為台灣用語的唯一正解。全形標點也要豁免英文、數值格式、URL 與程式碼；現有解析器只處理程式碼，不足以保證其他豁免。

## 5. 38 類痕跡逐類對照

下表各類均對應上游同編號章節。[完整來源][patterns]。**本 repo 的詞彙檢查器對以下 38 類皆無完整規則或相應語義測試**；表中只另外指出局部功能交集。不能把候選提示當成已實作的檢查能力。

| # | 類別摘要 | 裁決與反例／衝突 |
| --- | --- | --- |
| 1 | 意義與趨勢誇大 | 人工看證據；有明確版本與日期的里程碑可保留 |
| 2 | 關注度與報導誇大 | 人工核對實際報導；有來源的媒體清單不是套話 |
| 3 | 抽象分析尾句 | 人工；研究結論的分析句可能承載論點 |
| 4 | 廣告腔 | 人工；不得刪除必要 CTA 或捏造量化賣點 |
| 5 | 不明歸屬 | 人工補來源；字串比對不能判定文末已有引用與否 |
| 6 | 公式化前景段 | 人工；具日期的下一步可保留 |
| 7 | 過度正向與籠統 | 人工；不能為具體化編造細節或數字 |
| 8 | 可疑引用 | 交還查證；保留並標疑點，不憑格式判定真假 |
| 9 | 缺乏立場 | 人工；條件式風險評估不應被迫變成確定結論 |
| 10 | 迴避直接定義 | 人工；「作為函式參數」是技術關係，不應改成「是」 |
| 11 | 三項排比 | 人工；確有三個參數或三個方案就保留 |
| 12 | 否定對比句 | 人工；技術文件可多次需要澄清區別，不設全 repo 次數上限 |
| 13 | 人物代稱輪替 | 人工；識別人物與姓名需要上下文，不能全域同義替換 |
| 14 | 虛假涵蓋範圍 | 人工；從某版本到某版本的相容性範圍可驗收且須保留 |
| 15 | 導引句與假推論 | 人工；證據充足的因果銜接不因「這意味著」遭刪 |
| 16 | 勸誡反問 | 人工；教學中的真實提問與行動指示可保留 |
| 17 | 表演深度 | 人工；有算式的成本盤點不能因「算帳」遭刪 |
| 18 | 格言公式 | 人工；「位元組是八個位元」屬定義，不是金句 |
| 19 | 假坦白開場 | 人工；訪談原話與作者口吻不可直接刪 |
| 20 | 人工反應與短句轟炸 | 人工；可交代事件推進的真實停頓須保留 |
| 21 | 空泛時代開場 | 人工；有數據的研究背景或論文結構不套行銷標準 |
| 22 | 半形標點 | 暫不硬攔；英文、JSON、URL、數字與單位都可能合法，現有程式碼保護只涵蓋一部分 |
| 23 | 破折號密度 | 暫不設門檻；來源摘錄、定義及字數算法影響密度 |
| 24 | 粗體密度 | 暫不設門檻；任務格式與重要欄位要求粗體 |
| 25 | 粗體列表標籤 | 不搬；本 repo 的任務欄位本來就依此格式供工具讀取 |
| 26 | 過度編號 | 不全域攔；SOP、DoD 與逐步操作需要順序 |
| 27 | emoji 密度 | 不搬到詞彙器；任務狀態圖示有語義。前端 slop 工具只對特定裝飾 emoji 有局部交集 |
| 28 | 不必要表格 | 人工；本報告的規則逐列對照與 README 任務表適合表格 |
| 29 | 句長過於整齊 | 不硬攔；清單、警示訊息和短定義可能刻意一致 |
| 30 | 對話殘留 | 可選人工校稿提醒；範例對話中的相同文字必須保留 |
| 31 | 諂媚與罐頭同理 | 人工；真正客服回覆要保留有根據的同理，不列禁詞 |
| 32 | 通用樂觀結尾 | 人工；引用或說明問題模式的反例不刪 |
| 33 | 過多不確定語 | 人工；證據不足的「未查證／可能」不可為流暢而刪 |
| 34 | 知識限制聲明 | 人工；本 repo 要求明示查不到與未實測，不能消除證據限制 |
| 35 | 未填佔位 | 僅對最終發布內容可做候選提醒；templates 中的佔位是合法功能，現有 `佔位符` no-op 不提供檢查 |
| 36 | 預告式導言 | 人工；agent 的必要進度更新與操作說明應保留 |
| 37 | 工具參數／引用殘碼 | 可選發布提醒；URL 解析及原樣引用須先處理，不能把 `turn0` 一概刪除或據此斷言作者使用 AI |
| 38 | 不支援平台上的 Markdown | 不搬；此 repo 正是 Markdown，刪除標記會破壞任務與索引契約 |

前端 `verify_no_slop.py` 檢查的是 HTML／CSS 設計與少量英文黑話正規表示式，不是繁中 38 類校對引擎；不能以其存在宣稱已等價覆蓋，也不能把上游編輯 Skill 的保真與確認流程省略。[原始碼](../tools/verify_no_slop.py)

## 6. 候選規則、反例與整合裁決

以下是交給整合者判斷的規格候選，不是新增任務或已套用的規則。後續排程只記在 ROADMAP。

| 候選 | 正例（應建議） | 反例（必須保留） | 必要條件 |
| --- | --- | --- | --- |
| 技術詞組 | `啟動服務器` 建議「啟動伺服器」；`安裝軟件` 建議「安裝軟體」 | `產品名「服務器助手」`、引用原句、路徑與 URL | 限技術散文；尚未有實體／引用保護前只提醒 |
| 長詞先於短詞 | `短視頻教學` 建議「短影音教學」；`視頻教學` 建議「影片教學」 | 文章標題、引文與程式碼中的原詞 | 測兩條同時加入後的優先序與冪等性，不產生「短影片」中間結果 |
| 功能支援複合詞 | `支持 UTF-8 編碼` 建議「支援 UTF-8 編碼」 | `支持開源社群`、`支持候選人` | 明確技術受詞白名單，不能只匹配 `支持` |
| 標點提示 | 中文散文中的 `完成,請重試` 建議全形逗號 | `4,800 元`、`a,b`、英文句、URL、程式碼 | 語言／數值與 Markdown 範圍辨識；無此能力不設 fail gate |
| 最終成品佔位提示 | 明確標為發布成品卻殘留 `[產品名稱]` | `templates/`、教學範例、待填表單 | 呼叫者指定 final 模式；不在整個 repo 掃到就失敗 |
| 工具殘碼提示 | 成品出現孤立引用碼且沒有有效來源連結 | 解說 `turn0search0` 的教學、合法 URL 的原始參數 | 只提醒人工確認；不得重寫 URL 或宣稱 AI 作者鑑定 |

必須保留的既有映射：`源代碼 → 原始碼`、`默認值 → 預設值`、stdout 的 `渲染時會打印 → 渲染時會輸出`。若未來加 `代碼`、`默認`、`打印` 等短詞，必須先測長詞優先與各自語義；固定點只能保證收斂，不能保證用詞正確。

本輪用現有函式做了最小反例探測（`skip_code=True`）：

| 輸入摘要 | 實際結果 | 意義 |
| --- | --- | --- |
| `「數據庫」是引用原話。` | 引號內仍變成資料庫；1 個告警 | 一般中文引號沒有保護 |
| `[來源](https://example.org/數據庫)` | 連結目的地被改為資料庫；1 個告警 | URL 不是保護範圍 |
| `產品名：數據庫工具。` | 名稱被改；1 個告警 | 無專名辨識 |
| `這個服務器支持中文。` | 原樣；0 告警 | 這兩個詞沒有規則，不能宣稱已有覆蓋 |
| `渲染時會打印日誌。` | 轉為輸出日誌；1 個告警 | stdout 例外已存在，不能覆寫為列印 |
| 成對行內反引號／text 圍欄中的 `數據庫` | 原樣；0 告警 | 已有程式碼保護確實作用 |

因此優先裁決是借鏡「先保護再改寫」；不建議立即擴充全域短詞替換。38 類以人工編輯準則為主，本 repo 的結構化筆記與技術文件不宜硬套行銷文案標準。若之後收錄 Skill，限定使用者要求的對外文稿校對，保留一次授權可直接修改的例外；不自動觸發於程式碼、設定、任務格式、事實查核或全域指引。現有 `human-writing` 的實際安裝、觸發邊界與重疊未查證，不據此宣稱已完成互補整合。

## 7. 驗證與限制

- 已執行 `python -m unittest discover -s tests -p test_verify_zhtw_vocab.py`：9 項通過，exit 0。只驗既有檢查器，不是執行上游 benchmark。
- 已以本 repo 的 `apply_zhtw_vocab`／`scan_degraded_vocab` 執行第 6 節反例探測，exit 0；輸入是本次自寫案例，沒有執行第三方程式。
- 交付文件須依序執行 `python tools/build_index.py && python tools/verify_zhtw_vocab.py --check notes docs && python tools/verify_inbox.py`；最後狀態與結束碼由交付回報記錄，不預填通過。
- 2026-11-19 註：詞彙檢查器與測試已移至 [`SanHsien/zhtw-vocab-guard`](https://github.com/SanHsien/zhtw-vocab-guard)（保留 git 歷史）。本節兩條指令是當時在本 repo 內執行的紀錄，照舊保留；現在要重跑，測試改在該 repo 執行，文件檢查改用 `python C:\GitHub\zhtw-vocab-guard\tools\verify_zhtw_vocab.py --check notes docs`。本文「本 repo 的檢查器」均指搬移前的位置。
- 未實跑上游 42 條 benchmark、互動確認、模型改寫、跨平台安裝與 Prompt Injection 測試；未安裝、未複製 Skill 到私有 repo，未修改檢查器或測試。安全邊界是文字規範，不是工具權限或 OS 隔離。
- [Codex 安裝說明][install] 開頭稱沒有全域自動發現，後文又列依版本而定的 skills 目錄，內部說法不一致；本次不採納其安裝指令，現行 Codex 發現機制與安裝可行性未另驗。

## 附錄：上游 MIT notice

以下保留自固定 commit 的 [LICENSE][license]，用於本報告對照素材之授權標示；不表示其他引用來源一律受其涵蓋。

```text
MIT License

Copyright (c) 2026 Raymond Hou (雷蒙三十)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

[license]: https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/LICENSE
[skill]: https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/SKILL.md
[localization]: https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/taiwan-localization.md
[patterns]: https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/patterns.md
[protected]: https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/protected-list.md
[benchmark]: https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/evals/benchmark.md
[results]: https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/evals/results-v1.4.0.md
[install]: https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/install/codex.md
[cc-license]: https://github.com/Raymondhou0917/claude-code-resources/blob/1320df1e396e7630b09d2dc80fae4b2c96861d54/LICENSE
[cc-readme]: https://github.com/Raymondhou0917/claude-code-resources/blob/1320df1e396e7630b09d2dc80fae4b2c96861d54/README.md
