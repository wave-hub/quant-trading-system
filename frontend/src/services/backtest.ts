import { http } from './http';
import { 
    BacktestTaskCreatePayload, 
    BacktestTask, 
    BacktestTaskWithTrades,
    BacktestListResponse 
} from '../types/backtest';

export const getBacktestTasks = async (params?: { skip?: number; limit?: number }) => {
  const { data } = await http.get<BacktestListResponse>('/backtest/', { params });
  return data;
};

export const createBacktestTask = async (payload: BacktestTaskCreatePayload) => {
  const { data } = await http.post<BacktestTask>('/backtest/', payload);
  return data;
};

export const getBacktestTaskDetail = async (id: string) => {
  const { data } = await http.get<BacktestTaskWithTrades>(`/backtest/${id}`);
  return data;
};
