# AI 生成人物與聲音使用合規檢查清單（AI Persona Compliance Checklist）

- **建立依據**：查證報告 [`docs/ai-influencer-claims-check.md`](./ai-influencer-claims-check.md)（T-20261024-05）
- **查閱與建立日期**：2026-10-25
- **適用對象**：維護者評估或執行任何涉及 AI 生成人物、虛擬網紅（AI Influencer）、相片 Avatar、聲音複製（Voice Cloning）及口播影片產製專案
- **使用方式**：在專案動工、生成、發布前，逐項檢查並勾選確認；未全數符合前不得上線或公開發布

---

## 1. 合規檢查清單（Checklist）

### 類別一：AI 揭露（AI Disclosure & Transparency）
> 確保閱聽眾與平台明確知悉內容包含生成式 AI 元素，符合透明度規範並避免處罰。

- [ ] **貼文與短影音標籤**：於 Instagram、Facebook 等平台發布擬真人物影音前，在編輯或發布頁面主動啟用原生「AI Info」或「Add AI label」標籤。
- [ ] **帳號層級虛擬人物揭露**：若帳號定位為完全由 AI 虛擬人物經營，已於個人檔案設定中開啟「AI-generated profile」標籤，避免遭演算法限制探索與推薦資格。
- [ ] **畫面視覺揭露提示**：在口播影片本體或限時動態畫面適當位置，保留或加入清晰可辨之文字提示（例如「本影像包含 AI 生成內容」）或保留 C2PA / SynthID 等中繼資料數位水印。

---

### 類別二：被攝者書面同意（Subject Written Consent & Likeness Rights）
> 確保肖像來源合法，防範侵害人格權、肖像權與隱私權風險。

- [ ] **完整書面肖像授權**：若使用真人自拍或他人照片作為人物基礎，已簽署具法律約束力之書面授權書（明確約定授權範圍、商用用途、發布通路、授權期間與不可撤銷條款）。
- [ ] **嚴禁未授權第三方照片**：確認禁止自社群網路、公開網站抓取未經授權之朋友、網紅或公眾人物照片作為人物角色圖（Character Reference）或訓練素材。
- [ ] **平台生物與錄影驗證機制**：使用 HeyGen 等工具之 Digital Twin 或自訂 Avatar 功能時，嚴格遵循本人動態錄影或生理同意流程，絕不規避驗證程序。

---

### 類別三：聲音複製授權（Voice Cloning Authorization & Voice Rights）
> 保障語音特徵所有人權利，防範聲音侵權與深偽詐欺法規風險。

- [ ] **原發音人書面合法同意**：複製他人聲音前，已取得原發音人明確之書面授權合約，載明允許將其語音樣本訓練為文字轉語音（TTS）模型並進行特定商業口播。
- [ ] **完成平台語音驗證**：遵循 ElevenLabs 平台之 Voice Verification 驗證流程，確保帳號具備合法授權，禁止透過非授權錄音樣本私自複製他人聲線。
- [ ] **聲線仿冒法規審查**：確認語音生成之內容不涉及名人聲線仿冒、政治宣傳、誤導性聲明，符合美國 ELVIS Act 及相關防範不正競爭與人格權保護法規。

---

### 類別四：商用條款（Commercial Licensing & Subscription Compliance）
> 確保工具合約授權與商業營運目的相符，避免侵犯軟體著作權。

- [ ] **全面採用付費商用授權方案**：確認產製商用影音所涉及之工具（如 HeyGen Creator 以上方案、ElevenLabs Starter 以上方案）均具備有效商業使用授權（Commercial License），嚴禁使用免費版生成商用營利素材。
- [ ] **額度與點數合法取得**：依循官方訂閱機制購買 Credits 與點數，嚴禁透過腳本批次註冊免費試用帳號等違反服務條款（Terms of Service）之手段規避付費。
- [ ] **商用合約憑證留存**：留存軟體訂閱購買發票、收據與生效時之官方條款截圖，作為維護者日後因應版權或合作方查核之商業授權舉證依據。

---

### 類別五：平台政策（Platform Policies & Community Guidelines）
> 遵循社群平台最新防範濫用政策與內容推薦標準。

- [ ] **社群守則與防詐規範審查**：審視口播腳本，確認未涉及虛假承諾、誇大療效、非法金融投資或誤導性消費資訊，嚴守平台社群守則。
- [ ] **商業合作雙重標示**：若影片涉及業配、贊助或導購，除 AI 標籤外，須同步啟用平台「付費合作夥伴（Paid Partnership）」或廣告標籤，不可相互混淆或替代。
- [ ] **定期政策追蹤與動態調適**：建立定期排程追蹤 Meta、YouTube、TikTok 等各大平台對虛擬人與生成式影音的最新政策調整，即時修正發布標準。

---

## 2. 官方參考來源與查核紀錄

本清單依據下列官方政策與規範條款制定，維護者於 2026-10-25 查證確認：

1. **Meta 官方內容標示與政策**：
   - [Meta Newsroom: Meta’s Approach to Labeling AI-Generated Content and Manipulated Media](https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/)（查閱日期：2026-10-25）
   - [Meta Transparency Center: Manipulated Media Policy](https://transparency.meta.com/policies/community-standards/manipulated-media/)（查閱日期：2026-10-25）
   - [Instagram Help Center: About AI-generated profiles on Instagram](https://help.instagram.com/)（查閱日期：2026-10-25）
2. **HeyGen 官方使用條款與倫理守則**：
   - [HeyGen Terms of Service](https://www.heygen.com/terms)（查閱日期：2026-10-25）
   - [HeyGen Ethics & Trust Guidelines](https://www.heygen.com/ethics)（查閱日期：2026-10-25）
   - [HeyGen Official Pricing & Commercial Plans](https://www.heygen.com/pricing)（查閱日期：2026-10-25）
3. **ElevenLabs 官方服務條款與安全政策**：
   - [ElevenLabs Terms of Service](https://elevenlabs.io/terms)（查閱日期：2026-10-25）
   - [ElevenLabs Safety & Responsible AI Policy](https://elevenlabs.io/safety)（查閱日期：2026-10-25）
   - [ElevenLabs Official Pricing Plans](https://elevenlabs.io/pricing)（查閱日期：2026-10-25）
