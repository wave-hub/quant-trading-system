"""Schemas for factor combination APIs."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


FactorRef = Dict[str, Any]


class FactorInputRef(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    version: int = Field(default=1, ge=1)


CombineMethod = Literal["weighted_sum", "rank_fusion", "cross_sectional_regression"]


class CombineRequest(BaseModel):
    method: CombineMethod
    as_of_date: date

    inputs: List[FactorInputRef] = Field(min_length=1)

    # output factor
    output_name: str = Field(min_length=1, max_length=128)
    output_version: int = Field(default=1, ge=1)

    # weighted_sum params
    weights: Dict[str, float] = Field(
        default_factory=dict,
        description="key is factor name; missing -> 1.0",
    )
    normalize_weights: bool = True
    fill_value: float = 0.0

    # rank_fusion params
    rank_method: Literal["average", "sum", "median"] = "average"
    rank_ascending: bool = False
    fill_rank: Optional[float] = None

    # regression params
    target_rows: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Required for cross_sectional_regression. Each row: symbol,value",
    )
    add_intercept: bool = True
    ridge_alpha: float = Field(default=0.0, ge=0.0)

    metadata: Dict[str, Any] = Field(default_factory=dict)


class CombineResult(BaseModel):
    output_name: str
    output_version: int
    as_of_date: date
    row_count: int
    storage_path: str
    fit: Dict[str, Any] = Field(default_factory=dict)

