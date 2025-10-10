from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class KnowledgeCreate(BaseModel):
    """创建知识库请求模型"""
    name: str = Field(..., min_length=1, max_length=50, description="名称")
    content: str = Field(..., min_length=1, description="内容")
    description: str = Field(..., min_length=1, max_length=255, description="描述")
    type: int = Field(0, ge=0, le=1, description="类型：0-文字，1-文件")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('名称不能为空')
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('内容不能为空')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('描述不能为空')
        return v

class KnowledgeUpdate(BaseModel):
    """更新知识库请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="名称")
    content: Optional[str] = Field(None, min_length=1, description="内容")
    description: Optional[str] = Field(None, min_length=1, max_length=255, description="描述")
    type: Optional[int] = Field(None, ge=0, le=1, description="类型：0-文字，1-文件")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('名称不能为空')
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('内容不能为空')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('描述不能为空')
        return v

class KnowledgeOut(BaseModel):
    """知识库输出模型"""
    id: int
    uid: str
    name: str
    content: str
    description: str
    type: int
    from_user: Optional[str]
    created_time: datetime
    updated_time: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "uid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "产品介绍",
                "content": "这是一个优秀的产品...",
                "description": "产品相关知识库",
                "type": 0,
                "from_user": "user-uid-123",
                "created_time": "2023-01-01T12:00:00",
                "updated_time": "2023-01-01T12:00:00"
            }
        }

class KnowledgeListResponse(BaseModel):
    """知识库列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[KnowledgeOut] = Field(..., description="知识库列表")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")

class KnowledgeSearchParams(BaseModel):
    """知识库搜索参数模型"""
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    from_user: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class PaginationParams(BaseModel):
    """分页参数模型"""
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(20, ge=1, le=100, description="返回记录数限制")

class KnowledgeUidListResponse(BaseModel):
    """知识库UID列表响应模型"""
    knowledge_uids: List[str] = Field(..., description="知识库UID列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "knowledge_uids": ["550e8400-e29b-41d4-a716-446655440000", "660e8400-e29b-41d4-a716-446655440001"]
            }
        }