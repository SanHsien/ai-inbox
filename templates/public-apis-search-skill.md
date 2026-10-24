# Public APIs 動態檢索 Skill / MCP 伺服器規格 (Public APIs Search Protocol)

> 本規格文件收錄於 `templates/public-apis-search-skill.md`，定義 Agent 依據 `tools/public_apis_indexer.py` 產出之離線索引（`docs/free-public-apis.md`），動態檢索合適的免費公開 API 並生成 Generative UI 即時數據串接代碼的標準協議。以 ai-inbox 範本形式交付。

---

## 1. 技能定義 (YAML Frontmatter)

```yaml
name: public-apis-search
description: 檢索並推薦零金鑰（Auth: No）、跨域友善（CORS: Yes）與 HTTPS 加密的公開 API。為 Coding Agent 在構建前端原型、Generative UI 與概念驗證 Demo 時，提供即時、真實且免註冊的 Live Data 資料源。
triggers:
  - "public-apis"
  - "免費 API"
  - "公開 API"
  - "天氣 API"
  - "免金鑰 API"
  - "即時圖表"
  - "live data demo"
```

---

## 2. 核心三大檢索門檻 (The Three Gating Rules)

當 Agent 為 Generative UI 或前端原型挑選 API 時，必須嚴格遵守以下三道篩選門檻：

1. **零金鑰免註冊（Auth: No）**：
   - 優先選用完全無須 API Key、無須 OAuth、無須信用卡註冊的公開端點。
   - 避免讓使用者在體驗 Generative UI 互動時因配置密鑰而中斷體驗。
2. **瀏覽器跨域放行（CORS: Yes）**：
   - 凡是要在前端單檔 HTML / Artifact 中以 `fetch()` 呼叫的 API，必須確認 `CORS: Yes`。
   - 若為 `CORS: Unknown` 或 `No`，Agent 必須明示此 API 僅適用於後端 Node/Python 腳本，禁止直接在純前端環境中使用。
3. **安全傳輸（HTTPS: Yes）**：
   - 所有請求必須強制走 HTTPS，防止現代瀏覽器因 Mixed Content 策略全面阻擋請求。

---

## 3. 常用免金鑰黃金端點速查表 (Golden Public APIs Directory)

| 領域類別 | 推薦 API 服務 | 端點範例 | CORS | 適用場景 |
| :--- | :--- | :--- | :--- | :--- |
| **氣象天候** | **Open-Meteo** | `https://api.open-meteo.com/v1/forecast` | Yes | 全球高精度即時氣溫、風速、濕度與 7 天氣象預報圖表。 |
| **圖書文獻** | **Open Library** | `https://openlibrary.org/search.json?q={query}` | Yes | 書籍搜尋、ISBN 條碼查驗、封面縮圖與作者資訊。 |
| **遊戲動漫** | **PokéAPI** | `https://pokeapi.co/api/v2/pokemon/{name}` | Yes | 寶可夢屬性、數值圖表、技能與官方立繪圖片。 |
| **地理政區** | **REST Countries** | `https://restcountries.com/v3.1/name/{name}` | Yes | 國家代碼、國旗 SVG、人口、首都與地理座標。 |
| **語言字典** | **Free Dictionary** | `https://api.dictionaryapi.dev/api/v2/entries/en/{word}` | Yes | 英文單字音標、詞性、例句與發音音訊檔。 |

---

## 4. MCP Server 工具架構規格

若將本技能封裝為標準 MCP Server，其提供的 Tools 定義如下：

```json
{
  "tools": [
    {
      "name": "search_public_apis",
      "description": "依關鍵字或類別檢索 docs/free-public-apis.md 索引庫中的免費 API",
      "parameters": {
        "type": "object",
        "properties": {
          "category": { "type": "string", "description": "類別，如 Weather, Books, Anime, Geocoding" },
          "cors_only": { "type": "boolean", "default": true, "description": "僅回傳支援 CORS 的端點" }
        }
      }
    },
    {
      "name": "test_api_endpoint",
      "description": "即時發起 HTTP GET 探測，確認目標端點存活率、延遲與回傳 JSON 結構",
      "parameters": {
        "type": "object",
        "properties": {
          "url": { "type": "string", "description": "欲測試的 API 完整 URL" }
        },
        "required": ["url"]
      }
    }
  ]
}
```

---

## 5. Agent 提示詞注入樣板 (Prompt Template)

```markdown
當使用者要求「做一個即時資料展示網頁」、「畫某城市的氣候圖表」或「串接免費公開資料」時：
1. 嚴格查詢 `docs/free-public-apis.md` 抽取 Auth: No 且 CORS: Yes 的端點。
2. 預設使用 Fetch API 配合 Loading 骨架屏與 Error Boundary，防止網路逾時導致空白頁面。
3. 採用深色現代科技感介面，使用 Chart.js 或 Canvas 即時繪製視覺化圖表。
```
