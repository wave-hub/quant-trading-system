"""Factor store metadata models (DB index)."""

from sqlalchemy import Column, Date, Integer, String, Text, UniqueConstraint, JSON

from backend.config.database import Base
from backend.models.base import BaseModel


class FactorDefinition(BaseModel, Base):
    __tablename__ = "factor_definitions"

    name = Column(String(128), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1, index=True)
    description = Column(Text)
    formula = Column(Text)
    owner = Column(String(128))
    tags = Column(JSON, default=list)

    __table_args__ = (UniqueConstraint("name", "version", name="uq_factor_name_version"),)


class FactorPartitionIndex(BaseModel, Base):
    __tablename__ = "factor_partitions"

    factor_name = Column(String(128), nullable=False, index=True)
    factor_version = Column(Integer, nullable=False, default=1, index=True)
    as_of_date = Column(Date, nullable=False, index=True)

    storage_path = Column(Text, nullable=False)
    row_count = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint(
            "factor_name",
            "factor_version",
            "as_of_date",
            name="uq_factor_partition",
        ),
    )

