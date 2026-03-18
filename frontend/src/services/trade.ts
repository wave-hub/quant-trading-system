import { http } from './http';
import { 
    TradeAccount, TradeAccountSummary,
    TradePosition, TradeOrder, TradeOrderPayload,
    FundPayload, FundResult
} from '../types/trade';

export const getAccounts = async () => {
  const { data } = await http.get<TradeAccount[]>('/trade/accounts');
  return data;
};

export const getAccountSummary = async (accountId: string) => {
  const { data } = await http.get<TradeAccountSummary>(`/trade/accounts/${accountId}/summary`);
  return data;
};

export const getPositions = async (accountId: string) => {
  const { data } = await http.get<TradePosition[]>(`/trade/positions/${accountId}`);
  return data;
};

export const getOrders = async (accountId: string, params?: { limit?: number }) => {
  const { data } = await http.get<TradeOrder[]>(`/trade/orders/${accountId}`, { params });
  return data;
};

export const placeOrder = async (payload: TradeOrderPayload) => {
  const { data } = await http.post<TradeOrder>('/trade/orders', payload);
  return data;
};

/**
 * 资金划拨（充值/提现）
 * @param accountId 账户 ID
 * @param payload 包含操作类型和金额
 */
export const fundAccount = async (accountId: string, payload: FundPayload): Promise<FundResult> => {
  const { data } = await http.post<FundResult>(`/trade/accounts/${accountId}/fund`, payload);
  return data;
};

