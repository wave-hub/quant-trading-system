import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# ========= Custom Indicator =========

class CustomIndicatorBase(BaseModel):
    name: str = Field(..., title="Indicator Name", max_length=100)
    description: Optional[str] = None
    formula: str = Field(..., title="Indicator Calculation Formula (Code)")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    category: Optional[str] = None
    is_public: bool = False

class CustomIndicatorCreate(CustomIndicatorBase):
    pass

class CustomIndicatorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    formula: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None

class CustomIndicatorResponse(CustomIndicatorBase):
    id: uuid.UUID
    author_id: uuid.UUID
    usage_count: int

    model_config = {"from_attributes": True}


# ========= Custom Signal =========

class CustomSignalBase(BaseModel):
    name: str = Field(..., title="Signal Name", max_length=100)
    description: Optional[str] = None
    conditions: Dict[str, Any] = Field(default_factory=dict, title="Signal Trigger Conditions")
    indicators: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    is_public: bool = False

class CustomSignalCreate(CustomSignalBase):
    pass

class CustomSignalUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    indicators: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None

class CustomSignalResponse(CustomSignalBase):
    id: uuid.UUID
    author_id: uuid.UUID
    usage_count: int

    model_config = {"from_attributes": True}


# ========= Custom Position =========

class CustomPositionBase(BaseModel):
    name: str = Field(..., title="Position Sizing Name", max_length=100)
    description: Optional[str] = None
    algorithm: str = Field(..., title="Position Sizing Algorithm (Code)")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    category: Optional[str] = None
    is_public: bool = False

class CustomPositionCreate(CustomPositionBase):
    pass

class CustomPositionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    algorithm: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None

class CustomPositionResponse(CustomPositionBase):
    id: uuid.UUID
    author_id: uuid.UUID
    usage_count: int

    model_config = {"from_attributes": True}

# ========= Custom Risk Rule =========

class CustomRiskRuleBase(BaseModel):
    name: str = Field(..., title="Risk Rule Name", max_length=100)
    description: Optional[str] = None
    rule_config: Dict[str, Any] = Field(..., title="Risk Rule Logic Configuration")
    rule_type: Optional[str] = None
    severity: Optional[str] = None
    is_public: bool = False

class CustomRiskRuleCreate(CustomRiskRuleBase):
    pass

class CustomRiskRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    rule_config: Optional[Dict[str, Any]] = None
    rule_type: Optional[str] = None
    severity: Optional[str] = None
    is_public: Optional[bool] = None

class CustomRiskRuleResponse(CustomRiskRuleBase):
    id: uuid.UUID
    author_id: uuid.UUID
    usage_count: int

    model_config = {"from_attributes": True}
