"""Risk workflow database models."""

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID

from backend.config.database import Base
from backend.models.base import BaseModel


class RiskEvent(BaseModel, Base):
    """Top-level risk event, aligned with Step1-4 workflow."""

    __tablename__ = "risk_events"

    title = Column(String(200), nullable=False)
    event_type = Column(String(50), nullable=False)  # e.g. trading, compliance, market
    severity = Column(String(20), nullable=False)  # e.g. low/medium/high/critical
    status = Column(String(20), nullable=False, default="open")
    step = Column(String(50), nullable=False, default="step1_detected")

    description = Column(Text)
    source_role = Column(String(50))  # trader / risk_officer / etc
    reporter_id = Column(UUID(as_uuid=True), nullable=True)

    related_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    related_strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=True)

    detected_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    meta_data = Column(JSON, default=dict)


class RiskDecision(BaseModel, Base):
    """Decision record from Step2 investment/risk committee."""

    __tablename__ = "risk_decisions"

    event_id = Column(UUID(as_uuid=True), ForeignKey("risk_events.id"), index=True, nullable=False)

    summary = Column(Text, nullable=False)
    decision = Column(String(50), nullable=False)  # e.g. continue, reduce, close, hedge
    committee_members = Column(JSON, default=list)  # list of {id, name, role}
    attachments = Column(JSON, default=list)


class RiskMeasure(BaseModel, Base):
    """Concrete risk control / optimization measures (Step3 & Step4)."""

    __tablename__ = "risk_measures"

    event_id = Column(UUID(as_uuid=True), ForeignKey("risk_events.id"), index=True, nullable=False)

    step = Column(String(50), nullable=False)  # step3_execute_measures / step4_follow_up
    measure_type = Column(String(50), nullable=False)  # e.g. position_limit, stop_loss, process_fix
    description = Column(Text, nullable=False)
    owner = Column(String(128))
    status = Column(String(20), nullable=False, default="open")  # open/in_progress/done
    result = Column(Text)
    extra = Column(JSON, default=dict)

