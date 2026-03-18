import { http } from './http';
import { 
    CustomIndicator, CustomIndicatorCreatePayload,
    CustomSignal, CustomSignalCreatePayload,
    CustomPosition, CustomPositionCreatePayload,
    CustomRiskRule, CustomRiskRuleCreatePayload,
    CustomComponentListResponse 
} from '../types/custom';

// ================= Indicators =================
export const getIndicators = async (params?: { skip?: number; limit?: number; category?: string }) => {
  const { data } = await http.get<CustomComponentListResponse<CustomIndicator>>('/custom/indicators', { params });
  return data;
};

export const createIndicator = async (payload: CustomIndicatorCreatePayload) => {
  const { data } = await http.post<CustomIndicator>('/custom/indicators', payload);
  return data;
};

export const updateIndicator = async (id: string, payload: Partial<CustomIndicatorCreatePayload>) => {
  const { data } = await http.put<CustomIndicator>(`/custom/indicators/${id}`, payload);
  return data;
};

export const deleteIndicator = async (id: string) => {
  const { data } = await http.delete(`/custom/indicators/${id}`);
  return data;
};

// ================= Signals =================
export const getSignals = async (params?: { skip?: number; limit?: number; category?: string }) => {
  const { data } = await http.get<CustomComponentListResponse<CustomSignal>>('/custom/signals', { params });
  return data;
};

export const createSignal = async (payload: CustomSignalCreatePayload) => {
  const { data } = await http.post<CustomSignal>('/custom/signals', payload);
  return data;
};

export const updateSignal = async (id: string, payload: Partial<CustomSignalCreatePayload>) => {
  const { data } = await http.put<CustomSignal>(`/custom/signals/${id}`, payload);
  return data;
};

export const deleteSignal = async (id: string) => {
  const { data } = await http.delete(`/custom/signals/${id}`);
  return data;
};

// ================= Positions =================
export const getPositions = async (params?: { skip?: number; limit?: number; category?: string }) => {
  const { data } = await http.get<CustomComponentListResponse<CustomPosition>>('/custom/positions', { params });
  return data;
};

export const createPosition = async (payload: CustomPositionCreatePayload) => {
  const { data } = await http.post<CustomPosition>('/custom/positions', payload);
  return data;
};

export const updatePosition = async (id: string, payload: Partial<CustomPositionCreatePayload>) => {
  const { data } = await http.put<CustomPosition>(`/custom/positions/${id}`, payload);
  return data;
};

export const deletePosition = async (id: string) => {
  const { data } = await http.delete(`/custom/positions/${id}`);
  return data;
};

// ================= Risk Rules =================
export const getRiskRules = async (params?: { skip?: number; limit?: number; category?: string }) => {
  const { data } = await http.get<CustomComponentListResponse<CustomRiskRule>>('/custom/risk-rules', { params });
  return data;
};

export const createRiskRule = async (payload: CustomRiskRuleCreatePayload) => {
  const { data } = await http.post<CustomRiskRule>('/custom/risk-rules', payload);
  return data;
};

export const updateRiskRule = async (id: string, payload: Partial<CustomRiskRuleCreatePayload>) => {
  const { data } = await http.put<CustomRiskRule>(`/custom/risk-rules/${id}`, payload);
  return data;
};

export const deleteRiskRule = async (id: string) => {
  const { data } = await http.delete(`/custom/risk-rules/${id}`);
  return data;
};
