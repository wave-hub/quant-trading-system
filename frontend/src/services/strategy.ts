import { http } from './http';
import type { Strategy, StrategyListResponse, StrategyCreatePayload, StrategyUpdatePayload } from '../types/strategy';

export const getStrategies = (params?: { skip?: number; limit?: number; category?: string }) => {
  return http.get<StrategyListResponse>('/v1/strategies', { params }).then(res => res.data);
};

export const getStrategyById = (id: string) => {
  return http.get<Strategy>(`/v1/strategies/${id}`).then(res => res.data);
};

export const createStrategy = (data: StrategyCreatePayload) => {
  return http.post<Strategy>('/v1/strategies', data).then(res => res.data);
};

export const updateStrategy = (id: string, data: StrategyUpdatePayload) => {
  return http.put<Strategy>(`/v1/strategies/${id}`, data).then(res => res.data);
};

export const deleteStrategy = (id: string) => {
  return http.delete(`/v1/strategies/${id}`).then(res => res.data);
};
