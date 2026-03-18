"""Risk event workflow engine: Step1-4 as in investment risk process."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal


class RiskWorkflowStep(str, Enum):
    STEP1_DETECTED = "step1_detected"  # 发现并上报
    STEP2_ASSESS_DECIDE = "step2_assess_decide"  # 召开风控/投决会评估
    STEP3_EXECUTE_MEASURES = "step3_execute_measures"  # 执行风险控制措施
    STEP4_FOLLOW_UP = "step4_follow_up"  # 优化与复盘


class RiskEventStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


ValidNextStep = {
    RiskWorkflowStep.STEP1_DETECTED: {RiskWorkflowStep.STEP2_ASSESS_DECIDE},
    RiskWorkflowStep.STEP2_ASSESS_DECIDE: {RiskWorkflowStep.STEP3_EXECUTE_MEASURES},
    RiskWorkflowStep.STEP3_EXECUTE_MEASURES: {RiskWorkflowStep.STEP4_FOLLOW_UP},
    RiskWorkflowStep.STEP4_FOLLOW_UP: set(),
}


@dataclass(frozen=True)
class WorkflowTransition:
    event_id: str
    from_step: RiskWorkflowStep
    to_step: RiskWorkflowStep
    operator: str
    reason: str
    created_at: datetime


def validate_transition(
    from_step: RiskWorkflowStep,
    to_step: RiskWorkflowStep,
) -> None:
    allowed = ValidNextStep.get(from_step, set())
    if to_step not in allowed:
        raise ValueError(f"非法的风险事件流程流转: {from_step} -> {to_step}")


def suggested_status_for_step(step: RiskWorkflowStep) -> RiskEventStatus:
    if step == RiskWorkflowStep.STEP1_DETECTED:
        return RiskEventStatus.OPEN
    if step in (RiskWorkflowStep.STEP2_ASSESS_DECIDE, RiskWorkflowStep.STEP3_EXECUTE_MEASURES):
        return RiskEventStatus.IN_PROGRESS
    return RiskEventStatus.RESOLVED


RiskRole = Literal["trader", "risk_officer", "investment_manager", "committee", "ops", "other"]

