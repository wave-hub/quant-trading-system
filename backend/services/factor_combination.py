"""Factor combination service: read inputs from factor store, combine, write output."""

from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.factor_combination.combiners import (
    combine_rank_fusion,
    combine_weighted_sum,
    fit_cross_sectional_regression,
)
from backend.core.factors.types import FactorKey
from backend.services.factors import FactorService


class FactorCombinationService:
    def __init__(self, factor_service: FactorService | None = None):
        self.factor_service = factor_service or FactorService()

    async def _read_factor_df(
        self,
        db: AsyncSession,
        *,
        name: str,
        version: int,
        as_of_date: date,
    ) -> pd.DataFrame:
        idx = await self.factor_service.get_partition_index(
            db,
            name=name,
            version=version,
            as_of_date=as_of_date,
        )
        if not idx:
            # fall back to file existence even if DB index not present
            key = FactorKey(name=name, version=version)
            if not self.factor_service.store.exists(key, as_of_date):
                raise FileNotFoundError(f"factor partition not found: {name}@v{version} {as_of_date}")
            return self.factor_service.store.read(key, as_of_date)
        key = FactorKey(name=idx.factor_name, version=idx.factor_version)
        return self.factor_service.store.read(key, idx.as_of_date)

    async def combine_and_write(
        self,
        db: AsyncSession,
        *,
        method: str,
        as_of_date: date,
        inputs: list[dict],
        output_name: str,
        output_version: int,
        weights: dict[str, float] | None = None,
        normalize_weights: bool = True,
        fill_value: float = 0.0,
        rank_method: str = "average",
        rank_ascending: bool = False,
        fill_rank: float | None = None,
        target_rows: list[dict] | None = None,
        add_intercept: bool = True,
        ridge_alpha: float = 0.0,
        metadata: dict | None = None,
    ):
        factors: dict[str, pd.DataFrame] = {}
        for ref in inputs:
            df = await self._read_factor_df(
                db,
                name=ref["name"],
                version=int(ref.get("version", 1)),
                as_of_date=as_of_date,
            )
            factors[ref["name"]] = df

        fit_info: dict = {}
        if method == "weighted_sum":
            out_df = combine_weighted_sum(
                factors,
                weights=weights or {},
                normalize_weights=normalize_weights,
                fill_value=fill_value,
            )
        elif method == "rank_fusion":
            out_df = combine_rank_fusion(
                factors,
                method=rank_method,
                ascending=rank_ascending,
                fill_rank=fill_rank,
            )
        elif method == "cross_sectional_regression":
            if not target_rows:
                raise ValueError("target_rows is required for cross_sectional_regression")
            target = pd.DataFrame(target_rows)
            fit = fit_cross_sectional_regression(
                factors,
                target=target,
                add_intercept=add_intercept,
                fill_value=fill_value,
                ridge_alpha=ridge_alpha,
            )
            fit_info = {"weights": fit.weights, "intercept": fit.intercept, "r2": fit.r2}
            out_df = combine_weighted_sum(
                factors,
                weights=fit.weights,
                normalize_weights=False,
                fill_value=fill_value,
            )
        else:
            raise ValueError("method must be one of: weighted_sum, rank_fusion, cross_sectional_regression")

        await self.factor_service.upsert_definition(
            db,
            name=output_name,
            version=output_version,
            description=(metadata or {}).get("description"),
            formula=(metadata or {}).get("formula"),
            owner=(metadata or {}).get("owner"),
            tags=(metadata or {}).get("tags") or [],
        )

        idx = await self.factor_service.write_values(
            db,
            name=output_name,
            version=output_version,
            as_of_date=as_of_date,
            rows=out_df.to_dict(orient="records"),
            metadata={
                **(metadata or {}),
                "combine_method": method,
                "inputs": inputs,
                "fit": fit_info,
            },
        )

        return idx, fit_info

