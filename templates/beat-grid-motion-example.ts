/**
 * 音畫同步節拍網格 (Beat Grid) 渲染範例代碼
 * 支援 Remotion 與 GSAP 雙引擎卡點驅動
 * 由 tools/beat_grid.py 計算拍點影格後注入使用
 */

// 1. Remotion 影格同步範例 (React / Remotion Component)
// -------------------------------------------------------------
import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

// 假設由 BeatGridEngine(bpm=120, fps=60) 產出之拍點影格清單
export const BEAT_FRAMES = [0, 30, 60, 90, 120, 150, 180, 210, 240];
export const DOWNBEAT_FRAMES = [0, 120, 240]; // 4/4 拍第一拍小節強拍

export const BeatSyncedVideoScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 1. 尋找距離目前影格最近的前一個拍點
  const previousBeatFrame = BEAT_FRAMES.filter((f) => f <= frame).pop() ?? 0;
  const framesSinceBeat = frame - previousBeatFrame;

  // 2. 節拍脈衝 (Beat Pulse) 動畫：在拍點爆發放大，隨後平滑衰減
  const scale = interpolate(
    framesSinceBeat,
    [0, 4, 18],
    [1.0, 1.15, 1.0],
    { extrapolateRight: 'clamp' }
  );

  // 3. 小節強拍閃光轉場 (Downbeat Flash)
  const isNearDownbeat = DOWNBEAT_FRAMES.some((df) => Math.abs(frame - df) < 5);
  const flashOpacity = isNearDownbeat
    ? interpolate(Math.min(...DOWNBEAT_FRAMES.map((df) => Math.abs(frame - df))), [0, 5], [0.8, 0])
    : 0;

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: '#05070d',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* 拍點縮放卡點主標題 */}
      <h1
        style={{
          color: '#ffffff',
          fontSize: 72,
          fontWeight: 900,
          transform: `scale(${scale})`,
          fontFamily: 'Inter, sans-serif',
          letterSpacing: '-2px',
        }}
      >
        BEAT GRID SYNC
      </h1>

      {/* 強拍白色閃爍濾鏡 */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: '#ffffff',
          opacity: flashOpacity,
          pointerEvents: 'none',
        }}
      />
    </div>
  );
};


// 2. GSAP Timeline 拍點卡點範例 (Vanilla JS / Web Animation)
// -------------------------------------------------------------
import { gsap } from 'gsap';

export interface BeatCue {
  frame: number;
  time_seconds: float;
  is_downbeat: boolean;
}

export function createGsapBeatTimeline(cues: BeatCue[], targetElement: HTMLElement): gsap.core.Timeline {
  const tl = gsap.timeline({ defaults: { ease: 'power4.out' } });

  cues.forEach((cue) => {
    // 依據是否為強拍決定動態幅度
    const punchScale = cue.is_downbeat ? 1.3 : 1.1;
    const duration = cue.is_downbeat ? 0.35 : 0.2;

    tl.to(
      targetElement,
      {
        scale: punchScale,
        duration: duration * 0.3,
        ease: 'power2.out',
      },
      cue.time_seconds // 精確錨定在音訊拍點絕對秒數
    ).to(
      targetElement,
      {
        scale: 1.0,
        duration: duration * 0.7,
        ease: 'elastic.out(1, 0.4)',
      },
      cue.time_seconds + duration * 0.3
    );
  });

  return tl;
}
