---
name: github-app-s2s-agent-workflow
description: GitHub App 短期 installation token 交換腳本（Python 與 Bash）與夜間無人值守 Agent 的 GitHub Actions 工作流範本，含權限縮減、爆破半徑關卡與 Draft PR。Use when an unattended agent needs a workload-owned GitHub identity instead of a personal token. 需要讓背景 Agent 用 GitHub App 身分而不是個人 token 時使用。
---

# GitHub App S2S 認證腳本與夜間 Agent 工作流範本

> 規範：[`docs/github-apps-s2s-copilot-workload-identity-guide.md`](../docs/github-apps-s2s-copilot-workload-identity-guide.md)（本 repo）。複製到別的專案時，本檔已含全部程式碼與步驟，不依賴該連結，連結可刪。
> 用法：把下面兩個檔案存成標示的路徑，把「要填的值」填完，先照「本機乾跑」驗證，再手動觸發一次 `workflow_dispatch`。
> 查證日：2026-11-02。Copilot 的 App 認證在官方文件標示為 public preview，行為可能變動；對應來源在文末。

## 1. 要填的值

| 名稱 | 放哪裡 | 怎麼取得 |
| :--- | :--- | :--- |
| `YOUR_ORG/YOUR_REPO` | 工作流 `if:` 那一行 | 要跑夜間 Agent 的組織與 repo。Copilot 的 App 認證只支援組織安裝，個人帳號與 enterprise 安裝不行 |
| `APP_CLIENT_ID` | repo 或組織的 Actions variable（不是 secret） | GitHub App 設定頁的 Client ID（和 App ID 是不同的值） |
| `APP_PRIVATE_KEY` | repo 或組織的 Actions secret | App 設定頁產生私鑰後下載的 `.pem`，**整個檔案內容**（含開頭與結尾那兩行）貼進 secret；貼完就把下載的檔案刪掉 |
| App 的權限 | App 註冊頁 | 組織權限 `Copilot Requests: Read-only`；repo 權限 `Contents`、`Pull requests`、`Issues` 各 Read and write；其餘不勾 |
| `ai-ready` 標籤 | repo labels | 手動建立；只有維護者能貼，Agent 只處理有這個標籤的 issue |

## 2. 檔案一：`.github/scripts/app_installation_token.py`

用私鑰簽 JWT、換 installation token。只用標準函式庫；私鑰只讀環境變數 `GH_APP_PRIVATE_KEY`，不接受檔案路徑、不寫磁碟、不印出。

```python app_installation_token.py
#!/usr/bin/env python3
"""用 GitHub App 私鑰換 1 小時有效的 installation access token（只用 Python 標準函式庫）。

私鑰只從環境變數讀（GH_APP_PRIVATE_KEY），不接受檔案路徑、不寫入磁碟、不印出。
RS256 簽章用純 Python 的 PKCS#1 v1.5 實作；它不是常數時間運算，
只適合在一次性的 CI runner 或自己掌控的主機上跑，不要拿去對外提供簽章服務。

結束碼：0 成功；2 輸入或設定錯誤（含私鑰格式）；3 網路或 HTTP 錯誤；4 回應格式不符。
"""
import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote, urlparse

API_VERSION = "2026-03-10"  # 對照 docs.github.com 的 installation token 範例（查證日 2026-11-02）
MIN_KEY_BITS = 2048
RSA_OID = bytes.fromhex("2a864886f70d010101")
# EMSA-PKCS1-v1_5 的 SHA-256 DigestInfo 前綴（RFC 8017 第 9.2 節）
SHA256_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")
PEM_RE = re.compile(r"-----BEGIN ([A-Z ]+)-----([A-Za-z0-9+/=\s]+)-----END \1-----")
CLIENT_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
LEVELS = {"read", "write"}
# 本 repo 的取捨（不是 GitHub 的規定）：這些權限一律不准 write
DENY_WRITE = {"administration", "organization_administration", "members",
              "secrets", "organization_secrets", "workflows"}


class InputError(Exception):
    """輸入或設定錯誤；訊息不得含私鑰或 token。"""


def _tlv(buf, pos, want_tag):
    try:
        tag = buf[pos]
        length = buf[pos + 1]
    except IndexError:
        raise InputError("私鑰 DER 結構被截斷")
    pos += 2
    if length & 0x80:
        count = length & 0x7F
        if count == 0 or count > 4 or pos + count > len(buf):
            raise InputError("私鑰 DER 長度欄位不合法")
        length = int.from_bytes(buf[pos:pos + count], "big")
        pos += count
    end = pos + length
    if tag != want_tag or end > len(buf):
        raise InputError("私鑰 DER 結構不符 RSA 私鑰")
    return pos, end


def _int(buf, pos):
    start, end = _tlv(buf, pos, 0x02)
    return int.from_bytes(buf[start:end], "big"), end


def load_rsa_private_key(pem):
    """回傳 (n, e, d)。支援 PKCS#1（RSA PRIVATE KEY，GitHub 下載的格式）與未加密 PKCS#8。"""
    if "\\n" in pem and "\n" not in pem:  # 有些 secret 管理介面會把換行存成字面 \n
        pem = pem.replace("\\n", "\n")
    match = PEM_RE.search(pem)
    if not match:
        raise InputError("GH_APP_PRIVATE_KEY 不是 PEM 格式")
    label = match.group(1)
    if label not in ("RSA PRIVATE KEY", "PRIVATE KEY"):
        raise InputError("不支援的 PEM 類型：%s（只支援未加密的 RSA 私鑰）" % label)
    try:
        der = base64.b64decode("".join(match.group(2).split()), validate=True)
    except ValueError:
        raise InputError("私鑰 base64 內容損壞")
    start, end = _tlv(der, 0, 0x30)
    if label == "PRIVATE KEY":  # PKCS#8：SEQUENCE { version, SEQUENCE { OID, ... }, OCTET STRING }
        _, pos = _int(der, start)
        alg_start, pos = _tlv(der, pos, 0x30)
        oid_start, oid_end = _tlv(der, alg_start, 0x06)
        if der[oid_start:oid_end] != RSA_OID:
            raise InputError("PKCS#8 內不是 RSA 金鑰")
        start, end = _tlv(der, pos, 0x04)
        der = der[start:end]
        start, end = _tlv(der, 0, 0x30)
    version, pos = _int(der, start)
    n, pos = _int(der, pos)
    e, pos = _int(der, pos)
    d, pos = _int(der, pos)
    if version != 0 or n.bit_length() < MIN_KEY_BITS or e < 3 or d < 2:
        raise InputError("RSA 私鑰參數不合法或少於 %d 位元" % MIN_KEY_BITS)
    if pow(pow(2, e, n), d, n) != 2:
        raise InputError("RSA 私鑰內部不一致（可能已損壞）")
    return n, e, d


def rs256_sign(signing_input, n, d):
    k = (n.bit_length() + 7) // 8
    t = SHA256_PREFIX + hashlib.sha256(signing_input).digest()
    em = b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
    return pow(int.from_bytes(em, "big"), d, n).to_bytes(k, "big")


def _b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def build_jwt(client_id, n, d, now=None):
    """依 docs.github.com 的 JWT 規定：iat 往前 60 秒、exp 距現在不超過 10 分鐘、iss 用 client ID。"""
    if not CLIENT_ID_RE.match(client_id or ""):
        raise InputError("GH_APP_CLIENT_ID 為空或含不合法字元")
    now = int(time.time()) if now is None else int(now)
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {"iat": now - 60, "exp": now + 540, "iss": client_id}
    parts = [_b64url(json.dumps(x, separators=(",", ":")).encode()) for x in (header, payload)]
    signing_input = ".".join(parts).encode("ascii")
    return signing_input.decode() + "." + _b64url(rs256_sign(signing_input, n, d))


def parse_permissions(text):
    if not text:
        return {}
    try:
        perms = json.loads(text)
    except ValueError:
        raise InputError("--permissions 不是合法 JSON")
    if not isinstance(perms, dict):
        raise InputError("--permissions 必須是 JSON 物件")
    for name, level in perms.items():
        if level not in LEVELS:
            raise InputError("權限 %s 的等級只能是 read 或 write" % name)
        if level == "write" and name in DENY_WRITE:
            raise InputError("權限 %s:write 在本範本的拒絕清單內" % name)
    return perms


def check_api_url(url):
    parsed = urlparse(url)
    loopback = parsed.hostname in ("127.0.0.1", "localhost", "::1")
    if parsed.scheme != "https" and not (parsed.scheme == "http" and loopback):
        raise InputError("API URL 必須是 https（僅本機回送位址可用 http）")
    return url.rstrip("/")


def call_api(method, url, jwt, body=None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + jwt,
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": "app-installation-token-template",
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        try:
            message = json.loads(err.read().decode("utf-8")).get("message", "")
        except ValueError:
            message = ""
        print("HTTP %d：%s" % (err.code, str(message)[:200]), file=sys.stderr)
        sys.exit(3)
    except (urllib.error.URLError, OSError, TimeoutError) as err:
        print("連線失敗：%s" % type(err).__name__, file=sys.stderr)
        sys.exit(3)
    except ValueError:
        print("回應不是合法 JSON", file=sys.stderr)
        sys.exit(4)


def emit(token, github_output):
    if github_output:
        path = os.environ.get("GITHUB_OUTPUT")
        if not path:
            raise InputError("--github-output 只能在 GitHub Actions 內用（缺 GITHUB_OUTPUT）")
        print("::add-mask::" + token)  # 先遮罩再寫出，後續 log 會顯示 ***
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("%s=%s\n" % (github_output, token))
    elif sys.stdout.isatty():
        raise InputError("拒絕把 token 印到終端機；請用 $(...) 接住，或用 --github-output")
    else:
        sys.stdout.write(token + "\n")


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--installation-id", default=os.environ.get("GH_APP_INSTALLATION_ID"))
    parser.add_argument("--org", help="未給 installation id 時，用 GET /orgs/{org}/installation 查")
    parser.add_argument("--permissions", default="", help='縮小權限，例：{"organization_copilot_requests":"read"}')
    parser.add_argument("--repositories", default="", help="逗號分隔的 repo 名稱（不含 owner）")
    parser.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    parser.add_argument("--github-output", metavar="NAME", help="寫入 $GITHUB_OUTPUT 並先加遮罩")
    parser.add_argument("--dry-run", action="store_true", help="只簽出 JWT 並印出 claims，不連網")
    args = parser.parse_args(argv)
    try:
        n, e, d = load_rsa_private_key(os.environ.get("GH_APP_PRIVATE_KEY", ""))
        jwt = build_jwt(os.environ.get("GH_APP_CLIENT_ID", ""), n, d)
        if args.dry_run:
            claims = json.loads(base64.urlsafe_b64decode(jwt.split(".")[1] + "=="))
            print(json.dumps({"claims": claims, "jwt_chars": len(jwt), "key_bits": n.bit_length()}))
            return 0
        permissions = parse_permissions(args.permissions)
        repositories = [r for r in args.repositories.split(",") if r.strip()]
        base = check_api_url(args.api_url)
        installation_id = args.installation_id
        if not installation_id and args.org:
            found = call_api("GET", "%s/orgs/%s/installation" % (base, quote(args.org, safe="")), jwt)
            installation_id = str(found.get("id", ""))
        if not re.fullmatch(r"[0-9]+", installation_id or ""):
            raise InputError("需要數字的 installation id（--installation-id、GH_APP_INSTALLATION_ID 或 --org）")
        body = {}
        if permissions:
            body["permissions"] = permissions
        if repositories:
            body["repositories"] = [r.strip() for r in repositories]
        result = call_api("POST", "%s/app/installations/%s/access_tokens" % (base, installation_id), jwt, body)
        token = result.get("token") if isinstance(result, dict) else None
        if not isinstance(token, str) or not token.startswith("ghs_") or not result.get("expires_at"):
            print("回應缺少 ghs_ token 或 expires_at", file=sys.stderr)
            return 4
        granted = result.get("permissions") or {}
        if any(granted.get(name) != level for name, level in permissions.items()):
            print("回傳的權限沒有涵蓋要求的權限：%s" % json.dumps(granted), file=sys.stderr)
            return 4
        emit(token, args.github_output)
        print("token 有效至 %s；權限：%s" % (result["expires_at"], ",".join(sorted(result.get("permissions", {})))),
              file=sys.stderr)
        return 0
    except InputError as err:
        print("輸入錯誤：%s" % err, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
```

結束碼：0 成功；2 輸入或設定錯誤；3 網路或 HTTP 錯誤；4 回應格式不符。`--dry-run` 只簽 JWT 並印出 claims（不印 JWT 本身），不連網。

## 3. 檔案二：`.github/workflows/nightly-maintenance-agent.yml`

流程分成兩個 job，中間只傳一個 patch 檔：

```text
 job agent（視為不可信）                         job publish（新 runner、乾淨 checkout）
 ┌────────────────────────────────┐   patch    ┌──────────────────────────────────────────┐
 │ 領 Copilot 專用權杖（私鑰只在這  │  (artifact) │ git apply 套用 patch（不執行 repo 程式碼）│
 │ 一步，Agent 啟動前已結束）       │ ─────────► │ 爆破半徑關卡（檔數、禁止路徑、.git、連結） │
 │ 跑 Agent（改工作目錄）           │  只含工作樹 │ 停用 hook 的 commit（此時沒有任何 token） │
 │ git diff --binary 產 patch      │  變更的資料 │ 才領寫入權杖 → 推分支 → 開 Draft PR       │
 └────────────────────────────────┘            └──────────────────────────────────────────┘
```

**品質關卡（測試、lint）不在這個工作流裡跑。** 在有寫入憑證的環境裡執行 Agent 改過的程式碼，等於把憑證交給 Agent；所以測試改由 PR 觸發的 CI 跑（用 App token 開的 PR 會觸發 CI），並在主分支保護規則把那個 CI 設為必要檢查。若想在開 PR 前先跑，請另開一個 job：只給 `contents: read`、不放任何 secret、`needs: agent`、自己下載 patch 套用後跑測試，結果不影響 publish 以外的權限。

```yaml nightly-maintenance-agent.yml
name: nightly-maintenance-agent

on:
  schedule:
    - cron: "17 18 * * *" # UTC 18:17 = 台北 02:17；排程只在預設分支觸發，且可能延遲
  workflow_dispatch:
    inputs:
      issue_number:
        description: "指定要處理的 issue 編號（留空 = 取最舊的 ai-ready issue）"
        required: false
        type: string

permissions: {}

concurrency:
  group: nightly-maintenance-agent
  cancel-in-progress: false

jobs:
  # ---- Job 1：Agent 在這裡跑。它被視為不可信：只拿得到 Copilot 專用權杖，沒有 repo 寫入權杖 ----
  agent:
    if: github.repository == 'YOUR_ORG/YOUR_REPO'
    runs-on: ubuntu-latest
    timeout-minutes: 30
    permissions:
      contents: read
      issues: read
    outputs:
      has_patch: ${{ steps.patch.outputs.has_patch }}
      issue_number: ${{ steps.issue.outputs.number }}
    steps:
      - name: Check out (read-only, no persisted credentials)
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false

      - name: Select issue
        id: issue
        env:
          GH_TOKEN: ${{ github.token }}
          GH_REPO: ${{ github.repository }}
          INPUT_ISSUE: ${{ inputs.issue_number }}
        run: |
          set -euo pipefail
          number="$INPUT_ISSUE"
          if [ -z "$number" ]; then
            number=$(gh issue list --label ai-ready --state open --limit 1 \
              --search "sort:created-asc" --json number --jq '.[0].number // empty')
          fi
          if [ -z "$number" ]; then
            echo "found=false" >> "$GITHUB_OUTPUT"
            echo "沒有待處理的 ai-ready issue"
            exit 0
          fi
          [[ "$number" =~ ^[0-9]+$ ]] || { echo "issue 編號必須是數字" >&2; exit 1; }
          # issue 內容是不受信任的輸入：只存成檔案放在 workspace 之外，不內插進任何 shell 或 prompt 指令
          gh issue view "$number" --json number,title,body,labels > "$RUNNER_TEMP/issue.json"
          echo "found=true" >> "$GITHUB_OUTPUT"
          echo "number=$number" >> "$GITHUB_OUTPUT"

      # 私鑰只出現在這一步的環境變數，而且這一步在任何 Agent 程式碼執行之前就結束。
      # 之後的步驟（含 Agent）拿不到私鑰；Agent 啟動時這一步的行程已經不存在。
      - name: Mint Copilot-only installation token
        id: copilot
        if: steps.issue.outputs.found == 'true'
        env:
          GH_APP_CLIENT_ID: ${{ vars.APP_CLIENT_ID }}
          GH_APP_PRIVATE_KEY: ${{ secrets.APP_PRIVATE_KEY }}
          APP_ORG: ${{ github.repository_owner }}
        run: |
          python3 .github/scripts/app_installation_token.py \
            --org "$APP_ORG" \
            --permissions '{"organization_copilot_requests":"read"}' \
            --github-output copilot_token

      - name: Run agent (Copilot token only; no repo write credentials here)
        if: steps.issue.outputs.found == 'true'
        env:
          INSTALLATION_TOKEN: ${{ steps.copilot.outputs.copilot_token }}
        run: |
          # 換成你的 Agent 進入點：它要用 SDK 的 gitHubToken / github_token 選項讀 INSTALLATION_TOKEN，
          # 並設 useLoggedInUser: false（見指南第 4 節），從 "$RUNNER_TEMP/issue.json" 讀 issue，只改工作目錄裡的檔案。
          echo "尚未設定 Agent 指令：請替換這一步" >&2
          exit 1

      # 這一步仍在 Agent 的 job 裡，.git/ 可能已被 Agent 動過手腳，所以只把輸出當「資料」：
      # 關掉 fsmonitor、外部 diff 與 textconv。這一步沒有任何 secret；patch 到了 publish job 仍會被當成不可信輸入重新檢查。
      - name: Create patch (worktree changes only)
        id: patch
        if: steps.issue.outputs.found == 'true'
        run: |
          set -euo pipefail
          git -c core.fsmonitor=false add -A
          git -c core.fsmonitor=false diff --cached --binary --no-ext-diff --no-textconv > "$RUNNER_TEMP/agent.patch"
          if [ -s "$RUNNER_TEMP/agent.patch" ]; then
            echo "has_patch=true" >> "$GITHUB_OUTPUT"
          else
            echo "has_patch=false" >> "$GITHUB_OUTPUT"
            echo "Agent 沒有產生變更，結束"
          fi

      - name: Upload patch
        if: steps.patch.outputs.has_patch == 'true'
        uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2
        with:
          name: agent-patch
          path: ${{ runner.temp }}/agent.patch
          if-no-files-found: error
          retention-days: 3

  # ---- Job 2：新的 runner、乾淨 checkout。只處理 patch 這份「資料」，不執行 repo 裡的任何程式碼 ----
  publish:
    needs: agent
    if: needs.agent.outputs.has_patch == 'true'
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - name: Check out clean copy (no persisted credentials)
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false

      - name: Download patch
        uses: actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333 # v8.0.2
        with:
          name: agent-patch
          path: ${{ runner.temp }}/patch

      - name: Apply patch and blast radius gate
        env:
          PATCH_FILE: ${{ runner.temp }}/patch/agent.patch
          MAX_FILES: "10"
          MAX_PATCH_BYTES: "1048576"
          # 本範本的取捨：碰到這些路徑就拒絕；請依專案調整。.git 與 .gitattributes 任何層級都擋
          DENY_REGEX: '^\.github/|(^|/)\.git(/|$)|(^|/)\.gitattributes$|(^|/)\.gitmodules$|(^|/)Dockerfile$|(^|/)docker-compose[^/]*\.ya?ml$|\.tf$|\.tfvars$'
        run: |
          set -euo pipefail
          size=$(wc -c < "$PATCH_FILE")
          if [ "$size" -eq 0 ] || [ "$size" -gt "$MAX_PATCH_BYTES" ]; then
            echo "::error::patch 大小 $size 位元組不在 1..$MAX_PATCH_BYTES 範圍內" >&2
            exit 1
          fi
          # git apply 只寫工作樹與 index，不執行 hook，也不執行任何 repo 程式碼
          git apply --index "$PATCH_FILE"
          mapfile -d '' -t files < <(git diff --cached --no-renames --name-only -z)
          if [ "${#files[@]}" -eq 0 ]; then
            echo "::error::套用後沒有任何變更" >&2
            exit 1
          fi
          if [ "${#files[@]}" -gt "$MAX_FILES" ]; then
            echo "::error::變更 ${#files[@]} 個檔案，超過上限 $MAX_FILES" >&2
            exit 1
          fi
          if git diff --cached --no-renames --raw | grep -E '^:[0-7]+ (120000|160000) |^:(120000|160000) '; then
            echo "::error::patch 含符號連結或 submodule" >&2
            exit 1
          fi
          bad=$(printf '%s\n' "${files[@]}" | grep -E "$DENY_REGEX" || true)
          if [ -n "$bad" ]; then
            echo "::error::變更碰到禁止路徑" >&2
            printf '%s\n' "$bad" >&2
            exit 1
          fi
          echo "關卡通過：${#files[@]} 個檔案"

      # commit 不需要任何 token，所以這一步沒有 secret；並用 core.hooksPath=/dev/null 停用所有 hook
      - name: Commit with hooks disabled
        env:
          ISSUE_NUMBER: ${{ needs.agent.outputs.issue_number }}
          RUN_ID: ${{ github.run_id }}
          RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        run: |
          set -euo pipefail
          [[ "$ISSUE_NUMBER" =~ ^[0-9]+$ ]] || { echo "issue 編號必須是數字" >&2; exit 1; }
          git config user.name "nightly-maintenance-agent"
          git config user.email "nightly-maintenance-agent@users.noreply.github.com"
          git checkout -b "ai-agent/issue-${ISSUE_NUMBER}-${RUN_ID}"
          git -c core.hooksPath=/dev/null commit --no-verify \
            -m "fix: automated change for issue #${ISSUE_NUMBER}" -m "Generated by workflow run ${RUN_URL}"

      # 到這裡為止沒有領任何寫入權杖。以下才領 repo 範圍的權杖，之後不再執行任何來自 patch 的內容。
      - name: Mint repo-scoped installation token
        id: repo-token
        uses: actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510 # v3.3.0
        with:
          client-id: ${{ vars.APP_CLIENT_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}
          permission-contents: write
          permission-pull-requests: write
          permission-issues: write

      - name: Push branch and open draft PR
        env:
          GH_TOKEN: ${{ steps.repo-token.outputs.token }}
          GH_REPO: ${{ github.repository }}
          ISSUE_NUMBER: ${{ needs.agent.outputs.issue_number }}
          RUN_ID: ${{ github.run_id }}
          RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        run: |
          set -euo pipefail
          branch="ai-agent/issue-${ISSUE_NUMBER}-${RUN_ID}"
          base=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)
          # 用環境變數給 git 認證標頭並停用 hook，token 不出現在命令列或 .git/config
          export GIT_CONFIG_COUNT=2
          export GIT_CONFIG_KEY_0="http.https://github.com/.extraheader"
          export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"
          export GIT_CONFIG_KEY_1="core.hooksPath"
          export GIT_CONFIG_VALUE_1="/dev/null"
          git push origin "HEAD:refs/heads/$branch"
          gh label create ai-agent-generated --color BFD4F2 --description "Draft PR opened by the nightly agent" --force
          pr_url=$(gh pr create --draft --base "$base" --head "$branch" \
            --title "[AI-Agent-Generated] automated change for issue #${ISSUE_NUMBER}" \
            --label ai-agent-generated \
            --body "Refs #${ISSUE_NUMBER}. Opened as a draft by ${RUN_URL}. Tests have NOT run in this workflow; CI on this PR must pass and a human must review before merge. Revert with git revert on the merge commit if needed.")
          gh issue comment "$ISSUE_NUMBER" --body "Draft PR: ${pr_url}"
          echo "$pr_url"
```

### 3.1 設計重點

- **為什麼要拆兩個 job（一個已重現的漏洞）。** 若 Agent 與推送在同一個 job，Agent 可以寫入 `.git/hooks/pre-commit`；`git status` 與 `git diff --cached` 都看不到 `.git/` 內的變更，關卡照樣通過，之後帶著寫入權杖執行 `git commit` 時 hook 就跑起來，把環境變數裡的權杖寫走。拆開後 publish 在新的 runner 乾淨 checkout，`.git/` 不可能被 Agent 動過；patch 只是一份資料。測試用暫存 repo 重現了這個攻擊（見測試 `test_hook_attack_*`），並證明新流程拿不到權杖。
- **兩顆 token，各管一件事。** `actions/create-github-app-token` 目前的輸入沒有 Copilot Requests 這個權限（v3.3.0 的 `action.yml` 查不到），所以 Copilot 用的 token 由檔案一直接呼叫 REST API 領，且只要 `organization_copilot_requests: read`；寫入 repo 用的 token 由官方 action 領，且只要 `contents`、`pull-requests`、`issues` 的 write。
- **私鑰出現的位置。** publish job 的領權杖那一步一定有私鑰。agent job 也要領 Copilot 權杖，所以 agent job 的**第一個 Agent 之前的步驟**會用到私鑰；這一步是範本自己的腳本、在 Agent 程式碼啟動前就結束，之後的步驟（含 Agent）拿不到私鑰。官方 Workflow syntax 頁（2026-11-02 核對）寫明含機密的 job output 會在 runner 上被遮蔽、不會送給 GitHub Actions（本次未實際跑一次驗證），所以沒辦法再多拆一個只領權杖的 job。若你的威脅模型連這一步都不接受，請改用「Actions 內建 `GITHUB_TOKEN` 加 `copilot-requests: write`」那條路（指南第 5 節），它不需要私鑰。
- **issue 內容是不受信任的輸入。** 只存成檔案放在 `$RUNNER_TEMP`，不內插進 shell 或指令；`run:` 區塊內不使用 `${{ }}`，所有值都經 `env:` 傳入（GitHub 的安全強化文件建議用中間環境變數）。
- **預留的失敗點。** 「Run agent」預設 `exit 1`，沒替換就不會有 PR。這是刻意的：預設成功會讓空殼工作流看起來像在運作。
- **爆破半徑關卡**（publish job；`git apply` 本身也會拒絕寫進 `.git/` 的路徑，這裡是第二層）：patch 大小上限、變更檔數超過 `MAX_FILES`、碰到 `DENY_REGEX` 的路徑（預設含 `.github/`、任何層級的 `.git`、`.gitattributes`、`.gitmodules`、Dockerfile、docker-compose、Terraform）、符號連結或 submodule、或套用後沒有變更，都失敗。上限與路徑是本範本的取捨，不是 GitHub 的規定。
- **停用 hook**：commit 用 `git -c core.hooksPath=/dev/null commit --no-verify`，推送時也用環境變數把 `core.hooksPath` 設成 `/dev/null`；git 官方文件（git-config，`core.hooksPath`）就是用 `/dev/null` 說明如何停用 hook。commit 那一步沒有任何 token。
- **agent job 產生 patch 那一步**仍在 Agent 的 job 裡，`.git/config` 可能被改過（例如設定 filter 或 fsmonitor 讓 `git add` 執行指令）。範本關掉 fsmonitor、外部 diff、textconv，但不宣稱能完全擋住；這一步沒有任何 secret，最壞結果是 Agent 自己的 job 被它自己影響，patch 到 publish 仍會被重新檢查。
- **推送認證**：用 `GIT_CONFIG_*` 環境變數帶 `http.extraheader`，token 不出現在命令列或 `.git/config`；兩個 job 的 checkout 都是 `persist-credentials: false`。
- **用 App token 開 PR 的原因**：用 `GITHUB_TOKEN` 觸發的事件不會再觸發新的 workflow run（`workflow_dispatch`、`repository_dispatch` 例外），所以以 `GITHUB_TOKEN` 開的 PR 不會自動跑 CI；用 App token 開則會。
- **action 版本釘 SHA**：`actions/checkout` v7.0.1、`actions/create-github-app-token` v3.3.0、`actions/upload-artifact` v7.0.2、`actions/download-artifact` v8.0.2，皆釘在 commit SHA（2026-11-02 以 `gh api repos/.../commits/<tag>` 核對）。升級時重新核對 SHA，不要只改註解。
- **還需要在 repo 設定做的事**（工作流本身做不到）：主分支的保護規則要求 PR、至少一位真人 review 與 CI 必要檢查，且不要把這個 App 加進 bypass 名單；Actions 設定把 workflow 權限預設調成唯讀。

## 4. 本機乾跑（假私鑰，不連網）

私鑰只存在環境變數，不寫檔：

```bash
export GH_APP_CLIENT_ID="Iv1.fakeclientid0000"
export GH_APP_PRIVATE_KEY="$(openssl genrsa 2048 2>/dev/null)"
python3 .github/scripts/app_installation_token.py --dry-run
# 預期輸出一行 JSON：claims（iat、exp、iss）、jwt_chars、key_bits=2048；結束碼 0
unset GH_APP_PRIVATE_KEY
```

Windows PowerShell 沒有 `openssl` 時，可以在 Git Bash 裡跑上面這段。壞輸入會失敗：把 `GH_APP_PRIVATE_KEY` 設成空字串，或把 `GH_APP_CLIENT_ID` 設成含空白的字串，結束碼應為 2。

## 5. 這個範本沒有做到的事

- **Agent 本體不在範本內。** 「Run agent」是預留步驟。官方文件（查證日 2026-11-02）只給出建立 `CopilotClient` 並傳入 `gitHubToken`／`github_token` 與 `useLoggedInUser: false` 的範例；建立 session、送 prompt 的 API 本範本沒有逐一核對，請照 SDK 的 README 寫，標為**未驗證**。
- **工作流沒有在真實的 GitHub 上跑過。** 本範本的測試（`tests/test_github_app_s2s_template.py`）實跑了交換腳本（簽 JWT、對本機模擬伺服器換 token）、patch 產生、爆破半徑關卡與停用 hook 的 commit；整份 YAML 只做結構檢查（action 釘 SHA、`run:` 內無 `${{`、頂層 permissions 為空、agent 與 publish 分屬兩個 job、agent job 沒有寫入權杖），沒有在 Actions 上執行。第一次使用請先 `workflow_dispatch` 手動跑。
- **沒有提供 Bash 版。** 用 `openssl` 簽 JWT 時，私鑰要不落地就得靠行程替換（`<(...)`）；在我查證的 Windows Git Bash 環境，原生 openssl 讀不到 `/proc/<pid>/fd/*`，而本範本作者沒有 Linux 環境可實跑驗證，所以不放未跑過的腳本。Python 版同時支援 Linux、macOS、Windows。
- **純 Python RSA 簽章不是常數時間**，只適合一次性 runner；長駐服務請改用成熟的函式庫或雲端 KMS。
- **通知**：工作流失敗只會變紅燈；要推到 Slack、Telegram 等，請自行加步驟。
- **歷史上的 token 格式**：2026-04-27 起 GitHub 開始分階段把新 installation token 改成較長的無狀態格式（`ghs_APPID_JWT`），不要假設長度是 40 字元；本範本的檢查只看 `ghs_` 前綴。

## 6. 來源（皆於 2026-11-02 實際開啟並比對內容）

- [GitHub Copilot supports server-to-server authentication（Changelog，2026-10-27）](https://github.blog/changelog/2026-10-27-github-copilot-supports-server-to-server-authentication/)
- [Server-to-server authentication（Copilot SDK）](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/server-to-server-tokens)
- [Manage GitHub Apps that use your organization's Copilot](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/manage-app-copilot-access)
- [Generating a JSON Web Token (JWT) for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app)
- [Generating an installation access token for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)
- [Making authenticated API requests with a GitHub App in a GitHub Actions workflow](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow)
- [Authenticating as a GitHub App installation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation)（`x-access-token` 的 git 認證用法）
- [Triggering a workflow（GITHUB_TOKEN 不觸發新 run）](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow)
- [Security hardening for GitHub Actions（中間環境變數、釘 SHA）](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [actions/create-github-app-token v3.3.0](https://github.com/actions/create-github-app-token/tree/64ab729a6294000f5aa4a4bc0b73d1f32bc45510)（`action.yml` 與 README 於該 commit 讀取）
- [actions/checkout v7.0.1](https://github.com/actions/checkout/tree/3d3c42e5aac5ba805825da76410c181273ba90b1)
- [actions/upload-artifact v7.0.2](https://github.com/actions/upload-artifact/tree/cf430e030ddbb5b0abf93d22962f4752f3646cd9)、[actions/download-artifact v8.0.2](https://github.com/actions/download-artifact/tree/9000827ccba6bdab643e8b6fd33ac0654aef8333)
- [Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)（含機密的 job output 不會傳遞）
- [git-config：core.hooksPath](https://git-scm.com/docs/git-config)（以 `/dev/null` 停用 hook 的說明）、[git-apply](https://git-scm.com/docs/git-apply)
