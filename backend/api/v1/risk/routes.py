"""Risk workflow endpoints (Step1-4)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps.db import get_db_session
from backend.schemas.risk import (
    RiskDecisionCreate,
    RiskDecisionOut,
    RiskEventCreate,
    RiskEventDetail,
    RiskEventOut,
    RiskMeasureBase,
    RiskMeasureOut,
    RiskTransitionRequest,
)
from backend.services.risk import RiskService

router = APIRouter()
service = RiskService()


def _event_to_out(e) -> RiskEventOut:
    return RiskEventOut(
        id=str(e.id),
        title=e.title,
        event_type=e.event_type,
        severity=e.severity,
        status=e.status,
        step=e.step,
        description=e.description,
        source_role=e.source_role,
        reporter_id=str(e.reporter_id) if e.reporter_id else None,
        related_account_id=str(e.related_account_id) if e.related_account_id else None,
        related_strategy_id=str(e.related_strategy_id) if e.related_strategy_id else None,
        detected_at=e.detected_at,
        resolved_at=e.resolved_at,
        metadata=e.metadata or {},
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


@router.post("/events", response_model=RiskEventOut)
async def create_event(
    payload: RiskEventCreate,
    db: AsyncSession = Depends(get_db_session),
):
    e = await service.create_event(db, **payload.model_dump())
    return _event_to_out(e)


@router.get("/events", response_model=list[RiskEventOut])
async def list_events(
    status: str | None = None,
    db: AsyncSession = Depends(get_db_session),
):
    events = await service.list_events(db, status=status)
    return [_event_to_out(e) for e in events]


@router.get("/events/{event_id}", response_model=RiskEventDetail)
async def get_event_detail(
    event_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    event, decisions, measures = await service.get_event_detail(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="risk event not found")
    return RiskEventDetail(
        **_event_to_out(event).model_dump(),
        decisions=[
            RiskDecisionOut(
                id=str(d.id),
                summary=d.summary,
                decision=d.decision,
                committee_members=d.committee_members or [],
                attachments=d.attachments or [],
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in decisions
        ],
        measures=[
            RiskMeasureOut(
                id=str(m.id),
                step=m.step,
                measure_type=m.measure_type,
                description=m.description,
                owner=m.owner,
                status=m.status,
                result=m.result,
                extra=m.extra or {},
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in measures
        ],
    )


@router.post("/events/{event_id}/decision", response_model=RiskDecisionOut)
async def add_decision(
    event_id: str,
    payload: RiskDecisionCreate,
    db: AsyncSession = Depends(get_db_session),
):
    dec = await service.add_decision(
        db,
        event_id=event_id,
        **payload.model_dump(),
    )
    return RiskDecisionOut(
        id=str(dec.id),
        summary=dec.summary,
        decision=dec.decision,
        committee_members=dec.committee_members or [],
        attachments=dec.attachments or [],
        created_at=dec.created_at,
        updated_at=dec.updated_at,
    )


@router.post("/events/{event_id}/measures", response_model=RiskMeasureOut)
async def add_measure(
    event_id: str,
    payload: RiskMeasureBase,
    db: AsyncSession = Depends(get_db_session),
):
    meas = await service.add_measure(
        db,
        event_id=event_id,
        **payload.model_dump(),
    )
    return RiskMeasureOut(
        id=str(meas.id),
        step=meas.step,
        measure_type=meas.measure_type,
        description=meas.description,
        owner=meas.owner,
        status=meas.status,
        result=meas.result,
        extra=meas.extra or {},
        created_at=meas.created_at,
        updated_at=meas.updated_at,
    )


@router.post("/events/{event_id}/transition", response_model=RiskEventOut)
async def transition_event(
    event_id: str,
    payload: RiskTransitionRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        e = await service.transition_step(
            db,
            event_id=event_id,
            to_step=payload.to_step,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _event_to_out(e)

