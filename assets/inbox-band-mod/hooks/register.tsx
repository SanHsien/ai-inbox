import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Counts } from '../types'

const counts = atom({ plugin: 'inbox-band', key: 'counts' } as const, null)
const isHidden = atom({ plugin: 'inbox-band', key: 'isHidden' } as const, false)
const loads = atom({ plugin: 'inbox-band', key: 'loads' } as const, 0)

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

async function refresh($: EngineInterface): Promise<void> {
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
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await update($, loads, n => (n ?? 0) + 1)
    await refresh($)
    $.clock.every(REFRESH_MS, () => refresh($))
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const c = await read($, counts)
    if (e.props.hasSurvey || c === null || (await read($, isHidden))) {
      return next(e)
    }

    const { Box, Button, Text } = $.ui.resolve(e)
    const at = new Date(c.updatedAt)
    const hhmm = `${String(at.getHours()).padStart(2, '0')}:${String(at.getMinutes()).padStart(2, '0')}`
    const inbox = c.inboxOpen === null ? '?' : `${c.inboxOpen}（未做 ${c.inboxTodo}）`
    const relay = c.relayUnread === null ? '?' : String(c.relayUnread)
    const n = await read($, loads)

    return (
      <Box>
        <Text dimColor>
          [v0.3] ai-inbox 待辦 {inbox} · relay 未讀 {relay} · {hhmm} 更新 · 第 {n} 次載入{c.error ? ` · 讀取失敗：${c.error}` : ''}{' '}
        </Text>
        <Button key="refresh" label="更新" onPress={() => refresh($)} />
        <Button key="hide" label="隱藏" onPress={() => update($, isHidden, () => true)} />
      </Box>
    )
  })
}
