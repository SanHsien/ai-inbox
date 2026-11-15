# 本機 SVG Logo 方案唯讀比較

日期：2026-11-15。任務：T-20261115-03。作者：Codex。

**結論：暫不採納 LogoLoom MCP；目前優先由既有 agent 直接產出幾何 SVG。** LogoLoom 有批次匯出價值，但原始碼含未固定版本的 npx 備援與 shell 字串組裝，不能以「本機」或「無 API key」推定離線、安全或全程零成本。本輪沒有安裝、啟動 MCP、執行外部程式或產圖實測。

## 固定版本與一手來源

來源：[mcpware/logoloom](https://github.com/mcpware/logoloom/tree/9e5de3e95d24fd86ea9af3cbe77749df088ad176)，作者 package 宣告 ithiria894；MIT。固定 commit：`9e5de3e95d24fd86ea9af3cbe77749df088ad176`。以下連結均固定版本，檔案已實際閱讀。

| 代號 | 檔案 | 查閱重點 |
|---|---|---|
| L1 | [README](https://github.com/mcpware/logoloom/blob/9e5de3e95d24fd86ea9af3cbe77749df088ad176/README.md)、[package.json](https://github.com/mcpware/logoloom/blob/9e5de3e95d24fd86ea9af3cbe77749df088ad176/package.json)、[package-lock.json](https://github.com/mcpware/logoloom/blob/9e5de3e95d24fd86ea9af3cbe77749df088ad176/package-lock.json) | 設計與後處理分工、依賴與安裝風險 |
| L2 | [bin/cli.mjs](https://github.com/mcpware/logoloom/blob/9e5de3e95d24fd86ea9af3cbe77749df088ad176/bin/cli.mjs)、[src/server.mjs](https://github.com/mcpware/logoloom/blob/9e5de3e95d24fd86ea9af3cbe77749df088ad176/src/server.mjs) | stdio MCP、四個工具與參數 |
| L3 | [text-to-path.mjs](https://github.com/mcpware/logoloom/blob/9e5de3e95d24fd86ea9af3cbe77749df088ad176/src/tools/text-to-path.mjs)、[optimize-svg.mjs](https://github.com/mcpware/logoloom/blob/9e5de3e95d24fd86ea9af3cbe77749df088ad176/src/tools/optimize-svg.mjs) | 字型讀取、字形與 SVG 清理 |
| L4 | [export-brand-kit.mjs](https://github.com/mcpware/logoloom/blob/9e5de3e95d24fd86ea9af3cbe77749df088ad176/src/tools/export-brand-kit.mjs) | 寫檔、預覽 HTML、格式與匯出條件 |
| L5 | [image-to-svg.mjs](https://github.com/mcpware/logoloom/blob/9e5de3e95d24fd86ea9af3cbe77749df088ad176/src/tools/image-to-svg.mjs) | shell、npx、暫存與 Windows 路徑 |

## 資料流與模型額度

```text
需求 + 專案內容
      |
      v
既有 agent / 設計模型 --消耗訂閱額度或 API token--> SVG 字串
      |                                             |
      | 直接保存 SVG                                v
      +--------------------------------> LogoLoom stdio MCP
                                         | 字型讀取 / SVGO
                                         | sharp 匯出
                                         v
                                  outputDir 多檔 + preview.html

可選點陣圖 --> image_to_svg --> shell vtracer
                                  | 失敗
                                  v
                            npx -y vtracer-cli
                                  | 失敗且 binary
                                  v
                                potrace
```

L1 明說設計 SVG 由 Claude 完成，LogoLoom 做後處理。直接寫 SVG 與 MCP 方案都仍可能消耗上游模型用量；多輪概念、工具呼叫與錯誤修復都會增加上下文。本機 CPU／儲存與維護亦有成本。所查四個工具沒有直接模型 API 呼叫，這不等於依賴、安裝器、備援子程序或上游 agent 沒有外連（L2～L5）。

## 已查風險

| 範圍 | 靜態發現 | 影響與證據界線 |
|---|---|---|
| MCP 入口 | bin 直接 import server，server 建立 StdioServerTransport、註冊四工具；沒有本機 HTTP listener（L2） | stdio 不限制檔案或子程序權限；未啟動協定驗證 |
| 寫入目錄 | outputDir 只驗為字串，mkdir recursive，固定檔名 writeFileSync；沒有專案根目錄允許清單、既存檔保護或 symlink 檢查（L2、L4） | 工具可在程序可寫範圍覆寫同名檔案，途中失敗可能留下部分輸出；不是受限資產資料夾 |
| 預覽內容 | name 未跳脫即插入 HTML title／h1；SVG 亦直接寫出（L4） | 靜態可見 HTML 插入風險，未構造或開啟攻擊頁。若後續開預覽，須另處理不可信內容 |
| 字型 | fontPath 可指定可存取檔，否則用隨附 Inter-Bold.ttf；用 opentype.load；正規表示式處理 text／tspan（L3） | 不是完整 XML／SVG 排版引擎；不能保證中文、複雜字形、transform 與字型授權正確。字型二進位及授權來源未審計 |
| SVG 優化 | SVGO multipass；停用 convertPathData；移除 title／desc，aggressive 另移除 class／style（L3） | 可能改變可及性資訊與外觀；優化器不是不可信 SVG 的安全清洗器。未量測壓縮比例 |
| 子程序 | image_to_svg 用 execSync，把 imagePath 等值 join 為 shell 字串；沒有 argv 隔離／路徑引號（L5） | 帶空白的 Windows 路徑可能失敗；含 shell 控制字元時有命令注入風險。existsSync 不等於輸入安全；未執行驗證利用 |
| 外連與下載 | vtracer 失敗會執行 `npx -y vtracer-cli`，未固定版本；再依模式退回 potrace（L5） | 可能下載並執行另一套件，不能聲稱全程離線。這是明確程式路徑，非僅猜測依賴行為 |
| 暫存 | OS tmpdir 加 Date.now 檔名，成功後讀取／刪除；無專屬目錄與排他建立（L5） | 併行碰撞、連結與失敗後殘留未防護；30／60 秒 timeout 不是 OS 隔離 |
| 匯出品質 | favicon.ico 寫入 PNG 位元組；icon／wordmark 依特定 viewBox、translate 與正規表示式辨識；暗色與字標輸出有條件（L4） | 不能把 README 的 31 檔宣傳當每次保證，亦不能聲稱產生真正 ICO 容器或通過所有平台驗收 |

上表是原始碼追蹤與工程判斷，沒有動態確認漏洞可利用性。尤其不將未跑過的命令注入、SVG 外部資源解析或 native library 行為寫為已重現。

## package、鎖檔與未查範圍

L1 package 版本為 1.0.1，server 自報版本為 1.0.0（L2），版本標記不同。package 與鎖檔都有；package 使用範圍版本的 MCP SDK、opentype.js、SVGO、sharp。根 scripts 只有 start，未宣告自己的 install／postinstall；這不代表間接依賴沒有生命週期。server 直接 import zod，但 package 未直接宣告 zod，會依賴鎖檔／SDK 的實際安裝解析（L1、L2）。

鎖檔 lockfileVersion=3，根名稱與 bin 仍為 `@mcpware/logo-forge`／`logo-forge`，與 package 的 `@mcpware/logoloom`／`logoloom` 不一致；不能把「有鎖檔」寫成套件中繼資料完全一致。鎖檔列 zod 4.3.6，sharp 0.33.5 帶 hasInstallScript；腳本本體與實際安裝結果未查證（L1）。

| 已查 | 未查／不保證 |
|---|---|
| 根 package／lock、入口與四個工具完整文字 | node_modules 全部間接依賴的程式碼、原生二進位及 registry 發行物一致性 |
| 明確 npx 備援、shell、讀寫與暫存路徑 | SDK／sharp／libvips 的執行期網路與解析安全、資源耗用上限 |
| 隨附字型檔存在；README 要求 Node.js 18+（L1） | 本機 Node／sharp ABI、中文字形、外部向量化 CLI 與 Windows 安裝可行性 |
| SVG 與預覽內容的直接寫出行為 | 真實 Logo 視覺品質、印刷、ICO 解碼與商標可用性 |

Windows 不能照抄 README 的 apt 指令；vtracer／potrace 要有相容執行檔與 PATH，npx 還需 npm 與可能的網路。sharp 原生相依性必須另外查核目標 Node、CPU 與預建套件；本輪沒有下載這些依賴（L1、L5）。

## 方案比較與採納決策

| 方案 | 新增價值 | 額度／維護 | 本次決策 |
|---|---|---|---|
| 既有 agent 直接寫 SVG | 幾何圖元、viewBox、可編輯路徑即可交付小型 Logo | 既有模型額度；不新增 MCP 程序。SVG 內容仍須檢閱 | 優先採用；這是工作方式建議，本輪未產圖實測 |
| LogoLoom | 字型轉路徑、多尺寸、社群圖批次後處理（L3、L4） | 上游模型額度仍在；另增 Node／native／CLI／寫檔風險 | 暫不安裝；尚無批次需求足以抵銷風險 |
| Rikyū 遠端 MCP | 不在本次原始碼比較範圍 | 最新免費／付費／商用與協定可用性本輪未查證 | 不以其為零成本替代，也不登入或呼叫 |

若以後確有大量品牌套件需求，採納前至少需移除自動 npx 備援、改 argv 子程序、限制輸出根目錄與覆寫、固定依賴並完成既定安全審批。這些是採納條件說明，不是本輪新增實作待辦或已完成的修正；本次不建新 Skill、不修改全域設定。

## 驗證與 DoD

來源版本／URL、ASCII、已查／未查、模型用量、Windows 相依性及不採納結論均見上文。文件檢查紀錄如下；沒有將未安裝視為缺件，也沒有宣稱動態安全或圖像品質通過。

2026-11-15 整合時先執行 `python tools/build_index.py` 把本輪三份報告列入 README，再執行 `python tools/verify_zhtw_vocab.py --check docs && python tools/verify_inbox.py`：兩者結束碼 0（117 篇筆記、229 項任務）。撰寫時 README 尚未重產，inbox 檢查曾回 1，原因只有 README 過期與漏列報告。
