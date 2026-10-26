#!/usr/bin/env python3
"""
tools/screen_privacy.py
多模態 Agent 截圖／OCR 隱私規範的參考實作（規範：docs/multimodal-screen-privacy-spec.md）。

三層防護中，本檔實作可跨平台、純文字的部分：
- 第一層：normalize_title / sanitize_title / classify_window（blocked / self / nocap / ok）
- 第三層：inspect_ocr_text（命中機密即丟）/ redact_text（機密與 PII 脫敏）
第二層（Windows UIA 無障礙樹探測）需要 COM，平台相依，不在此提供。

本檔的正則常數是規範的唯一正本：文件與程式不一致時以程式為準。
只使用 Python 標準函式庫。
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------
# 第 2 節：標題正規化與清洗
# --------------------------------------------------------------------------

_LEADING_MARKS = re.compile(r"^(?:[⠀-⣿✳✻✽✶✢·◐◓◑◒◴◵◶◷⏺●○•]+\s*)+")
_NOTIFY_COUNT = re.compile(r"^\(\d+\+?\)\s*")
# 只留主機名：授權段（user:pass@）、沒有路徑時緊接在主機後的 ?query／#fragment 都是機密
_URL = re.compile(r"(?:https?|ftps?|wss?|sftp|ssh)://([^\s/?#]+)\S*", re.IGNORECASE)
_STRIP = re.compile(r"[`<>|{}\\]")
_WS = re.compile(r"\s+")
_SCHEME = re.compile(
    r"\b(?:javascript|vbscript|file):|\bdata:(?=[\w.+-]+/[\w.+-]+[;,])", re.IGNORECASE
)
_INVISIBLE_CATEGORIES = ("Cc", "Cf", "Co", "Cn")


def normalize_title(title: str) -> str:
    """消除視窗動態前綴（轉圈動畫、未存檔標記、通知計數）。"""
    t = (title or "").strip()
    for _ in range(3):
        t2 = _NOTIFY_COUNT.sub("", _LEADING_MARKS.sub("", t))
        if t2 == t:
            break
        t = t2
    return t.strip()


def sanitize_title(text: str, limit: int = 160) -> str:
    """過濾不可見字元、危險 Scheme 與控制符號，截斷長度。"""
    clean = _drop_invisible(text, keep="\n\t")
    clean = _URL.sub(lambda m: f"[網址:{m.group(1).rsplit('@', 1)[-1]}]", clean)
    clean = _SCHEME.sub("[連結]:", clean)
    clean = _STRIP.sub("", clean)
    clean = _WS.sub(" ", clean).strip()
    return clean[:limit]


def _drop_invisible(text: str, keep: str = "") -> str:
    """去除控制字元 (Cc)、格式字元 (Cf: 零寬/雙向覆寫)、私用區 (Co)、未指派碼位 (Cn)。"""
    return "".join(
        ch for ch in (text or "") if ch in keep or unicodedata.category(ch) not in _INVISIBLE_CATEGORIES
    )


# --------------------------------------------------------------------------
# 第 3 節：視窗分類常數（blocked）
# --------------------------------------------------------------------------

BLOCKED_APPS = frozenset({
    "1password.exe", "bitwarden.exe", "keepass.exe", "keepassxc.exe", "lastpass.exe",
    "dashlane.exe", "proton pass.exe", "enpass.exe", "com.1password.1password",
    "com.agilebits.onepassword7", "com.bitwarden.desktop", "org.keepassxc.keepassxc",
    "com.apple.keychainaccess", "com.apple.passwords", "me.proton.pass.electron",
    "in.sinew.enpass-desktop",
})

# A. 醫療與病歷。bare `\bclinic\b` 已收斂為 `clinic records/chart/portal`（否則 "Mayo Clinic" 新聞頁整個被擋）。
TITLE_MEDICAL = (
    r"(?i)(?:病歷|病例|病患|患者|病人|個案管理|健保|掛號|門診|處方|檢驗報告|診斷書|診斷證明"
    r"|病历|医保|挂号|门诊|处方|检验报告|诊断书|诊断证明"
    r"|カルテ|診療録|処方箋|診察券|検査結果|환자|진료|처방전|의무기록|진단서"
    r"|\bpatients?\b|medical records?|\bEHR\b|\bclinic (?:records?|charts?|portal)\b"
    r"|\bdiagnos[ie]s\b|\bprescriptions?\b"
    r"|\bpaciente\b|historia clínica|historial médico|receta médica|dossier médical"
    r"|ordonnance médicale|Patientenakte|Krankenakte|Arztbrief|prontuário|receita médica)"
)

# B. 無痕與私密瀏覽視窗標題
TITLE_PRIVATE_BROWSING = (
    r"(?i)(?:\bInPrivate\b|\bIncognito\b|無痕|无痕|\(シークレット\)"
    r"|シークレット ?(?:ウィンドウ|モード)|시크릿 ?(?:모드|창)|incógnito|Inkognito"
    r"|navigation privée|navigazione anonima|navegación privada|navegação privada"
    r"|Private Browsing|私密瀏覽|隱私瀏覽|隐私浏览|privates Fenster|Приватн|Инкогнито)"
)

# C. 密碼管理器標題
TITLE_PASSWORD_MANAGER = (
    r"(?i)(?:1Password|Bitwarden|KeePass|LastPass|Dashlane|Password Manager"
    r"|密碼管理|密码管理|パスワード ?マネージャー|비밀번호 관리자)"
)

# D. 網路銀行與金融交易平台
TITLE_BANKING = (
    r"(?i)(?:網路銀行|網銀|网上银行|网银|ネットバンキング|インターネットバンキング|인터넷뱅킹"
    r"|\b(?:internet|online) banking\b|banca (?:en línea|online)|banque en ligne|Online-Banking"
    r"|internet banking)"
)

# E. 成人與限制級內容標題
TITLE_ADULT = (
    r"(?i)(?:\bporn\b|\bnsfw\b|\bhentai\b|\bjav\b|\bmilf\b|onlyfans|fansly|pornhub|xvideos"
    r"|xhamster|xnxx|redtube|youporn|spankbang|chaturbate|stripchat|missav|javdb|javbus"
    r"|rule34|e-hentai|nhentai"
    r"|成人(?:影片|網站|論壇|動漫|漫畫|直播|网站|论坛|动漫|漫画)"
    r"|色情|情色|18禁|十八禁|無碼|无码|有碼|有码|av女優|啪啪|自慰|痴女|巨乳|做愛|做爱"
    r"|性愛|性爱|約炮|约炮|裸聊|エロ|アダルト|無修正|야동|포르노|19금|섹스)"
)

# F. 機密檔名。分兩條，取捨見文件 3.2 節 F：
#   - TITLE_SECRET_FILE_ANYWHERE：只對編輯器／檔案總管類應用，標題任何位置出現都阻斷。
#   - TITLE_SECRET_FILE_AT_END：任何應用，但標題第一段（" - " 之前）必須不含空白、且「以」該檔名結尾，
#     例如 "server.pem - Notepad"、瀏覽器顯示原始檔的分頁（標題是檔名或網址）；
#     "How to read a .pem file - Chrome" 第一段含空白，不會中。
TITLE_SECRET_FILE_ANYWHERE = (
    r"(?i)(?:(?:^|[\s\\/])\.env(?:\.[\w-]+)?\b|credentials?\.json"
    r"|secrets?\.(?:json|ya?ml|toml)|\.pem\b|\bid_rsa\b|\.pfx\b|\.p12\b)"
)
TITLE_SECRET_FILE_AT_END = (
    r"(?i)(?:(?:^|[\s\\/])\.env(?:\.[\w-]+)?|credentials?\.json"
    r"|secrets?\.(?:json|ya?ml|toml)|\bid_rsa|\.(?:pem|pfx|p12))$"
)

# 檔名規則「標題任何位置」生效的應用（編輯器、檔案總管）。
FILE_VIEWER_APPS = frozenset({
    "code.exe", "code - insiders.exe", "cursor.exe", "windsurf.exe", "zed.exe",
    "notepad.exe", "notepad++.exe", "sublime_text.exe", "explorer.exe",
    "idea64.exe", "pycharm64.exe", "webstorm64.exe", "devenv.exe", "gvim.exe", "nvim-qt.exe",
})

# --------------------------------------------------------------------------
# 第 2.3 節：self / nocap 常數
# --------------------------------------------------------------------------

SELF_APPS = frozenset({"antigravity.exe", "claude.exe", "codex.exe"})
TERMINAL_APPS = frozenset({
    "windowsterminal.exe", "wt.exe", "powershell.exe", "pwsh.exe", "cmd.exe", "conhost.exe",
    "wezterm-gui.exe", "alacritty.exe", "mintty.exe", "terminal", "iterm2", "ghostty",
})
TITLE_SELF = r"(?i)\b(?:Claude Code|Antigravity|Codex)\b"

NOCAP_APPS = frozenset({
    "line.exe", "slack.exe", "discord.exe", "telegram.exe", "whatsapp.exe", "wechat.exe",
    "weixin.exe", "teams.exe", "ms-teams.exe", "outlook.exe", "olk.exe", "thunderbird.exe",
    "steam.exe", "league of legends.exe", "leagueclient.exe", "valorant.exe",
})
# 網頁版信箱與通訊軟體：服務名稱必須是標題中以 " - " 分隔的獨立一段，避免 "Slack API docs" 之類誤傷。
TITLE_NOCAP = (
    r"(?i)(?:(?:^|\s[-–—|]\s)(?:Gmail|Outlook|Yahoo Mail|Proton Mail|Slack|Discord"
    r"|WhatsApp|Messenger|Telegram|LINE)(?:\s[-–—|]\s|$)|收件匣|收件箱|受信トレイ|받은편지함)"
)

# --------------------------------------------------------------------------
# 第 5.2 節：機密憑證（命中即丟）。順序有意義：先到先遮，所以 sk-ant- 必須排在 sk- 前面。
# --------------------------------------------------------------------------

SECRET_KEYWORDS = r"(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|密碼|密鑰|金鑰|權杖|口令)"
_NOT_PLACEHOLDER = r"(?!(?:undefined|null|none|true|false|string|number|process|import|require|getenv)\b)"
_Q = "'" + '"'  # 單引號與雙引號
_KEY_TAIL = r"[A-Za-z0-9_]{0,40}[" + _Q + r"]?\s{0,8}[:=：]\s{0,8}"
_VALUE_CHARS = r"[A-Za-z0-9!@#$%^&_\-+=/]"

# 明文密碼賦值（兩條，皆有界量詞以避免 "password" 重複造成的二次方回溯）：
#   引號包住的值：8 字元以上即視為機密。
#   未加引號的值：必須含數字或符號，且不是 snake_case 識別字（getpass_value_here、get_token_v2）。
SECRET_ASSIGN_QUOTED = (
    r"(?i)" + SECRET_KEYWORDS + _KEY_TAIL + r"([" + _Q + r"])" + _NOT_PLACEHOLDER + _VALUE_CHARS + r"{8,}\1"
)
SECRET_ASSIGN_BARE = (
    r"(?i)" + SECRET_KEYWORDS + _KEY_TAIL + _NOT_PLACEHOLDER
    + r"(?=[A-Za-z0-9_\-]*[0-9!@#$%^&+=/])"
    + r"(?![a-z]+(?:_[a-z0-9]+)+(?:[" + _Q + r"\s;,]|$))"
    + _VALUE_CHARS + r"{8,}(?=[" + _Q + r"\s;,]|$)"
)

# (標籤, 正則, 遮蔽替代詞)
SECRET_RULES: Tuple[Tuple[str, str, str], ...] = (
    ("私鑰區塊", r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----", "[私鑰]"),
    ("Stripe API Key", r"(?<![A-Za-z0-9_])[sr]k_(?:live|test)_[A-Za-z0-9]{16,}(?![A-Za-z0-9_])", "[Stripe金鑰]"),
    ("Anthropic API Key", r"(?<![A-Za-z0-9_])sk-ant-[A-Za-z0-9_-]{32,}(?![A-Za-z0-9_])", "[Anthropic金鑰]"),
    ("OpenAI API Key", r"(?<![A-Za-z0-9_])sk-(?:proj-|admin-)?[A-Za-z0-9_-]{32,}(?![A-Za-z0-9_])", "[OpenAI金鑰]"),
    ("GitHub Token", r"(?<![A-Za-z0-9_])(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}(?![A-Za-z0-9_])", "[GitHub金鑰]"),
    ("GitHub Fine-grained PAT", r"(?<![A-Za-z0-9_])github_pat_[A-Za-z0-9_]{22,}(?![A-Za-z0-9_])", "[GitHub金鑰]"),
    ("AWS Access Key", r"(?<![A-Za-z0-9_])(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}(?![A-Za-z0-9_])", "[AWS金鑰]"),
    ("Google Cloud Key", r"(?<![A-Za-z0-9_])AIza[0-9A-Za-z_\-]{35}(?![A-Za-z0-9_])", "[Google金鑰]"),
    ("Slack Token", r"(?<![A-Za-z0-9_])(?:xox[abprs]|xapp)-[A-Za-z0-9\-]{10,}", "[Slack權杖]"),
    ("Supabase Secret", r"(?<![A-Za-z0-9_])sb_secret_[A-Za-z0-9_\-]{10,}|(?<![A-Za-z0-9_])sbp_[A-Za-z0-9]{20,}", "[Supabase金鑰]"),
    ("Resend API Key", r"(?<![A-Za-z0-9_])re_[A-Za-z0-9]{8,}_[A-Za-z0-9]{16,}", "[Resend金鑰]"),
    ("npm Access Token", r"(?<![A-Za-z0-9_])npm_[A-Za-z0-9]{36}(?![A-Za-z0-9_])", "[npm權杖]"),
    ("Hugging Face Token", r"(?<![A-Za-z0-9_])hf_[A-Za-z0-9]{30,}", "[Hugging Face權杖]"),
    ("SendGrid API Key", r"(?<![A-Za-z0-9_])SG\.[A-Za-z0-9_\-]{16,}\.[A-Za-z0-9_\-]{16,}", "[SendGrid金鑰]"),
    ("GitLab PAT", r"(?<![A-Za-z0-9_])glpat-[A-Za-z0-9_\-]{20,}", "[GitLab權杖]"),
    ("Webhook Secret", r"(?<![A-Za-z0-9_])whsec_[A-Za-z0-9]{24,}", "[Webhook金鑰]"),
    ("Discord Token", r"(?<![A-Za-z0-9_])[MN][A-Za-z\d]{23,25}\.[\w-]{6}\.[\w-]{27,}", "[Discord權杖]"),
    ("Telegram Bot Token", r"(?<![A-Za-z0-9_])\d{8,10}:[A-Za-z0-9_-]{35}(?![A-Za-z0-9_])", "[Telegram權杖]"),
    ("JSON Web Token (JWT)", r"(?<![A-Za-z0-9_])eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{4,}", "[JWT]"),
    ("Bearer 授權標頭", r"(?i)(?<![A-Za-z0-9_])Bearer\s+[A-Za-z0-9._~+/\-]{16,}=*", "Bearer [遮蔽]"),
    # 舊版寫成 [^\\s:@/]：照抄進原始字串會變成「排除反斜線與字母 s」，帳號含 s 就漏抓。
    ("帳密連線字串", r"(?i)(?<![A-Za-z0-9_])([a-z][a-z0-9+.\-]{1,20})://[^\s:@/]{1,64}:[^\s@/]{1,128}@[^\s" + _Q + r"]+",
     r"\1://[連線字串]"),
    ("明文密碼賦值（引號）", SECRET_ASSIGN_QUOTED, "[遮蔽的祕密]"),
    ("明文密碼賦值", SECRET_ASSIGN_BARE, "[遮蔽的祕密]"),
)

# --------------------------------------------------------------------------
# 第 5.3 節：PII 脫敏（只遮蔽，不丟棄）。正則為實際使用形式（`|` 不是 markdown 的 `\|`）。
# --------------------------------------------------------------------------

PII_RULES: Tuple[Tuple[str, str, str], ...] = (
    # 第二碼 1/2 為身分證，8/9 為新式外僑居留證（與 health-bank-toolkit 的遮罩規則一致）
    ("台灣身分證字號", r"(?<![A-Za-z0-9_])[A-Z][1289]\d{8}(?![0-9])", "[身分證]"),
    ("信用卡號", r"(?<!\d)\d(?:[- ]?\d){12,18}(?!\d)", "[卡號]"),  # 另需通過 Luhn 檢查碼（見 _luhn_ok）
    ("台灣手機號碼", r"(?<!\d)09\d{2}[- ]?\d{3}[- ]?\d{3}(?!\d)", "[手機]"),
    ("電子郵件信箱", r"[A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9.\-]{1,253}\.[A-Za-z]{2,24}", "[email]"),
    ("資料庫無密碼連線",
     r"(?i)\b(postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://[^\s" + _Q + r"]+", r"\1://[連線字串]"),
    ("CLI 密碼參數",
     r"(?i)(--?(?:password|passwd|pwd|token|secret|api-key)[\s=]+)\S+", r"\1[遮蔽]"),
)

# 第 5.4 節：關鍵字計數防禦
SENSITIVE_KEYWORDS: Tuple[str, ...] = ("診斷", "處方", "掛號", "健保", "薪資單", "所得扣繳", "信用卡帳單")
KEYWORD_THRESHOLD = 2

ACTION_DROP = "drop_image"
ACTION_PASS = "pass"
# 會跟著截圖一起送出的高敏感號碼：OCR 命中就丟棄整張圖，不只遮文字
DROP_IMAGE_PII = frozenset({"台灣身分證字號", "信用卡號"})


def _compile_all() -> None:
    """依目前的常數（重新）編譯正則。測試或實驗替換常數後可再呼叫。"""
    global _TITLE_BLOCKED, _TITLE_FILE_ANY, _TITLE_FILE_END, _TITLE_SELF, _TITLE_NOCAP
    global _SECRETS, _PII
    _TITLE_BLOCKED = [
        re.compile(p)
        for p in (TITLE_MEDICAL, TITLE_PRIVATE_BROWSING, TITLE_PASSWORD_MANAGER, TITLE_BANKING, TITLE_ADULT)
    ]
    _TITLE_FILE_ANY = re.compile(TITLE_SECRET_FILE_ANYWHERE)
    _TITLE_FILE_END = re.compile(TITLE_SECRET_FILE_AT_END)
    _TITLE_SELF = re.compile(TITLE_SELF)
    _TITLE_NOCAP = re.compile(TITLE_NOCAP)
    _SECRETS = [(label, re.compile(p), repl) for label, p, repl in SECRET_RULES]
    _PII = [(label, re.compile(p), repl) for label, p, repl in PII_RULES]


_compile_all()

_SEGMENT_SPLIT = re.compile(r"\s[-–—]\s")
_WS_ANY = re.compile(r"\s")


def _norm_app(app: Optional[str]) -> str:
    name = (app or "").strip().replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name


def _is_file_viewer_app(app: str) -> bool:
    return app in FILE_VIEWER_APPS


# --------------------------------------------------------------------------
# 第 2.3 節：視窗四級分類
# --------------------------------------------------------------------------

def classify_window(app: str, title: str) -> str:
    """回傳 "blocked" | "self" | "nocap" | "ok"，優先序依此排列（先中先贏）。"""
    app_n = _norm_app(app)
    t = normalize_title(_drop_invisible(title))  # 零寬字元不能拿來繞過比對

    if app_n in BLOCKED_APPS or any(rx.search(t) for rx in _TITLE_BLOCKED):
        return "blocked"
    if _is_file_viewer_app(app_n) and _TITLE_FILE_ANY.search(t):
        return "blocked"
    first = _SEGMENT_SPLIT.split(t, 1)[0].strip()
    if first and not _WS_ANY.search(first) and _TITLE_FILE_END.search(first):
        return "blocked"

    if app_n in SELF_APPS or (app_n in TERMINAL_APPS and _TITLE_SELF.search(t)):
        return "self"
    if app_n in NOCAP_APPS or _TITLE_NOCAP.search(t):
        return "nocap"
    return "ok"


# --------------------------------------------------------------------------
# 第 5 節：OCR 檢查與脫敏
# --------------------------------------------------------------------------

def redact_secrets(text: str) -> Tuple[str, List[str]]:
    """依 SECRET_RULES 順序遮蔽機密，回傳（遮蔽後文字, 命中的標籤）。"""
    hits: List[str] = []
    for label, rx, repl in _SECRETS:
        text, n = rx.subn(repl, text)
        if n:
            hits.append(label)
    return text, hits


def scan_secrets(text: str) -> List[str]:
    """回傳命中的機密標籤（先到先遮：sk-ant- 只會算 Anthropic，不會再算 OpenAI）。"""
    return redact_secrets(text or "")[1]


def keyword_hits(text: str) -> List[str]:
    lowered = (text or "").lower()
    return [kw for kw in SENSITIVE_KEYWORDS if kw.lower() in lowered]


def _luhn_ok(digits: str) -> bool:
    """信用卡號的 Luhn 檢查碼；13～19 位數但不符合的多半是訂單或流水號。"""
    nums = [int(c) for c in digits if c.isdigit()]
    if not 13 <= len(nums) <= 19:
        return False
    total = 0
    for i, n in enumerate(reversed(nums)):
        if i % 2:
            n = n * 2 - 9 if n > 4 else n * 2
        total += n
    return total % 10 == 0


_DIGIT_GROUP = re.compile(r"\d+")
_CARD_LABEL = "信用卡號"


# 卡號後面緊接的有效期限（12 25）、安全碼（123）每組最多 4 位；超過就不當成尾巴切掉
_CARD_TAIL_MAX_DIGITS = 4
# 實際發行的卡號長度（13/14/15/16/19）。17、18 位幾乎不存在，但「16 位編號＋兩位數」恰好是 18 位，
# 放行它們會讓每個 16 位流水號多一份約 10% 的 Luhn 誤中機率
_CARD_LENGTHS = frozenset({13, 14, 15, 16, 19})


def _card_spans(rx: "re.Pattern[str]", text: str) -> List[Tuple[int, int]]:
    """信用卡號候選字串裡通過 Luhn 的卡號 (起, 迄) 位置。

    候選正則是貪婪的：卡號後面緊接空白加數字（有效期限「12 25」、安全碼「123」）時，
    整串會被一起吞進去，13～19 位的整體多半不過 Luhn，真正的卡號就漏掉了。
    所以先看整串，不過就從尾端一組一組切掉再試；候選一律從第一組起算，
    只切尾巴、且被切掉的每組不超過 4 位。不從中間起算，也不取任意片段：
    否則訂單編號（16 位不過 Luhn）後面隨便接兩位數就有機會從第二組中間切出一個「有效卡號」。
    """
    spans: List[Tuple[int, int]] = []
    for m in rx.finditer(text):
        groups = [(g.start() + m.start(), g.end() + m.start()) for g in _DIGIT_GROUP.finditer(m.group(0))]
        for last in range(len(groups) - 1, -1, -1):
            dropped = groups[last + 1:]
            if any(b - a > _CARD_TAIL_MAX_DIGITS for a, b in dropped):
                break  # 再往前切只會切掉更長的組
            digits = "".join(text[a:b] for a, b in groups[: last + 1])
            if len(digits) in _CARD_LENGTHS and _luhn_ok(digits):
                spans.append((groups[0][0], groups[last][1]))
                break
    return spans


def _pii_matches(label: str, rx: "re.Pattern[str]", text: str) -> List[str]:
    if label == _CARD_LABEL:
        return [text[a:b] for a, b in _card_spans(rx, text)]
    return [m.group(0) for m in rx.finditer(text)]


def drop_image_pii_hits(text: str) -> List[str]:
    """命中的高敏感號碼類別（身分證、卡號）。這些號碼會隨截圖一起送出，命中就丟棄整張圖。"""
    return [label for label, rx, _ in _PII if label in DROP_IMAGE_PII and _pii_matches(label, rx, text)]


def inspect_ocr_text(text: str) -> Tuple[bool, str]:
    """回傳 (is_sensitive, action)。命中機密、身分證或卡號，或獨立敏感關鍵字達門檻，一律 drop_image。"""
    if not text:
        return False, ACTION_PASS
    if scan_secrets(text):
        return True, ACTION_DROP
    # 截圖本身會帶著這些號碼送出去，只遮 OCR 文字沒有用：身分證、卡號一律丟棄整張圖
    if drop_image_pii_hits(text):
        return True, ACTION_DROP
    if len(keyword_hits(text)) >= KEYWORD_THRESHOLD:
        return True, ACTION_DROP
    return False, ACTION_PASS


def redact_text(text: str) -> str:
    """先遮蔽機密（縱深防禦），再遮蔽 PII。卡號只遮通過 Luhn 檢查的數字串。"""
    masked, _ = redact_secrets(text or "")
    for label, rx, repl in _PII:
        if label == _CARD_LABEL:
            cursor, parts = 0, []
            for a, b in _card_spans(rx, masked):
                parts += [masked[cursor:a], repl]
                cursor = b
            masked = "".join(parts) + masked[cursor:]
        else:
            masked = rx.sub(repl, masked)
    return masked


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="screen_privacy.py",
        description="截圖／OCR 隱私規範參考實作：視窗分類與 OCR 洩鑰檢查（規範見 docs/multimodal-screen-privacy-spec.md）。",
    )
    parser.add_argument("--title", help="視窗標題，印出分類 blocked / self / nocap / ok")
    parser.add_argument("--app", default="", help="程式執行檔名（例如 chrome.exe），搭配 --title 使用")
    parser.add_argument("--ocr-file", help="OCR 文字檔路徑（UTF-8），印出是否丟棄與脫敏結果")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.title is None and args.ocr_file is None:
        parser.error("至少需要 --title 或 --ocr-file")

    if args.title is not None:
        print(f"classification: {classify_window(args.app, args.title)}")

    if args.ocr_file is not None:
        try:
            text = Path(args.ocr_file).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"[!] 讀不到 OCR 檔：{exc}", file=sys.stderr)
            return 2
        sensitive, action = inspect_ocr_text(text)
        print(f"sensitive: {str(sensitive).lower()}")
        print(f"action: {action}")
        if sensitive:
            reasons = (scan_secrets(text) or drop_image_pii_hits(text)
                       or ["敏感關鍵字達門檻：" + "、".join(keyword_hits(text))])
            print("reasons: " + "; ".join(reasons))
            print("（已丟棄，不輸出文字）")
        else:
            print("redacted:")
            print(redact_text(text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
