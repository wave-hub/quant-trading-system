import { http } from './http'

export type RiskEvent = {
  id: string
  title: string
  event_type: string
  severity: string
  status: string
  step: string
  description?: string | null
  source_role?: string | null
  reporter_id?: string | null
  related_account_id?: string | null
  related_strategy_id?: string | null
  detected_at?: string | null
  resolved_at?: string | null
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export type RiskDecision = {
  id: string
  summary: string
  decision: string
  committee_members: Array<Record<string, any>>
  attachments: Array<Record<string, any>>
  created_at: string
  updated_at: string
}

export type RiskMeasure = {
  id: string
  step: string
  measure_type: string
  description: string
  owner?: string | null
  status: string
  result?: string | null
  extra: Record<string, any>
  created_at: string
  updated_at: string
}

export type RiskEventDetail = RiskEvent & {
  decisions: RiskDecision[]
  measures: RiskMeasure[]
}

export async function listRiskEvents(status?: string): Promise<RiskEvent[]> {
  const res = await http.get('/v1/risk/events', { params: status ? { status } : {} })
  return res.data
}

export async function createRiskEvent(payload: {
  title: string
  event_type: string
  severity: string
  description?: string
  source_role?: string
  reporter_id?: string
  related_account_id?: string
  related_strategy_id?: string
  metadata?: Record<string, any>
}): Promise<RiskEvent> {
  const res = await http.post('/v1/risk/events', payload)
  return res.data
}

export async function getRiskEventDetail(eventId: string): Promise<RiskEventDetail> {
  const res = await http.get(`/v1/risk/events/${eventId}`)
  return res.data
}

export async function addRiskDecision(eventId: string, payload: Omit<RiskDecision, 'id' | 'created_at' | 'updated_at'>) {
  const res = await http.post(`/v1/risk/events/${eventId}/decision`, payload)
  return res.data as RiskDecision
}

export async function addRiskMeasure(eventId: string, payload: Omit<RiskMeasure, 'id' | 'created_at' | 'updated_at'>) {
  const res = await http.post(`/v1/risk/events/${eventId}/measures`, payload)
  return res.data as RiskMeasure
}

export async function transitionRiskEvent(eventId: string, payload: { to_step: string; operator: string; reason: string }) {
  const res = await http.post(`/v1/risk/events/${eventId}/transition`, payload)
  return res.data as RiskEvent
}

