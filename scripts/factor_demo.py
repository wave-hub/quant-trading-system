from __future__ import annotations

import asyncio
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.database import async_session_maker, init_db
from backend.services.factors import FactorService


async def main():
    await init_db()
    service = FactorService()

    async with async_session_maker() as db:  # type: AsyncSession
        await service.upsert_definition(
            db,
            name="demo_momentum_5d",
            version=1,
            description="Demo factor: 5d momentum",
            formula="close/close.shift(5)-1",
            owner="system",
            tags=["demo", "momentum"],
        )

        idx = await service.write_values(
            db,
            name="demo_momentum_5d",
            version=1,
            as_of_date=date.today(),
            rows=[
                {"symbol": "AAPL", "value": 0.0123},
                {"symbol": "MSFT", "value": -0.0042},
            ],
            metadata={"source": "factor_demo"},
        )

        print("WROTE:", idx.factor_name, idx.as_of_date, idx.storage_path, idx.row_count)


if __name__ == "__main__":
    asyncio.run(main())

