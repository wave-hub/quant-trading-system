"""Parquet IO helpers with graceful dependency errors."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _require_pyarrow() -> Any:
    try:
        import pyarrow  # noqa: F401
        import pyarrow.parquet as pq  # noqa: F401
        return pq
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "缺少依赖 `pyarrow`，无法读写 Parquet。"
            "请在虚拟环境中执行：python3 -m pip install -r requirements.txt"
        ) from e


def write_parquet(df: pd.DataFrame, path: str) -> None:
    pq = _require_pyarrow()
    table = __import__("pyarrow").Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, path)


def read_parquet(path: str) -> pd.DataFrame:
    pq = _require_pyarrow()
    return pq.read_table(path).to_pandas()

