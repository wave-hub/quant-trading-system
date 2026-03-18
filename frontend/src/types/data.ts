export interface Stock {
  id: string;
  symbol: string;
  name: string;
  market: string;
  industry?: string;
  list_date?: string;
  is_hs?: string;
  created_at: string;
  updated_at: string;
}

export interface StockListResponse {
  total: number;
  items: Stock[];
}

export interface MarketData {
  id: string;
  symbol: string;
  trade_date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
  adj_close?: number;
  ma5?: number;
  ma20?: number;
  created_at: string;
  updated_at: string;
}

export interface MarketDataListResponse {
  total: number;
  items: MarketData[];
}
