"""Factor store service integrating file store and DB index."""

from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.factors.store import FactorStore, FactorWriteMode
from backend.core.factors.types import FactorKey, FactorWriteRequest
from backend.models.factor import FactorDefinition, FactorPartitionIndex


class FactorService:
    def __init__(self, store: FactorStore | None = None):
        self.store = store or FactorStore()

    async def upsert_definition(
        self,
        db: AsyncSession,
        *,
        name: str,
        version: int,
        description: str | None = None,
        formula: str | None = None,
        owner: str | None = None,
        tags: list[str] | None = None,
    ) -> FactorDefinition:
        stmt = select(FactorDefinition).where(
            FactorDefinition.name == name,
            FactorDefinition.version == version,
        )
        existing = (await db.execute(stmt)).scalars().first()
        if existing:
            existing.description = description
            existing.formula = formula
            existing.owner = owner
            existing.tags = tags or []
            await db.flush()
            return existing

        obj = FactorDefinition(
            name=name,
            version=version,
            description=description,
            formula=formula,
            owner=owner,
            tags=tags or [],
        )
        db.add(obj)
        await db.flush()
        return obj

    async def list_definitions(self, db: AsyncSession, *, name: str | None = None) -> list[FactorDefinition]:
        stmt = select(FactorDefinition)
        if name:
            stmt = stmt.where(FactorDefinition.name == name)
        stmt = stmt.order_by(FactorDefinition.name.asc(), FactorDefinition.version.desc())
        return list((await db.execute(stmt)).scalars().all())

    async def write_values(
        self,
        db: AsyncSession,
        *,
        name: str,
        version: int,
        as_of_date: date,
        rows: list[dict],
        metadata: dict | None = None,
        mode: FactorWriteMode = FactorWriteMode.overwrite,
    ) -> FactorPartitionIndex:
        df = pd.DataFrame(rows)
        key = FactorKey(name=name, version=version)
        part = self.store.write(
            FactorWriteRequest(
                key=key,
                as_of_date=as_of_date,
                values=df,
                metadata=metadata,
            ),
            mode=mode,
        )

        stmt = select(FactorPartitionIndex).where(
            FactorPartitionIndex.factor_name == name,
            FactorPartitionIndex.factor_version == version,
            FactorPartitionIndex.as_of_date == as_of_date,
        )
        existing = (await db.execute(stmt)).scalars().first()
        if existing:
            existing.storage_path = str(part.path)
            existing.row_count = part.row_count
            await db.flush()
            return existing

        idx = FactorPartitionIndex(
            factor_name=name,
            factor_version=version,
            as_of_date=as_of_date,
            storage_path=str(part.path),
            row_count=part.row_count,
        )
        db.add(idx)
        await db.flush()
        return idx

    async def get_partition_index(
        self,
        db: AsyncSession,
        *,
        name: str,
        version: int,
        as_of_date: date,
    ) -> FactorPartitionIndex | None:
        stmt = select(FactorPartitionIndex).where(
            FactorPartitionIndex.factor_name == name,
            FactorPartitionIndex.factor_version == version,
            FactorPartitionIndex.as_of_date == as_of_date,
        )
        return (await db.execute(stmt)).scalars().first()

