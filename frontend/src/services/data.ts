import { http } from './http';
import type { StockListResponse, MarketDataListResponse } from '../types/data';

export const getStocks = (params?: { skip?: number; limit?: number }) => {
  return http.get<StockListResponse>('/v1/data/market/stocks', { params }).then(res => res.data);
};

export const getMarketData = (params: { symbol: string; start_date?: string; end_date?: string }) => {
  return http.get<MarketDataListResponse>('/v1/data/market/history', { params }).then(res => res.data);
};

export const syncStocks = () => {
  return http.post<{ message: string; synced_count: number }>('/v1/data/market/sync/stocks').then(res => res.data);
};

export const syncMarketData = (data: { symbol: string; start_date?: string; end_date?: string }) => {
  return http.post<{ message: string; synced_count: number }>('/v1/data/market/sync/history', null, { params: data }).then(res => res.data);
};
