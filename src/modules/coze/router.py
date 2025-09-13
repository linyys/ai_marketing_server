from fastapi import APIRouter, Form, Request, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from . import controller
from utils.auth import get_current_user
from . import streamingController
from db.database import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


router = APIRouter(tags=["coze"], prefix="/coze")

streaming_headers = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
}

@router.post("/copywriting_create")
async def copywriting_create(params: controller._copywriting_create) -> controller.WorkflowResponse:
    return await controller.copywriting_create(params)

@router.post("/prompt_generate")
async def prompt_generate(params: controller._prompt_generate) -> controller.WorkflowResponse:
    return await controller.prompt_generate(params)

@router.get("/query_workflow")
async def query_workflow(task_id: str) -> dict:
    print(task_id)
    return await controller.query_workflow(task_id)