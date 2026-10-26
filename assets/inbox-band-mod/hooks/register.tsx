import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Counts } from '../types'

const counts = atom({ plugin: 'inbox-band', key: 'counts' } as const, null)
const loads = atom({ plugin: 'inbox-band', key: 'loads' } as const, 0)
const refreshes = atom({ plugin: 'inbox-band', key: 'refreshes' } as const, 0)

const README = 'C:/GitHub/ai-inbox/README.md'
const REFRESH_MS = 60_000
// README 由 build_index.py 產生的統計行：> 共 86 項任務：🔴 未做 1／🟡 進行中 0／…
const STATS = /🔴 未做 (\d+)／🟡 進行中 (\d+)/

async function readInbox($: EngineInterface): Promise<{ todo: number; open: number }> {
  const text = await $.fs.read(README)
  const m = STATS.exec(text)
  if (!m) throw new Error('README 找不到任務統計行')
  const todo = Number(m[1])
  return { todo, open: todo + Number(m[2]) }
}

async function readRelay($: EngineInterface): Promise<number> {
  // --no-sync：只讀本機信箱，不做 git pull／push（每分鐘跑一次不能碰網路）
  const r = await $.process.run(['python', '-m', 'agent_relay', 'status', '--json', '--no-sync'], {
    timeoutMs: 15_000,
  })
  if (r.exitCode !== 0) throw new Error(`agent_relay status exit ${r.exitCode}`)
  const data = JSON.parse(r.stdout) as { mailboxes: Record<string, { new: number }> }
  return Object.values(data.mailboxes).reduce((sum, box) => sum + box.new, 0)
}

function hhmmss(ms: number): string {
  const at = new Date(ms)
  return [at.getHours(), at.getMinutes(), at.getSeconds()].map(n => String(n).padStart(2, '0')).join(':')
}

function summary(c: Counts): string {
  const inbox = c.inboxOpen === null ? '?' : `${c.inboxOpen}（未做 ${c.inboxTodo}）`
  const relay = c.relayUnread === null ? '?' : String(c.relayUnread)
  return `ai-inbox 待辦 ${inbox} · relay 未讀 ${relay}`
}

async function refresh($: EngineInterface): Promise<Counts> {
  const errors: string[] = []
  const inbox = await readInbox($).catch((err: unknown) => {
    errors.push(`ai-inbox：${String(err)}`)
    return null
  })
  const relay = await readRelay($).catch((err: unknown) => {
    errors.push(`relay：${String(err)}`)
    return null
  })
  const next: Counts = {
    inboxOpen: inbox?.open ?? null,
    inboxTodo: inbox?.todo ?? null,
    relayUnread: relay,
    updatedAt: await $.clock.now(),
    error: errors.length ? errors.join('；') : null,
  }
  await update($, counts, () => next)
  await update($, refreshes, n => (n ?? 0) + 1)
  return next
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await update($, loads, n => (n ?? 0) + 1)
    await refresh($)
    $.clock.every(REFRESH_MS, () => refresh($))
    return next(e)
  })

  // 不放「隱藏」鈕：選項框出現時按 Enter／數字鍵會誤觸，隱藏後又沒有辦法叫回來
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const c = await read($, counts)
    if (e.props.hasSurvey || c === null) {
      return next(e)
    }

    const { Box, Button, Text } = $.ui.resolve(e)
    const n = await read($, loads)
    const k = await read($, refreshes)

    // 「第 N 次載入」只在 mod 重新載入時變；每次讀取（含按「更新」）變的是「第 N 次更新」與秒數
    return (
      <Box>
        <Text dimColor>
          [v0.4] {summary(c)} · {hhmmss(c.updatedAt)} 第 {k} 次更新 · 第 {n} 次載入{c.error ? ` · 讀取失敗：${c.error}` : ''}{' '}
        </Text>
        <Button
          key="refresh"
          label="更新"
          onPress={async () => {
            const r = await refresh($)
            const times = await read($, refreshes)
            // 數字沒變時畫面看不出差別，用 toast 回報按下去有作用
            $.ui.toast(r.error ? `更新失敗：${r.error}` : `已更新（第 ${times} 次）：${summary(r)}`)
          }}
        />
      </Box>
    )
  })
}
