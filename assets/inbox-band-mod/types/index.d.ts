/** 一次讀取的結果；讀不到的那一項是 null，原因寫在 error。 */
export type Counts = {
  /** ai-inbox 未做＋進行中 */
  inboxOpen: number | null
  /** ai-inbox 未做 */
  inboxTodo: number | null
  /** agent-relay 各信箱 new 的總和 */
  relayUnread: number | null
  /** 讀取完成的時間（epoch 毫秒） */
  updatedAt: number
  error: string | null
}

declare module 'claude-code' {
  interface PluginState {
    // loads：每次載入（含熱重載）加 1；模組變數在重新載入時會歸零，只有 $.state 會留下
    // refreshes：每次讀取（定時或按「更新」）加 1，讓數字沒變時也看得出有更新
    'inbox-band': { counts: Counts | null; loads: number; refreshes: number }
  }
}
