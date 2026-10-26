#!/usr/bin/env python3
"""
tools/render_artifact_html.py
把「語意草稿（Draft）」確定性地編譯成單檔自包含 HTML（規格：docs/visual-agent-artifacts-engineering-spec.md）。

用法：
    python tools/render_artifact_html.py draft.md -o out.html
    python tools/render_artifact_html.py - < draft.md > out.html

保證：
- 同一份輸入永遠得到位元組完全相同的輸出（沒有時間戳、亂數、雜湊表順序）。
- 所有使用者文字一律先 HTML 跳脫；不支援連結與原始 HTML，所以沒有 javascript: 之類的注入面。
- 輸出沒有外部資源；頁面另加 CSP meta，只允許內嵌樣式與內嵌腳本。
只使用 Python 標準函式庫。
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
from pathlib import Path


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+)`")
_FENCE = re.compile(r"^```\s*([A-Za-z0-9_-]*)\s*(.*?)\s*$")
_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
_ULI = re.compile(r"^[-*]\s+(.*)$")
_OLI = re.compile(r"^\d+[.)]\s+(.*)$")
_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
_CELL_MARK = {"ok": ("ok", "✓"), "no": ("no", "✗"), "warn": ("warn", "!")}
_CALLOUT_KINDS = ("info", "warn", "ok", "no")
_ID = re.compile(r"[^A-Za-z0-9_-]")


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def inline(text: str) -> str:
    """先跳脫，再套用 `code` 與 **粗體**。跳脫後才加標籤，所以使用者文字進不了標籤層。"""
    out = esc(text)
    out = _CODE.sub(lambda m: f"<code>{m.group(1)}</code>", out)
    out = _BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", out)
    return out


def parse_frontmatter(lines: list[str]) -> tuple[dict[str, str], int]:
    if not lines or lines[0].strip() != "---":
        return {}, 0
    meta: dict[str, str] = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return meta, i + 1
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return {}, 0  # 沒有結尾的 --- 就當作沒有 frontmatter


def _split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", s)]


def _render_table(rows: list[list[str]]) -> str:
    head, body = rows[0], rows[1:]
    parts = ['<div class="tablewrap"><table><thead><tr>']
    parts += [f"<th>{inline(c)}</th>" for c in head]
    parts.append("</tr></thead><tbody>")
    for r in body:
        parts.append("<tr>")
        for c in r + [""] * (len(head) - len(r)):
            mark = _CELL_MARK.get(c.strip().lower())
            if mark:
                parts.append(f'<td class="{mark[0]}">{mark[1]}</td>')
            else:
                parts.append(f"<td>{inline(c)}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts)


def _render_flow(body: list[str], direction: str) -> str:
    """flow：每行 `A -> B -> C` 一條鏈。版面由 CSS flex 決定，沒有任何座標。"""
    d = "col" if direction.upper() in ("TB", "TD", "COL") else "row"
    chains = []
    for line in body:
        nodes = [n.strip() for n in line.split("->") if n.strip()]
        if not nodes:
            continue
        items = '<span class="arrow">→</span>'.join(f'<span class="node">{inline(n)}</span>' for n in nodes)
        chains.append(f'<div class="chain">{items}</div>')
    return f'<div class="flow {d}">{"".join(chains)}</div>'


def _render_ask(body: list[str], ask_id: str, index: int) -> str:
    """ask：第一行是問題；`- ` 開頭是選項；`(single)` 結尾表示單選。"""
    aid = _ID.sub("", ask_id) or f"q{index}"
    question = body[0].strip() if body else ""
    single = question.endswith("(single)")
    if single:
        question = question[: -len("(single)")].strip()
    opts = [m.group(1).strip() for m in (_ULI.match(b.strip()) for b in body[1:]) if m]
    kind = "radio" if single else "checkbox"
    parts = [
        f'<fieldset class="ask" data-ask="{esc(aid)}" data-question="{esc(question)}">',
        f"<legend>{inline(question)}</legend>",
    ]
    for n, opt in enumerate(opts):
        parts.append(
            f'<label><input type="{kind}" name="{esc(aid)}" value="{esc(opt)}"> <span>{inline(opt)}</span></label>'
        )
    parts.append("</fieldset>")
    return "".join(parts)


def render_body(lines: list[str]) -> tuple[str, bool]:
    """回傳 (body HTML, 是否含 ask 區塊)。"""
    out: list[str] = []
    i, n = 0, len(lines)
    para: list[str] = []
    has_ask = False
    ask_count = 0

    def flush_para() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(p.strip() for p in para))}</p>")
            para.clear()

    while i < n:
        line = lines[i]
        stripped = line.strip()
        fence = _FENCE.match(stripped)
        if fence:
            flush_para()
            kind, arg = fence.group(1).lower(), fence.group(2)
            j = i + 1
            body: list[str] = []
            while j < n and not lines[j].strip().startswith("```"):
                body.append(lines[j])
                j += 1
            i = j + 1  # 沒有結尾圍欄就吃到檔尾
            if kind == "flow":
                out.append(_render_flow(body, arg or "LR"))
            elif kind == "ask":
                ask_count += 1
                has_ask = True
                out.append(_render_ask(body, arg, ask_count))
            elif kind == "callout":
                ck = arg.lower() if arg.lower() in _CALLOUT_KINDS else "info"
                text = " ".join(b.strip() for b in body if b.strip())
                out.append(f'<aside class="callout {ck}">{inline(text)}</aside>')
            else:
                label = f'<span class="lang">{esc(kind)}</span>' if kind else ""
                out.append(f'<pre>{label}<code>{esc(chr(10).join(body))}</code></pre>')
            continue
        if not stripped:
            flush_para()
            i += 1
            continue
        h = _HEADING.match(stripped)
        if h:
            flush_para()
            lvl = len(h.group(1))
            out.append(f"<h{lvl}>{inline(h.group(2))}</h{lvl}>")
            i += 1
            continue
        if "|" in stripped and i + 1 < n and _TABLE_SEP.match(lines[i + 1]) and "|" in lines[i + 1]:
            flush_para()
            rows = [_split_row(stripped)]
            j = i + 2
            while j < n and lines[j].strip() and "|" in lines[j]:
                rows.append(_split_row(lines[j]))
                j += 1
            out.append(_render_table(rows))
            i = j
            continue
        ul, ol = _ULI.match(stripped), _OLI.match(stripped)
        if ul or ol:
            flush_para()
            tag, rx = ("ul", _ULI) if ul else ("ol", _OLI)
            items = []
            while i < n and (m := rx.match(lines[i].strip())):
                items.append(f"<li>{inline(m.group(1))}</li>")
                i += 1
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue
        para.append(line)
        i += 1
    flush_para()
    return "\n".join(out), has_ask


CSS = """
:root{--bg:#0f1218;--panel:#171c26;--line:#2a3242;--fg:#e6e9ef;--mute:#9aa4b5;--acc:#6ea8fe;--ok:#4cc38a;--no:#f0686b;--warn:#e5b34d}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,"Segoe UI","Noto Sans TC","Microsoft JhengHei",sans-serif}
main{max-width:860px;margin:0 auto;padding:32px 20px 96px}
h1{font-size:1.9rem;margin:0 0 .6em}h2{font-size:1.35rem;margin:1.8em 0 .5em;border-bottom:1px solid var(--line);padding-bottom:.2em}h3{font-size:1.1rem;margin:1.4em 0 .4em;color:var(--acc)}
p,ul,ol{margin:.6em 0}code{background:#222a38;padding:.1em .35em;border-radius:4px;font-family:Consolas,monospace;font-size:.92em}
pre{position:relative;background:#0b0e14;border:1px solid var(--line);border-radius:8px;padding:14px;overflow:auto}pre code{background:none;padding:0}
.lang{position:absolute;top:4px;right:10px;color:var(--mute);font-size:.75rem}
.tablewrap{overflow-x:auto}table{border-collapse:collapse;width:100%;margin:1em 0}th,td{border:1px solid var(--line);padding:8px 12px;text-align:left}th{background:var(--panel)}
td.ok{color:var(--ok);font-weight:700}td.no{color:var(--no);font-weight:700}td.warn{color:var(--warn);font-weight:700}
.callout{border-left:4px solid var(--acc);background:var(--panel);padding:10px 14px;border-radius:0 8px 8px 0;margin:1em 0}
.callout.ok{border-color:var(--ok)}.callout.no{border-color:var(--no)}.callout.warn{border-color:var(--warn)}
.flow{margin:1em 0;display:flex;gap:10px}.flow.col{flex-direction:column}.flow.row{flex-direction:column}
.chain{display:flex;flex-wrap:wrap;align-items:center;gap:8px}.flow.col .chain{flex-direction:column;align-items:flex-start}
.node{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 12px}.arrow{color:var(--acc)}
.ask{border:1px solid var(--line);border-radius:8px;margin:1em 0;padding:10px 14px;background:var(--panel)}.ask legend{padding:0 6px;font-weight:700}
.ask label{display:block;padding:3px 0;cursor:pointer}
#fb{position:fixed;left:0;right:0;bottom:0;background:var(--panel);border-top:1px solid var(--line);padding:10px 20px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
#fb input[type=text]{flex:1;min-width:180px;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px 10px}
#fb button{background:var(--acc);color:#04122b;border:0;border-radius:6px;padding:7px 16px;font-weight:700;cursor:pointer}
#fbout{width:100%;display:none;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;min-height:90px}
"""

SCRIPT = """
(function(){
var btn=document.getElementById('fbcopy'),out=document.getElementById('fbout'),note=document.getElementById('fbnote'),title=document.body.getAttribute('data-title')||'';
function collect(){
  var lines=['[決策回饋] '+title];
  document.querySelectorAll('fieldset.ask').forEach(function(f){
    var picked=[];f.querySelectorAll('input:checked').forEach(function(i){picked.push(i.value);});
    lines.push('- '+f.getAttribute('data-question')+'：'+(picked.length?picked.join('、'):'（未選）'));
  });
  if(note.value.trim()){lines.push('備註：'+note.value.trim());}
  return lines.join('\\n');
}
btn.addEventListener('click',function(){
  var text=collect();out.value=text;out.style.display='block';
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(function(){btn.textContent='已複製';},function(){out.select();btn.textContent='請手動複製';});
  }else{out.select();try{document.execCommand('copy');btn.textContent='已複製';}catch(e){btn.textContent='請手動複製';}}
});
})();
"""

CSP = "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:"


def render(source: str) -> str:
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    lines = source.split("\n")
    meta, start = parse_frontmatter(lines)
    body, has_ask = render_body(lines[start:])
    title = meta.get("title", "")
    if not title:
        for ln in lines[start:]:
            m = _HEADING.match(ln.strip())
            if m:
                title = re.sub(r"[`*]", "", m.group(2))
                break
    title = title or "Artifact"
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
    feedback = ""
    script = ""
    if has_ask:
        feedback = (
            '<div id="fb"><input type="text" id="fbnote" placeholder="備註（選填）">'
            '<button type="button" id="fbcopy">複製決策回饋</button>'
            '<textarea id="fbout" readonly></textarea></div>'
        )
        script = f"<script>{SCRIPT}</script>"
    return (
        "<!DOCTYPE html>\n"
        f'<html lang="zh-Hant"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta http-equiv="Content-Security-Policy" content="{esc(CSP)}">'
        f'<meta name="draft-sha256" content="{digest}">'
        f"<title>{esc(title)}</title><style>{CSS}</style></head>\n"
        f'<body data-title="{esc(title)}"><main>\n'
        f"{'<h1>' + esc(title) + '</h1>' if meta.get('title') else ''}\n"
        f"{body}\n</main>{feedback}{script}</body></html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    ap = argparse.ArgumentParser(description="把語意草稿（Draft）確定性編譯成單檔自包含 HTML。")
    ap.add_argument("input", help="草稿檔路徑；用 - 讀 stdin")
    ap.add_argument("-o", "--output", help="輸出 HTML 路徑；省略則寫到 stdout")
    args = ap.parse_args(argv)
    if args.input == "-":
        source = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    else:
        source = Path(args.input).read_text(encoding="utf-8")
    result = render(source)
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(result)
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
