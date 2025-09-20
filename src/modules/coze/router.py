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


@router.post("/streaming/copywriting_create")
async def copywriting_create(
    request: Request, 
    prompt: str = Form(...),
    content: str = Form(...)
) -> controller.WorkflowResponse:
    params = {"prompt": prompt, "content": content}
    return StreamingResponse(
        streamingController.forward_sse(
            request, streamingController.get_workflow_id("copywriting_create"), params
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


@router.get("/query_workflow")
async def query_workflow(task_id: str) -> dict:
    print(task_id)
    return await controller.query_workflow(task_id)
