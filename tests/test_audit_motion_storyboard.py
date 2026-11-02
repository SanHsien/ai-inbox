"""真實像素、反例與 CLI 契約。瀏覽器預設 skip；AI_INBOX_BROWSER_TESTS=1 才執行。"""
from __future__ import annotations
import concurrent.futures
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import audit_motion_storyboard as motion

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools/audit_motion_storyboard.py'
HAS_PIL = importlib.util.find_spec('PIL') is not None
HAS_PLAYWRIGHT = importlib.util.find_spec('playwright') is not None


def page(body='', style='', script='window.seek=function(t){};'):
    return '<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#123;color:white}'+style+'</style>'+body+'<script>'+script+'</script>'


MOVING = page('<h1 style="position:absolute;left:80px;top:30px">Motion test</h1><div id="box" style="position:absolute;top:240px;width:150px;height:150px;background:white"></div>',
              script="window.seek=function(t){document.getElementById('box').style.left=(80+t/5)+'px'};")


class UnitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='motion_unit_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def require_pillow(self):
        if not HAS_PIL:
            self.skipTest('缺少 Pillow，未執行像素測試')
        from PIL import Image
        return Image

    def test_luminance_and_corrupt(self):
        Image = self.require_pillow()
        for value in (0, 128, 255):
            path = self.root / 'image.png'
            Image.new('RGB', (32,32), (value,)*3).save(path)
            mean, std, issues = motion.analyze_image_luminance(path)
            self.assertEqual(mean, value)
            self.assertEqual(std, 0)
            self.assertTrue(issues)
        path.write_bytes(b'broken PNG')
        self.assertEqual(motion.analyze_image_luminance(path)[:2], (None,None))
        self.assertIn('corrupt:', motion.analyze_image_luminance(path)[2][0])
        frame = motion.FrameInfo(0, 0, str(path), issues=motion.analyze_image_luminance(path)[2])
        motion.calculate_frame_scores([frame], [])
        self.assertEqual(frame.total_score, 0)

    def test_pixels_same_statistics_but_moving(self):
        Image = self.require_pillow()
        a, b = Image.new('RGB',(20,20)), Image.new('RGB',(20,20))
        a.paste('white',(0,0,5,5)); b.paste('white',(10,10,15,15))
        first, second = self.root/'a.png', self.root/'b.png'
        a.save(first); b.save(second)
        self.assertEqual(motion.analyze_image_luminance(first)[:2], motion.analyze_image_luminance(second)[:2])
        self.assertGreater(motion.pixel_difference(first,second), 0)
        self.assertEqual(motion.pixel_difference(first,first), 0)

    def test_anti_slop_score_and_comments(self):
        snippets = ['body{background:linear-gradient(red,green);text-align:center}', '.a{transition:opacity .5s}',
                    '.a{box-shadow:0 25px 50px black}', '.a{transition:transform 1s linear}',
                    "n.textContent=Math.floor(Math.random()*100)"]
        for i, snippet in enumerate(snippets,1):
            with self.subTest(rule=i):
                violations = motion.check_html_anti_slop(snippet)
                self.assertEqual([v.rule_id for v in violations], [f'SLOP-M0{i}'])
                frame = motion.FrameInfo(0,0,mean_luminance=100,contrast_std=30,seek_delta=0)
                motion.calculate_frame_scores([frame],violations)
                self.assertEqual(frame.scores['anti_slop'],1.5)
                self.assertEqual(frame.total_score,9)
        self.assertEqual(motion.check_html_anti_slop('<!-- elevate Math.random() --><script>/* Math.random() */\n// Math.random()\n</script>'),[])
        self.assertEqual(motion.check_html_anti_slop('<h1>elevate 🚀</h1>'),[])

    def test_parameters(self):
        # 目標檔存在、且瀏覽器擷取一旦被呼叫就直接報錯：確保 exit 2 真的來自參數驗證，不是來自檔案不存在
        target = self.root/'page.html'; target.write_text(MOVING,encoding='utf-8')
        cases = [('--frames','0'),('--frames','-3'),('--frames','1'),('--frames','121'),
                 ('--duration','-100'),('--duration','0'),('--duration','nan'),('--duration','inf'),
                 ('--duration','600001'),('--timestamps','NaN'),('--timestamps',','),
                 ('--timestamps','0,0'),('--timestamps','100,0'),('--timestamps','0,99999'),
                 ('--timestamps','-1,100'),('--timestamps','0'),('--min-score','0'),('--min-score','nan'),('--min-score','7.9'),('--min-score','11')]
        with patch.object(motion,'extract_keyframes_playwright',side_effect=AssertionError('參數驗證應在開瀏覽器前擋下')):
            for option,value in cases:
                with self.subTest(option=option,value=value), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(motion.main([str(target),option,value]),2)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(motion.main([str(self.root/'missing.html')]),2)

    def test_dependencies_exit_two(self):
        target = self.root/'page.html'; target.write_text(MOVING,encoding='utf-8')
        with patch.dict(sys.modules,{'PIL':None}), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(motion.main([str(target),'--output-dir',str(self.root/'out')]),2)

    def test_missing_playwright_exit_two(self):
        self.require_pillow()
        target = self.root/'page.html'; target.write_text(MOVING,encoding='utf-8')
        with patch.dict(sys.modules,{'playwright':None,'playwright.sync_api':None}), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(motion.main([str(target),'--output-dir',str(self.root/'out')]),2)

    def test_incomplete_exit_three(self):
        self.require_pillow()
        target = self.root/'page.html'; target.write_text(MOVING,encoding='utf-8')
        with patch.object(motion,'extract_keyframes_playwright',side_effect=motion.IncompleteError('INCOMPLETE: timeout')), contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(motion.main([str(target),'--output-dir',str(self.root/'out')]),3)
        self.assertIn('INCOMPLETE',stderr.getvalue())

    def test_errors_are_hard_gate_and_png_exists(self):
        Image = self.require_pillow()
        target = self.root/'page.html'; target.write_text(MOVING,encoding='utf-8')
        image = Image.new('RGB',(40,40),'black'); image.paste('white',(0,0,20,20))
        filename=self.root/'valid.png'; image.save(filename)
        frames=[motion.FrameInfo(i,i*100,str(filename),120,40,seek_delta=0) for i in range(2)]
        with patch.object(motion,'extract_keyframes_playwright',return_value=(frames,['console: deliberate error'])):
            report=motion.audit_motion_storyboard(target,frames_count=2,output_dir=self.root/'out')
        self.assertFalse(report.passed)
        self.assertEqual(report.lowest_score,10)
        self.assertTrue(report.errors)
        with Image.open(report.contact_sheet_image) as sheet:
            sheet.load(); self.assertEqual(sheet.size,(960,205))

    def test_text_measurements(self):
        Image = self.require_pillow()
        raw=io.BytesIO(); Image.new('RGB',(200,100),'black').save(raw,format='PNG')
        def box(x=10,y=10,rgba=(255,255,255,1),nid=1):
            return dict(nid=nid,x=x,y=y,w=80,h=30,color='unused',rgba=list(rgba),alpha=1,clipped=False)
        good=box()
        self.assertEqual(motion.measure_text([good],raw.getvalue(),(200,100)),[])
        self.assertEqual(good['contrast_ratio'],21)
        self.assertTrue(any('碰撞' in s for s in motion.measure_text([box(),box(20,nid=2)],raw.getvalue(),(200,100))))
        self.assertTrue(any('超出' in s for s in motion.measure_text([box(180)],raw.getvalue(),(200,100))))
        self.assertTrue(any('contrast:' in s for s in motion.measure_text([box(rgba=(1,1,1,1))],raw.getvalue(),(200,100))))
        # 半透明文字要與背景合成後再量，不能拿原始顏色當結果
        self.assertTrue(any('contrast:' in s for s in motion.measure_text([box(rgba=(255,255,255,.05))],raw.getvalue(),(200,100))))
        # 瀏覽器沒給可用 sRGB 值時算量測失敗，不可預設通過
        for bad in (None,[1,2,3],[float('nan'),0,0,1],'rgb(1,2,3)'):
            unreadable=box(); unreadable['rgba']=bad
            self.assertTrue(any('無法量測' in s for s in motion.measure_text([unreadable],raw.getvalue(),(200,100))),bad)
        missing=box(); del missing['rgba']
        self.assertTrue(any('無法量測' in s for s in motion.measure_text([missing],raw.getvalue(),(200,100))))

    def test_collision_rule_tolerates_leading_but_not_overlap(self):
        def box(x,y,nid,w=100,h=40):
            return dict(nid=nid,x=x,y=y,w=w,h=h)
        # 同一文字節點自己的換行（含完全重疊的行框）不是作者排版錯誤
        self.assertFalse(motion.boxes_collide(box(0,0,1),box(0,0,1)))
        # 不同節點、緊行距（交集高度 6px / 40px = 15%）不算
        self.assertFalse(motion.boxes_collide(box(0,0,1),box(0,34,2)))
        # 不同節點、明顯重疊算
        self.assertTrue(motion.boxes_collide(box(0,0,1),box(4,8,2)))
        self.assertTrue(motion.boxes_collide(box(0,0,1),box(0,20,2)))
        # 只是貼邊或分開不算
        self.assertFalse(motion.boxes_collide(box(0,0,1),box(100,0,2)))
        self.assertFalse(motion.boxes_collide(box(0,0,1),box(0,40,2)))

    def test_corrupt_frame_fails_audit(self):
        Image = self.require_pillow()
        target = self.root/'page.html'; target.write_text(MOVING,encoding='utf-8')
        bad=self.root/'bad.png'; bad.write_bytes(b'broken PNG')
        mean,std,issues=motion.analyze_image_luminance(bad)
        frames=[motion.FrameInfo(i,i*100,str(bad),mean,std,seek_delta=0,issues=list(issues)) for i in range(2)]
        with patch.object(motion,'extract_keyframes_playwright',return_value=(frames,[])):
            report=motion.audit_motion_storyboard(target,frames_count=2,output_dir=self.root/'out')
        self.assertFalse(report.passed)
        self.assertEqual(report.lowest_score,0)
        self.assertTrue(any('contact-sheet' in e for e in report.errors),report.errors)

    def test_missing_pillow_gives_no_numbers(self):
        # 缺 Pillow 時不得回任何亮度數值（不可回 128/45 之類的假值）
        with patch.dict(sys.modules,{'PIL':None}):
            with self.assertRaises(motion.DependencyError):
                motion.analyze_image_luminance(self.root/'any.png')
            with self.assertRaises(motion.DependencyError):
                motion.pixel_difference(self.root/'a.png',self.root/'b.png')

    def test_unmeasured_is_reported_and_warned(self):
        Image = self.require_pillow()
        target = self.root/'page.html'; target.write_text(MOVING,encoding='utf-8')
        image = Image.new('RGB',(40,40),'black'); image.paste('white',(0,0,20,20))
        filename=self.root/'valid.png'; image.save(filename)
        def frames():
            return [motion.FrameInfo(i,i*100,str(filename),120,40,seek_delta=0,pixel_delta=None if i == 0 else 1,
                                     unmeasured=[{'kind':'svg_text','count':2}] + ([{'kind':'canvas_text','count':5}] if i else []))
                    for i in range(3)]
        with patch.object(motion,'extract_keyframes_playwright',return_value=(frames(),[])):
            report=motion.audit_motion_storyboard(target,frames_count=3,output_dir=self.root/'out')
        kinds={item['kind']:item for item in report.unmeasured}
        self.assertEqual(set(kinds),{'svg_text','canvas_text'})
        self.assertEqual(kinds['svg_text']['frames'],[0,1,2])
        self.assertEqual(kinds['canvas_text']['frames'],[1,2])
        self.assertEqual(kinds['canvas_text']['count'],5)
        self.assertIn('未量測',Path(report.contact_sheet_html).read_text(encoding='utf-8'))
        with patch.object(motion,'extract_keyframes_playwright',return_value=(frames(),[])), contextlib.redirect_stderr(io.StringIO()) as stderr, contextlib.redirect_stdout(io.StringIO()) as stdout:
            code=motion.main([str(target),'--frames','3','--output-dir',str(self.root/'out2'),'--json'])
        self.assertEqual(code,0)  # 依指示：標示未量測並警告，不改變品質閘門
        self.assertIn('[WARN] 未量測',stderr.getvalue())
        self.assertIn('SVG 文字',stderr.getvalue())
        self.assertEqual(len(json.loads(stdout.getvalue())['unmeasured']),2)
        clean=[motion.FrameInfo(i,i*100,str(filename),120,40,seek_delta=0,pixel_delta=None if i == 0 else 1) for i in range(3)]
        with patch.object(motion,'extract_keyframes_playwright',return_value=(clean,[])):
            self.assertEqual(motion.audit_motion_storyboard(target,frames_count=3,output_dir=self.root/'out3').unmeasured,[])

    def test_total_timeout_watchdog_exits_three(self):
        calls=[]
        with patch.dict(os.environ,{'AI_INBOX_MOTION_TOTAL_TIMEOUT_S':'1'}), patch.object(motion.os,'_exit',side_effect=calls.append), contextlib.redirect_stderr(io.StringIO()) as stderr:
            with motion.Watchdog():
                time.sleep(1.6)
        self.assertEqual(calls,[3])
        self.assertIn('INCOMPLETE',stderr.getvalue())
        calls.clear()
        with patch.dict(os.environ,{'AI_INBOX_MOTION_TOTAL_TIMEOUT_S':'1'}), patch.object(motion.os,'_exit',side_effect=calls.append):
            with motion.Watchdog():
                pass
            time.sleep(1.4)
        self.assertEqual(calls,[],'正常結束後計時器必須取消')
        with patch.dict(os.environ,{'AI_INBOX_MOTION_TOTAL_TIMEOUT_S':'0'}), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(motion.main([str(self.root/'missing.html')]),2)


class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get('AI_INBOX_BROWSER_TESTS') != '1':
            raise unittest.SkipTest('瀏覽器預設不跑；設 AI_INBOX_BROWSER_TESTS=1')
        if not HAS_PIL or not HAS_PLAYWRIGHT:
            raise unittest.SkipTest('缺少 Pillow 或 Playwright，未執行瀏覽器驗證')
        cls.timeout=motion.positive_env('AI_INBOX_MOTION_TEST_TIMEOUT_SECONDS',90)
        cls.workers=motion.positive_env('AI_INBOX_MOTION_TEST_WORKERS',1)
        cls.channel=os.environ.get('AI_INBOX_MOTION_TEST_CHANNEL','msedge' if os.name=='nt' else '')

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='motion_browser_')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def run_page(self,source,name='case',extra=(),env=None,expect_code=None):
        target=self.root/(name+'.html'); target.write_text(source,encoding='utf-8')
        out=self.root/name
        cmd=[sys.executable,str(TOOL),str(target),'--frames','3','--duration','1000','--output-dir',str(out),'--json',*extra]
        if self.channel: cmd += ['--channel',self.channel]
        code,stdout,error=self.run_command(cmd,env)
        self.last_error=error
        if expect_code is not None:
            self.assertEqual(code,expect_code,error)
            return code,error,out
        if code==3:
            raise unittest.SkipTest('INCOMPLETE: '+error)
        if code==2 and ('瀏覽器不可用' in error or '缺少' in error):
            raise unittest.SkipTest('依賴不可用：'+error[:300])
        self.assertIn(code,(0,1),error)
        return code,json.loads(stdout.decode('utf-8-sig')),out

    def run_command(self,cmd,env=None,timeout_fails=False):
        kwargs={} if os.name=='nt' else {'start_new_session':True}
        if env: kwargs['env']={**os.environ,**env}
        with subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kwargs) as process:
            try:
                stdout,stderr=process.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                # 只終止這個測試建立的程序樹，避免背景 Chromium 殘留。
                if os.name=='nt':
                    subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True)
                else:
                    os.killpg(process.pid,signal.SIGKILL)
                process.communicate()
                # 被測程式自己應該在逾時內結束（exit 3）；測試行程等不到就是被測程式的缺陷，不是機器忙
                if timeout_fails:
                    self.fail(f'被測程式在 {self.timeout}s 內沒有自行結束')
                raise unittest.SkipTest(f'INCOMPLETE: 瀏覽器測試逾時 {self.timeout}s；不是通過或失敗')
        error=stderr.decode('utf-8',errors='replace')
        return process.returncode,stdout,error

    def test_good_pixels_and_contact_sheet(self):
        code,report,out=self.run_page(MOVING)
        self.assertEqual(code,0,report)
        self.assertTrue(report['passed'])
        self.assertEqual(len(report['frames']),3)
        from PIL import Image,ImageChops,ImageStat
        for frame in report['frames']:
            self.assertEqual(frame['seek_delta'],0)
            self.assertEqual(frame['issues'],[])
            self.assertGreater(frame['text_boxes'][0]['contrast_ratio'],4.5)
            with Image.open(frame['file_path']) as a, Image.open(out/f'reverse_{frame["frame_index"]:04d}.png') as b:
                self.assertIsNone(ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox())
        with Image.open(report['frames'][0]['file_path']) as a,Image.open(report['frames'][1]['file_path']) as b:
            self.assertGreater(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean),0)
        for frame in report['frames'][1:]: self.assertGreater(frame['pixel_delta'],0)
        with Image.open(report['contact_sheet_image']) as sheet:
            sheet.load(); self.assertEqual(sheet.size,(960,205))
        self.assertEqual(len(report['worst_3_frames']),3)
        self.assertTrue(Path(report['contact_sheet_html']).is_file())

    def check_bad_cases(self,cases):
        def run(item):
            name,source,expected=item
            code,report,_=self.run_page(source,name)
            return name,code,report,expected
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as pool:
            for name,code,report,expected in pool.map(run,cases):
                with self.subTest(case=name):
                    self.assertEqual(code,1,report)
                    self.assertFalse(report['passed'])
                    messages=report['errors']+[i for f in report['frames'] for i in f['issues']]
                    self.assertTrue(any(expected in i for i in messages),(expected,messages))

    def test_blank_and_static(self):
        self.check_bad_cases([(name,page(style=f'body{{background:{color}}}'),'blank:') for name,color in [('black','#000'),('white','#fff'),('gray','#808080'),('dark','#090d16')]]+
                             [('static',MOVING.replace("(80+t/5)","80"),'static:')])

    def test_impure_seek(self):
        self.check_bad_cases([('accumulate',MOVING.replace('window.seek=function(t){','let x=0;window.seek=function(t){x+=137;').replace('(80+t/5)', '(x%1000)'),'seek:'),
                             ('random',MOVING.replace('(80+t/5)','(Math.random()*800)'),'seek:'),
                             ('timer',MOVING.replace("window.seek=function(t)","setInterval(()=>{document.getElementById('box').style.top=Math.random()*400+'px'},16);window.seek=function(t)"),'seek:')])

    def test_layout_contrast(self):
        self.check_bad_cases([
            ('overlap',MOVING.replace('<div id=', '<h1 style="position:absolute;left:85px;top:35px">Collision</h1><div id='),'layout:'),
            ('offscreen',MOVING.replace('left:80px;top:30px','left:1200px;top:700px'),'layout:'),
            ('lowcontrast',MOVING.replace('color:white','color:#112234'),'contrast:'),
            ('opacity',MOVING.replace('<h1 style="','<h1 style="opacity:.02;'),'contrast:'),
            ('clipped',MOVING.replace('<h1 style=', '<section style="overflow:hidden;width:100px;height:20px"><h1 style=').replace('</h1>','</h1></section>'),'layout:')])

    def test_legitimate_text_is_not_flagged(self):
        # 緊行距的多行標題、瀏覽器新色彩語法的淺色文字，都是合法設計，不可誤報
        wrapped=MOVING.replace('<h1 style="position:absolute;left:80px;top:30px">Motion test</h1>',
                               '<h1 style="position:absolute;left:80px;top:30px;width:300px;font:700 48px/1 sans-serif">Two line heading that wraps around</h1>')
        light=MOVING.replace('color:white','color:oklch(0.97 0.01 250)')
        for name,source in [('wrapped',wrapped),('oklch_light',light)]:
            with self.subTest(case=name):
                code,report,_=self.run_page(source,name)
                self.assertEqual(code,0,report)
                self.assertGreaterEqual(len(report['frames'][0]['text_boxes']),1)
                if name=='wrapped':
                    self.assertGreaterEqual(len(report['frames'][0]['text_boxes']),2,'換行標題要量到多個行框，否則通過沒有意義')

    def test_unmeasured_text_is_reported(self):
        # SVG 文字、Canvas 文字、被蓋住的文字工具量不到：不改變 exit code，但報告必須有「未量測」欄位並印警告
        svg=MOVING.replace('<div id="box"','<svg width="600" height="100" style="position:absolute;left:80px;top:130px"><text x="10" y="60" font-size="40" fill="#123">svg text</text></svg><div id="box"')
        canvas=MOVING.replace('<div id="box"','<canvas id="cv" width="600" height="100" style="position:absolute;left:80px;top:130px"></canvas><div id="box"').replace(
            "window.seek=function(t){","const cx=document.getElementById('cv').getContext('2d');window.seek=function(t){cx.clearRect(0,0,600,100);cx.fillStyle='#123';cx.font='40px sans-serif';cx.fillText('canvas text',10,60);")
        covered=MOVING.replace('<div id="box"','<h2 style="position:absolute;left:80px;top:150px;margin:0">Covered</h2><div style="position:absolute;left:60px;top:140px;width:500px;height:80px;background:#000"></div><div id="box"')
        for name,source,kind in [('svg',svg,'svg_text'),('canvas',canvas,'canvas_text'),('covered',covered,'occluded_text')]:
            with self.subTest(case=name):
                code,report,_=self.run_page(source,'um_'+name)
                self.assertEqual(code,0,report)
                self.assertIn(kind,[item['kind'] for item in report['unmeasured']])
                self.assertIn('[WARN] 未量測',self.last_error)
        code,report,_=self.run_page(MOVING,'um_clean')
        self.assertEqual(report['unmeasured'],[])
        self.assertNotIn('[WARN]',self.last_error)

    def test_oklch_dark_text_fails_contrast(self):
        self.check_bad_cases([('oklch_dark',MOVING.replace('color:white','color:oklch(0.2 0.02 250)'),'contrast:')])

    def test_autonomous_animation_with_noop_seek(self):
        # 頁面自己跑計時器或 CSS 動畫：即使 seek 沒做事、畫面看似在動，也必須失敗（直接計數，不靠兩次截圖剛好不同）
        css=page('<h1 style="position:absolute;left:80px;top:30px">Autoplay</h1><div style="position:absolute;top:300px;width:100px;height:100px;background:#fff;animation:m 2s ease-in-out infinite"></div>',
                 '@keyframes m{from{left:0}to{left:800px}}')
        raf=MOVING.replace('</script>','let n=0;(function f(){n++;document.getElementById("box").style.top=(240+n%2*20)+"px";requestAnimationFrame(f)})()</script>')
        interval=MOVING.replace('</script>','let k=0;setInterval(()=>{k++;document.getElementById("box").style.top=(240+k%2*20)+"px"},50)</script>')
        chain=MOVING.replace('</script>','let q=0;(function g(){q++;document.getElementById("box").style.top=(240+q%2*20)+"px";setTimeout(g,30)})()</script>')
        self.check_bad_cases([('css_autoplay',css,'autoplay:'),('raf_loop',raf,'timer:'),('set_interval',interval,'timer:'),('timeout_chain',chain,'timer:')])

    def test_paused_web_animation_driven_by_seek_passes(self):
        # 合法寫法：CSS 動畫預設暫停，由 seek 用 currentTime 控制；不是自動播放
        driven=page('<h1 style="position:absolute;left:80px;top:30px">Driven</h1><div id="box" style="position:absolute;top:300px;width:100px;height:100px;background:#fff;animation:m 3s ease-in-out paused both"></div>',
                    '@keyframes m{from{left:0}to{left:800px}}',
                    "window.seek=function(t){for(const a of document.getAnimations()){a.currentTime=t}};window.seek(0);")
        code,report,_=self.run_page(driven,'driven')
        self.assertEqual(code,0,report)
        self.assertEqual(report['errors'],[])

    def test_sync_infinite_loop_is_incomplete(self):
        hang=page(script='window.seek=function(t){if(t>0){while(true){}}};')
        code,error,_=self.run_page(hang,'hang',env={'AI_INBOX_MOTION_TOTAL_TIMEOUT_S':'20'},expect_code=3)
        self.assertIn('INCOMPLETE',error)

    def test_errors(self):
        self.check_bad_cases([
            ('pageerror',MOVING.replace('</script>','undefinedFunctionCall();</script>'),'pageerror:'),
            ('console',MOVING.replace('</script>',"console.error('deliberate');</script>"),'console:'),
            ('throws',page(script="window.seek=function(){throw new Error('boom')}"),'capture:'),
            ('rejects',page(script="window.seek=function(){return Promise.reject(new Error('boom'))}"),'capture:')])

    def test_missing_runtime_seek(self):
        self.check_bad_cases([('missing',page(script='/* window.seek=function(t){} */'),'runtime: 缺少 window.seek'),
                             ('notfunction',page(script='window.seek=123;'),'runtime: 缺少 window.seek')])

    def test_slop(self):
        for name,style,rule in [('fade','.a{transition:opacity .5s}','SLOP-M02'),('linear','.a{transition:transform 1s linear}','SLOP-M04'),('gradient','body{background:linear-gradient(red,green);text-align:center}','SLOP-M01')]:
            with self.subTest(rule=rule):
                code,report,_=self.run_page(MOVING.replace('</style>',style+'</style>'),name)
                self.assertEqual(code,1)
                self.assertIn(rule,[v['rule_id'] for v in report['anti_slop_violations']])
        code,report,_=self.run_page(MOVING+'<!-- elevate 🚀 -->','benign')
        self.assertEqual(code,0,report)

    def test_document_examples(self):
        for name in ['docs/code-driven-motion-design-studio-spec.md','templates/motion-design-studio-skill.md']:
            with self.subTest(document=name):
                example=re.search(r'```html\n(.*?)```',(ROOT/name).read_text(encoding='utf-8'),re.S).group(1)
                code,report,_=self.run_page(example,Path(name).stem)
                self.assertEqual(code,0,report)

    def test_portable_export_sequence(self):
        document=(ROOT/'templates/motion-design-studio-skill.md').read_text(encoding='utf-8')
        script=re.search(r'```python\n(.*?)```',document,re.S).group(1)
        exporter=self.root/'render_frames.py'; exporter.write_text(script,encoding='utf-8')
        target=self.root/'index.html'; target.write_text(MOVING,encoding='utf-8')
        frames=self.root/'frames'
        command=[sys.executable,str(exporter),str(target),'--duration','1000','--fps','4','--output-dir',str(frames)]
        if self.channel: command += ['--channel',self.channel]
        code,_,error=self.run_command(command)
        self.assertEqual(code,0,error)
        self.assertEqual([p.name for p in sorted(frames.glob('*.png'))],[f'frame_{i:04d}.png' for i in range(4)])
        from PIL import Image,ImageChops
        with Image.open(frames/'frame_0000.png') as a,Image.open(frames/'frame_0003.png') as b:
            self.assertEqual(a.size,(1280,720))
            self.assertIsNotNone(ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox())
        code,_,_=self.run_command(command)
        self.assertEqual(code,2)  # 非空目錄不可混入舊序列。

    def test_export_frame_timeout_is_incomplete(self):
        document=(ROOT/'templates/motion-design-studio-skill.md').read_text(encoding='utf-8')
        exporter=self.root/'render_frames.py'; exporter.write_text(re.search(r'```python\n(.*?)```',document,re.S).group(1),encoding='utf-8')
        target=self.root/'hang.html'; target.write_text(page(script='window.seek=function(t){if(t>0){while(true){}}};'),encoding='utf-8')
        command=[sys.executable,str(exporter),str(target),'--duration','1000','--fps','4','--output-dir',str(self.root/'hang_frames'),'--frame-timeout','5']
        if self.channel: command += ['--channel',self.channel]
        code,_,error=self.run_command(command,timeout_fails=True)
        self.assertEqual(code,3,error)
        self.assertIn('INCOMPLETE',error)
        bad=command[:-2]+['--frame-timeout','0']
        bad[bad.index('--output-dir')+1]=str(self.root/'other')
        self.assertEqual(self.run_command(bad)[0],2)


if __name__=='__main__':
    unittest.main()
