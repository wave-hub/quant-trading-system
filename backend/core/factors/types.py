"""Factor domain types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Literal, Mapping, Sequence

import pandas as pd


FactorFrequency = Literal["1d", "1h", "1m"]


@dataclass(frozen=True)
class FactorKey:
    name: str
    version: int = 1

    def as_str(self) -> str:
        return f"{self.name}@v{self.version}"


@dataclass(frozen=True)
class FactorWriteRequest:
    key: FactorKey
    as_of_date: date
    values: pd.DataFrame
    metadata: Mapping[str, Any] | None = None

    @property
    def required_columns(self) -> Sequence[str]:
        return ("symbol", "value")

