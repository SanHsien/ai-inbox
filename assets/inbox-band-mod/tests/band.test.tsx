import { expect, test } from 'claude-code/testing'

const README = '> 共 86 項任務：🔴 未做 2／🟡 進行中 1／🟢 已做 69／⚪ 不做 14\n'
const STATUS = JSON.stringify({ mailboxes: { commander: { new: 3, cur: 1 }, claude: { new: 1, cur: 0 } } })

const BAND = {
  plugin: 'inbox-band',
  component: 'AbovePrompt',
  requestId: 'band',
  props: {
    hasSurvey: false,
    isWorking: false,
    maxRows: 5,
    bodyColumns: 100,
    scroll: { offset: 0, bodyRows: 5 },
    view: {},
  },
} as const

type On = Parameters<Parameters<typeof test>[1]>[1]

// 測試環境沒有檔案系統也不能執行程式：這些 hook 扮演引擎回答 $ 的呼叫
function engine(on: On, opts: { readme?: string; relayExit?: number } = {}) {
  const calls: string[][] = []
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('clock.now', () => ({ value: Date.UTC(2026, 9, 26, 1, 5) }))
  on('clock.every', () => ({ value: undefined }))
  on('fs.read', (_, e) => {
    if (opts.readme === undefined) return { value: README }
    return { value: opts.readme }
  })
  on('process.run', (_, e) => {
    calls.push([...e.argv])
    return {
      value: {
        exitCode: opts.relayExit ?? 0,
        stdout: STATUS,
        stderr: '',
        isStdoutTruncated: false,
        isStderrTruncated: false,
      },
    }
  })
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>engine</Text>
  })
  return calls
}

test('畫出 ai-inbox 待辦數與 relay 未讀數，各個介面都一樣', async ($, on) => {
  const calls = engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of ['terminal', 'desktop', 'vscode', 'mobile'] as const) {
    const ui = await $.ui.mount({ ...BAND, surface })
    const row = await ui.find({ type: 'Text', text: /ai-inbox/ })
    expect(row?.text).toMatch(/^\[v0\.4\] ai-inbox 待辦 3（未做 2） · relay 未讀 4 · \d\d:\d\d:\d\d 第 \d+ 次更新 · 第 1 次載入/)
    await ui.unmount()
  }
  // 每分鐘都會跑，所以一定要 --no-sync，不可做 git pull／push
  expect(calls[0]).toEqual(['python', '-m', 'agent_relay', 'status', '--json', '--no-sync'])
})

test('讀不到時顯示問號與原因，不會整條消失', async ($, on) => {
  engine(on, { readme: '沒有統計行', relayExit: 1 })
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const row = await ui.find({ type: 'Text', text: /ai-inbox/ })
  expect(row?.text).toMatch(/ai-inbox 待辦 \? · relay 未讀 \?/)
  expect(row?.text).toMatch(/讀取失敗：ai-inbox：.*README 找不到任務統計行；relay：.*exit 1/)
  await ui.unmount()
})

test('按「更新」重新讀取並用 toast 回報結果', async ($, on) => {
  const calls = engine(on)
  const toasts: string[] = []
  on('ui.toast', (_, e) => {
    toasts.push(e.text)
    return { value: undefined }
  })
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  // 測試環境的定時器也會觸發讀取，所以比「按之前／之後」，不比絕對次數
  const times = async () => Number(/第 (\d+) 次更新/.exec((await ui.find({ type: 'Text', text: /ai-inbox/ }))?.text ?? '')?.[1])
  const before = await times()
  const runsBefore = calls.length
  await ui.press({ key: 'refresh' })
  expect(calls.length).toBeGreaterThan(runsBefore)
  // 數字沒變也要看得出按下去有作用：更新次數變大，並跳 toast
  expect(await times()).toBeGreaterThan(before)
  expect(toasts.length).toBe(1)
  expect(toasts[0]).toMatch(/^已更新（第 \d+ 次）：ai-inbox 待辦 3（未做 2） · relay 未讀 4$/)
  await ui.unmount()
})

test('選項框占用時讓位，結束後 band 回來', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const survey = await $.ui.mount({ ...BAND, surface: 'desktop', props: { ...BAND.props, hasSurvey: true } })
  expect(await survey.find({ type: 'Text', text: /ai-inbox/ })).toBeUndefined()
  await survey.unmount()

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ type: 'Text', text: /ai-inbox/ })).toBeDefined()
  await ui.unmount()
})
