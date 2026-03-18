"""Risk workflow service."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.risk.workflow import (
    RiskEventStatus,
    RiskWorkflowStep,
    suggested_status_for_step,
    validate_transition,
)
from backend.models.risk import RiskDecision, RiskEvent, RiskMeasure


class RiskService:
    async def create_event(
        self,
        db: AsyncSession,
        *,
        title: str,
        event_type: str,
        severity: str,
        description: str | None = None,
        source_role: str | None = None,
        reporter_id: str | None = None,
        related_account_id: str | None = None,
        related_strategy_id: str | None = None,
        metadata: dict | None = None,
    ) -> RiskEvent:
        now = datetime.utcnow()
        event = RiskEvent(
            title=title,
            event_type=event_type,
            severity=severity,
            description=description,
            source_role=source_role,
            reporter_id=reporter_id,
            related_account_id=related_account_id,
            related_strategy_id=related_strategy_id,
            status=RiskEventStatus.OPEN.value,
            step=RiskWorkflowStep.STEP1_DETECTED.value,
            detected_at=now,
            metadata=metadata or {},
        )
        db.add(event)
        await db.flush()
        return event

    async def list_events(self, db: AsyncSession, *, status: str | None = None) -> list[RiskEvent]:
        stmt = select(RiskEvent)
        if status:
            stmt = stmt.where(RiskEvent.status == status)
        stmt = stmt.order_by(RiskEvent.created_at.desc())
        return list((await db.execute(stmt)).scalars().all())

    async def get_event(self, db: AsyncSession, event_id: str) -> RiskEvent | None:
        stmt = select(RiskEvent).where(RiskEvent.id == event_id)
        return (await db.execute(stmt)).scalars().first()

    async def add_decision(
        self,
        db: AsyncSession,
        *,
        event_id: str,
        summary: str,
        decision: str,
        committee_members: list[dict] | None = None,
        attachments: list[dict] | None = None,
    ) -> RiskDecision:
        dec = RiskDecision(
            event_id=event_id,
            summary=summary,
            decision=decision,
            committee_members=committee_members or [],
            attachments=attachments or [],
        )
        db.add(dec)
        await db.flush()
        return dec

    async def add_measure(
        self,
        db: AsyncSession,
        *,
        event_id: str,
        step: str,
        measure_type: str,
        description: str,
        owner: str | None = None,
        status: str = "open",
        result: str | None = None,
        extra: dict | None = None,
    ) -> RiskMeasure:
        meas = RiskMeasure(
            event_id=event_id,
            step=step,
            measure_type=measure_type,
            description=description,
            owner=owner,
            status=status,
            result=result,
            extra=extra or {},
        )
        db.add(meas)
        await db.flush()
        return meas

    async def get_event_detail(self, db: AsyncSession, event_id: str):
        event = await self.get_event(db, event_id)
        if not event:
            return None, [], []
        stmt_d = select(RiskDecision).where(RiskDecision.event_id == event_id)
        stmt_m = select(RiskMeasure).where(RiskMeasure.event_id == event_id)
        decisions = list((await db.execute(stmt_d)).scalars().all())
        measures = list((await db.execute(stmt_m)).scalars().all())
        return event, decisions, measures

    async def transition_step(
        self,
        db: AsyncSession,
        *,
        event_id: str,
        to_step: str,
    ) -> RiskEvent:
        event = await self.get_event(db, event_id)
        if not event:
            raise ValueError("risk event not found")
        from_step = RiskWorkflowStep(event.step)
        target_step = RiskWorkflowStep(to_step)
        validate_transition(from_step, target_step)

        event.step = target_step.value
        event.status = suggested_status_for_step(target_step).value
        if target_step == RiskWorkflowStep.STEP4_FOLLOW_UP:
            event.resolved_at = datetime.utcnow()
        await db.flush()
        return event

