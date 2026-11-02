#!/usr/bin/env python3
"""
tools/audit_oauth_credentials.py
審查本機 AI 工具（Grok CLI、Codex、Claude Code）的 OAuth 憑證檔「放得安不安全」。唯讀，不改任何檔案。

只看 metadata：檔案位置、權限／ACL、是否被 git 追蹤或未被忽略、有哪些「憑證欄位名稱」存在、
設定檔是否讓本機代理監聽在外部網卡。**絕不輸出 token、金鑰、密碼的內容**（但檔案路徑會照印：家目錄底下顯示成 ~/...，
其他位置顯示完整路徑；貼出報告前，請自行檢查路徑裡有沒有不想公開的帳號或資料夾名稱）：
  - 內容只用來判斷「某欄位是否有非空的明文值」，值在判斷完就丟棄，不進任何 Finding；
  - 輸出只會出現固定詞彙的欄位類別（refresh_token、access_token、api_key……），不回顯檔案裡原本的鍵名；
  - 監聽位址只在能被解析成 IP 時才印出（IPv6 的 %scope 先去掉），其餘一律印固定說明文字。
檔案編碼：依 BOM 解碼 UTF-8／UTF-16／UTF-32（PowerShell 5 的 > 預設寫 UTF-16）。
  無 BOM 時：UTF-8 內容夾帶大量 NUL（尾端、前端皆可）仍會掃到；無 BOM 的 UTF-16 只在欄位名稱與值是 ASCII 時掃得到。
  **已知限制（會漏報）**：無 BOM 的 UTF-16 若內容以中文等非 ASCII 字元為主（NUL 不到四分之一），或無 BOM 的 UTF-32，
  都會被當成 UTF-8 而掃不到憑證欄位；PowerShell 5 的 > 與 Out-File 會寫 BOM，不屬於這種情況。
本工具也不讀取或呼叫任何遠端服務，不嘗試使用憑證。

預設掃描（各目錄的第一層檔案，加上 oauth-proxy/ 子資料夾；不遞迴 sessions 之類的大目錄）：
  ~/.grok/   ~/.codex/（或 CODEX_HOME）   ~/.claude/（或 CLAUDE_CONFIG_DIR）
  --home 指定時不讀環境變數，只看 <home>/.grok、.codex、.claude；--dir 可再加目錄。

檢查項目（ERROR 一定失敗；WARN 預設只提醒，加 --strict 才失敗；INFO 不影響結束碼）：
    ERROR  perm-loose        POSIX：含明文憑證欄位的檔案，群組或其他人有任何權限（應為 0600 或更嚴）
    ERROR  acl-broad         Windows：含明文憑證欄位的檔案，ACL 授權給 Everyone／Users／Guests／Authenticated Users／Domain Users 等
    ERROR  git-tracked       憑證檔已被 git 追蹤（在 git 工作樹內且已 add／commit）
    ERROR  listen-exposed    設定檔的 bind／listen 設成萬用位址（0.0.0.0、::、空主機）或非 loopback IP
    ERROR  git-tracked-credential  --repo 指定的 repo 裡，追蹤了含明文憑證欄位的 auth.json 之類檔案
    WARN   plaintext-token   檔案內有非空的明文憑證欄位（Codex、Claude Code 的預設就是明文檔，這是提醒不是故障）
    WARN   perm-loose / acl-broad  同上，但檔案名稱像憑證檔、卻沒找到明文欄位時降為 WARN
    WARN   git-not-ignored   憑證檔在 git 工作樹內，沒被追蹤但也沒被 .gitignore 忽略（git add -A 就會收進去）
    WARN   backup-copy       憑證檔的備份副本（.bak、.old、~ 之類）仍含明文欄位
    WARN   listen-unknown-host  bind／listen 是非 IP 的主機名稱（非 localhost），無法判斷是否對外
    WARN   listen-port-only  bind／listen 只有連接埠、沒指定主機
    WARN   git-tracked-credential  --repo 內追蹤了名稱像憑證檔的檔案，但沒找到明文欄位
    INFO   git-unknown / skipped-large / acl-unreadable  無法判斷或略過的原因

用法：
    python tools/audit_oauth_credentials.py [--home DIR] [--dir DIR ...] [--repo DIR ...] [--json] [--strict]
結束碼：0 通過；1 有 ERROR（或 --strict 且有 WARN）；2 參數錯誤。
只使用 Python 標準函式庫；ACL 檢查在 Windows 上呼叫內建的 icacls，git 檢查呼叫 git（不在 PATH 就降為 INFO）。
"""

from __future__ import annotations

import argparse
import fnmatch
import ipaddress
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

DEFAULT_DIRS = (".grok", ".codex", ".claude")
PROXY_SUBDIR = "oauth-proxy"
MAX_BYTES = 1024 * 1024
CREDENTIAL_GLOBS = ("auth*.json*", "*credentials*.json*", "oauth*.json*")
SCAN_SUFFIXES = (".json", ".toml", ".yaml", ".yml", ".env")
BACKUP_RE = re.compile(r"(?:\.(?:bak|old|orig|save|backup|copy|tmp)(?:\.|$)|~$)", re.I)

# 憑證欄位：正規化（camelCase 轉 snake_case、小寫）後比對；輸出只會用這裡定義的類別名稱。
_TOKEN_KEY = re.compile(
    r"(?:^|_)(?:(?P<kind>access_token|refresh_token|id_token|auth_token|session_token|bearer_token|oauth_token|"
    r"api_key|apikey|client_secret|secret_key)|(?P<bare>token))$"
)
_KV = re.compile(
    r"""["']?(?P<key>[A-Za-z_][A-Za-z0-9_.\-]{0,63})["']?[ \t]*[:=][ \t]*"""
    r"""(?P<val>"(?:[^"\\\n]|\\.)*"|'[^'\n]*'|"[^"\n]+|[^\s,}\]\[{"'#;]+)"""
)
_PLACEHOLDER_WORDS = {"null", "none", "true", "false", "nil", "undefined", "redacted", "changeme", "ollama"}

# 監聽欄位：bind／listen 系列（A 類）看到非 loopback 就算對外；host／hostname（B 類）只在萬用位址時才算。
_LISTEN_A = re.compile(r"(?:^|_)(?:bind|listen)(?:_?(?:addr|address|host|ip))?$")
_LISTEN_B = re.compile(r"^(?:host|hostname|proxy_host)$")

# icacls 輸出裡代表「很多人」的主體（英文名稱與 well-known SID）：Everyone、Users、Guests、Authenticated Users、
# Anonymous Logon、<網域>\Domain Users／Domain Guests，以及對應的 SID。非英文版 Windows 的本地化名稱不在清單內（已知限制），
# 但 SID 形式的輸出仍會比對到。
_BROAD_WHO = (
    r"everyone|builtin\\users|builtin\\guests|nt authority\\authenticated users|nt authority\\anonymous logon"
    r"|[\w.-]+\\domain users|[\w.-]+\\domain guests"
    r"|s-1-1-0|s-1-5-7|s-1-5-11|s-1-5-32-54[56]|s-1-5-21-[\d-]+-51[34]"
)
# 不去猜「檔案路徑在哪裡結束」：直接找「很多人」的主體後面緊接 :(權限)。
# icacls 第一行是「路徑 主體:(權限)」；路徑含中文時，輸出編碼若沒解對，路徑前綴會是亂碼，但不影響這個比對。
_BROAD_ACE = re.compile(r"(?<![\w\\.-])(?P<who>" + _BROAD_WHO + r")[ \t]*:(?P<rights>(?:\([^)\r\n]*\))+)", re.I)


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


class Finding:
    def __init__(self, level: str, code: str, file: str, msg: str):
        self.level, self.code, self.file, self.msg = level, code, file, msg

    def as_dict(self) -> dict:
        return {"level": self.level, "code": self.code, "file": self.file, "message": self.msg}

    def __str__(self) -> str:
        return f"{self.level:5} {self.code:22} {self.file}  {self.msg}"


# ---------------------------------------------------------------- 內容解析（只回傳類別與旗標，不回傳值）


def decode_text(raw: bytes) -> str:
    """依 BOM 解碼（UTF-8／UTF-16／UTF-32）。沒有 BOM、但空位元組（NUL）很多時無法確定是 UTF-16 還是夾了 NUL 的 UTF-8，
    所以不猜，直接把 NUL 全部拿掉再當 UTF-8 讀：
    UTF-8 內容後面接了一大段 NUL（預先配置或寫入中斷的檔案）、前面墊了二進位垃圾，都仍然掃得到；
    無 BOM 的 UTF-16 只要欄位名稱與值是 ASCII，拿掉 NUL 後就是原文，也掃得到。其餘當 UTF-8（壞位元組換成替代字元）。
    PowerShell 5 的 > 與 Out-File 預設寫 UTF-16LE 加 BOM，若當 UTF-8 讀，每個字元中間都夾著空字元，什麼都比對不到。"""
    if raw.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
        return raw.decode("utf-32", "replace")
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16", "replace")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig", "replace")
    text = raw.decode("utf-8", "replace")
    if len(raw) >= 4 and (raw[1::2].count(0) > len(raw) // 4 or raw[0::2].count(0) > len(raw) // 4):
        return text.replace("\x00", "")
    return text


def _normalize_key(key: str) -> str:
    key = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", key)
    return re.sub(r"[-.]", "_", key).lower()


def _looks_secret(value: str) -> bool:
    """非空、不是環境變數參照或佔位字樣、長度夠長，才當作「明文值」。回傳布林，值本身不外流。"""
    v = value.strip().strip("\"'")
    if len(v) < 12:
        return False
    low = v.lower()
    if low in _PLACEHOLDER_WORDS or v.startswith(("$", "%", "<", "{{")) or low.startswith(("env:", "file:", "keyring:")):
        return False
    return True


def token_kinds(text: str) -> list[str]:
    """回傳文字中「有非空明文值」的憑證欄位類別（去重排序）。只回類別名，不回值也不回原鍵名。"""
    kinds: set[str] = set()
    for m in _KV.finditer(text):
        m_key = _TOKEN_KEY.search(_normalize_key(m.group("key")))
        if not m_key:
            continue
        if _looks_secret(m.group("val")):
            kinds.add(m_key.group("kind") or "token")
    return sorted(kinds)


def _host_part(value: str) -> str | None:
    """從 'http://0.0.0.0:80/v1'、'[::1]:80'、':8080'、'10.0.0.5' 取出主機；取不出來回 None。空字串代表「未指定主機」。"""
    v = value.strip().strip("\"'")
    v = re.sub(r"^[A-Za-z][A-Za-z0-9+.\-]*://", "", v)
    v = v.split("/", 1)[0]
    if v.startswith("["):
        end = v.find("]")
        return v[1:end] if end > 0 else None
    if v.count(":") == 1:
        v = v.split(":", 1)[0]
    elif v.count(":") > 1:
        return v  # 裸 IPv6，例如 ::
    return v


def _without_comment_lines(text: str) -> str:
    """去掉整行註解（# 、// 、; 開頭）。只用在監聽設定：被註解掉的 bind 不是現行設定。
    憑證欄位不套用——註解掉的明文 token 一樣躺在磁碟上。"""
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith(("#", "//", ";")))


def listen_issues(text: str) -> list[tuple[str, str, str]]:
    """回傳 [(level, code, 說明)]。說明只含固定文字，或能被 ipaddress 解析的 IP（不含 IPv6 的 %scope）。"""
    out: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for m in _KV.finditer(_without_comment_lines(text)):
        key = _normalize_key(m.group("key"))
        family_a = bool(_LISTEN_A.search(key))
        if not family_a and not _LISTEN_B.match(key):
            continue
        host = _host_part(m.group("val"))
        if host is None:
            continue
        label: str | None = None
        level, code = "ERROR", "listen-exposed"
        if "%" in host:  # IPv6 zone id（fe80::1%eth0）：scope 是任意字串，一律丟掉，只留位址本身
            host = host.split("%", 1)[0]
            if not host:
                continue
        if host == "":
            if family_a:
                label = "未指定主機（多數執行環境等同監聽所有網卡）"
        elif host.isdigit():
            if family_a:
                level, code = "WARN", "listen-port-only"
                label = "只指定了連接埠、沒有指定主機；是否綁定所有網卡取決於程式，請確認"
        else:
            try:
                ip = ipaddress.ip_address(host)
            except ValueError:
                ip = None
            if ip is not None:
                if ip.is_unspecified:
                    label = f"萬用位址 {ip}，所有網卡都可連入"
                elif family_a and not ip.is_loopback:
                    label = f"非 loopback 位址 {ip}"
            elif family_a and host.lower() not in {"localhost", "localhost.localdomain"}:
                level, code = "WARN", "listen-unknown-host"
                label = "bind／listen 設成非 IP 的主機名稱，無法判斷是否對外"
        if label and (code, label) not in seen:
            seen.add((code, label))
            out.append((level, code, label))
    return out


# ---------------------------------------------------------------- Windows ACL


def broad_principals_in_icacls(text: str, path: str = "") -> list[str]:
    """從 icacls 輸出找出被授權（非 DENY）的「很多人」主體。path 若出現在輸出裡會先剝掉（沒找到也沒關係）。"""
    if path:
        idx = text.lower().find(path.lower())
        if idx >= 0:
            text = text[:idx] + " " + text[idx + len(path):]
    found: list[str] = []
    for m in _BROAD_ACE.finditer(text):
        if "(deny)" in m.group("rights").lower():
            continue
        who = m.group("who")
        if who.lower() not in (f.lower() for f in found):
            found.append(who)
    return found


def oem_encoding() -> str:
    """icacls 等主控台程式用 OEM 碼頁輸出（zh-TW 是 cp950）。取不到就退回 utf-8。"""
    try:
        import ctypes

        cp = ctypes.windll.kernel32.GetOEMCP()  # type: ignore[attr-defined]
        name = f"cp{cp}"
        "".encode(name)
        return name
    except Exception:  # 非 Windows、ctypes 不可用、碼頁 Python 不認得
        return "utf-8"


def _read_icacls(path: Path) -> str | None:
    try:
        proc = subprocess.run(["icacls", str(path)], capture_output=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.decode(oem_encoding(), "replace")


# ---------------------------------------------------------------- git


def _git(args: list[str], cwd: Path) -> tuple[int, str, str] | None:
    env = {**os.environ, "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0"}
    try:
        proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, timeout=20, env=env)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")


def git_state(path: Path) -> str:
    """回傳 'no-repo'｜'tracked'｜'ignored'｜'not-ignored'｜'unknown'。"""
    inside = _git(["rev-parse", "--is-inside-work-tree"], path.parent)
    if inside is None:
        return "unknown"
    rc, out, err = inside
    if rc != 0:
        return "no-repo" if "not a git repository" in err.lower() else "unknown"
    if out.strip() != "true":
        return "no-repo"
    tracked = _git(["ls-files", "--error-unmatch", "--", path.name], path.parent)
    if tracked is None:
        return "unknown"
    if tracked[0] == 0:
        return "tracked"
    ignored = _git(["check-ignore", "-q", "--", path.name], path.parent)
    if ignored is None or ignored[0] not in (0, 1):
        return "unknown"
    return "ignored" if ignored[0] == 0 else "not-ignored"


# ---------------------------------------------------------------- 審查


def is_credential_name(name: str) -> bool:
    low = name.lower()
    return any(fnmatch.fnmatchcase(low, g) for g in CREDENTIAL_GLOBS)


def candidate_dirs(home: Path, env: dict[str, str] | None) -> list[Path]:
    """預設目錄；env 不為 None 時再加上 CODEX_HOME、CLAUDE_CONFIG_DIR（兩者都是對應工具文件寫明的設定目錄變數）。"""
    dirs = [home / d for d in DEFAULT_DIRS]
    if env is not None:
        for var in ("CODEX_HOME", "CLAUDE_CONFIG_DIR"):
            if env.get(var):
                dirs.append(Path(env[var]).expanduser())
    unique: list[Path] = []
    for d in dirs:
        if d not in unique:
            unique.append(d)
    return unique


def display_path(path: Path, home: Path) -> str:
    try:
        rel = path.resolve().relative_to(home.resolve())
        return "~/" + rel.as_posix()
    except (ValueError, OSError):
        return path.as_posix()


def _files_to_scan(directory: Path) -> list[Path]:
    files: list[Path] = []
    for base in (directory, directory / PROXY_SUBDIR):
        if not base.is_dir():
            continue
        for p in sorted(base.iterdir(), key=lambda x: x.name):
            if not p.is_file():
                continue
            low = p.name.lower()
            if is_credential_name(p.name) or low.endswith(SCAN_SUFFIXES) or low.startswith(".env"):
                files.append(p)
    return files


def audit_file(
    path: Path,
    home: Path,
    *,
    is_windows: bool,
    icacls: Callable[[Path], str | None],
    git_check: Callable[[Path], str],
) -> tuple[list[Finding], dict]:
    shown = display_path(path, home)
    findings: list[Finding] = []
    info = {"token_fields": []}
    try:
        st = path.stat()
        if st.st_size > MAX_BYTES:
            return [Finding("INFO", "skipped-large", shown, f"檔案超過 {MAX_BYTES // 1024} KB，略過內容檢查")], info
        text = decode_text(path.read_bytes())
    except OSError as exc:
        return [Finding("INFO", "unreadable", shown, f"讀不到檔案（{type(exc).__name__}）")], info

    kinds = token_kinds(text)
    info["token_fields"] = kinds
    cred_named = is_credential_name(path.name)

    if kinds:
        findings.append(
            Finding("WARN", "plaintext-token", shown, f"含明文憑證欄位：{', '.join(kinds)}（只列欄位類別，不列值）；工具支援時優先改用 OS 憑證庫")
        )
        if BACKUP_RE.search(path.name):
            findings.append(Finding("WARN", "backup-copy", shown, "這是憑證檔的備份副本，仍含明文欄位；確認不再需要後請維護者自行處理"))

    if kinds or cred_named:
        level = "ERROR" if kinds else "WARN"
        if is_windows:
            out = icacls(path)
            if out is None:
                findings.append(Finding("INFO", "acl-unreadable", shown, "icacls 無法讀取 ACL，未檢查"))
            else:
                broad = broad_principals_in_icacls(out, str(path))
                if broad:
                    findings.append(
                        Finding(level, "acl-broad", shown, f"ACL 授權給：{', '.join(broad)}；請移除，僅留擁有者（以及 SYSTEM、Administrators）")
                    )
        else:
            mode = st.st_mode & 0o777
            if mode & 0o077:
                findings.append(Finding(level, "perm-loose", shown, f"權限 {mode:04o}，群組或其他人可存取；應為 0600 或更嚴"))
        state = git_check(path)
        if state == "tracked":
            findings.append(Finding("ERROR", "git-tracked", shown, "已被 git 追蹤；先 git rm --cached 並更換（revoke／重新登入）憑證，歷史也要清"))
        elif state == "not-ignored":
            findings.append(Finding("WARN", "git-not-ignored", shown, "在 git 工作樹內且未被 .gitignore 忽略，git add -A 會把它收進去"))
        elif state == "unknown":
            findings.append(Finding("INFO", "git-unknown", shown, "無法判斷 git 狀態（沒有 git，或 git 拒絕存取該資料夾）"))

    for level, code, label in listen_issues(text):
        findings.append(Finding(level, code, shown, label))
    return findings, info


def audit_repo(repo: Path) -> list[Finding]:
    """--repo：列出被追蹤的檔案，找名稱像憑證檔的；有明文欄位是 ERROR，只有名稱是 WARN。"""
    shown = repo.as_posix()
    res = _git(["ls-files", "-z"], repo)
    if res is None or res[0] != 0:
        return [Finding("INFO", "git-unknown", shown, "無法列出該 repo 的追蹤檔（不是 git repo，或沒有 git）")]
    out: list[Finding] = []
    for rel in sorted(n for n in res[1].split("\0") if n):
        if not is_credential_name(Path(rel).name):
            continue
        target = repo / rel
        kinds: list[str] = []
        try:
            if target.is_file() and target.stat().st_size <= MAX_BYTES:
                kinds = token_kinds(decode_text(target.read_bytes()))
        except OSError:
            pass
        if kinds:
            out.append(Finding("ERROR", "git-tracked-credential", f"{shown}::{rel}", f"被追蹤且含明文憑證欄位：{', '.join(kinds)}（只列類別）"))
        else:
            out.append(Finding("WARN", "git-tracked-credential", f"{shown}::{rel}", "被追蹤的檔案名稱像憑證檔，沒找到明文欄位，請人工確認"))
    return out


def audit(
    home: Path,
    dirs: list[Path],
    repos: list[Path] | None = None,
    *,
    is_windows: bool | None = None,
    icacls: Callable[[Path], str | None] = _read_icacls,
    git_check: Callable[[Path], str] = git_state,
) -> tuple[list[Finding], dict]:
    win = (sys.platform == "win32") if is_windows is None else is_windows
    findings: list[Finding] = []
    stats = {"dirs_found": 0, "files_scanned": 0, "files_with_token_fields": 0}
    for d in dirs:
        if not d.is_dir():
            continue
        stats["dirs_found"] += 1
        for f in _files_to_scan(d):
            stats["files_scanned"] += 1
            file_findings, info = audit_file(f, home, is_windows=win, icacls=icacls, git_check=git_check)
            findings.extend(file_findings)
            if info["token_fields"]:
                stats["files_with_token_fields"] += 1
    for repo in repos or []:
        findings.extend(audit_repo(repo))
    return findings, stats


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="審查本機 AI 工具（Grok CLI、Codex、Claude Code）的 OAuth 憑證檔位置、權限與 git 狀態（唯讀，絕不輸出 token 內容）。"
    )
    ap.add_argument("--home", help="家目錄（預設為目前使用者；指定時不讀 CODEX_HOME、CLAUDE_CONFIG_DIR）")
    ap.add_argument("--dir", action="append", default=[], metavar="DIR", help="再多掃描的目錄（可重複）")
    ap.add_argument("--repo", action="append", default=[], metavar="DIR", help="檢查該 git repo 是否追蹤了憑證檔（可重複）")
    ap.add_argument("--strict", action="store_true", help="WARN 也算失敗")
    ap.add_argument("--json", action="store_true", help="輸出 JSON")
    return ap


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    args = build_parser().parse_args(argv)
    if args.home:
        home = Path(args.home)
        if not home.is_dir():
            print(f"錯誤：不是資料夾：{home}", file=sys.stderr)
            return 2
        env = None
    else:
        home = Path.home()
        env = dict(os.environ)
    extra_dirs = [Path(d) for d in args.dir]
    for d in extra_dirs:
        if not d.is_dir():
            print(f"錯誤：--dir 不是資料夾：{d}", file=sys.stderr)
            return 2
    dirs = candidate_dirs(home, env) + extra_dirs
    repos = [Path(r) for r in args.repo]
    for r in repos:
        if not r.is_dir():
            print(f"錯誤：不是資料夾：{r}", file=sys.stderr)
            return 2
    findings, stats = audit(home, dirs, repos)
    errors = sum(f.level == "ERROR" for f in findings)
    warns = sum(f.level == "WARN" for f in findings)
    by_code: dict[str, int] = {}
    for f in findings:
        by_code[f.code] = by_code.get(f.code, 0) + 1
    if args.json:
        print(
            json.dumps(
                {"stats": stats, "errors": errors, "warnings": warns, "by_code": by_code, "findings": [f.as_dict() for f in findings]},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for f in findings:
            print(f)
        if not stats["files_scanned"]:
            print("未發現任何可審查的憑證或設定檔（沒有 .grok、.codex、.claude 目錄，或裡面沒有 json／toml／yaml／env 檔）")
        print(
            f"掃描目錄 {stats['dirs_found']} 個、檔案 {stats['files_scanned']} 個（含明文憑證欄位 {stats['files_with_token_fields']} 個）；"
            f"ERROR {errors}、WARN {warns}" + (f"（{', '.join(f'{k}={v}' for k, v in sorted(by_code.items()))}）" if by_code else "")
        )
    if errors or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
