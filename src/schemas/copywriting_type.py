from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CopywritingTypeBase(BaseModel):
    name: str = Field(..., max_length=50, description="名称")
    prompt: str = Field(..., max_length=255, description="提示词")
    template: str = Field(..., max_length=255, description="模板")
    description: str = Field(..., max_length=255, description="描述")


class CopywritingTypeCreate(CopywritingTypeBase):
    pass


class CopywritingTypeUpdate(CopywritingTypeBase):
    pass


class CopywritingTypeOut(CopywritingTypeBase):
    id: int
    uid: str
    created_time: datetime
    updated_time: datetime
    updated_user_id: str

    class Config:
        orm_mode = True


class CopywritingTypeSearchParams(BaseModel):
    name: Optional[str] = Field(None, description="名称")
    page: int = 1
    page_size: int = 10