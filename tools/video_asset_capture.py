#!/usr/bin/env python3
"""
tools/video_asset_capture.py
Code-as-Video 影視工作室素材自動捕獲與時間函式代碼範例生成工具。

使用 Playwright 輸入公開網址自動抓取：
1. 真機高解析度截圖（screenshot.png）
2. 提取網頁主色系與品牌調性（theme.json）
3. 自動生成包含確定性 seek(t) 時間函式架構的單檔 HTML/Canvas 動畫範例（video_seek_canvas.html）
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse


HTML_CANVAS_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <title>{title} — Code-as-Video seek(t) Studio Demo</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: {background_color};
      color: {text_color};
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
    }}
    #stage-container {{
      position: relative;
      width: 960px;
      height: 540px;
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
      background: #0d0f12;
    }}
    canvas {{
      width: 100%;
      height: 100%;
      display: block;
    }}
    #controls {{
      margin-top: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      width: 960px;
      background: rgba(255, 255, 255, 0.05);
      padding: 10px 16px;
      border-radius: 6px;
      font-size: 13px;
    }}
    #scrubber {{
      flex: 1;
      cursor: pointer;
    }}
    .badge {{
      background: {primary_color};
      color: #fff;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
    }}
  </style>
</head>
<body>

  <div id="stage-container">
    <canvas id="video-canvas" width="1920" height="1080"></canvas>
  </div>

  <div id="controls">
    <button id="play-btn">播放 / 暫停</button>
    <input type="range" id="scrubber" min="0" max="{duration}" step="0.016" value="0">
    <span id="time-display">0.00s / {duration_label}s</span>
    <span class="badge">V = f(t) seek(t)</span>
  </div>

  <script>
    const canvas = document.getElementById('video-canvas');
    const ctx = canvas.getContext('2d');
    const scrubber = document.getElementById('scrubber');
    const timeDisplay = document.getElementById('time-display');
    const playBtn = document.getElementById('play-btn');

    const THEME = {theme_json};
    const DURATION = {duration};

    // 載入真實截圖（若存在）
    const screenshotImg = new Image();
    let imageLoaded = false;
    screenshotImg.src = '{screenshot_rel}';
    screenshotImg.onload = () => {{
      imageLoaded = true;
      seek(parseFloat(scrubber.value));
    }};

    // 物理彈簧與節奏插值函式
    function spring(t, start, end, stiffness = 220, damping = 20) {{
      if (t <= 0) return start;
      const progress = Math.min(t, 1.0);
      const decay = Math.exp(-damping * progress * 0.1);
      const val = 1 - decay * Math.cos(stiffness * progress * 0.05);
      return start + (end - start) * Math.min(Math.max(val, 0), 1.05);
    }}

    function clamp(val, min, max) {{
      return Math.max(min, Math.min(max, val));
    }}

    /**
     * 核心時間函式：Frame = f(t, state)
     * 任意時刻直接隨機尋軌渲染，具備像素級確定性
     */
    window.seek = function(t) {{
      t = clamp(t, 0, DURATION);

      // 1. 清空畫布與繪製現代非對稱幾何背景（反漸層套路）
      ctx.fillStyle = THEME.background_color || '#0d0f12';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 細緻幾何輔助網格
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
      ctx.lineWidth = 1;
      const gridSize = 80;
      for (let x = 0; x < canvas.width; x += gridSize) {{
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }}
      for (let y = 0; y < canvas.height; y += gridSize) {{
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }}

      // 2. 宏觀相機推拉運鏡 (Hero Close-up -> Feature Pan)
      // t: 0.0 ~ 2.0: Dolly in 聚焦
      // t: 2.0 ~ 5.0: Horizontal Pan + 微幅旋轉
      ctx.save();
      const scale = spring(t / 2.0, 0.92, 1.04);
      const panX = (t > 2.0) ? (t - 2.0) * -25 : 0;
      ctx.translate(canvas.width / 2 + panX, canvas.height / 2);
      ctx.scale(scale, scale);

      // 3. 渲染真實產品畫面主卡片 (3D 輕量透視投影)
      const cardWidth = 1200;
      const cardHeight = 675;
      const cardX = -cardWidth / 2;
      const cardY = -cardHeight / 2 + 30;

      // 卡片陰影
      ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
      ctx.shadowBlur = 40;
      ctx.shadowOffsetY = 20;

      // 邊框與背景
      ctx.fillStyle = '#161920';
      ctx.strokeStyle = THEME.primary_color || '#3b82f6';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(cardX, cardY, cardWidth, cardHeight, 16);
      ctx.fill();
      ctx.stroke();

      ctx.shadowColor = 'transparent';

      // 貼入真機截圖
      if (imageLoaded) {{
        ctx.save();
        ctx.beginPath();
        ctx.roundRect(cardX, cardY, cardWidth, cardHeight, 16);
        ctx.clip();
        ctx.drawImage(screenshotImg, cardX, cardY, cardWidth, cardHeight);
        ctx.restore();
      }} else {{
        // 若截圖未載入則繪製幾何線框示意
        ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.fillRect(cardX + 20, cardY + 20, cardWidth - 40, cardHeight - 40);
        ctx.fillStyle = '#fff';
        ctx.font = '24px monospace';
        ctx.fillText('Real Asset Capture Area (' + THEME.title + ')', cardX + 40, cardY + 80);
      }}

      ctx.restore();

      // 4. Kinetic Typography（動態標題依節奏登場）
      // t: 0.5s 開始彈簧位移進入
      if (t >= 0.5) {{
        const textProgress = spring(t - 0.5, 0, 1);
        ctx.save();
        ctx.translate(140, 160 + (1 - textProgress) * 40);
        ctx.globalAlpha = textProgress;
        ctx.fillStyle = THEME.accent_color || '#38bdf8';
        ctx.font = '600 28px -apple-system, sans-serif';
        ctx.fillText('FEATURE SPOTLIGHT // ' + THEME.title, 0, 0);

        ctx.fillStyle = '#ffffff';
        ctx.font = '800 64px -apple-system, sans-serif';
        ctx.fillText('Evidence-First Architecture', 0, 75);
        ctx.restore();
      }}

      // 5. 畫面時間碼與音畫節拍提示
      ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
      ctx.font = '16px monospace';
      ctx.fillText('FRAME TIME: ' + t.toFixed(3) + 's / ' + DURATION.toFixed(2) + 's', 140, canvas.height - 80);

      // 同步 UI 控制項
      scrubber.value = t;
      timeDisplay.innerText = t.toFixed(2) + 's / ' + DURATION.toFixed(2) + 's';
    }};

    // 播放循環
    let isPlaying = false;
    let animId = null;
    let lastTimestamp = null;

    function loop(timestamp) {{
      if (!lastTimestamp) lastTimestamp = timestamp;
      const dt = (timestamp - lastTimestamp) / 1000;
      lastTimestamp = timestamp;

      let nextTime = parseFloat(scrubber.value) + dt;
      if (nextTime > DURATION) {{
        nextTime = 0;
      }}
      window.seek(nextTime);

      if (isPlaying) {{
        animId = requestAnimationFrame(loop);
      }}
    }}

    playBtn.addEventListener('click', () => {{
      isPlaying = !isPlaying;
      if (isPlaying) {{
        playBtn.innerText = '暫停';
        lastTimestamp = null;
        animId = requestAnimationFrame(loop);
      }} else {{
        playBtn.innerText = '播放';
        if (animId) cancelAnimationFrame(animId);
      }}
    }});

    scrubber.addEventListener('input', (e) => {{
      if (isPlaying) {{
        isPlaying = false;
        playBtn.innerText = '播放';
        if (animId) cancelAnimationFrame(animId);
      }}
      window.seek(parseFloat(e.target.value));
    }});

    // 初始化渲染第 0 幀
    window.seek(0);
  </script>
</body>
</html>
"""


# CSS 顏色值白名單字元：十六進位、rgb()/hsl() 函式、顏色名稱；其餘一律改用預設色，
# 避免頁面提供的樣式字串跳出 <style> 區塊。
_SAFE_COLOR_RE = re.compile(r"^[#A-Za-z0-9 .,()%/-]{1,64}$")


def _safe_color(value: Any, default: str) -> str:
    text = str(value or "").strip()
    return text if _SAFE_COLOR_RE.match(text) else default


def _json_for_script(data: Any) -> str:
    """序列化成可安全嵌入 <script> 的 JSON：跳脫 < > & 與 JS 行分隔符，擋下 </script> 跳出。"""
    text = json.dumps(data, ensure_ascii=False)
    for ch, esc in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"), ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
        text = text.replace(ch, esc)
    return text


def validate_url(url: str) -> str:
    """只允許 http(s)。file:// 等協定會讓 Chromium 讀本機檔案並截圖外洩。"""
    url = (url or "").strip()
    # urlparse 會默默去掉 tab、換行等字元再判斷，驗過的字串會跟實際開啟的不同，直接拒絕
    if any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in url):
        raise ValueError(f"網址含空白或控制字元：{url!r}")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"只接受 http(s) 網址：{url!r}")
    return url


def extract_css_colors(html_content: str, default_theme: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """從 HTML/CSS 內容中抽取色彩資訊作為備用或補充。"""
    theme = {
        "primary_color": "#2563eb",
        "background_color": "#0a0c10",
        "text_color": "#f8fafc",
        "accent_color": "#38bdf8",
    }
    if default_theme:
        theme.update(default_theme)

    # 檢測 hex 顏色
    hex_colors = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}\b", html_content)
    if hex_colors:
        # 去重並挑選
        unique_colors = list(dict.fromkeys(hex_colors))
        if len(unique_colors) >= 1:
            theme["primary_color"] = unique_colors[0]
        if len(unique_colors) >= 2:
            theme["accent_color"] = unique_colors[1]

    return theme


def capture_url_assets(
    url: str,
    output_dir: Path,
    width: int = 1920,
    height: int = 1080,
    offline_fallback: bool = False,
) -> Dict[str, Any]:
    """使用 Playwright 捕獲真實網頁截圖與色彩，若失敗或處於 offline 模式則安全降級。"""
    url = validate_url(url)
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = output_dir / "screenshot.png"
    theme_path = output_dir / "theme.json"
    demo_html_path = output_dir / "video_seek_canvas.html"

    captured_data: Dict[str, Any] = {
        "url": url,
        "title": "Captured Page",
        "primary_color": "#3b82f6",
        "background_color": "#0d1117",
        "text_color": "#f0f6fc",
        "accent_color": "#58a6ff",
        "screenshot_file": "screenshot.png",
    }

    if not offline_fallback:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(url, wait_until="domcontentloaded", timeout=20000)

                # 提取標題
                title = page.title() or "Captured Product"
                captured_data["title"] = title

                # 截取全螢幕或視口截圖
                page.screenshot(path=str(screenshot_path), full_page=False)

                # 透過瀏覽器評估主色系
                styles = page.evaluate(
                    """() => {
                    const body = document.body;
                    const style = window.getComputedStyle(body);
                    const btn = document.querySelector('button, a.btn, a[class*="button"], a');
                    const btnStyle = btn ? window.getComputedStyle(btn) : null;
                    const h1 = document.querySelector('h1, h2');
                    const h1Style = h1 ? window.getComputedStyle(h1) : null;

                    return {
                        bg: style.backgroundColor || '#0d1117',
                        text: style.color || '#f0f6fc',
                        btnBg: btnStyle ? btnStyle.backgroundColor : null,
                        btnColor: btnStyle ? btnStyle.color : null,
                        accent: h1Style ? h1Style.color : null
                    };
                }"""
                )

                if styles.get("btnBg") and styles["btnBg"] not in ("rgba(0, 0, 0, 0)", "transparent"):
                    captured_data["primary_color"] = styles["btnBg"]
                if styles.get("bg") and styles["bg"] not in ("rgba(0, 0, 0, 0)", "transparent"):
                    captured_data["background_color"] = styles["bg"]
                if styles.get("text"):
                    captured_data["text_color"] = styles["text"]
                if styles.get("accent"):
                    captured_data["accent_color"] = styles["accent"]

                browser.close()
        except Exception as e:
            print(f"[WARN] Playwright 連線抓取失敗 ({e})，使用確定性本地降級模式", file=sys.stderr)
            offline_fallback = True

    if offline_fallback:
        # 降級產出示意截圖 (1 像素透明 PNG 或純色 PNG)
        # 建立簡約 16x16 PNG
        import base64
        # 1x1 灰色 PNG
        tiny_png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        if not screenshot_path.exists():
            screenshot_path.write_bytes(tiny_png)
        captured_data["title"] = f"Sample Studio Capture ({url})"

    # 儲存 theme.json
    theme_path.write_text(json.dumps(captured_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # 生成 HTML/Canvas seek(t) 範例
    # 網頁標題與顏色來自不受信任的頁面：標題做 HTML 跳脫、顏色做白名單、JSON 做 script 安全序列化
    for key, default in (
        ("primary_color", "#3b82f6"),
        ("background_color", "#0d1117"),
        ("text_color", "#f0f6fc"),
        ("accent_color", "#58a6ff"),
    ):
        captured_data[key] = _safe_color(captured_data.get(key), default)
    html_code = HTML_CANVAS_TEMPLATE.format(
        title=html.escape(str(captured_data["title"])),
        background_color=captured_data["background_color"],
        text_color=captured_data["text_color"],
        primary_color=captured_data["primary_color"],
        accent_color=captured_data["accent_color"],
        duration=6.0,
        duration_label="6.00",
        theme_json=_json_for_script(captured_data),
        screenshot_rel="screenshot.png",
    )
    demo_html_path.write_text(html_code, encoding="utf-8")

    return captured_data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Code-as-Video 網頁素材自動捕獲與 seek(t) 範例生成器"
    )
    parser.add_argument(
        "--url",
        "-u",
        default="https://example.com",
        help="目標產品官網網址 (例如: https://example.com 或 https://openlibrary.org)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="assets/captured",
        help="素材與範例輸出目錄 (預設: assets/captured)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="強制離線/測試降級模式，不發起真實網路請求",
    )

    args = parser.parse_args()

    # 保證 Windows 終端 UTF-8；stderr 也要處理，否則 [WARN] 訊息含特殊字元時會 UnicodeEncodeError
    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    out_dir = Path(args.output_dir)
    print(f"[*] 開始捕獲網頁資產: {args.url}")
    try:
        data = capture_url_assets(args.url, out_dir, offline_fallback=args.offline)
    except (ValueError, OSError) as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    print(f"[+] 捕獲成功！網頁標題: {data.get('title')}")
    print(f"    - 主色: {data.get('primary_color')}")
    print(f"    - 背景色: {data.get('background_color')}")
    print(f"    - 截圖路徑: {(out_dir / 'screenshot.png').resolve()}")
    print(f"    - 色彩設定: {(out_dir / 'theme.json').resolve()}")
    print(f"    - seek(t) 動畫範例: {(out_dir / 'video_seek_canvas.html').resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
