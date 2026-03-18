from __future__ import annotations

import asyncio
from datetime import date

from backend.config.database import async_session_maker, init_db
from backend.services.factor_combination import FactorCombinationService
from backend.services.factors import FactorService


async def seed_inputs(as_of: date):
    fs = FactorService()
    async with async_session_maker() as db:
        await fs.upsert_definition(
            db,
            name="demo_value",
            version=1,
            description="demo value factor",
            tags=["demo"],
        )
        await fs.upsert_definition(
            db,
            name="demo_momentum",
            version=1,
            description="demo momentum factor",
            tags=["demo"],
        )
        await fs.write_values(
            db,
            name="demo_value",
            version=1,
            as_of_date=as_of,
            rows=[
                {"symbol": "AAPL", "value": 0.2},
                {"symbol": "MSFT", "value": 0.8},
                {"symbol": "TSLA", "value": -0.1},
            ],
            metadata={"seed": True},
        )
        await fs.write_values(
            db,
            name="demo_momentum",
            version=1,
            as_of_date=as_of,
            rows=[
                {"symbol": "AAPL", "value": 1.2},
                {"symbol": "MSFT", "value": -0.4},
                {"symbol": "TSLA", "value": 0.3},
            ],
            metadata={"seed": True},
        )


async def run():
    await init_db()
    as_of = date.today()
    await seed_inputs(as_of)

    svc = FactorCombinationService()
    async with async_session_maker() as db:
        # A) weighted sum
        idx, fit = await svc.combine_and_write(
            db,
            method="weighted_sum",
            as_of_date=as_of,
            inputs=[{"name": "demo_value", "version": 1}, {"name": "demo_momentum", "version": 1}],
            output_name="demo_combo_weighted",
            output_version=1,
            weights={"demo_value": 0.7, "demo_momentum": 0.3},
            metadata={"description": "weighted demo combo"},
        )
        print("weighted:", idx.storage_path, idx.row_count, fit)

        # C) rank fusion
        idx, fit = await svc.combine_and_write(
            db,
            method="rank_fusion",
            as_of_date=as_of,
            inputs=[{"name": "demo_value", "version": 1}, {"name": "demo_momentum", "version": 1}],
            output_name="demo_combo_rank",
            output_version=1,
            rank_method="average",
            metadata={"description": "rank fusion demo combo"},
        )
        print("rank:", idx.storage_path, idx.row_count, fit)

        # B) cross-sectional regression (target: next-day returns mock)
        idx, fit = await svc.combine_and_write(
            db,
            method="cross_sectional_regression",
            as_of_date=as_of,
            inputs=[{"name": "demo_value", "version": 1}, {"name": "demo_momentum", "version": 1}],
            output_name="demo_combo_reg",
            output_version=1,
            target_rows=[
                {"symbol": "AAPL", "value": 0.01},
                {"symbol": "MSFT", "value": -0.02},
                {"symbol": "TSLA", "value": 0.03},
            ],
            ridge_alpha=1e-6,
            metadata={"description": "regression-weighted demo combo"},
        )
        print("reg:", idx.storage_path, idx.row_count, fit)


if __name__ == "__main__":
    asyncio.run(run())

