from fastapi import APIRouter, Form, Request, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from . import controller
from utils.auth import get_current_user
from . import streamingController
from utils.workflow_config import get_workflow_id
from db.database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import logging

logger = logging.getLogger(__name__)


router = APIRouter(tags=["coze"], prefix="/coze")

streaming_headers = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
}


class CopywritingCreateRequest(BaseModel):
    prompt: str
    content: str


@router.post("/streaming/copywriting_create")
async def copywriting_create(
    request: Request,
    data: CopywritingCreateRequest
) -> StreamingResponse:
    params = {"prompt": data.prompt, "content": data.content}
    return StreamingResponse(
        streamingController.forward_sse(
            request, get_workflow_id("copywriting_create"), params
        ),
        headers=streaming_headers,
    )



class VideoAnalysisItem(BaseModel):
    desc: str
    tag_name: List[str]
    digg_count: int
    comment_count: int
    share_count: int
    collect_count: int
    recommend_count: int
    play_count: int


class VideoMarketAnalysisRequest(BaseModel):
    input: List[VideoAnalysisItem]


@router.post("/streaming/video_market_analysis")
async def video_market_analysis(
    request: Request,
    data: VideoMarketAnalysisRequest
) -> StreamingResponse:
    params = {"input": [item.model_dump() for item in data.input]}
    return StreamingResponse(
        streamingController.forward_sse(
            request, get_workflow_id("video_market_analysis"), params
        ),
        headers=streaming_headers,
    )


class MarketAnalysisVideoItem(BaseModel):
    desc: str
    look_count: int
    digg_count: int
    comment_count: int
    share_count: int


class MarketAnalysisRequest(BaseModel):
    keyword: str
    lenovo_keyword: List[str]
    video_list: List[MarketAnalysisVideoItem]


@router.post("/streaming/market_analysis")
async def market_analysis(
    request: Request,
    data: MarketAnalysisRequest
) -> StreamingResponse:
    params = {
        "keyword": data.keyword,
        "lenovo_keyword": data.lenovo_keyword,
        "video_list": [item.model_dump() for item in data.video_list],
    }
    return StreamingResponse(
        streamingController.forward_sse(
            request, get_workflow_id("market_analysis"), params
        ),
        headers=streaming_headers,
    )


@router.post("/prompt_generate")
async def prompt_generate(
    prompt_template: str = Form(...),
    requirement: str = Form(...)
) -> controller.WorkflowResponse:
    params = {"prompt_template": prompt_template, "requirement": requirement}
    return await controller.prompt_generate(params)


@router.post("/video_to_text")
async def video_to_text(
    video_url: str = Form(...)
) -> controller.WorkflowResponse:
    params = {"video_url": video_url}
    return await controller.video_to_text(params)


@router.get("/query_workflow")
async def query_workflow(task_id: str) -> dict:
    print(task_id)
    return await controller.query_workflow(task_id)
