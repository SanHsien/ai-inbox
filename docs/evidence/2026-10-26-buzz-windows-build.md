# Buzz 在 Windows 11 的編譯檢查與 Job Object 驗證（T-20261026-09）

執行日期：2026-10-26。倉庫：`SanHsien/buzz`（Block 官方 buzz 的 fork，本機 `C:\GitHub\buzz`），未修改任何被追蹤檔案（`git status --short` 前後皆為空），未 commit／push。

**結論先講**：`cargo check -p buzz-dev-mcp -p buzz-agent` **在本機失敗，不是程式碼問題**——本機 Visual Studio Build Tools 2022 沒有安裝 C++ 工作負載（找不到 MSVC `link.exe`），所有相依套件的 build script 都連結失敗。所以 `buzz-dev-mcp` 與 `buzz-agent` 本身**尚未被編譯到**。Job Object 機制改以原始碼閱讀加上獨立的 Win32 實驗驗證（實驗不是 buzz 的 Rust 程式碼本身，見第 4 節）。DoD 的「編譯檢查完成」因此**未達成**，需要裝好 C++ 工作負載後重跑（第 2 節）。

## 1. 環境

| 項目 | 值 |
| --- | --- |
| 作業系統 | Windows 11 Pro 10.0.26300（原生，非 WSL） |
| Rust | `~/.cargo/bin/cargo.exe`；`rust-toolchain.toml` 釘 `channel = "1.95.0"`，首次執行 rustup 自動安裝 `1.95.0-x86_64-pc-windows-msvc`（下載 6 個 component）；另有 `stable-x86_64-pc-windows-msvc` 為預設 |
| C++ 工具 | `vswhere -all` 只找到 Visual Studio Build Tools 2022（17.14.42）；`vswhere -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64` 無輸出；`...\BuildTools\VC\Tools\MSVC` 目錄不存在；僅有 Windows SDK `10.0.26100.0` |

## 2. cargo check 實測

指令（兩次，輸出皆保留在 `%TEMP%`）：

```text
# 第 1 次：Git Bash 內
cd /c/GitHub/buzz && export PATH="$HOME/.cargo/bin:$PATH" && cargo check -p buzz-dev-mcp -p buzz-agent
# 第 2 次：PowerShell 內
cd C:\GitHub\buzz; & "$env:USERPROFILE\.cargo\bin\cargo.exe" check -p buzz-dev-mcp -p buzz-agent
```

| 次 | 耗時 | 結束碼 | 警告數 | 錯誤 | 關鍵行 |
| --- | --- | --- | --- | --- | --- |
| 1（bash） | 約 151 秒（含 toolchain 安裝與 crates.io／git 相依下載，下載了 `rust-s3`、`sqlx`、`mesh-llm` 三個 git 相依的索引） | 101 | 1（`build failed, waiting for other jobs to finish`） | 19 個 `could not compile ... (build script)` | `error: linking with link.exe failed: exit code: 1` … `link: extra operand '...rcgu.o'`——bash 的 PATH 上先找到 Git 內附的 coreutils `link`，不是 MSVC 連結器 |
| 2（PowerShell） | 28.6 秒（相依已下載） | 101 | 1（同上） | 19 個 build script 編譯失敗 | `error: linker link.exe not found` / `note: program not found` |

兩次的根因一致：沒有 MSVC 連結器。第 1 次在 bash 看到的 `extra operand` 是 coreutils `link` 被誤當連結器的次要現象。失敗的 build script 包含 `proc-macro2`、`serde`、`libc`、`rustls`、`aws-lc-rs`、`getrandom` 等，都發生在編譯 buzz 自己的 crate 之前。

我沒有安裝 Visual Studio 元件：那會修改系統環境，超出本任務授權。補救步驟（需維護者執行，約數 GB）：

```text
開啟「Visual Studio Installer」→ Build Tools 2022 →「修改」→ 勾選「使用 C++ 的桌面開發」
（至少含 MSVC v143 x64/x86 建置工具 與 Windows 11 SDK）
然後從「x64 Native Tools Command Prompt」或一般 PowerShell 重跑：
cd C:\GitHub\buzz; & "$env:USERPROFILE\.cargo\bin\cargo.exe" check -p buzz-dev-mcp -p buzz-agent
```

編譯注意事項（讀自原始碼，**非實測**）：`rust-toolchain.toml` 釘 1.95.0；`buzz-dev-mcp/Cargo.toml` 第 52 行對 Windows 加 `windows-sys 0.61`（features：`Win32_Foundation`、`Win32_Security`、`Win32_System_JobObjects`、`Win32_System_Registry`、`Win32_System_Threading`），註解稱它已是 workspace 的傳遞相依，不新增 crate；相依樹含 `aws-lc-rs` 的 build script（原生程式碼編譯，依賴 C 工具鏈，是否還需 CMake／NASM 未驗證）。另需 Git for Windows 提供 `bash.exe`（`shell.rs` 的 `resolve_bash`，可用環境變數 `BUZZ_SHELL` 指定）。

## 3. Job Object 實作位置（原始碼）

檔案 `crates/buzz-dev-mcp/src/shell.rs`（Windows 分支）：

| 行號 | 內容 |
| --- | --- |
| 735–750 | `struct KillGroup { job: HANDLE }`，手寫 `unsafe impl Send/Sync`（HANDLE 是核心物件參考，非執行緒綁定） |
| 755–791 | `KillGroup::new`：`CreateJobObjectW(null,null)` 建匿名 job；`SetInformationJobObject(JobObjectExtendedLimitInformation)` 設 `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`；對子行程 `AssignProcessToJobObject`。失敗時 job 為 null，後續呼叫無動作 |
| 793–813 | `kill_immediate`／`kill_graceful`／`terminate`：Windows 無 SIGTERM，兩者都呼叫 `TerminateJobObject(job, 137)`（137 對齊 Unix 的 SIGKILL 回報碼） |
| 818 | `disarm` 為空操作 |
| 821–837 | `Drop`：`CloseHandle(job)`；最後一個 handle 關閉時，因 KILL_ON_JOB_CLOSE 殺掉殘留行程（保底） |
| 405–640 | 其他 `#[cfg(windows)]` 區塊（bash 解析、spawn 設定） |
| 1144 起 | `windows_resolver_tests`：只測 `resolve_bash`（`BUZZ_SHELL` 覆寫、System32 WSL 排除）；**沒有針對 Job Object 的單元測試**，且 `timeout_fires`（行 1032）是共用測試。這些測試同樣因無連結器而無法在本機執行 |

已知風險（讀碼推論）：行程先 spawn 再 Assign，兩者之間 spawn 出的孫行程不會進 job；實務上 bash 啟動到 fork 子行程有延遲，窗口很小，但沒有用 `CREATE_SUSPENDED` 消除。

## 4. Job Object 行為實驗（獨立於 buzz 程式碼）

因為 buzz 無法編譯，我用 PowerShell `Add-Type` 的 C# P/Invoke，把 `shell.rs` 的相同呼叫序列（`CreateJobObjectW(null,null)` → `SetInformationJobObject(ExtendedLimit, KILL_ON_JOB_CLOSE)` → `AssignProcessToJobObject` → `TerminateJobObject(job,137)`／`CloseHandle`）在 `%TEMP%\jobexp` 重現。這驗證的是**同一組 Win32 API 的行為**，不是 buzz 的 Rust 程式碼。腳本未放進 buzz 或本 repo。實際輸出：

```text
=== Test A: cmd.exe tree, TerminateJobObject(137) ===
SetInformationJobObject ok=True structSize=144
Assign ok=True pid=87720
descendants before: conhost.exe(18876), PING.EXE(58044)
alive after terminate: 0 of 3
root exit code: 137
=== Test B: Git bash (MSYS) tree, TerminateJobObject ===
SetInformationJobObject ok=True structSize=144
Assign ok=True pid=20460
descendants before: conhost.exe(54088), bash.exe(44856)
alive after terminate: 0 of 3
root exit code: 137
=== Test C: KILL_ON_JOB_CLOSE (CloseHandle only, no Terminate) ===
tree size: 3
alive after CloseHandle: 0 of 3
=== Control: no job object, kill only root ===
alive after killing root only: 2 of 3
```

解讀：

- A：`cmd.exe /c "ping ... & cmd /c ping ..."`，終止 job 後根行程與 2 個後代全部消失，根行程結束碼 137。
- B：Git for Windows 的 `bash.exe -c "sleep 60 & sleep 60 & wait"`（MSYS 行程），後代偵測到 `bash.exe`、`conhost.exe`，終止後 0/3 存活，結束碼 137。
- C：不呼叫 Terminate，只 `CloseHandle`，KILL_ON_JOB_CLOSE 同樣清掉整棵樹，對應 `Drop` 的保底。
- 對照組：不用 job、只殺根行程，後代存活 2/3——證明 job 才是讓子行程樹一併終止的原因。
- 限制：樹的深度只有 2～3 層；MSYS 的 `sleep` 多為 fork 出的同名 bash.exe 行程，只偵測到 1 個；未測 spawn 與 Assign 之間的競態，也未測 buzz 實際的逾時路徑（`timeout_fires`）。實驗結束後已清除所有 ping 行程（`tasklist` 無 ping 殘留）。

## 5. DoD 對照

| DoD | 狀態 |
| --- | --- |
| 在 `SanHsien/buzz` 完成 `buzz-dev-mcp` 與 `buzz-agent` 編譯檢查 | **未達成**：環境缺 MSVC 連結器，第 2 節有完整指令、輸出與補救步驟 |
| 記錄執行日誌 | 已記錄（第 2 節） |
| Job Object 驗證結果 | 原始碼定位（第 3 節）＋同 API 實驗（第 4 節）已完成；buzz 自身的測試未能執行 |

因 DoD 第一項未達成，建議 `T-20261026-09` 先不結案，待裝好 C++ 工作負載、`cargo check` 與 `cargo test -p buzz-dev-mcp` 實際通過後再補記。
