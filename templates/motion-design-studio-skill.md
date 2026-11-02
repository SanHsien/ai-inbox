---
name: motion-design-studio
description: 以 seek(t)、分鏡像素與文字量測、PNG 序列及 FFmpeg 製作動態設計。
---

# Motion Design Studio 可攜範本

本範本配合 ai-inbox 的 `docs/code-driven-motion-design-studio-spec.md`。
分鏡工具是有限度的機械檢查，不是美感裁判。複製到其他專案時，先完成下列安裝，再填入品牌資料。

## 1. 安裝到其他專案

從同一份 ai-inbox checkout **一起複製**這些檔案，不只複製本文：

```text
ai-inbox/tools/audit_motion_storyboard.py --> 新專案/tools/audit_motion_storyboard.py
ai-inbox/docs/code-driven-motion-design-studio-spec.md --> 新專案/docs/code-driven-motion-design-studio-spec.md
本文第 4 節 Python 區塊 --> 新專案/tools/render_frames.py
本文第 3 節 HTML 區塊 --> 新專案/index.html
```

從新專案根目錄執行；跨平台使用相同 Python 指令：

```bash
python -m venv .venv
```

啟用環境：PowerShell 用 `.venv\Scripts\Activate.ps1`，bash 用 `source .venv/bin/activate`。

```bash
python -m pip install Pillow playwright
python -m playwright install chromium
ffmpeg -version
```

FFmpeg 必須另外安裝並放入 PATH；可從 [官方下載入口](https://ffmpeg.org/download.html) 選擇作業系統套件。
記錄 `python -m pip freeze` 與 `ffmpeg -version`，讓驗收可重現；不要自行聲稱未實測版本相容。
沒有瀏覽器/套件回 exit 2，不能視為通過。若使用已安裝的 Edge 或 Chrome，audit 與 export 都帶相同 `--channel`。

## 2. 品牌提取與 CLAUDE.md 填空

先取得官方品牌規範或獲授權的設計稿。從其 CSS 自訂屬性、設計 token 或開發者工具的 computed style 記錄實際色值；下載官方 SVG 並確認使用授權。沒有官方色票時，人工採樣後註明「從素材取樣，非官方規範」。不可拿範例配色冒充品牌色。

```text
品牌/產品：________
來源 URL / 本機授權素材：________
查證日期與頁面元素：________
BG_PRIMARY（#RRGGBB，對應 --bg-primary）：________
TEXT_PRIMARY（#RRGGBB，對應 --text-primary）：________
ACCENT_BRAND（#RRGGBB，對應 --accent-brand）：________
Logo SVG 路徑與授權：________
字型與授權：________
文字/背景最差對比（>=4.5）：________
```

檢查來源記錄後，只改第 3 節 `:root` 的三個變數，再重新跑量測；對比不足的組合由 audit 擋下，不要靠調低 `--min-score` 或刪規則通過。以下可複製至根目錄 `CLAUDE.md`：

```markdown
# 動態工作室規則
- 規範：docs/code-driven-motion-design-studio-spec.md；品牌資料先填完並留來源。
- window.seek(t 毫秒) 完成時必須已繪製；任意順序同 t 像素相同。不累加狀態，不使用未設種子的隨機數、setInterval 或持續的 rAF/setTimeout 迴圈；CSS 動畫須 paused，由 seek 設 currentTime。
- 本專案偏好 zeta 0.7..0.85 的欠阻尼彈簧、40..80ms 錯落進場；不得把過阻尼套成臨界阻尼。
- SLOP-M01 漸層置中、M02 全體同步淡入、M03 浮誇陰影/標籤、M04 生硬線性/無阻尼、M05 假數字/隨機粒子都需避免。
- audit 會保守標記原始碼候選，必須查明問題；Emoji 不屬 M05。不可降低門檻或關閉檢查求通過。
- 正式文字用 DOM；SVG/Canvas 文字、遮擋與複雜混色另人工檢查，不能宣稱工具已量過。
- 執行 python tools/audit_motion_storyboard.py index.html --duration 3000 --frames 6 --output-dir artifacts/storyboard --json。
- 全部影格 >=8 且無 issues/errors/Anti-Slop 才通過。缺依賴、逾時、壞圖均不可導出；先修 Worst-3。
- 通過後才執行 tools/render_frames.py 並用 FFmpeg 合成；保留原始 PNG。
```

## 3. 可執行 seek 範例

這是與規範一致的中性驗證 fixture。品牌顏色只在 `:root` 三個變數填空；初始畫面保留內容，不用全透明影格。

```html
<!doctype html>
<html lang="zh-Hant">
<meta charset="utf-8">
<title>Motion fixture</title>
<style>
:root{--bg-primary:#112233;--text-primary:#ffffff;--accent-brand:#ffb703} /* 填空：換成第 2 節取得的品牌色票 */
body{margin:0;background:var(--bg-primary);color:var(--text-primary);font:32px sans-serif}
h1,p{position:absolute;margin:0;left:80px}
h1{top:80px;font-size:48px}p{top:230px}
#card{position:absolute;left:80px;top:380px;width:240px;height:120px;background:var(--accent-brand)}
</style>
<h1 id="title">Motion Studio</h1>
<p id="subtitle">Deterministic frames</p>
<div id="card"></div>
<script>
function spring(t,k=16,c=6,m=1){
  const z=c/(2*Math.sqrt(k*m));
  if(!(k>0 && m>0 && z>0 && z<1)) throw new Error('underdamped only');
  if(t<=0) return 0;
  const w=Math.sqrt(k/m), d=w*Math.sqrt(1-z*z);
  return 1-Math.exp(-z*w*t)*(Math.cos(d*t)+z*w/d*Math.sin(d*t));
}
window.seek=function(ms){
  const t=Math.max(0,ms)/1000;
  document.getElementById('title').style.transform=`translateX(${80*spring(t/3)}px)`;
  document.getElementById('subtitle').style.transform=`translateX(${80*spring((t-.06)/3)}px)`;
  document.getElementById('card').style.transform=`translateX(${80*spring((t-.12)/3)}px)`;
};
window.seek(0);
</script>
</html>
```

## 4. seek 逐幀輸出腳本

將下列完整內容存成 `tools/render_frames.py`。此腳本依賴 Playwright，不需要 Node 或 ai-inbox 的 checkout；它是導出器，不取代 audit。每幀時間為 `i*1000/fps`，不重複最後端點；檔名從 `frame_0000.png` 開始。要求輸出目錄不存在或為空，防止舊序列混入。

```python
import argparse
import math
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=Path)
    parser.add_argument('--duration', type=float, default=3000)
    parser.add_argument('--fps', type=int, default=60)
    parser.add_argument('--output-dir', type=Path, default=Path('frames'))
    parser.add_argument('--channel', choices=['chrome', 'msedge'])
    args = parser.parse_args()
    if not math.isfinite(args.duration) or not 0 < args.duration <= 600000 or not 1 <= args.fps <= 120:
        parser.error('duration: 0 < 有限毫秒 <=600000；fps: 1..120')
    if not args.target.is_file():
        parser.error('目標 HTML 不存在')
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        parser.error('輸出目錄必須為空，請指定新目錄')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('缺少 Playwright；python -m pip install playwright', file=sys.stderr)
        return 2
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, channel=args.channel, timeout=15000)
        except Exception as exc:
            print(f'瀏覽器不可用：{exc}', file=sys.stderr)
            return 2
        try:
            page = browser.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            page.goto(args.target.resolve().as_uri(), timeout=15000)
            page.evaluate('() => document.fonts.ready')
            if not page.evaluate("() => typeof window.seek === 'function'"):
                raise RuntimeError('缺少 window.seek')
            for i in range(math.ceil(args.duration * args.fps / 1000)):
                page.evaluate('''async t => {
                    let timer;
                    try { await Promise.race([Promise.resolve(window.seek(t)),
                        new Promise((_, reject) => {timer=setTimeout(()=>reject(new Error('seek timeout')),15000)})]);
                    } finally {clearTimeout(timer)}
                }''', i * 1000 / args.fps)
                page.screenshot(path=str(args.output_dir / f'frame_{i:04d}.png'), timeout=15000)
                if errors:
                    raise RuntimeError('; '.join(errors))
        except Exception as exc:
            print(f'導出失敗（部分 PNG 不可交付）：{exc}', file=sys.stderr)
            return 1
        finally:
            browser.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

## 5. 自審、序列與影片的完整命令

在新專案根目錄執行下列單行命令（PowerShell 7 / bash）：

```bash
python tools/audit_motion_storyboard.py index.html --duration 3000 --frames 6 --output-dir artifacts/storyboard --json && python tools/render_frames.py index.html --duration 3000 --fps 60 --output-dir frames && ffmpeg -y -framerate 60 -start_number 0 -i frames/frame_%04d.png -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart output.mp4
```

命名全程使用 `frame_%04d.png`，不是 `f_%04d.png`；Contact Sheet 是抽樣，不可直接當完整影片序列。
CRF 18 是有損起點，不保證視覺無失真；`+faststart` 搬移 moov metadata，不保證秒開；不在未驗證時稱任何編碼格式為無損母帶。
舊序列或部分失敗輸出須保留診斷，重新導出到新目錄，不能混用。
若要更換 fps，同時修改輸出腳本參數與 ffmpeg 的 framerate。

## 6. 驗收循環、路由與來源

```text
品牌填空 -> 實作 seek -> audit
                        | FAIL -> 看 Worst-3 / issues -> 修正 -> audit
                        | INCOMPLETE -> 停止交付，排除依賴/逾時
                        v PASS
                   render_frames -> FFmpeg -> 人工播放核對
```

audit：exit 0 通過；1 頁面/像素/排版品質失敗；2 參數/依賴錯誤；3 INCOMPLETE。
只檢查工具可量到的項目，人工仍須看品牌、資訊順序與剪輯；完整限制見複製後的規範第 4 節。
局部修改使用平台已驗證的低成本路由；完整或多鏡頭任務先定規格再決定 review，不硬綁不存在的 effort 選項。

查證日期 2026-11-02：Playwright 的 launch/channel 與 Page 事件、FFmpeg n7.1 faststart、H.264 指南（Internet Archive 快照，原站被反機器人頁擋下）、Remotion random、Motion Canvas、Threads 貼文的逐項內容及未能開啟的 ffmpeg-formats.html，均見規範第 6 節。本文的門檻都是本 repo 的取捨，不是這些來源給的數字。
