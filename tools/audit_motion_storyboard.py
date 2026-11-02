#!/usr/bin/env python3
"""分鏡量測；0=通過，1=品質/頁面/影格失敗，2=參數/依賴錯誤，3=INCOMPLETE 逾時。
環境變數：AI_INBOX_MOTION_TIMEOUT_MS（單一瀏覽器操作/seek，預設 15000）、AI_INBOX_MOTION_TOTAL_TIMEOUT_S（整體，預設 600）。"""
from __future__ import annotations

import argparse
import html
import io
import json
import math
import os
import re
import sys
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path


class DependencyError(RuntimeError):
    pass


class IncompleteError(RuntimeError):
    pass


def pillow():
    try:
        from PIL import Image, ImageChops, ImageStat
        return Image, ImageChops, ImageStat
    except ImportError as exc:
        raise DependencyError('缺少 Pillow：python -m pip install Pillow') from exc


@dataclass
class SlopViolation:
    rule_id: str
    rule_name: str
    description: str


@dataclass
class FrameInfo:
    frame_index: int
    timestamp_ms: float
    file_path: str = ''
    mean_luminance: float | None = None
    contrast_std: float | None = None
    pixel_delta: float | None = None
    seek_delta: float | None = None
    text_boxes: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    scores: dict = field(default_factory=dict)
    total_score: float = 0.0


@dataclass
class AuditReport:
    target_path: str
    passed: bool
    min_score_threshold: float
    lowest_score: float
    average_score: float
    worst_3_frames: list
    frames: list
    anti_slop_violations: list
    errors: list
    contact_sheet_image: str = ''
    contact_sheet_html: str = ''


def check_html_anti_slop(source):
    """僅為原始碼啟發式提示，不宣稱理解設計意圖。每規則只計一次。"""
    source = re.sub(r'<!--.*?-->|/\*.*?\*/|(?m:^\s*//[^\n]*)', '', source, flags=re.S)
    rules = [
        ('SLOP-M01', '漸層置中', r'(?=.*(?:linear|radial)-gradient\s*\()(?=.*(?:text-align\s*:\s*center|justify-content\s*:\s*center))'),
        ('SLOP-M02', '同步淡入候選', r'(?:transition\s*:[^;}]*opacity|animation\s*:[^;}]*fade)'),
        ('SLOP-M03', '浮誇陰影候選', r'(?:shadow-2xl|box-shadow\s*:[^;}]*\b(?:25|50)px)'),
        ('SLOP-M04', '線性/無阻尼候選', r'(?:(?:transition|animation)(?:-timing-function)?\s*:[^;}]*\blinear\b|alternate\s+infinite)'),
        ('SLOP-M05', '隨機數字/粒子候選', r'Math\s*\.\s*random\s*\('),
    ]
    return [SlopViolation(key, name, '需人工確認；本 repo 採保守阻擋')
            for key, name, pattern in rules if re.search(pattern, source, re.S | re.I)]


def analyze_image_luminance(image_path):
    Image, _, ImageStat = pillow()
    try:
        with Image.open(image_path) as image:
            stats = ImageStat.Stat(image.convert('L'))
            mean, std = stats.mean[0], stats.stddev[0]
            return mean, std, ['blank: 灰階標準差 < 1'] if std < 1 else []
    except (OSError, ValueError) as exc:
        return None, None, [f'corrupt: 影格解析失敗 {exc}']


def pixel_difference(first, second):
    """平均每 RGB channel 絕對差，保留位置資訊，不比較平均亮度代替。"""
    Image, ImageChops, ImageStat = pillow()
    with Image.open(first) as a, Image.open(second) as b:
        if a.size != b.size:
            raise ValueError('影格尺寸不一致')
        return sum(ImageStat.Stat(ImageChops.difference(a.convert('RGB'), b.convert('RGB'))).mean) / 3


def contrast_ratio(foreground, background):
    def luminance(color):
        values = [v / 255 for v in color[:3]]
        values = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
        return sum(a * b for a, b in zip(values, (.2126, .7152, .0722)))
    a, b = sorted((luminance(foreground), luminance(background)))
    return (b + .05) / (a + .05)


# 每個文字節點用 Range 取實際行框，避免父子元素重複計數。
TEXT_METRICS = r"""() => {
 const boxes=[];
 const cx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
 const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
 let n, nid=0;
 while(n=walker.nextNode()) {
  nid++;
  const e=n.parentElement;
  if(!n.textContent.trim() || !e || e.closest('script,style,noscript,svg')) continue;
  const s=getComputedStyle(e);
  let alpha=1, hidden=false, clipped=false;
  for(let p=e;p;p=p.parentElement) {
   const c=getComputedStyle(p); alpha*=Number(c.opacity);
   hidden ||= c.display==='none'||c.visibility==='hidden';
  }
  if(hidden || alpha===0) continue;
  const range=document.createRange(); range.selectNodeContents(n);
  for(const r of range.getClientRects()) {
   if(!r.width || !r.height) continue;
   clipped=false;
   for(let p=e.parentElement;p;p=p.parentElement) {
    const c=getComputedStyle(p), q=p.getBoundingClientRect();
    if(/hidden|clip|scroll|auto/.test(c.overflowX) && (r.left<q.left || r.right>q.right)) clipped=true;
    if(/hidden|clip|scroll|auto/.test(c.overflowY) && (r.top<q.top || r.bottom>q.bottom)) clipped=true;
   }
   // 由瀏覽器把任何 CSS 色彩語法（rgb、oklch、color-mix 等）換成 sRGB 8 位元，避免自行剖析字串。
   cx.clearRect(0,0,1,1); cx.fillStyle='#000'; cx.fillStyle=s.color; cx.fillRect(0,0,1,1);
   const d=cx.getImageData(0,0,1,1).data;
   boxes.push({nid,text:n.textContent.trim().slice(0,80),x:r.x,y:r.y,w:r.width,h:r.height,
     color:s.color,rgba:[d[0],d[1],d[2],d[3]/255],alpha,clipped});
  }
 }
 return boxes;
}"""


OVERLAP_RATIO = 0.25  # 本 repo 的取捨：交集面積超過較小行框的 25% 才算碰撞，容許緊行距的相鄰行框


def boxes_collide(a, b):
    """同一文字節點自己的換行不算碰撞；不同節點的行框交集面積超過較小者的 OVERLAP_RATIO 才算。"""
    if a.get('nid') is not None and a.get('nid') == b.get('nid'):
        return False
    width = min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x'])
    height = min(a['y'] + a['h'], b['y'] + b['h']) - max(a['y'], b['y'])
    if width <= 0 or height <= 0:
        return False
    return width * height > OVERLAP_RATIO * min(a['w'] * a['h'], b['w'] * b['h'])


# seek 契約要求頁面不自己跑計時器。載入前包住計時 API 計數；閒置時仍持續排程或有 CSS 動畫在播就是違規。
# 比對正反向像素只能機率性抓到自走動畫（兩次截圖剛好同相位會漏），所以另外直接計數。
TIMER_PROBE = r"""(() => {
 const w=window, n=w.__motionNative={setTimeout:w.setTimeout.bind(w),clearTimeout:w.clearTimeout.bind(w)};
 const log=w.__motionTimers={interval:0,raf:0,timeout:0};
 const si=w.setInterval.bind(w), raf=w.requestAnimationFrame.bind(w), st=w.setTimeout.bind(w);
 w.setInterval=(...a)=>{log.interval++;return si(...a)};
 w.requestAnimationFrame=(...a)=>{log.raf++;return raf(...a)};
 w.setTimeout=(...a)=>{log.timeout++;return st(...a)};
})();"""

IDLE_MS = 300
IDLE_LIMIT = 3  # 本 repo 的取捨：閒置 300ms 內排程 >=3 次視為自走迴圈


def check_idle_contract(page):
    """seek 完成後頁面應該靜止：沒有 setInterval、沒有持續的 rAF/setTimeout 迴圈、沒有播放中的 CSS/Web 動畫。"""
    page.evaluate("() => { const t=window.__motionTimers; t.raf=0; t.timeout=0; }")
    page.wait_for_timeout(IDLE_MS)
    state = page.evaluate("""() => ({timers: window.__motionTimers,
      running: document.getAnimations().filter(a => a.playState === 'running').length})""")
    errors = []
    timers = state['timers']
    if timers['interval']:
        errors.append(f"timer: 頁面呼叫了 setInterval {timers['interval']} 次（seek 契約禁止自動計時器）")
    if timers['raf'] >= IDLE_LIMIT:
        errors.append(f"timer: 閒置 {IDLE_MS}ms 內仍排程 requestAnimationFrame {timers['raf']} 次（自走迴圈）")
    if timers['timeout'] >= IDLE_LIMIT:
        errors.append(f"timer: 閒置 {IDLE_MS}ms 內仍排程 setTimeout {timers['timeout']} 次（自走迴圈）")
    if state['running']:
        errors.append(f"autoplay: seek 完成後仍有 {state['running']} 個 CSS/Web 動畫在播放（應以暫停動畫加 currentTime 由 seek 控制）")
    return errors


def measure_text(boxes, background_bytes, viewport):
    Image, _, _ = pillow()
    issues = []
    with Image.open(io.BytesIO(background_bytes)) as image:
        rgb = image.convert('RGB')
        for i, box in enumerate(boxes):
            x, y, w, h = (box[k] for k in ('x', 'y', 'w', 'h'))
            if box['clipped'] or x < 0 or y < 0 or x + w > viewport[0] or y + h > viewport[1]:
                issues.append(f'layout: 文字框 {i} 超出畫面或被裁切')
            for j, other in enumerate(boxes[:i]):
                if boxes_collide(box, other):
                    issues.append(f'layout: 文字框 {i} 與 {j} 碰撞')
            rgba = box.get('rgba')
            if not (isinstance(rgba, (list, tuple)) and len(rgba) == 4 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in rgba)):
                issues.append(f'contrast: 文字框 {i} 色彩無法量測')
                continue
            opacity = box['alpha'] * rgba[3]
            # 隱藏文字後，在行框的左、中、右量背景；採最差比值。
            ratios = []
            for fraction in (.1, .5, .9):
                px = min(rgb.width-1, max(0, int(x + w*fraction)))
                py = min(rgb.height-1, max(0, int(y + h*.5)))
                bg = rgb.getpixel((px, py))
                fg = [a*opacity + b*(1-opacity) for a, b in zip(rgba[:3], bg)]
                ratios.append(contrast_ratio(fg, bg))
            box['contrast_ratio'] = min(ratios)
            if box['contrast_ratio'] < 4.5:
                issues.append(f'contrast: 文字框 {i} 對比 {box["contrast_ratio"]:.3f} < 4.5')
    return issues


def extract_keyframes_playwright(html_path, timestamps_ms, output_dir, viewport=(1280, 720), preferred_channel=None):
    pillow()
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
    except ImportError as exc:
        raise DependencyError('缺少 Playwright：python -m pip install playwright；python -m playwright install chromium') from exc
    timeout = positive_env('AI_INBOX_MOTION_TIMEOUT_MS', 15000)
    frames, errors = [], []
    output_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, channel=preferred_channel, timeout=timeout)
        except BrowserTimeout as exc:
            raise IncompleteError('INCOMPLETE: 瀏覽器啟動逾時') from exc
        except Exception as exc:
            raise DependencyError(f'瀏覽器不可用，請安裝 Chromium 或指定 --channel：{exc}') from exc
        try:
            page = browser.new_page(viewport={'width': viewport[0], 'height': viewport[1]}, device_scale_factor=1)
            page.set_default_timeout(timeout)
            page.on('pageerror', lambda error: errors.append(f'pageerror: {error}'))
            page.on('console', lambda message: errors.append(f'console: {message.text}') if message.type == 'error' else None)
            page.add_init_script(TIMER_PROBE)
            page.goto(html_path.resolve().as_uri(), wait_until='load', timeout=timeout)
            page.evaluate('() => document.fonts.ready')
            has_seek = page.evaluate("() => typeof window.seek === 'function'")
            if not has_seek:
                errors.append('runtime: 缺少 window.seek(t)')
                return frames, errors

            def seek(t_ms):
                # evaluate 本身沒有 timeout；在頁面端限制非同步 seek。
                page.evaluate('''async ([t, timeout]) => {
                  let timer;
                  const native = window.__motionNative;
                  try { await Promise.race([Promise.resolve(window.seek(t)), new Promise((_, reject) => {
                    timer=native.setTimeout(()=>reject(new Error('MOTION_INCOMPLETE_TIMEOUT')),timeout);
                  })]); } finally { native.clearTimeout(timer); }
                }''', [t_ms, timeout])

            for idx, t_ms in enumerate(timestamps_ms):
                seek(t_ms)
                frame_file = output_dir / f'frame_{idx:04d}.png'
                page.screenshot(path=str(frame_file), full_page=False)
                mean, std, issues = analyze_image_luminance(frame_file)
                boxes = page.evaluate(TEXT_METRICS)
                style = page.add_style_tag(content='*{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important}')
                try:
                    background = page.screenshot(full_page=False)
                finally:
                    style.evaluate('(element) => element.remove()')
                issues.extend(measure_text(boxes, background, viewport))
                frames.append(FrameInfo(idx, t_ms, str(frame_file), mean, std, text_boxes=boxes, issues=issues))
            # 逆序重訪每個 t，與先前正序影格比較。
            for frame in reversed(frames):
                seek(frame.timestamp_ms)
                repeat = output_dir / f'reverse_{frame.frame_index:04d}.png'
                page.screenshot(path=str(repeat), full_page=False)
                frame.seek_delta = pixel_difference(frame.file_path, repeat)
                if frame.seek_delta != 0:
                    frame.issues.append('seek: 同一時間正反向像素不一致')
            for previous, frame in zip(frames, frames[1:]):
                frame.pixel_delta = pixel_difference(previous.file_path, frame.file_path)
                if frame.pixel_delta == 0:
                    frame.issues.append('static: 相鄰影格完全相同')
            errors.extend(check_idle_contract(page))
        except BrowserTimeout as exc:
            raise IncompleteError('INCOMPLETE: 頁面操作逾時') from exc
        except Exception as exc:
            if 'MOTION_INCOMPLETE_TIMEOUT' in str(exc):
                raise IncompleteError('INCOMPLETE: seek 逾時') from exc
            errors.append(f'capture: {exc}')
        finally:
            browser.close()
    return frames, errors


def calculate_frame_scores(frames, anti_slop_violations, has_seek_defined=True):
    for frame in frames:
        frame.scores = {
            'layout': max(0, 2.5 - sum(i.startswith('layout:') for i in frame.issues)),
            'contrast': 0.0 if any(i.startswith(('contrast:', 'blank:', 'corrupt:')) for i in frame.issues) else 2.5,
            'motion': 0.0 if any(i.startswith(('static:', 'seek:')) for i in frame.issues) else 2.5,
            'anti_slop': max(0, 2.5 - len(anti_slop_violations) * 1.0),
        }
        frame.total_score = round(sum(frame.scores.values()), 2) if has_seek_defined else 0.0
        if frame.mean_luminance is None or frame.seek_delta is None:
            frame.total_score = 0.0


def generate_contact_sheet_image(frames, output_path):
    Image, _, _ = pillow()
    from PIL import ImageDraw
    sheet = Image.new('RGB', (960, math.ceil(len(frames)/3)*205), '#222222')
    draw = ImageDraw.Draw(sheet)
    for idx, frame in enumerate(frames):
        with Image.open(frame.file_path) as image:
            image = image.convert('RGB'); image.thumbnail((320, 180))
            x, y = (idx % 3)*320, (idx//3)*205
            sheet.paste(image, (x, y))
            draw.text((x+5, y+182), f'#{idx} t={frame.timestamp_ms:g}ms score={frame.total_score:g}', fill='white')
    sheet.save(output_path)
    return str(output_path)


def positive_env(name, default):
    value = int(os.environ.get(name, default))
    if not 1 <= value <= 3600000:
        raise ValueError(f'{name} 必須為 1..3600000')
    return value


class Watchdog:
    """整體逾時保險：page.evaluate 沒有逾時，同步無窮迴圈的 seek 會讓行程永遠卡住。
    逾時就印 INCOMPLETE 並以 exit 3 結束（Playwright driver 隨 stdin 關閉回收瀏覽器）。"""

    def __init__(self):
        self.seconds = positive_env('AI_INBOX_MOTION_TOTAL_TIMEOUT_S', 600)
        self.timer = threading.Timer(self.seconds, self.expire)
        self.timer.daemon = True

    def expire(self):
        print(f'INCOMPLETE: 整體逾時 {self.seconds} 秒（可能是 seek 同步無窮迴圈）；不是通過', file=sys.stderr, flush=True)
        os._exit(3)

    def __enter__(self):
        self.timer.start()
        return self

    def __exit__(self, *exc):
        self.timer.cancel()


def validate(duration, count, timestamps, min_score):
    if not math.isfinite(duration) or not 0 < duration <= 600000:
        raise ValueError('--duration 必須為有限值，0 < ms <= 600000')
    if not 2 <= count <= 120:
        raise ValueError('--frames 必須為 2..120')
    if not math.isfinite(min_score) or not 8 <= min_score <= 10:
        raise ValueError('--min-score 必須為 8..10，不可放寬品質閘門')
    if timestamps is not None and (not 2 <= len(timestamps) <= 120 or any(not math.isfinite(t) or not 0 <= t <= duration for t in timestamps) or timestamps != sorted(set(timestamps))):
        raise ValueError('--timestamps 須有 2..120 個嚴格遞增有限值，位於 0..duration')


def audit_motion_storyboard(html_path, duration_ms=3000., frames_count=6, timestamps=None, output_dir=None, min_score=8., preferred_channel=None):
    validate(duration_ms, frames_count, timestamps, min_score)
    pillow()
    html_path = Path(html_path)
    source = html_path.read_text(encoding='utf-8')
    violations = check_html_anti_slop(source)
    output_dir = Path(output_dir) if output_dir else html_path.parent/'artifacts'/'storyboard_audit'
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamps = timestamps if timestamps is not None else [i*duration_ms/(frames_count-1) for i in range(frames_count)]
    frames, errors = extract_keyframes_playwright(html_path, timestamps, output_dir, preferred_channel=preferred_channel)
    if len(frames) != len(timestamps):
        errors.append('capture: 未取得全部影格')
    calculate_frame_scores(frames, violations)
    sheet = ''
    if frames:
        try:
            sheet = generate_contact_sheet_image(frames, output_dir/'contact_sheet.png')
            if not sheet or not Path(sheet).is_file():
                errors.append('contact-sheet: PNG 未產生')
        except (OSError, ValueError) as exc:
            errors.append(f'contact-sheet: {exc}')
    scores = [f.total_score for f in frames]
    # 任何量測失敗都是硬閘門，不允許靠其他維度抵消。
    passed = bool(frames) and not errors and not violations and not any(f.issues for f in frames) and min(scores) >= min_score
    report = AuditReport(str(html_path), passed, min_score, min(scores, default=0), round(sum(scores)/len(scores), 2) if scores else 0,
                         [asdict(f) for f in sorted(frames, key=lambda f: f.total_score)[:3]],
                         [asdict(f) for f in frames], [asdict(v) for v in violations], errors, sheet)
    output_dir.mkdir(parents=True, exist_ok=True)
    report.contact_sheet_html = str(output_dir/'contact_sheet.html')
    body = ''.join(f'<figure><img width="320" src="{Path(f.file_path).name}"><figcaption>t={f.timestamp_ms:g}ms score={f.total_score:g} {html.escape(str(f.issues))}</figcaption></figure>' for f in frames)
    Path(report.contact_sheet_html).write_text('<!doctype html><meta charset="utf-8"><title>Motion audit</title>'+f'<h1>{"PASS" if passed else "FAIL"}</h1>'+body+f'<pre>{html.escape(str(errors))}</pre>', encoding='utf-8')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', type=Path)
    parser.add_argument('--duration', type=float, default=3000.)
    parser.add_argument('--frames', type=int, default=6)
    parser.add_argument('--timestamps')
    parser.add_argument('--min-score', type=float, default=8.)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--channel', choices=['chrome', 'msedge'])
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        timestamps = [float(t) for t in args.timestamps.split(',')] if args.timestamps is not None else None
        with Watchdog():
            report = audit_motion_storyboard(args.target, args.duration, args.frames, timestamps, args.output_dir, args.min_score, args.channel)
    except IncompleteError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except (DependencyError, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2) if args.json else f'[{"PASS" if report.passed else "FAIL"}] min={report.lowest_score:g}\n{report.contact_sheet_html}')
    return 0 if report.passed else 1


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(main())
