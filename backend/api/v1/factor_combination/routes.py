"""Factor combination endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps.db import get_db_session
from backend.schemas.factor_combination import CombineRequest, CombineResult
from backend.services.factor_combination import FactorCombinationService

router = APIRouter()
service = FactorCombinationService()


@router.post("/", response_model=CombineResult)
async def combine(
    payload: CombineRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        idx, fit = await service.combine_and_write(
            db,
            method=payload.method,
            as_of_date=payload.as_of_date,
            inputs=[x.model_dump() for x in payload.inputs],
            output_name=payload.output_name,
            output_version=payload.output_version,
            weights=payload.weights,
            normalize_weights=payload.normalize_weights,
            fill_value=payload.fill_value,
            rank_method=payload.rank_method,
            rank_ascending=payload.rank_ascending,
            fill_rank=payload.fill_rank,
            target_rows=payload.target_rows,
            add_intercept=payload.add_intercept,
            ridge_alpha=payload.ridge_alpha,
            metadata=payload.metadata,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CombineResult(
        output_name=idx.factor_name,
        output_version=idx.factor_version,
        as_of_date=idx.as_of_date,
        row_count=idx.row_count,
        storage_path=idx.storage_path,
        fit=fit,
    )

