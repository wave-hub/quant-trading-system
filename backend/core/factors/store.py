"""Factor store (Parquet primary + optional DB index)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Optional

import pandas as pd
from loguru import logger

from backend.config import get_settings

from .types import FactorKey, FactorWriteRequest
from .parquet_io import read_parquet, write_parquet


class FactorWriteMode(str, Enum):
    overwrite = "overwrite"
    append = "append"


@dataclass(frozen=True)
class FactorPartition:
    key: FactorKey
    as_of_date: date
    path: Path
    row_count: int
    written_at: datetime


class FactorStore:
    """File-backed factor store with deterministic partitioning."""

    def __init__(self, root: str | Path | None = None):
        settings = get_settings()
        self.root = Path(root or getattr(settings, "FACTOR_STORE_PATH", "data/factors"))
        self.root.mkdir(parents=True, exist_ok=True)

    def _partition_dir(self, key: FactorKey, as_of_date: date) -> Path:
        # data/factors/<factor_name>/v=<version>/date=YYYY-MM-DD/
        return (
            self.root
            / key.name
            / f"v={key.version}"
            / f"date={as_of_date.isoformat()}"
        )

    def _data_file(self, key: FactorKey, as_of_date: date) -> Path:
        return self._partition_dir(key, as_of_date) / "values.parquet"

    def _meta_file(self, key: FactorKey, as_of_date: date) -> Path:
        return self._partition_dir(key, as_of_date) / "meta.json"

    def write(
        self,
        req: FactorWriteRequest,
        mode: FactorWriteMode = FactorWriteMode.overwrite,
    ) -> FactorPartition:
        df = req.values.copy()
        missing = [c for c in req.required_columns if c not in df.columns]
        if missing:
            raise ValueError(f"factor values missing columns: {missing}")

        df = df[list(req.required_columns)]
        df["symbol"] = df["symbol"].astype(str)
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["symbol", "value"])

        part_dir = self._partition_dir(req.key, req.as_of_date)
        part_dir.mkdir(parents=True, exist_ok=True)
        data_path = self._data_file(req.key, req.as_of_date)

        if mode == FactorWriteMode.append and data_path.exists():
            existing = self.read(req.key, req.as_of_date)
            df = pd.concat([existing, df], ignore_index=True)

        write_parquet(df, str(data_path))

        meta = {
            "factor": req.key.name,
            "version": req.key.version,
            "date": req.as_of_date.isoformat(),
            "row_count": int(df.shape[0]),
            "written_at": datetime.utcnow().isoformat(),
            "metadata": req.metadata or {},
        }
        self._meta_file(req.key, req.as_of_date).write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        logger.info(
            "FactorStore wrote {} rows to {}",
            meta["row_count"],
            str(data_path),
        )
        return FactorPartition(
            key=req.key,
            as_of_date=req.as_of_date,
            path=data_path,
            row_count=int(df.shape[0]),
            written_at=datetime.fromisoformat(meta["written_at"]),
        )

    def read(self, key: FactorKey, as_of_date: date) -> pd.DataFrame:
        data_path = self._data_file(key, as_of_date)
        if not data_path.exists():
            raise FileNotFoundError(str(data_path))
        return read_parquet(str(data_path))

    def exists(self, key: FactorKey, as_of_date: date) -> bool:
        return self._data_file(key, as_of_date).exists()

    def meta(self, key: FactorKey, as_of_date: date) -> Optional[Mapping[str, Any]]:
        meta_path = self._meta_file(key, as_of_date)
        if not meta_path.exists():
            return None
        return json.loads(meta_path.read_text(encoding="utf-8"))

