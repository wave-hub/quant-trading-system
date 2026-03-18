"""Custom indicators, signals, positions and risk rules models."""

from sqlalchemy import Column, String, Text, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from backend.config.database import Base
from backend.models.base import BaseModel


class CustomIndicator(BaseModel, Base):
    """Custom indicator model."""

    __tablename__ = "custom_indicators"

    name = Column(String(100), nullable=False)
    description = Column(Text)
    formula = Column(Text, nullable=False)
    parameters = Column(JSON, default=dict)
    category = Column(String(50))
    is_public = Column(Boolean, default=False)
    author_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    usage_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<CustomIndicator(id={self.id}, name={self.name})>"


class CustomSignal(BaseModel, Base):
    """Custom signal model."""

    __tablename__ = "custom_signals"

    name = Column(String(100), nullable=False)
    description = Column(Text)
    conditions = Column(JSON, nullable=False)
    indicators = Column(JSON)
    category = Column(String(50))
    is_public = Column(Boolean, default=False)
    author_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    usage_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<CustomSignal(id={self.id}, name={self.name})>"


class CustomPosition(BaseModel, Base):
    """Custom position sizing model."""

    __tablename__ = "custom_positions"

    name = Column(String(100), nullable=False)
    description = Column(Text)
    algorithm = Column(Text, nullable=False)
    parameters = Column(JSON, default=dict)
    category = Column(String(50))
    is_public = Column(Boolean, default=False)
    author_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    usage_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<CustomPosition(id={self.id}, name={self.name})>"


class CustomRiskRule(BaseModel, Base):
    """Custom risk rule model."""

    __tablename__ = "custom_risk_rules"

    name = Column(String(100), nullable=False)
    description = Column(Text)
    rule_config = Column(JSON, nullable=False)
    rule_type = Column(String(50))
    severity = Column(String(20))
    is_public = Column(Boolean, default=False)
    author_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    usage_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<CustomRiskRule(id={self.id}, name={self.name})>"


class StrategyGroup(BaseModel, Base):
    """Strategy group model for combining strategies."""

    __tablename__ = "strategy_groups"

    name = Column(String(100), nullable=False)
    description = Column(Text)
    strategies = Column(JSON, nullable=False)
    fusion_rule = Column(JSON)
    optimization_params = Column(JSON)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    def __repr__(self):
        return f"<StrategyGroup(id={self.id}, name={self.name})>"


class RiskAlert(BaseModel, Base):
    """Risk alert model."""

    __tablename__ = "risk_alerts"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), index=True)
    alert_type = Column(String(50), nullable=False)
    message = Column(Text)
    severity = Column(String(20))
    resolved = Column(Boolean, default=False)

    def __repr__(self):
        return f"<RiskAlert(id={self.id}, type={self.alert_type}, severity={self.severity})>"
