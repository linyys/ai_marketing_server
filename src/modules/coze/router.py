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

# 新增导入：积分服务与流式包装器、任务管理器
from utils.point_service import PointService
from utils.streaming_point_middleware import wrap_sse_with_point_deduction
from modules.coze.task_manager import global_task_manager
import json

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
    data: CopywritingCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> StreamingResponse:
    params = {"prompt": data.prompt, "content": data.content}
    workflow_id = get_workflow_id("copywriting_create")
    # 事前校验（流式）
    PointService.check_streaming_workflow_points(db, current_user, workflow_id)

    upstream = streamingController.forward_sse(request, workflow_id, params)
    wrapped = wrap_sse_with_point_deduction(
        upstream, db, current_user.uid, workflow_id
    )
    return StreamingResponse(
        wrapped,
        headers=streaming_headers,
    )


class VideoMarketAnalysisItem(BaseModel):
    desc: str
    tag_name: List[str]
    digg_count: int
    comment_count: int
    share_count: int
    collect_count: int
    recommend_count: int
    play_count: int


class VideoMarketAnalysisRequest(BaseModel):
    input: List[VideoMarketAnalysisItem]


@router.post("/streaming/video_market_analysis")
async def video_market_analysis(
    request: Request,
    data: VideoMarketAnalysisRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> StreamingResponse:
    params = {"input": [item.model_dump() for item in data.input]}
    workflow_id = get_workflow_id("video_market_analysis")
    # 事前校验（流式）
    PointService.check_streaming_workflow_points(db, current_user, workflow_id)

    upstream = streamingController.forward_sse(request, workflow_id, params)
    wrapped = wrap_sse_with_point_deduction(
        upstream, db, current_user.uid, workflow_id
    )
    return StreamingResponse(
        wrapped,
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
    data: MarketAnalysisRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> StreamingResponse:
    params = {
        "keyword": data.keyword,
        "lenovo_keyword": data.lenovo_keyword,
        "video_list": [item.model_dump() for item in data.video_list],
    }
    workflow_id = get_workflow_id("market_analysis")
    # 事前校验（流式）
    PointService.check_streaming_workflow_points(db, current_user, workflow_id)

    upstream = streamingController.forward_sse(request, workflow_id, params)
    wrapped = wrap_sse_with_point_deduction(
        upstream, db, current_user.uid, workflow_id
    )
    return StreamingResponse(
        wrapped,
        headers=streaming_headers,
    )


@router.post("/prompt_generate")
async def prompt_generate(
    prompt_template: str = Form(...),
    requirement: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> controller.WorkflowResponse:
    params = {"prompt_template": prompt_template, "requirement": requirement}
    workflow_id = get_workflow_id("prompt_generate")
    # 非流式事前校验
    PointService.check_non_streaming_workflow_points(db, current_user, workflow_id)
    return await controller.prompt_generate(params)


@router.post("/video_to_text")
async def video_to_text(
    video_url: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> controller.WorkflowResponse:
    params = {"video_url": video_url}
    workflow_id = get_workflow_id("video_to_text")
    # 非流式事前校验
    PointService.check_non_streaming_workflow_points(db, current_user, workflow_id)
    return await controller.video_to_text(params)


@router.get("/query_workflow")
async def query_workflow(task_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    # 先读取 workflow_id（controller 内部成功后会删除 task）
    workflow_id = global_task_manager.get_workflow_id(task_id)
    resp = await controller.query_workflow(task_id)

    # 成功返回时进行非流式扣费（不允许负数）
    try:
        if resp.get("code") == 0 and workflow_id:
            # 将输出转为字符串进行计量（按字符）
            # 注意：若配置为按次或按分钟，服务层会自动处理单位
            output_str = json.dumps(resp.get("data"), ensure_ascii=False)
            PointService.consume_points_by_response(
                db=db,
                user_uid=current_user.uid,
                from_user_uid=current_user.uid,
                workflow_id=workflow_id,
                response_text=output_str,
                allow_negative=False,
                record_desc_prefix=f"非流式扣费: workflow_id={workflow_id}",
            )
    except Exception:
        # 扣费失败不影响查询响应，但应在日志系统记录
        pass

    return resp
