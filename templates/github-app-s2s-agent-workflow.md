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

流程：挑一個 `ai-ready` issue → 只用 Copilot 專用 token 跑 Agent → 有變更才進關卡 → 通過後才領有寫入權限的 repo token → 推分支、開 Draft PR。

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

permissions:
  contents: read
  issues: read

concurrency:
  group: nightly-maintenance-agent
  cancel-in-progress: false

jobs:
  agent:
    if: github.repository == 'YOUR_ORG/YOUR_REPO'
    runs-on: ubuntu-latest
    timeout-minutes: 30
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

      - name: Detect changes
        id: detect
        if: steps.issue.outputs.found == 'true'
        run: |
          if [ -n "$(git status --porcelain)" ]; then
            echo "changed=true" >> "$GITHUB_OUTPUT"
          else
            echo "changed=false" >> "$GITHUB_OUTPUT"
            echo "Agent 沒有產生變更，結束"
          fi

      - name: Quality gate (tests / lint / typecheck)
        if: steps.detect.outputs.changed == 'true'
        run: |
          # 換成你專案的指令，例如：python -m unittest discover -s tests && python -m ruff check .
          # 任何一個非 0 都讓這一步失敗，後面的 push 與 PR 都不會執行。
          echo "尚未設定品質關卡指令：請替換這一步" >&2
          exit 1

      - name: Blast radius gate
        if: steps.detect.outputs.changed == 'true'
        env:
          MAX_FILES: "10"
          # 本範本的取捨：碰到這些路徑就拒絕；請依專案調整
          DENY_REGEX: '^\.github/|(^|/)Dockerfile$|(^|/)docker-compose[^/]*\.ya?ml$|\.tf$|\.tfvars$'
        run: |
          set -euo pipefail
          git add -A
          mapfile -t files < <(git diff --cached --name-only)
          if [ "${#files[@]}" -eq 0 ]; then
            echo "::error::沒有任何變更" >&2
            exit 1
          fi
          if [ "${#files[@]}" -gt "$MAX_FILES" ]; then
            echo "::error::變更 ${#files[@]} 個檔案，超過上限 $MAX_FILES" >&2
            exit 1
          fi
          bad=$(printf '%s\n' "${files[@]}" | grep -E "$DENY_REGEX" || true)
          if [ -n "$bad" ]; then
            echo "::error::變更碰到禁止路徑" >&2
            printf '%s\n' "$bad" >&2
            exit 1
          fi
          echo "關卡通過：${#files[@]} 個檔案"

      - name: Mint repo-scoped installation token
        id: repo-token
        if: steps.detect.outputs.changed == 'true'
        uses: actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510 # v3.3.0
        with:
          client-id: ${{ vars.APP_CLIENT_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}
          permission-contents: write
          permission-pull-requests: write
          permission-issues: write

      - name: Push branch and open draft PR
        if: steps.detect.outputs.changed == 'true'
        env:
          GH_TOKEN: ${{ steps.repo-token.outputs.token }}
          GH_REPO: ${{ github.repository }}
          ISSUE_NUMBER: ${{ steps.issue.outputs.number }}
          RUN_ID: ${{ github.run_id }}
          RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        run: |
          set -euo pipefail
          branch="ai-agent/issue-${ISSUE_NUMBER}-${RUN_ID}"
          base=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)
          git config user.name "nightly-maintenance-agent"
          git config user.email "nightly-maintenance-agent@users.noreply.github.com"
          git checkout -b "$branch"
          git commit -m "fix: automated change for issue #${ISSUE_NUMBER}" -m "Generated by workflow run ${RUN_URL}"
          # 用環境變數給 git 認證標頭，不把 token 放進命令列或 .git/config
          export GIT_CONFIG_COUNT=1
          export GIT_CONFIG_KEY_0="http.https://github.com/.extraheader"
          export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"
          git push origin "HEAD:refs/heads/$branch"
          gh label create ai-agent-generated --color BFD4F2 --description "Draft PR opened by the nightly agent" --force
          pr_url=$(gh pr create --draft --base "$base" --head "$branch" \
            --title "[AI-Agent-Generated] automated change for issue #${ISSUE_NUMBER}" \
            --label ai-agent-generated \
            --body "Refs #${ISSUE_NUMBER}. Opened as a draft by ${RUN_URL}. A human must review before merge; revert with git revert on the merge commit if needed.")
          gh issue comment "$ISSUE_NUMBER" --body "Draft PR: ${pr_url}"
          echo "$pr_url"
```

### 3.1 設計重點

- **兩顆 token，各管一件事。** `actions/create-github-app-token` 目前的輸入沒有 Copilot Requests 這個權限（v3.3.0 的 `action.yml` 查不到），所以 Copilot 用的 token 由檔案一直接呼叫 REST API 領，且只要 `organization_copilot_requests: read`；寫入 repo 用的 token 由官方 action 領，且只要 `contents`、`pull-requests`、`issues` 的 write。Agent 那一步拿不到寫入權限，通過關卡後才領 repo token。
- **issue 內容是不受信任的輸入。** 只存成檔案放在 `$RUNNER_TEMP`，不內插進 shell 或指令；`run:` 區塊內不使用 `${{ }}`，所有值都經 `env:` 傳入（GitHub 的安全強化文件建議用中間環境變數）。
- **兩個預留的失敗點。** 「Run agent」與「Quality gate」兩步預設 `exit 1`，沒替換就不會有 PR。這是刻意的：預設成功會讓空殼工作流看起來像在運作。
- **爆破半徑關卡**：變更檔數超過 `MAX_FILES`、碰到 `DENY_REGEX` 的路徑（預設含 `.github/`、Dockerfile、Terraform）、或根本沒有變更，都失敗。上限與路徑是本範本的取捨，不是 GitHub 的規定。
- **推送認證**：用 `GIT_CONFIG_*` 環境變數帶 `http.extraheader`，token 不出現在命令列或 `.git/config`；checkout 時 `persist-credentials: false`，Agent 那一步的工作目錄裡沒有任何憑證。
- **用 App token 開 PR 的原因**：用 `GITHUB_TOKEN` 觸發的事件不會再觸發新的 workflow run（`workflow_dispatch`、`repository_dispatch` 例外），所以以 `GITHUB_TOKEN` 開的 PR 不會自動跑 CI；用 App token 開則會。
- **action 版本釘 SHA**：`actions/checkout` 釘在 v7.0.1 的 commit，`actions/create-github-app-token` 釘在 v3.3.0 的 commit（2026-11-02 以 `gh api repos/.../commits/<tag>` 核對）。升級時重新核對 SHA，不要只改註解。
- **還需要在 repo 設定做的事**（工作流本身做不到）：主分支的保護規則要求 PR 與至少一位真人 review，且不要把這個 App 加進 bypass 名單；Actions 設定把 workflow 權限預設調成唯讀。

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
- **工作流沒有在真實的 GitHub 上跑過。** 本範本的測試（`tests/test_github_app_s2s_template.py`）實跑了兩支腳本（簽 JWT、對本機模擬伺服器換 token）與爆破半徑關卡；整份 YAML 只做結構檢查（action 釘 SHA、`run:` 內無 `${{`、頂層 permissions 最小），沒有在 Actions 上執行。第一次使用請先 `workflow_dispatch` 手動跑。
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
