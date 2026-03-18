"""Pydantic schemas for factor store APIs."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FactorDefinitionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    version: int = Field(default=1, ge=1)
    description: Optional[str] = None
    formula: Optional[str] = None
    owner: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class FactorDefinitionOut(BaseModel):
    id: str
    name: str
    version: int
    description: Optional[str] = None
    formula: Optional[str] = None
    owner: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class FactorWritePayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    version: int = Field(default=1, ge=1)
    as_of_date: date
    rows: List[Dict[str, Any]] = Field(
        description="Each row requires: symbol, value"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FactorPartitionOut(BaseModel):
    factor: str
    version: int
    as_of_date: date
    storage_path: str
    row_count: int

