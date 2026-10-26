# Buzz 在 Windows 11 的編譯檢查與 Job Object 驗證（T-20261026-09）

執行日期：2026-10-26。倉庫：`SanHsien/buzz`（Block 官方 buzz 的 fork，本機 `C:\GitHub\buzz`），未修改任何被追蹤檔案（`git status --short` 前後皆為空），未 commit／push。

**結論先講**：補裝 MSVC 後重跑（第 2.1 節），`cargo check -p buzz-dev-mcp -p buzz-agent` **通過（exit 0、0 個警告）**；`cargo test -p buzz-dev-mcp` 單執行緒跑 **102/102 通過**，含走 Windows Job Object 殺行程樹路徑的 `timeout_fires`。預設平行跑時有 2 項失敗，查明是 buzz 測試之間搶同一個環境變數，不是 Job Object 或編譯問題（第 2.2 節）。第一次執行失敗的紀錄（缺 MSVC 連結器）保留在第 2 節。

## 1. 環境

| 項目 | 值 |
| --- | --- |
| 作業系統 | Windows 11 Pro 10.0.26300（原生，非 WSL） |
| Rust | `~/.cargo/bin/cargo.exe`；`rust-toolchain.toml` 釘 `channel = "1.95.0"`，首次執行 rustup 自動安裝 `1.95.0-x86_64-pc-windows-msvc`（下載 6 個 component）；另有 `stable-x86_64-pc-windows-msvc` 為預設 |
| C++ 工具 | 第一次：`vswhere -all` 只找到 Visual Studio Build Tools 2022（17.14.42），沒有 VC 工具、`...\BuildTools\VC\Tools\MSVC` 不存在。補裝「使用 C++ 的桌面開發」後：`vswhere -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64` 回 `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools`，MSVC `14.44.35207` |

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

### 2.1 補裝 MSVC 後重跑（2026-10-26）

buzz 當時的 HEAD 是 `abc369f`（fork 有新 commit，相對第一次的 `9e8c9fc`）；工作樹前後皆乾淨。

```text
PS> & "$env:USERPROFILE\.cargo\bin\cargo.exe" --version
cargo 1.95.0 (f2d3ce0bd 2026-03-21)
PS> & "$env:USERPROFILE\.cargo\bin\cargo.exe" check -p buzz-dev-mcp -p buzz-agent
    Checking buzz-agent v0.1.0 (C:\GitHub\buzz\crates\buzz-agent)
    Checking buzz-dev-mcp v0.1.0 (C:\GitHub\buzz\crates\buzz-dev-mcp)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 1m 28s
exit=0（89 秒，0 個 warning）
```

注意：PowerShell 的 PATH 沒有 `~\.cargo\bin`，直接打 `cargo` 會找不到，要用完整路徑（或把它加進 PATH）。

### 2.2 buzz-dev-mcp 測試

```text
PS> cargo test -p buzz-dev-mcp
test shell::tests::timeout_fires ... FAILED
test shell::tests::workdir_is_honored ... FAILED
test result: FAILED. 100 passed; 2 failed  （exit 101，107 秒）
  panicked at crates\buzz-dev-mcp\src\shell.rs:998:37: json: Error("expected ident", line: 1, column: 3)

PS> cargo test -p buzz-dev-mcp --lib shell::tests::timeout_fires
test result: ok. 1 passed; 0 failed; 101 filtered out

PS> cargo test -p buzz-dev-mcp -- --test-threads=1
test shell::tests::timeout_fires ... ok
test result: ok. 102 passed; 0 failed  （另 2 項整合測試也通過，exit 0）
```

原因（讀碼確認）：`windows_resolver_tests` 會用 `env::set_var("BUZZ_SHELL", ...)` 指向假的或不存在的 shell，並用模組內的 `ENV_MUTEX` 互斥；但 `shell::tests` 建立 `SharedState` 時也會讀 `BUZZ_SHELL` 解析 shell，卻沒有拿同一把鎖。平行執行時剛好讀到假 shell，啟動失敗，回傳 `failed to spawn shell: …` 純文字，測試把它當 JSON 解析就壞了（`fai` 對不上 `false`，所以是第 3 欄報錯）。單獨跑或單執行緒跑都通過。這是 buzz 測試的隔離問題，只影響測試，不影響 Job Object 行為；後續已在 buzz `e3561ee`（2026-10-26）修正：把鎖改成 crate 共用的 `lock_shell_env()`，`shell::tests` 與 `read_file::tests` 建 `SharedState` 時也持鎖；預設平行跑 `cargo test -p buzz-dev-mcp` 連續 3 次 102/102 通過，rebase 到 `6b9d953` 後再跑一次也通過。

`timeout_fires` 用 Git Bash 跑 `sleep 5`、逾時 150 ms：通過代表逾時路徑經 Job Object 把 bash 與 MSYS 子行程整棵終止，exit code 124、`timed_out = true`；若子行程沒被殺掉，測試會卡到 `sleep` 自己結束（約 5 秒）才回來，單獨跑這一項整個測試只花 0.27 秒，遠短於 5 秒，代表子行程確實被殺掉、沒有等 sleep 自己結束。

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
- 限制：樹的深度只有 2～3 層；MSYS 的 `sleep` 多為 fork 出的同名 bash.exe 行程，只偵測到 1 個；未測 spawn 與 Assign 之間的競態。buzz 實際的逾時路徑另由第 2.2 節的 `timeout_fires` 驗證。實驗結束後已清除所有 ping 行程（`tasklist` 無 ping 殘留）。

## 5. DoD 對照

| DoD | 狀態 |
| --- | --- |
| 在 `SanHsien/buzz` 完成 `buzz-dev-mcp` 與 `buzz-agent` 編譯檢查 | **達成**：第 2.1 節，exit 0、0 個警告 |
| 記錄執行日誌 | 達成：第 2 節（失敗紀錄）、第 2.1～2.2 節（重跑） |
| Job Object 驗證結果 | 達成：原始碼定位（第 3 節）、buzz 自己的 `timeout_fires` 單執行緒通過（第 2.2 節）、同 API 實驗（第 4 節） |

未做：spawn 與 AssignProcessToJobObject 之間的競態沒有實測；buzz 測試的環境變數競爭已於 buzz `e3561ee` 修正（見第 2.2 節）。
