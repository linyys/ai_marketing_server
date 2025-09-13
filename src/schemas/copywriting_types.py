from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class CopywritingTypeCreate(BaseModel):
    """创建文案类型请求模型"""
    name: str = Field(..., min_length=1, max_length=50, description="名称")
    prompt: str = Field(..., min_length=1, max_length=255, description="提示词")
    template: str = Field(..., min_length=1, max_length=255, description="模板")
    description: str = Field(..., min_length=1, max_length=255, description="描述")
    icon: str = Field(..., min_length=1, max_length=15, description="图标")
    updated_admin_uid: str = Field(..., description="更新管理员ID")

    @field_validator('name', 'prompt', 'template', 'description', 'icon')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('字段不能为空')
        return v

class CopywritingTypeUpdate(BaseModel):
    """更新文案类型请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="名称")
    prompt: Optional[str] = Field(None, min_length=1, max_length=255, description="提示词")
    template: Optional[str] = Field(None, min_length=1, max_length=255, description="模板")
    description: Optional[str] = Field(None, min_length=1, max_length=255, description="描述")
    icon: Optional[str] = Field(None, min_length=1, max_length=15, description="图标")
    updated_admin_uid: str = Field(..., description="更新管理员ID")

    @field_validator('name', 'prompt', 'template', 'description', 'icon')
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('字段不能为空')
        return v

class CopywritingTypeOut(BaseModel):
    """文案类型输出模型"""
    id: int
    uid: str
    name: str
    prompt: str
    template: str
    description: str
    icon: str
    updated_admin_uid: str
    is_del: int
    created_time: datetime
    updated_time: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "uid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "产品介绍文案",
                "prompt": "请为以下产品写一段介绍文案",
                "template": "产品名称：{product_name}\n产品特点：{features}",
                "description": "用于生成产品介绍的文案模板",
                "updated_admin_uid": "admin-uid-123",
                "is_del": 0,
                "created_time": "2023-01-01T12:00:00",
                "updated_time": "2023-01-01T12:00:00"
            }
        }

class CopywritingTypeListResponse(BaseModel):
    """文案类型列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[CopywritingTypeOut] = Field(..., description="文案类型列表")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")

class CopywritingTypeSearchParams(BaseModel):
    """文案类型搜索参数模型"""
    name: Optional[str] = Field(None, description="名称")
    is_del: Optional[int] = Field(None, description="是否删除：0-未删除，1-已删除")
    start_time: Optional[datetime] = Field(None, description="创建时间开始")
    end_time: Optional[datetime] = Field(None, description="创建时间结束")

class CopywritingTypeDelete(BaseModel):
    """删除文案类型请求模型"""
    updated_admin_uid: str = Field(..., description="更新管理员ID")