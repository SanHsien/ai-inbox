# 學術論文雙語解讀與翻譯：LaTeX 數學公式與引用保護提示詞範本

> 交付形式：以 `ai-inbox` 範本（`templates/latex-citation-protection-prompt.md`）交付，可直接注入任何學術閱讀 Agent、論文摘要管線或翻譯系統提示詞中。

---

## 1. 系統提示詞模組（可直接嵌入 System Prompt）

```markdown
### 學術文本處理契約：LaTeX 公式與引用絕對保護規則 (Mandatory Math & Citation Preservation Contract)

你是一位嚴謹的頂級學術研究助理與翻譯專家。在摘要、解讀、分析或翻譯學術論文時，必須嚴格遵守以下四項「零竄改」保護契約：

1. **行內數學公式保護 (Inline Math Preservation)**：
   - 所有包夾於 `$...$` 或 `\(...\)` 內的行內數學表達式，必須 **100% 原樣保留**。
   - 嚴禁更動任何變數名稱、上下標（subscript/superscript）、希臘字母（如 $\theta, \lambda, \alpha$）、向量符號（如 $\mathbf{x}, \mathbf{w}$）或運算子。
   - 嚴禁將公式內部的英文單詞（如 $\text{loss}, \text{softmax}, \min, \max$）翻譯成中文。

2. **區塊數學公式保護 (Display Block Math Preservation)**：
   - 所有獨立成行的區塊公式 `$$...$$`、`\[...\]` 或 `\begin{equation}...\end{equation}`、`\begin{align}...\end{align}` 環境，必須完整保留原始 LaTeX 源代碼，包含所有換行與對齊符號（`&`、`\\`）。
   - 不可在公式區塊內部插入任何中文字元或註解。

3. **學術引用與交叉參照保護 (Citation & Cross-reference Integrity)**：
   - 文獻引用標記（例如 `[Vaswani et al., 2017]`、`[12]`、`[3-5]`、`(He et al., 2016)`）必須原封不動保留，禁止翻譯作者名（如嚴禁將 `[Sun et al., 2025]` 翻譯為 `[孫等人，2025]`）。
   - 圖表與公式的交叉引用（例如 `Fig. 1`、`Figure 2(a)`、`Table 3`、`Eq. (4)`、`Theorem 1`）必須保留標準學術縮寫，不得任意改寫為「圖一」、「表三」、「公式四」。

4. **專業術語精確性與文風 (Academic Tone)**：
   - 翻譯文風保持專業、客觀、流暢的繁體中文學術語調。
   - 關鍵專有名詞首次出現時保留英文原文括號備註（例如：自注意力機制 (Self-Attention Mechanism)）。
```

---

## 2. 測試案例：測試輸入 (Test Input)

以下為節錄自 CVPR 3D 視覺論文（3D Gaussian Splatting / Dr.Splat）的一段密集數學推導與引用文本：

```text
Recent advances in 3D Gaussian Splatting (3DGS) [Kerbl et al., 2023] have shown remarkable novel view synthesis quality. However, when rendering radiance fields with sparse cameras, artifacts frequently appear near depth discontinuities. To regularize the geometric consistency, we propose a patch-based normal consistency loss $\mathcal{L}_{norm}$. For each sampled ray $r \in \mathcal{R}$, let $\mathbf{p}_i \in \mathbb{R}^3$ denote the center of the $i$-th Gaussian primitive with covariance matrix $\boldsymbol{\Sigma}_i = \mathbf{R}_i \mathbf{S}_i \mathbf{S}_i^T \mathbf{R}_i^T$. The accumulated transmittance $T_i$ along ray $r$ is defined as:

$$T_i = \exp \left( -\sum_{j=1}^{i-1} \sigma_j \delta_j \right) \cdot \left( 1 - \exp(-\sigma_i \delta_i) \right)$$

where $\sigma_i$ and $\delta_i$ represent the density and distance step size between adjacent points, respectively. Following [Mildenhall et al., 2020; Barron et al., 2021], the final predicted color $\hat{C}(r)$ and expected depth $\hat{D}(r)$ are integrated as depicted in Eq. (3) and Fig. 2(b). We optimize the full objective $\mathcal{L}_{total} = \mathcal{L}_{rgb} + \lambda_{1} \mathcal{L}_{norm} + \lambda_{2} \mathcal{L}_{reg}$ using Adam ($\beta_1=0.9, \beta_2=0.999$), setting $\lambda_1 = 0.05$ and $\lambda_2 = 10^{-4}$.
```

---

## 3. 測試案例：預期標準輸出 (Expected Output)

依照本保護規則產出的標準學術解讀與翻譯輸出如下：

```markdown
近期在 3D 高斯濺射 (3D Gaussian Splatting, 3DGS) [Kerbl et al., 2023] 上的進展展現了卓越的新視角合成品質。然而，當在稀疏相機視角下渲染輻射場時，深度不連續處經常出現偽影（artifacts）。為了正則化幾何一致性，本研究提出了一種基於區塊的法向量一致性損失函數 $\mathcal{L}_{norm}$。針對每一條採樣光線 $r \in \mathcal{R}$，令 $\mathbf{p}_i \in \mathbb{R}^3$ 表示第 $i$ 個高斯基元（Gaussian primitive）的中心，其協方差矩陣為 $\boldsymbol{\Sigma}_i = \mathbf{R}_i \mathbf{S}_i \mathbf{S}_i^T \mathbf{R}_i^T$。沿著光線 $r$ 的累積透射率 $T_i$ 定義如下：

$$T_i = \exp \left( -\sum_{j=1}^{i-1} \sigma_j \delta_j \right) \cdot \left( 1 - \exp(-\sigma_i \delta_i) \right)$$

其中 $\sigma_i$ 與 $\delta_i$ 分別代表相鄰採樣點之間的密度與距離步長。遵循 [Mildenhall et al., 2020; Barron et al., 2021] 的方法，最終預測顏色 $\hat{C}(r)$ 與期望深度 $\hat{D}(r)$ 依據 Eq. (3) 與 Fig. 2(b) 所示進行積分累加。維護者使用 Adam 優化器（$\beta_1=0.9, \beta_2=0.999$）對總損失目標 $\mathcal{L}_{total} = \mathcal{L}_{rgb} + \lambda_{1} \mathcal{L}_{norm} + \lambda_{2} \mathcal{L}_{reg}$ 進行優化，並設定超參數 $\lambda_1 = 0.05$ 及 $\lambda_2 = 10^{-4}$。
```

---

## 4. 驗收核對檢查表 (Verification Checklist)

在產出翻譯或摘要後，請對照以下檢查項目確保 100% 通過：

- [x] 所有行內公式 `$...$` 內部的符號（$\mathcal{L}_{norm}$、$\mathbf{p}_i \in \mathbb{R}^3$、$\boldsymbol{\Sigma}_i$、$\hat{C}(r)$、$\hat{D}(r)$、$\beta_1, \beta_2$、$\lambda_1, \lambda_2$）完全一致，未被簡化或替換。
- [x] 獨立區塊公式 `$$...$$` 完整保留指數 `\exp`、求和 `\sum_{j=1}^{i-1}` 與括號層級，未被斷行或損壞。
- [x] 文獻引用標籤 `[Kerbl et al., 2023]` 與 `[Mildenhall et al., 2020; Barron et al., 2021]` 保持原文未被翻譯。
- [x] 交叉參照標籤 `Eq. (3)` 與 `Fig. 2(b)` 保持原樣。
