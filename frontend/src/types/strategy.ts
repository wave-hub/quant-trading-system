export interface Strategy {
  id: string;
  name: string;
  description?: string;
  category?: string;
  is_visual: boolean;
  parameters: Record<string, any>;
  code: string;
  status: string;
  version: number;
  user_id: string;
  canvas_data?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface StrategyListResponse {
  total: number;
  items: Strategy[];
}

export interface StrategyCreatePayload {
  name: string;
  description?: string;
  category?: string;
  code: string;
  type: 'code' | 'visual';
  parameters?: Record<string, any>;
}

export interface StrategyUpdatePayload {
  name?: string;
  description?: string;
  category?: string;
  code?: string;
  status?: string;
  parameters?: Record<string, any>;
  canvas_data?: Record<string, any>;
}
