"""Factor store endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps.db import get_db_session
from backend.schemas.factors import (
    FactorDefinitionCreate,
    FactorDefinitionOut,
    FactorPartitionOut,
    FactorWritePayload,
)
from backend.services.factors import FactorService

router = APIRouter()
service = FactorService()


@router.get("/definitions", response_model=list[FactorDefinitionOut])
async def list_definitions(
    name: str | None = None,
    db: AsyncSession = Depends(get_db_session),
):
    defs = await service.list_definitions(db, name=name)
    return [
        FactorDefinitionOut(
            id=str(d.id),
            name=d.name,
            version=d.version,
            description=d.description,
            formula=d.formula,
            owner=d.owner,
            tags=d.tags or [],
        )
        for d in defs
    ]


@router.post("/definitions", response_model=FactorDefinitionOut)
async def upsert_definition(
    payload: FactorDefinitionCreate,
    db: AsyncSession = Depends(get_db_session),
):
    d = await service.upsert_definition(db, **payload.model_dump())
    return FactorDefinitionOut(
        id=str(d.id),
        name=d.name,
        version=d.version,
        description=d.description,
        formula=d.formula,
        owner=d.owner,
        tags=d.tags or [],
    )


@router.post("/values", response_model=FactorPartitionOut)
async def write_values(
    payload: FactorWritePayload,
    db: AsyncSession = Depends(get_db_session),
):
    idx = await service.write_values(
        db,
        name=payload.name,
        version=payload.version,
        as_of_date=payload.as_of_date,
        rows=payload.rows,
        metadata=payload.metadata,
    )
    return FactorPartitionOut(
        factor=idx.factor_name,
        version=idx.factor_version,
        as_of_date=idx.as_of_date,
        storage_path=idx.storage_path,
        row_count=idx.row_count,
    )


@router.get("/values/index", response_model=FactorPartitionOut)
async def get_values_index(
    name: str,
    version: int,
    as_of_date: str,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        d = __import__("datetime").datetime.fromisoformat(as_of_date).date()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid as_of_date: {e}")

    idx = await service.get_partition_index(db, name=name, version=version, as_of_date=d)
    if not idx:
        raise HTTPException(status_code=404, detail="partition not found")
    return FactorPartitionOut(
        factor=idx.factor_name,
        version=idx.factor_version,
        as_of_date=idx.as_of_date,
        storage_path=idx.storage_path,
        row_count=idx.row_count,
    )

