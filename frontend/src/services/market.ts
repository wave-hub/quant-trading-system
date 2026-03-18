import { http } from './http'
import type { IndicesResponse } from '../types/market'

/**
 * 获取 A 股核心大盘指数实时行情
 */
export const getIndices = async (): Promise<IndicesResponse> => {
  const { data } = await http.get<IndicesResponse>('/v1/data/market/indices')
  return data
}
