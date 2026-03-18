"""Pydantic schemas for risk event workflow APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RiskMeasureBase(BaseModel):
    step: str = Field(description="step3_execute_measures or step4_follow_up")
    measure_type: str
    description: str
    owner: Optional[str] = None
    status: str = Field(default="open")
    result: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class RiskMeasureOut(RiskMeasureBase):
    id: str
    created_at: datetime
    updated_at: datetime


class RiskDecisionCreate(BaseModel):
    summary: str
    decision: str
    committee_members: List[Dict[str, Any]] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)


class RiskDecisionOut(RiskDecisionCreate):
    id: str
    created_at: datetime
    updated_at: datetime


class RiskEventCreate(BaseModel):
    title: str
    event_type: str
    severity: str
    description: Optional[str] = None
    source_role: Optional[str] = None
    reporter_id: Optional[str] = None
    related_account_id: Optional[str] = None
    related_strategy_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RiskEventOut(BaseModel):
    id: str
    title: str
    event_type: str
    severity: str
    status: str
    step: str
    description: Optional[str] = None
    source_role: Optional[str] = None
    reporter_id: Optional[str] = None
    related_account_id: Optional[str] = None
    related_strategy_id: Optional[str] = None
    detected_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class RiskEventDetail(RiskEventOut):
    decisions: List[RiskDecisionOut] = Field(default_factory=list)
    measures: List[RiskMeasureOut] = Field(default_factory=list)


class RiskTransitionRequest(BaseModel):
    to_step: str
    operator: str
    reason: str

