# feedback-desk Windows 11 原生環境評估報告（T-20261024-03）

## 1. 評估背景與目標
依據任務 `T-20261024-03`，在 Windows 11 原生環境（非 WSL）下評估開源專案 `feedback-desk`（`github:aixwangtw/feedback-desk`）的 CLI 與相依結構。
本次評估遵循安全規範：僅於暫存目錄（`$env:TEMP\fd-eval-test`）執行，僅測試 `node -v`、`init` 與檢查其 `package.json` / `bin` 結構，不執行雲端 `deploy`，且完成後立即清理暫存資料夾。

## 2. 環境檢測：Node.js 版本
執行指令：`node -v`
```text
v26.12.1
```
檢驗結果：符合官方 `package.json` 宣告之 `"engines": { "node": ">=20" }` 要求。

## 3. CLI 初始化執行與錯誤紀錄
執行指令：
`npx --yes --allow-git=all github:aixwangtw/feedback-desk init --name test-desk`

### 3.1 執行輸出與錯誤訊息
在 Windows 11 原生終端機（PowerShell / CMD）中執行，指令回傳非零退出碼（Exit Code: 1），未產出目標檔案，npm debug log 與行程輸出之核心錯誤堆疊如下：

```text
> feedback-desk@0.1.0 prepare
> node scripts/build.mjs

node:internal/child_process:1175
    result.error = new ErrnoException(result.error, 'spawnSync ' + options.file);
                   ^

<ref *1> Error: spawnSync C:\Users\SanHsien\AppData\Local\Temp\fd-eval-test\repo\node_modules\.bin\tailwindcss ENOENT
    at Object.spawnSync (node:internal/child_process:1175:20)
    at spawnSync (node:child_process:976:24)
    at execFileSync (node:child_process:1019:15)
    at file:///C:/Users/SanHsien/AppData/Local/Temp/fd-eval-test/repo/scripts/build.mjs:34:1
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5) {
  errno: -4058,
  code: 'ENOENT',
  syscall: 'spawnSync C:\\Users\\SanHsien\\AppData\\Local\\Temp\\fd-eval-test\\repo\\node_modules\\.bin\\tailwindcss',
  path: 'C:\\Users\\SanHsien\\AppData\\Local\\Temp\\fd-eval-test\\repo\\node_modules\\.bin\\tailwindcss',
  spawnargs: [
    '-i',
    'C:\\Users\\SanHsien\\AppData\\Local\\Temp\\fd-eval-test\\repo\\client\\app.css',
    '-o',
    'C:\\Users\\SanHsien\\AppData\\Local\\Temp\\fd-eval-test\\repo\\dist\\public\\assets\\app.css',
    '--minify'
  ],
  error: [Circular *1],
  status: null,
  signal: null,
  output: null,
  pid: 0,
  stdout: undefined,
  stderr: undefined
}

Node.js v26.12.1
npm error code 1
```

## 4. package.json 與 bin 結構剖析

### 4.1 package.json 關鍵結構
```json
{
  "name": "feedback-desk",
  "version": "0.1.0",
  "type": "module",
  "bin": {
    "feedback-desk": "dist/cli.js"
  },
  "files": [
    "dist",
    "migrations",
    "README.md",
    "LICENSE"
  ],
  "engines": {
    "node": ">=20"
  },
  "scripts": {
    "build": "node scripts/build.mjs",
    "prepare": "node scripts/build.mjs"
  }
}
```

### 4.2 結構與跨平台根因分析
1. **未發布 npm registry 與未納入 dist 追蹤**：
   - 官方尚未發布至 npm registry，需以 `github:aixwangtw/feedback-desk` 透過 git 下載。
   - Git 儲存庫的 `.gitignore` 明列 `dist/`，因此 clone 下來的儲存庫中並無預建置的 `dist/cli.js`。
2. **npm prepare 生命週期於原生 Windows 失敗**：
   - 套件安裝時會觸發 `prepare` 腳本（`node scripts/build.mjs`）。
   - 在 `scripts/build.mjs` 第 34 行：
     `execFileSync(join(root, 'node_modules', '.bin', 'tailwindcss'), ...)`
   - Windows 原生環境下的 npm 於 `.bin/` 產生的是 `tailwindcss`（無副檔名 shell 腳本）、`tailwindcss.cmd` 與 `tailwindcss.ps1`。
   - `execFileSync` 在 Windows 上無法直接執行無副檔名腳本，產生 `ENOENT`；若手動指定 `tailwindcss.cmd`，依 Node.js Windows 安全限制（CVE-2024-27980 修正），未帶 `{ shell: true }` 時會引發 `EINVAL` 阻擋。
3. **修復後的 CLI 行為驗證（沙盒實測）**：
   - 若將 `scripts/build.mjs` 調整為指定 `.cmd` 並賦予 `{ shell: true }`，建置即可產出 `dist/cli.js`。
   - 手動以 `node dist/cli.js init --name test-desk` 執行時，能正確產出 `wrangler.jsonc` 並複製 `.feedback-desk/migrations/`、`.feedback-desk/public/` 與 `.feedback-desk/worker/` 構件。

## 5. 評估結論
結論：在 upstream 未發布預建置 npm 套件或未修正 scripts/build.mjs 的 Windows 原生子行程呼叫前，官方文檔記載之 npx --allow-git=all github:aixwangtw/feedback-desk 於 Windows 11 原生環境無法直接執行，必須透過 WSL（或由維護者採用本地 clone 手動修補建置腳本）方可運作。
