/**
 * 大盘指数数据类型定义
 */

/** 单条指数行情数据 */
export interface IndexData {
  code: string
  name: string
  latest_price: number
  change_amount: number
  change_percent: number
  volume: number
  turnover: number
  open_price: number
  high_price: number
  low_price: number
  prev_close: number
}

/** 指数列表响应 */
export interface IndicesResponse {
  items: IndexData[]
  total: number
}
