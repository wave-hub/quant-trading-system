from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, UUID4

class StrategyBase(BaseModel):
    name: str = Field(..., max_length=100, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    category: Optional[str] = Field(None, max_length=50, description="分类标签")
    is_visual: bool = Field(False, description="是否是可视化搭建出来的策略")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="执行参数字典")

class StrategyCreate(StrategyBase):
    code: str = Field(..., description="策略核心 Python 代码")
    type: str = Field("code", description="策略类型标识")  # 前端用于区分是代码模式还是可视化

class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, max_length=20)
    canvas_data: Optional[Dict[str, Any]] = None

class StrategyResponse(StrategyBase):
    id: UUID4
    code: str
    status: str
    version: int
    user_id: UUID4
    canvas_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class StrategyListResponse(BaseModel):
    total: int
    items: List[StrategyResponse]
